package com.scooter.violation.processing_service.dto;

import lombok.Data;
import java.util.UUID;

@Data
public class ViolationDTO {
    private UUID id;
    private UUID taskId;
    private UUID frameId;
    private String type;
    private Integer timestampInVideo;
    private Integer frameNumber;
    private Integer duration;
}
