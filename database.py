"""
============================================
AutoHire AI - Database Module
============================================
Handles all MySQL database operations using mysql-connector-python.
Implements OOP with a DatabaseManager class for clean, reusable DB access.
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import Config


class DatabaseManager:
    """
    Manages all database interactions for the AutoHire AI application.
    Provides methods for CRUD operations on job listings and logging.
    """

    def __init__(self):
        """Initialize database manager with configuration."""
        self.config = {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME
        }

    def _get_connection(self):
        """
        Create and return a new database connection.
        Uses context manager pattern for safe connection handling.
        """
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"[DB ERROR] Failed to connect: {e}")
            raise

    # ==========================================
    # Job Listings - CRUD Operations
    # ==========================================

    def insert_job(self, job_data):
        """
        Insert a single job listing into the database.
        Skips duplicates based on unique job_link constraint.

        Args:
            job_data (dict): Dictionary with keys:
                - job_title, company_name, location, job_link, date_posted, source

        Returns:
            tuple: (success: bool, reason: str)
                - (True, 'inserted') if job was added
                - (False, 'duplicate') if job_link already exists
                - (False, 'error: ...') if a database error occurred
        """
        # First check if this job_link already exists
        check_query = "SELECT id FROM job_listings WHERE job_link = %s"
        query = """
            INSERT INTO job_listings 
            (job_title, company_name, location, job_link, date_posted, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Check for duplicate
            cursor.execute(check_query, (job_data.get('job_link', ''),))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return (False, 'duplicate')

            # Insert the new job
            cursor.execute(query, (
                job_data.get('job_title', 'N/A'),
                job_data.get('company_name', 'N/A'),
                job_data.get('location', 'Not Specified'),
                job_data.get('job_link', ''),
                job_data.get('date_posted', 'Not Available'),
                job_data.get('source', 'unknown')
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return (True, 'inserted')
        except Error as e:
            print(f"[DB ERROR] Insert job failed: {e}")
            return (False, f'error: {str(e)}')

    def insert_jobs_bulk(self, jobs_list):
        """
        Insert multiple job listings at once.
        Uses INSERT IGNORE to skip duplicates automatically.

        Args:
            jobs_list (list): List of job dictionaries

        Returns:
            int: Number of jobs actually inserted (excluding duplicates)
        """
        query = """
            INSERT IGNORE INTO job_listings 
            (job_title, company_name, location, job_link, date_posted, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            values = [
                (
                    job.get('job_title', 'N/A'),
                    job.get('company_name', 'N/A'),
                    job.get('location', 'Not Specified'),
                    job.get('job_link', ''),
                    job.get('date_posted', 'Not Available'),
                    job.get('source', 'unknown')
                )
                for job in jobs_list
            ]
            cursor.executemany(query, values)
            conn.commit()
            inserted_count = cursor.rowcount
            cursor.close()
            conn.close()
            print(f"[DB] Inserted {inserted_count} new jobs out of {len(jobs_list)} scraped")
            return inserted_count
        except Error as e:
            print(f"[DB ERROR] Bulk insert failed: {e}")
            return 0

    def get_all_jobs(self, filters=None):
        """
        Retrieve all active job listings with optional filtering.

        Args:
            filters (dict, optional): Filter criteria:
                - company: filter by company name (partial match)
                - role: filter by job title (partial match)
                - location: filter by location (partial match)
                - source: filter by source platform

        Returns:
            list: List of job dictionaries
        """
        query = "SELECT * FROM job_listings WHERE is_active = TRUE"
        params = []

        # Build dynamic WHERE clause based on filters
        if filters:
            if filters.get('company'):
                query += " AND company_name LIKE %s"
                params.append(f"%{filters['company']}%")
            if filters.get('role'):
                query += " AND job_title LIKE %s"
                params.append(f"%{filters['role']}%")
            if filters.get('location'):
                query += " AND location LIKE %s"
                params.append(f"%{filters['location']}%")
            if filters.get('source'):
                query += " AND source = %s"
                params.append(filters['source'])

        query += " ORDER BY scraped_at DESC"

        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            jobs = cursor.fetchall()
            cursor.close()
            conn.close()

            # Convert datetime objects to strings for JSON serialization
            for job in jobs:
                if isinstance(job.get('scraped_at'), datetime):
                    job['scraped_at'] = job['scraped_at'].strftime('%Y-%m-%d %H:%M:%S')

            return jobs
        except Error as e:
            print(f"[DB ERROR] Get jobs failed: {e}")
            return []

    def get_job_by_id(self, job_id):
        """
        Retrieve a single job listing by its ID.

        Args:
            job_id (int): The job listing ID

        Returns:
            dict or None: Job dictionary if found, None otherwise
        """
        query = "SELECT * FROM job_listings WHERE id = %s AND is_active = TRUE"
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (job_id,))
            job = cursor.fetchone()
            cursor.close()
            conn.close()

            if job and isinstance(job.get('scraped_at'), datetime):
                job['scraped_at'] = job['scraped_at'].strftime('%Y-%m-%d %H:%M:%S')

            return job
        except Error as e:
            print(f"[DB ERROR] Get job by ID failed: {e}")
            return None

    def delete_job(self, job_id):
        """
        Soft delete a job listing (sets is_active to FALSE).

        Args:
            job_id (int): The job listing ID to delete

        Returns:
            bool: True if deleted, False otherwise
        """
        query = "UPDATE job_listings SET is_active = FALSE WHERE id = %s"
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (job_id,))
            conn.commit()
            success = cursor.rowcount > 0
            cursor.close()
            conn.close()
            return success
        except Error as e:
            print(f"[DB ERROR] Delete job failed: {e}")
            return False

    def get_unemailed_jobs(self):
        """
        Retrieve all jobs that haven't been included in an email alert yet.

        Returns:
            list: List of unemailed job dictionaries
        """
        query = """
            SELECT * FROM job_listings 
            WHERE is_emailed = FALSE AND is_active = TRUE
            ORDER BY scraped_at DESC
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            jobs = cursor.fetchall()
            cursor.close()
            conn.close()

            for job in jobs:
                if isinstance(job.get('scraped_at'), datetime):
                    job['scraped_at'] = job['scraped_at'].strftime('%Y-%m-%d %H:%M:%S')

            return jobs
        except Error as e:
            print(f"[DB ERROR] Get unemailed jobs failed: {e}")
            return []

    def mark_jobs_as_emailed(self, job_ids):
        """
        Mark multiple jobs as emailed after sending notification.

        Args:
            job_ids (list): List of job IDs to mark as emailed
        """
        if not job_ids:
            return
        placeholders = ', '.join(['%s'] * len(job_ids))
        query = f"UPDATE job_listings SET is_emailed = TRUE WHERE id IN ({placeholders})"
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, job_ids)
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"[DB ERROR] Mark emailed failed: {e}")

    # ==========================================
    # Statistics
    # ==========================================

    def get_stats(self):
        """
        Get dashboard statistics.

        Returns:
            dict: Statistics including total jobs, sources breakdown, etc.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            # Total active jobs
            cursor.execute("SELECT COUNT(*) as total FROM job_listings WHERE is_active = TRUE")
            total = cursor.fetchone()['total']

            # Jobs by source
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM job_listings WHERE is_active = TRUE 
                GROUP BY source
            """)
            by_source = {row['source']: row['count'] for row in cursor.fetchall()}

            # Jobs added today
            cursor.execute("""
                SELECT COUNT(*) as today 
                FROM job_listings 
                WHERE is_active = TRUE AND DATE(scraped_at) = CURDATE()
            """)
            today = cursor.fetchone()['today']

            # Unique companies
            cursor.execute("""
                SELECT COUNT(DISTINCT company_name) as companies 
                FROM job_listings WHERE is_active = TRUE
            """)
            companies = cursor.fetchone()['companies']

            cursor.close()
            conn.close()

            return {
                'total_jobs': total,
                'jobs_today': today,
                'unique_companies': companies,
                'by_source': by_source
            }
        except Error as e:
            print(f"[DB ERROR] Get stats failed: {e}")
            return {
                'total_jobs': 0,
                'jobs_today': 0,
                'unique_companies': 0,
                'by_source': {}
            }

    # ==========================================
    # Logging
    # ==========================================

    def log_scrape(self, source, jobs_found, jobs_added, status, error_msg=None):
        """Log a scraping session result."""
        query = """
            INSERT INTO scrape_logs (source, jobs_found, jobs_added, status, error_message, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (source, jobs_found, jobs_added, status, error_msg, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"[DB ERROR] Log scrape failed: {e}")

    def log_email(self, recipient, jobs_count, status, error_msg=None):
        """Log an email notification attempt."""
        query = """
            INSERT INTO email_logs (recipient, jobs_count, status, error_message)
            VALUES (%s, %s, %s, %s)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (recipient, jobs_count, status, error_msg))
            conn.commit()
            cursor.close()
            conn.close()
        except Error as e:
            print(f"[DB ERROR] Log email failed: {e}")

    def initialize_database(self):
        """
        Create the database and tables if they don't exist.
        Useful for first-time setup.
        """
        try:
            # First connect without database to create it
            init_config = self.config.copy()
            init_config.pop('database')
            conn = mysql.connector.connect(**init_config)
            cursor = conn.cursor()

            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            cursor.execute(f"USE {Config.DB_NAME}")

            # Create job_listings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_listings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    job_title VARCHAR(255) NOT NULL,
                    company_name VARCHAR(255) NOT NULL,
                    location VARCHAR(255) DEFAULT 'Not Specified',
                    job_link VARCHAR(512) NOT NULL UNIQUE,
                    date_posted VARCHAR(100) DEFAULT 'Not Available',
                    source VARCHAR(50) NOT NULL,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_emailed BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    INDEX idx_company (company_name),
                    INDEX idx_title (job_title),
                    INDEX idx_location (location),
                    INDEX idx_source (source),
                    INDEX idx_scraped_at (scraped_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Create scrape_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scrape_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    source VARCHAR(50) NOT NULL,
                    jobs_found INT DEFAULT 0,
                    jobs_added INT DEFAULT 0,
                    status ENUM('success', 'failed', 'partial') NOT NULL,
                    error_message TEXT DEFAULT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Create email_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    recipient VARCHAR(255) NOT NULL,
                    jobs_count INT DEFAULT 0,
                    status ENUM('sent', 'failed') NOT NULL,
                    error_message TEXT DEFAULT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            conn.commit()
            cursor.close()
            conn.close()
            print("[DB] Database and tables initialized successfully!")
            return True
        except Error as e:
            print(f"[DB ERROR] Database initialization failed: {e}")
            return False
