package com.scooter.violation.processing_service.dto;

import com.scooter.violation.processing_service.entity.ViolationStatus;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
public class AnalysisTaskDTO {
    private UUID id;
    private String filePath;
    private ViolationStatus status;
    private Integer videoDuration;
    private Integer fps;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
}
