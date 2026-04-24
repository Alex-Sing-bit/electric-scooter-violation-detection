package com.scooter.violation.processing_service.service;

import com.scooter.violation.processing_service.entity.AnalysisTask;
import com.scooter.violation.processing_service.entity.ViolationStatus;
import com.scooter.violation.processing_service.repository.AnalysisTaskRepository;
import io.minio.MinioClient;
import io.minio.StatObjectArgs;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisService {

    private final AnalysisTaskRepository analysisTaskRepository;
    private final MinioClient minioClient;
    private final StringRedisTemplate redisTemplate;

    private final String BUCKET_NAME = "scooter-violations";
    private final String QUEUE_NAME = "task_queue";

    @Transactional
    public void startAnalysis(UUID violationId) {
        AnalysisTask analysisTask = analysisTaskRepository.findById(violationId)
                .orElseThrow(() -> new RuntimeException("Нарушение не найдено"));

        try {
            minioClient.statObject(
                    StatObjectArgs.builder()
                            .bucket(BUCKET_NAME)
                            .object(analysisTask.getFilePath())
                            .build()
            );
            log.info("Файл найден в MinIO: {}", analysisTask.getFilePath());
        } catch (Exception e) {
            log.error("Файл не найден в MinIO: {}", analysisTask.getFilePath());
            throw new RuntimeException("Файл еще не загружен в облако");
        }

        analysisTask.setStatus(ViolationStatus.PROCESSING);
        analysisTask.setStartedAt(LocalDateTime.now());
        analysisTaskRepository.save(analysisTask);

        redisTemplate.opsForList().leftPush(QUEUE_NAME, violationId.toString());

        log.info("Задача отправлена в Redis. ID: {}", violationId);
    }
}