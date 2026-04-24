package com.scooter.violation.processing_service.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.util.UUID;

@Entity
@Table(name = "violations",
        indexes = {
                @Index(name = "idx_task_id", columnList = "task_id"),
                @Index(name = "idx_type", columnList = "type")
        })
@Data
public class Violation {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id", nullable = false)
    private AnalysisTask task;

    @Column(name = "type", nullable = false)
    private String type;

    @Column(name = "timestamp_in_video", nullable = false)
    private Integer timestampInVideo;

    @Column(name = "frame_number")
    private Integer frameNumber;

    @Column(name = "duration")
    private Integer duration;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "frame_id")
    private ViolationFrame frame;
}