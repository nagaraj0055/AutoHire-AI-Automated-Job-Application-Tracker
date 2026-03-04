-- ============================================
-- AutoHire AI - Database Schema
-- Automated Job Application Tracker
-- ============================================

-- Create the database
CREATE DATABASE IF NOT EXISTS autohire_ai;
USE autohire_ai;

-- ============================================
-- Table: job_listings
-- Stores all scraped job postings
-- ============================================
CREATE TABLE IF NOT EXISTS job_listings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    location VARCHAR(255) DEFAULT 'Not Specified',
    job_link VARCHAR(512) NOT NULL UNIQUE,        -- Unique constraint prevents duplicates
    date_posted VARCHAR(100) DEFAULT 'Not Available',
    source VARCHAR(50) NOT NULL,                  -- linkedin, naukri, indeed
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_emailed BOOLEAN DEFAULT FALSE,             -- Track if job was included in email alert
    is_active BOOLEAN DEFAULT TRUE,               -- Soft delete support

    -- Indexes for fast filtering
    INDEX idx_company (company_name),
    INDEX idx_title (job_title),
    INDEX idx_location (location),
    INDEX idx_source (source),
    INDEX idx_scraped_at (scraped_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: scrape_logs
-- Tracks scraping history and status
-- ============================================
CREATE TABLE IF NOT EXISTS scrape_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    jobs_found INT DEFAULT 0,
    jobs_added INT DEFAULT 0,
    status ENUM('success', 'failed', 'partial') NOT NULL,
    error_message TEXT DEFAULT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Table: email_logs
-- Tracks email notification history
-- ============================================
CREATE TABLE IF NOT EXISTS email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipient VARCHAR(255) NOT NULL,
    jobs_count INT DEFAULT 0,
    status ENUM('sent', 'failed') NOT NULL,
    error_message TEXT DEFAULT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Insert sample data for testing
-- ============================================
INSERT INTO job_listings (job_title, company_name, location, job_link, date_posted, source) VALUES
('Software Engineer', 'Google', 'Bangalore, India', 'https://careers.google.com/jobs/1', '2 days ago', 'linkedin'),
('Backend Developer', 'Microsoft', 'Hyderabad, India', 'https://careers.microsoft.com/jobs/1', '1 day ago', 'linkedin'),
('Full Stack Developer', 'Amazon', 'Mumbai, India', 'https://amazon.jobs/1', '3 days ago', 'indeed'),
('Software Engineer II', 'Meta', 'Remote', 'https://metacareers.com/jobs/1', 'Just posted', 'linkedin'),
('Python Developer', 'Infosys', 'Pune, India', 'https://infosys.com/careers/1', '5 days ago', 'naukri'),
('Junior Software Engineer', 'TCS', 'Chennai, India', 'https://tcs.com/careers/1', '1 week ago', 'naukri'),
('DevOps Engineer', 'Flipkart', 'Bangalore, India', 'https://flipkart.com/careers/1', '4 days ago', 'indeed'),
('Frontend Developer', 'Swiggy', 'Bangalore, India', 'https://swiggy.com/careers/1', '2 days ago', 'naukri');
