package com.scooter.violation.processing_service.controller;

import com.scooter.violation.processing_service.dto.ViolationDTO;
import com.scooter.violation.processing_service.service.ViolationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class ViolationController {

    private final ViolationService violationService;

    @Transactional
    @DeleteMapping("/violations/{violationId}")
    public ResponseEntity<?> deleteViolation(@PathVariable UUID violationId) {
        boolean deleted = violationService.delete(violationId);
        return deleted
                ? new ResponseEntity<>(HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @Transactional
    @GetMapping("/violations")
    public ResponseEntity<List<ViolationDTO>> getAllViolations() {
        List<ViolationDTO> violations = violationService.readAll();
        return violations != null
                ? new ResponseEntity<>(violations, HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @Transactional
    @GetMapping("/violations/{violationId}")
    public ResponseEntity<ViolationDTO> getViolationById(@PathVariable UUID violationId) {
        ViolationDTO violation = violationService.read(violationId);
        return violation != null
                ? new ResponseEntity<>(violation, HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @Transactional
    @GetMapping("/violations/type/{type}")
    public ResponseEntity<List<ViolationDTO>> getViolationsByType(@PathVariable String type) {
        List<ViolationDTO> violations = violationService.readByType(type);
        return violations != null
                ? new ResponseEntity<>(violations, HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }
}
