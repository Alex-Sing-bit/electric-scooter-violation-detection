package com.scooter.violation.processing_service.service;

import io.minio.GetPresignedObjectUrlArgs;
import io.minio.MinioClient;
import io.minio.http.Method;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.concurrent.TimeUnit;

@Slf4j
@Service
public class StorageService {

    private final MinioClient minioClient;
    private final String bucket;
    private final RestTemplate restTemplate;

    @Autowired
    public StorageService(
            MinioClient minioClient,
            @Value("${minio.bucket-name}") String bucket,
            RestTemplate restTemplate) {
        this.minioClient = minioClient;
        this.bucket = bucket;
        this.restTemplate = restTemplate;
    }

    public String generatePresignedUploadUrl(String fileName) throws Exception {

        String internalUrl = minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                        .method(Method.PUT)
                        .bucket(bucket)
                        .object(fileName)
                        .expiry(15, TimeUnit.MINUTES)
                        .build()
        );

        return internalUrl.replace("http://minio:9000", "http://localhost");
    }

    public String getFileUrl(String fileName) throws Exception {

        return minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                        .method(Method.GET)
                        .bucket(bucket)
                        .object("originals/" + fileName)
                        .expiry(2, TimeUnit.HOURS)
                        .build()
        );
    }
}