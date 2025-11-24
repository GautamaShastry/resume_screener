package com.resume.resume_analyzer.controller;

import com.resume.resume_analyzer.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping("/pdf/{matchResultId}")
    public ResponseEntity<byte[]> downloadPdfReport(@PathVariable Long matchResultId) {
        try {
            byte[] pdfBytes = reportService.getPdfReport(matchResultId);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDispositionFormData("attachment", "resume-analysis-report.pdf");
            headers.setContentLength(pdfBytes.length);

            return ResponseEntity.ok()
                    .headers(headers)
                    .body(pdfBytes);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    @GetMapping("/html/{matchResultId}")
    public ResponseEntity<String> viewHtmlReport(@PathVariable Long matchResultId) {
        try {
            String html = reportService.getHtmlReport(matchResultId);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.TEXT_HTML);

            return ResponseEntity.ok()
                    .headers(headers)
                    .body(html);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("<html><body><h1>Error generating report: " + e.getMessage() + "</h1></body></html>");
        }
    }
}