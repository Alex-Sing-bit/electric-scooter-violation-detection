package com.scooter.violation.processing_service.messaging;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.scooter.violation.processing_service.entity.AnalysisTask;
import com.scooter.violation.processing_service.entity.Violation;
import com.scooter.violation.processing_service.entity.ViolationFrame;
import com.scooter.violation.processing_service.entity.ViolationStatus;
import com.scooter.violation.processing_service.repository.ViolationFrameRepository;
import com.scooter.violation.processing_service.repository.AnalysisTaskRepository;
import com.scooter.violation.processing_service.repository.ViolationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
@Slf4j
public class RedisResultListener {

    private final AnalysisTaskRepository analysisTaskRepository;
    private final ViolationFrameRepository frameRepository;
    private final ViolationRepository violationRepository;
    private final ObjectMapper objectMapper;
    private final StringRedisTemplate redisTemplate;

    private final String FINISHED_QUEUE = "finished_queue";

    @Scheduled(fixedDelay = 1000)
    public void listenResults() {
        String rawMessage = redisTemplate.opsForList().rightPop(FINISHED_QUEUE, Duration.ofSeconds(1));

        if (rawMessage == null) return;

        try {
            AnalysisResultMessage message = objectMapper.readValue(rawMessage, AnalysisResultMessage.class);
            processResults(message);
        } catch (Exception e) {
            log.error("Ошибка при обработке результата из Redis: {}", e.getMessage());
        }
    }

    @Transactional
    public void processResults(AnalysisResultMessage message) {
        AnalysisTask analysisTask = analysisTaskRepository.findById(message.getId())
                .orElseThrow(() -> new RuntimeException("Violation not found"));

        if ("COMPLETED".equals(message.getStatus())) {
            analysisTask.setStatus(ViolationStatus.COMPLETED);
            analysisTask.setFps(message.getFps());
            analysisTask.setVideoDuration(message.getVideo_duration());

            if (message.getViolations() != null) {
                for (var frameData : message.getViolations()) {
                    updateFrame(frameData, analysisTask);
                }
            }

            analysisTask.setCompletedAt(LocalDateTime.now());
            analysisTaskRepository.save(analysisTask);
            log.info("Результаты для ID {} успешно сохранены в БД", message.getId());
        } else {
            analysisTask.setStatus(ViolationStatus.FAILED);
            analysisTask.setCompletedAt(LocalDateTime.now());
            log.error("Задача {} завершилась с ошибкой", analysisTask.getId());
        }
    }

    private void updateFrame(AnalysisResultMessage.ViolationFrameData frameData, AnalysisTask analysisTask) {
        ViolationFrame frame = new ViolationFrame();
        frame.setTask(analysisTask);

        frame.setFramePath(frameData.getMinio_path());
        frame.setFrameNumber(frameData.getFrame());
        frame.setTimestampInVideo(frameData.getTimestamp());
        ViolationFrame savedFrame = frameRepository.save(frame);

        if (frameData.getViolations() != null && !frameData.getViolations().isEmpty()) {
            for (String violationType : frameData.getViolations()) {
                updateViolation(frameData, violationType, savedFrame, analysisTask);
            }
        }
    }


    private void updateViolation(AnalysisResultMessage.ViolationFrameData frameData, String violationType,
                                 ViolationFrame savedFrame, AnalysisTask analysisTask) {
        Violation violation = new Violation();

        violation.setTask(analysisTask);

        violation.setFrame(savedFrame);

        violation.setType(violationType);

        violation.setTimestampInVideo(frameData.getTimestamp());
        violation.setFrameNumber(frameData.getFrame());
        violation.setDuration(frameData.getDuration());

        violationRepository.save(violation);
    }
}