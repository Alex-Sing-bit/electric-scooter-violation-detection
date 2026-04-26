package com.scooter.violation.processing_service.service;

import com.scooter.violation.processing_service.dto.ViolationDTO;
import com.scooter.violation.processing_service.dto.ViolationFrameDTO;
import com.scooter.violation.processing_service.entity.ViolationFrame;
import com.scooter.violation.processing_service.repository.ViolationFrameRepository;
import com.scooter.violation.processing_service.repository.ViolationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ViolationFrameService {

    private final ViolationFrameRepository repository;
    private final ViolationRepository violationRepository;

    public List<ViolationFrameDTO> getAllFrames() {
        return repository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public List<ViolationDTO> getViolationsByFrameId(UUID frameId) {
        return violationRepository.findByFrameId(frameId).stream().map(this::toViolationDTO).collect(Collectors.toList());
    }

    private ViolationFrameDTO toDTO(ViolationFrame entity) {
        ViolationFrameDTO dto = new ViolationFrameDTO();
        dto.setId(entity.getId());
        dto.setTaskId(entity.getTask().getId());
        dto.setFramePath(entity.getFramePath());
        dto.setFrameNumber(entity.getFrameNumber());
        dto.setTimestampInVideo(entity.getTimestampInVideo());
        return dto;
    }

    private ViolationDTO toViolationDTO(com.scooter.violation.processing_service.entity.Violation entity) {
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
