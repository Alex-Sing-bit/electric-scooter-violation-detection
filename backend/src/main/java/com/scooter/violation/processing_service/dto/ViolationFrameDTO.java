package com.scooter.violation.processing_service.dto;

import lombok.Data;
import java.util.UUID;

@Data
public class ViolationFrameDTO {
    private UUID id;
    private UUID taskId;
    private String framePath;
    private Integer frameNumber;
    private Integer timestampInVideo;
}
