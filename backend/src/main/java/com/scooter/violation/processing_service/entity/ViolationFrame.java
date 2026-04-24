package com.scooter.violation.processing_service.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "violation_frames")
@Data
public class ViolationFrame {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "task_id", nullable = false)
    private AnalysisTask task;

    @Column(name = "frame_path", nullable = false)
    private String framePath;

    @Column(name = "frame_number", nullable = false)
    private Integer frameNumber;

    @Column(name = "timestamp", nullable = false)
    private Integer timestampInVideo;

    @OneToMany(mappedBy = "frame", cascade = CascadeType.ALL)
    private List<Violation> violations;
}