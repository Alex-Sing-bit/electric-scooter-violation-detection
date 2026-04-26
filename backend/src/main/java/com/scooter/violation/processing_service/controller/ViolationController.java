package com.scooter.violation.processing_service.controller;

import com.scooter.violation.processing_service.entity.Violation;
import com.scooter.violation.processing_service.repository.ViolationRepository;
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
    @PostMapping("/violations")
    public void addViolation(@RequestBody Violation violation) throws Exception {
        violationService.create(violation);
    }

    @Transactional
    @PostMapping("/violations/{violationId}")
    public void addViolation(@PathVariable UUID violationId, @RequestBody Violation violation) throws Exception {
        violationService.update(violation, violationId);
    }

    @Transactional
    @GetMapping("/violations")
    public ResponseEntity<List<Violation>> getViolations() throws Exception {
        List<Violation> violations = violationService.readAll();

        return violations != null && !violations.isEmpty()
                ? new ResponseEntity<>(violations, HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }

    @Transactional
    @GetMapping("/violations/{violationId}")
    public ResponseEntity<Violation> getViolation(@PathVariable UUID violationId) throws Exception {
        Violation violation = violationService.read(violationId);

        return violation != null
                ? new ResponseEntity<>(violation, HttpStatus.OK)
                : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }
}
