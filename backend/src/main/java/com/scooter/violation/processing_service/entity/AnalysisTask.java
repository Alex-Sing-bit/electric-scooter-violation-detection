package com.scooter.violation.processing_service.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;
import org.locationtech.jts.geom.Point;

import java.util.UUID;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "analysis_tasks")
@Data
public class AnalysisTask {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "file_path", nullable = false)
    private String filePath;

    @Enumerated(EnumType.STRING)
    private ViolationStatus status;

    @Column(name = "video_duration")
    private Integer videoDuration;

    @Column(name = "fps")
    private Integer fps;

    @Column(name = "started_at")
    private LocalDateTime startedAt;

    @Column(name = "completed_at")
    private LocalDateTime completedAt;

    @OneToMany(mappedBy = "task", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<ViolationFrame> frames;

    @OneToMany(mappedBy = "task", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Violation> violations;

}