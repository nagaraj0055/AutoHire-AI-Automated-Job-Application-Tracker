"""
============================================
AutoHire AI - Scheduler Module
============================================
Automates job scraping and email alerts using APScheduler.
Runs scraping every 12 hours and email alerts daily.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime
from scraper import JobScraperManager
from email_service import EmailService
from config import Config


class JobScheduler:
    """
    Manages scheduled tasks for the AutoHire AI application.
    
    Scheduled Jobs:
    1. Job Scraping - Runs every N hours (configurable, default 12)
    2. Email Alerts  - Runs daily at 9:00 AM
    """

    def __init__(self):
        """Initialize the scheduler with APScheduler BackgroundScheduler."""
        self.scheduler = BackgroundScheduler(
            job_defaults={
                'coalesce': True,         # Combine missed jobs into one
                'max_instances': 1,       # Prevent overlapping runs
                'misfire_grace_time': 3600  # Allow 1 hour grace for missed jobs
            }
        )
        self.scraper_manager = JobScraperManager()
        self.email_service = EmailService()

        # Register event listeners for monitoring
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def _job_listener(self, event):
        """
        Listen for job execution events and log them.

        Args:
            event: APScheduler event object
        """
        if event.exception:
            print(f"[SCHEDULER ❌] Job {event.job_id} failed: {event.exception}")
        else:
            print(f"[SCHEDULER ✅] Job {event.job_id} executed successfully at {datetime.now()}")

    def _run_scraping(self):
        """
        Callback function for the scraping job.
        Runs all scrapers and prints a summary.
        """
        print(f"\n[SCHEDULER] Running automated scraping at {datetime.now()}")
        try:
            results = self.scraper_manager.run_all()
            total = sum(len(jobs) for jobs in results.values())
            print(f"[SCHEDULER] Scraping complete. Total jobs: {total}")
        except Exception as e:
            print(f"[SCHEDULER ERROR] Scraping failed: {e}")

    def _run_email_alert(self):
        """
        Callback function for the email alert job.
        Sends an email with all new (unemailed) jobs.
        """
        print(f"\n[SCHEDULER] Running email alert at {datetime.now()}")
        try:
            self.email_service.send_daily_alert()
        except Exception as e:
            print(f"[SCHEDULER ERROR] Email alert failed: {e}")

    def start(self):
        """
        Start the scheduler with all configured jobs.
        
        Jobs:
        - scrape_jobs: Runs every SCRAPE_INTERVAL_HOURS hours
        - email_alert: Runs daily at 9:00 AM
        """
        # ---- Job 1: Automated Scraping ----
        self.scheduler.add_job(
            func=self._run_scraping,
            trigger=IntervalTrigger(hours=Config.SCRAPE_INTERVAL_HOURS),
            id='scrape_jobs',
            name=f'Scrape Jobs Every {Config.SCRAPE_INTERVAL_HOURS} Hours',
            replace_existing=True
        )

        # ---- Job 2: Daily Email Alert ----
        self.scheduler.add_job(
            func=self._run_email_alert,
            trigger=CronTrigger(hour=9, minute=0),  # 9:00 AM daily
            id='email_alert',
            name='Daily Email Alert at 9 AM',
            replace_existing=True
        )

        self.scheduler.start()
        print(f"\n{'='*50}")
        print("  AutoHire AI Scheduler Started")
        print(f"{'='*50}")
        print(f"  📋 Scraping interval: Every {Config.SCRAPE_INTERVAL_HOURS} hours")
        print(f"  📧 Email alerts: Daily at 9:00 AM")
        print(f"  ⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")

    def stop(self):
        """Stop the scheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[SCHEDULER] Stopped")

    def get_status(self):
        """
        Get the current status of all scheduled jobs.

        Returns:
            list: List of job status dictionaries
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else 'Not scheduled',
                'trigger': str(job.trigger)
            })
        return jobs

    def trigger_scrape_now(self):
        """Manually trigger an immediate scraping job."""
        print("[SCHEDULER] Manual scraping triggered")
        self._run_scraping()

    def trigger_email_now(self):
        """Manually trigger an immediate email alert."""
        print("[SCHEDULER] Manual email alert triggered")
        self._run_email_alert()


# ============================================
# CLI Entry Point for standalone scheduler
# ============================================
if __name__ == "__main__":
    import time as _time

    print("AutoHire AI - Standalone Scheduler")
    print("-" * 40)

    scheduler = JobScheduler()
    scheduler.start()

    try:
        # Keep the main thread alive
        while True:
            _time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()
        print("\nScheduler stopped.")
