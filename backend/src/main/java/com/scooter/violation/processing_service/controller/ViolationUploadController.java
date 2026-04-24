package com.scooter.violation.processing_service.controller;

import com.scooter.violation.processing_service.entity.AnalysisTask;
import com.scooter.violation.processing_service.entity.ViolationStatus;
import com.scooter.violation.processing_service.repository.AnalysisTaskRepository;
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
    private final AnalysisTaskRepository analysisTaskRepository;
    private final AnalysisService analysisService;

    @Transactional
    @GetMapping("/presigned-url")
    public ResponseEntity<?> getPresignedUrl(@RequestParam String extension) throws Exception {
        AnalysisTask analysisTask = new AnalysisTask();
        analysisTask.setStatus(ViolationStatus.PENDING);
        analysisTask.setFilePath("pending/" + UUID.randomUUID());
        AnalysisTask savedAnalysisTask = analysisTaskRepository.save(analysisTask);

        String fileName = savedAnalysisTask.getId().toString() + "." + extension;
        String filePath = "originals/" + fileName;

        savedAnalysisTask.setFilePath(filePath);
        analysisTaskRepository.save(savedAnalysisTask);

        String uploadUrl = storageService.generatePresignedUploadUrl(filePath);

        return ResponseEntity.ok(new UploadResponse(
                savedAnalysisTask.getId(),
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