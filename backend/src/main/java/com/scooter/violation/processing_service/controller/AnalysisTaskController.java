package com.scooter.violation.processing_service.controller;

import com.scooter.violation.processing_service.dto.AnalysisTaskDTO;
import com.scooter.violation.processing_service.dto.ViolationDTO;
import com.scooter.violation.processing_service.dto.ViolationFrameDTO;
import com.scooter.violation.processing_service.entity.ViolationStatus;
import com.scooter.violation.processing_service.service.AnalysisTaskService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
public class AnalysisTaskController {

    private final AnalysisTaskService service;

    @GetMapping
    public List<AnalysisTaskDTO> getTasks(@RequestParam(required = false) ViolationStatus status) {
        return status != null
                ? service.getTasksByStatus(status)
                : service.getAllTasks();
    }

    @GetMapping("/{taskId}/frames")
    public List<ViolationFrameDTO> getFramesByTaskId(@PathVariable UUID taskId) {
        return service.getFramesByTaskId(taskId);
    }

    @GetMapping("/{taskId}/violations")
    public List<ViolationDTO> getViolationsByTaskId(@PathVariable UUID taskId) {
        return service.getViolationsByTaskId(taskId);
    }
}
