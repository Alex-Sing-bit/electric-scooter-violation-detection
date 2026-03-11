package com.scooter.violation.processing_service.controller;

import com.scooter.violation.processing_service.entity.Violation;
import com.scooter.violation.processing_service.entity.ViolationStatus;
import com.scooter.violation.processing_service.repository.ViolationRepository;
import com.scooter.violation.processing_service.service.AnalysisService;
import com.scooter.violation.processing_service.service.StorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/uploads")
@RequiredArgsConstructor
public class ViolationUploadController {

    private final StorageService storageService;
    private final ViolationRepository violationRepository;
    private final AnalysisService analysisService;

    @Transactional
    @GetMapping("/presigned-url")
    public ResponseEntity<?> getPresignedUrl(@RequestParam String extension) throws Exception {
        String fileName = UUID.randomUUID() + "." + extension;
        String filePath = "originals/" + fileName;

        Violation violation = new Violation();
        violation.setFilePath(filePath);
        violation.setStatus(ViolationStatus.PENDING);

        Violation savedViolation = violationRepository.save(violation);

        String uploadUrl = storageService.generatePresignedUploadUrl(filePath);

        return ResponseEntity.ok(new UploadResponse(
                savedViolation.getId(),
                uploadUrl,
                filePath
        ));
    }

    @PostMapping("/analyze/{id}")
    public ResponseEntity<String> analyze(@PathVariable UUID id) {
        try {
            analysisService.startAnalysis(id);
            return ResponseEntity.ok("Анализ запущен");
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}