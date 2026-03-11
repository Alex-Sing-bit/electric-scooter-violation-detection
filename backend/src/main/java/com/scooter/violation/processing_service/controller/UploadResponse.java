package com.scooter.violation.processing_service.controller;

import java.util.UUID;

public record UploadResponse(
        UUID violationId,
        String uploadUrl,
        String filePath
) {}