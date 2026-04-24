package com.scooter.violation.processing_service.messaging;

import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class AnalysisResultMessage {
    private UUID id;
    private String status;
    private Integer video_duration;
    private Integer fps;
    private List<ViolationFrameData> violations;

    @Data
    public static class ViolationFrameData {
        private Integer timestamp;
        private Integer duration;
        private Integer frame;
        private List<String> violations;
        private String minio_path;
    }
}