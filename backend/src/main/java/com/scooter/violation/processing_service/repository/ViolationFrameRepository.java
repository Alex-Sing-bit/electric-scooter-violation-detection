package com.scooter.violation.processing_service.repository;

import com.scooter.violation.processing_service.entity.ViolationFrame;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface ViolationFrameRepository extends JpaRepository<ViolationFrame, UUID> {
    List<ViolationFrame> findByTaskId(UUID taskId);
}