package com.scooter.violation.processing_service.service;

import com.scooter.violation.processing_service.entity.Violation;
import com.scooter.violation.processing_service.repository.ViolationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class ViolationService {
    @Autowired
    private ViolationRepository violationRepository;

    public void create(Violation client) {
        violationRepository.save(client);
    }

    public List<Violation> readAll() {
        return violationRepository.findAll();
    }

    public Violation read(UUID id) {
        return violationRepository.getReferenceById(id);
    }

    public boolean update(Violation client, UUID id) {
        if (violationRepository.existsById(id)) {
            client.setId(id);
            violationRepository.save(client);
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
}
