package com.scooter.violation.processing_service.repository;

import com.scooter.violation.processing_service.entity.AnalysisTask;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;
import java.util.UUID;

public interface AnalysisTaskRepository extends JpaRepository<AnalysisTask, UUID> {

}