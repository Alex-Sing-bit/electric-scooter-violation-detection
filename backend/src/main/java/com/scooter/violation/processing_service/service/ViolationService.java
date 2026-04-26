package com.scooter.violation.processing_service.service;

import com.scooter.violation.processing_service.dto.ViolationDTO;
import com.scooter.violation.processing_service.entity.Violation;
import com.scooter.violation.processing_service.repository.ViolationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ViolationService {
    private final ViolationRepository violationRepository;

    public void create(ViolationDTO dto) {
        Violation entity = toEntity(dto);
        violationRepository.save(entity);
    }

    public List<ViolationDTO> readAll() {
        return violationRepository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public List<ViolationDTO> readByType(String type) {
        return violationRepository.findByType(type).stream().map(this::toDTO).collect(Collectors.toList());
    }

    public ViolationDTO read(UUID id) {
        return violationRepository.findById(id).map(this::toDTO).orElse(null);
    }

    public boolean update(ViolationDTO dto, UUID id) {
        if (violationRepository.existsById(id)) {
            Violation entity = toEntity(dto);
            entity.setId(id);
            violationRepository.save(entity);
            return true;
        }
        return false;
    }

    public boolean delete(UUID id) {
        if (violationRepository.existsById(id)) {
            violationRepository.deleteById(id);
            return true;
        }
        return false;
    }

    private ViolationDTO toDTO(Violation entity) {
        ViolationDTO dto = new ViolationDTO();
        dto.setId(entity.getId());
        if (entity.getTask() != null) dto.setTaskId(entity.getTask().getId());
        if (entity.getFrame() != null) dto.setFrameId(entity.getFrame().getId());
        dto.setType(entity.getType());
        dto.setTimestampInVideo(entity.getTimestampInVideo());
        dto.setFrameNumber(entity.getFrameNumber());
        dto.setDuration(entity.getDuration());
        return dto;
    }

    private Violation toEntity(ViolationDTO dto) {
        Violation entity = new Violation();
        entity.setType(dto.getType());
        entity.setTimestampInVideo(dto.getTimestampInVideo());
        entity.setFrameNumber(dto.getFrameNumber());
        entity.setDuration(dto.getDuration());
        return entity;
    }
}
