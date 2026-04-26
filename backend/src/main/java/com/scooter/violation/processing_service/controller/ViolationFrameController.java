package com.scooter.violation.processing_service.controller;

import com.scooter.violation.processing_service.dto.ViolationDTO;
import com.scooter.violation.processing_service.dto.ViolationFrameDTO;
import com.scooter.violation.processing_service.service.ViolationFrameService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/frames")
@RequiredArgsConstructor
public class ViolationFrameController {

    private final ViolationFrameService service;

    @GetMapping
    public List<ViolationFrameDTO> getAllFrames() {
        return service.getAllFrames();
    }

    @GetMapping("/{frameId}/violations")
    public List<ViolationDTO> getViolationsByFrameId(@PathVariable UUID frameId) {
        return service.getViolationsByFrameId(frameId);
    }
}
