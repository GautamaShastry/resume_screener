package com.resume.resume_analyzer.repository;

import com.resume.resume_analyzer.entity.Otp;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface OtpRepository extends JpaRepository<Otp, Long> {
    Optional<Otp> findByEmailAndVerifiedFalse(String email);
    Optional<Otp> findByEmailAndOtpCodeAndVerifiedFalse(String email, String otpCode);
}