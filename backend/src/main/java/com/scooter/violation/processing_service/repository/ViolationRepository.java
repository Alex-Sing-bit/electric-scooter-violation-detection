package com.scooter.violation.processing_service.repository;

import com.scooter.violation.processing_service.entity.Violation;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface ViolationRepository extends JpaRepository<Violation, UUID> {
    List<Violation> findByTaskId(UUID taskId);
    List<Violation> findByFrameId(UUID frameId);
    List<Violation> findByType(String type);
}
