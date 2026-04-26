package com.scooter.violation.processing_service.repository;

import com.scooter.violation.processing_service.entity.AnalysisTask;
import com.scooter.violation.processing_service.entity.ViolationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface AnalysisTaskRepository extends JpaRepository<AnalysisTask, UUID> {
    List<AnalysisTask> findByStatus(ViolationStatus status);
}