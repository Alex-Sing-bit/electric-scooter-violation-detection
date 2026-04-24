package com.scooter.violation.processing_service.repository;

import com.scooter.violation.processing_service.entity.Violation;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface ViolationRepository extends JpaRepository<Violation, UUID> {

}
