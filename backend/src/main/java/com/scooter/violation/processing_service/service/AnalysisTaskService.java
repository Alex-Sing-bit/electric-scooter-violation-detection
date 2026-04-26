package com.scooter.violation.processing_service.service;

import com.scooter.violation.processing_service.dto.AnalysisTaskDTO;
import com.scooter.violation.processing_service.dto.ViolationDTO;
import com.scooter.violation.processing_service.dto.ViolationFrameDTO;
import com.scooter.violation.processing_service.entity.AnalysisTask;
import com.scooter.violation.processing_service.entity.Violation;
import com.scooter.violation.processing_service.entity.ViolationFrame;
import com.scooter.violation.processing_service.entity.ViolationStatus;
import com.scooter.violation.processing_service.repository.AnalysisTaskRepository;
import com.scooter.violation.processing_service.repository.ViolationFrameRepository;
import com.scooter.violation.processing_service.repository.ViolationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AnalysisTaskService {

    private final AnalysisTaskRepository repository;
    private final ViolationFrameRepository frameRepository;
    private final ViolationRepository violationRepository;

    public List<AnalysisTaskDTO> getAllTasks() {
        return repository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public List<AnalysisTaskDTO> getTasksByStatus(ViolationStatus status) {
        return repository.findByStatus(status).stream().map(this::toDTO).collect(Collectors.toList());
    }

    public List<ViolationFrameDTO> getFramesByTaskId(UUID taskId) {
        return frameRepository.findByTaskId(taskId).stream().map(this::toFrameDTO).collect(Collectors.toList());
    }

    public List<ViolationDTO> getViolationsByTaskId(UUID taskId) {
        return violationRepository.findByTaskId(taskId).stream().map(this::toViolationDTO).collect(Collectors.toList());
    }

    private AnalysisTaskDTO toDTO(AnalysisTask entity) {
        AnalysisTaskDTO dto = new AnalysisTaskDTO();
        dto.setId(entity.getId());
        dto.setFilePath(entity.getFilePath());
        dto.setStatus(entity.getStatus());
        dto.setVideoDuration(entity.getVideoDuration());
        dto.setFps(entity.getFps());
        dto.setStartedAt(entity.getStartedAt());
        dto.setCompletedAt(entity.getCompletedAt());
        return dto;
    }

    private ViolationFrameDTO toFrameDTO(ViolationFrame entity) {
        ViolationFrameDTO dto = new ViolationFrameDTO();
        dto.setId(entity.getId());
        dto.setTaskId(entity.getTask().getId());
        dto.setFramePath(entity.getFramePath());
        dto.setFrameNumber(entity.getFrameNumber());
        dto.setTimestampInVideo(entity.getTimestampInVideo());
        return dto;
    }

    private ViolationDTO toViolationDTO(Violation entity) {
        ViolationDTO dto = new ViolationDTO();
        dto.setId(entity.getId());
        dto.setTaskId(entity.getTask().getId());
        if(entity.getFrame() != null) dto.setFrameId(entity.getFrame().getId());
        dto.setType(entity.getType());
        dto.setTimestampInVideo(entity.getTimestampInVideo());
        dto.setFrameNumber(entity.getFrameNumber());
        dto.setDuration(entity.getDuration());
        return dto;
    }
}
