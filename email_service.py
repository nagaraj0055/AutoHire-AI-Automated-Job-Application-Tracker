"""
============================================
AutoHire AI - Email Notification Service
============================================
Sends daily email alerts with new job postings.
Uses SMTP (Gmail) with HTML-formatted emails.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from database import DatabaseManager
from config import Config


class EmailService:
    """
    Handles email notifications for new job postings.
    Sends beautifully formatted HTML emails with job details.
    """

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.host = Config.EMAIL_HOST
        self.port = Config.EMAIL_PORT
        self.user = Config.EMAIL_USER
        self.password = Config.EMAIL_PASSWORD
        self.recipient = Config.EMAIL_RECIPIENT
        self.db = DatabaseManager()

    def _build_html_email(self, jobs):
        """
        Build a professional HTML email body with job listings.

        Args:
            jobs (list): List of job dictionaries to include

        Returns:
            str: Formatted HTML email body
        """
        # Count jobs by source for summary
        sources = {}
        for job in jobs:
            src = job.get('source', 'unknown')
            sources[src] = sources.get(src, 0) + 1

        source_summary = " | ".join([f"{k.title()}: {v}" for k, v in sources.items()])

        # Build job rows for the HTML table
        job_rows = ""
        for i, job in enumerate(jobs, 1):
            # Alternate row colors for readability
            bg_color = "#f8f9ff" if i % 2 == 0 else "#ffffff"
            source_color = {
                'linkedin': '#0077B5',
                'indeed': '#2164f3',
                'naukri': '#4a90d9'
            }.get(job.get('source', ''), '#6c757d')

            job_rows += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 14px 16px; border-bottom: 1px solid #e8ecf1; font-weight: 600; color: #1a1a2e;">
                    {job.get('job_title', 'N/A')}
                </td>
                <td style="padding: 14px 16px; border-bottom: 1px solid #e8ecf1; color: #4a4a6a;">
                    {job.get('company_name', 'N/A')}
                </td>
                <td style="padding: 14px 16px; border-bottom: 1px solid #e8ecf1; color: #4a4a6a;">
                    📍 {job.get('location', 'N/A')}
                </td>
                <td style="padding: 14px 16px; border-bottom: 1px solid #e8ecf1;">
                    <span style="background-color: {source_color}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px;">
                        {job.get('source', 'N/A').title()}
                    </span>
                </td>
                <td style="padding: 14px 16px; border-bottom: 1px solid #e8ecf1; color: #6c757d; font-size: 13px;">
                    {job.get('date_posted', 'N/A')}
                </td>
                <td style="padding: 14px 16px; border-bottom: 1px solid #e8ecf1; text-align: center;">
                    <a href="{job.get('job_link', '#')}" 
                       style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; 
                              padding: 6px 16px; border-radius: 20px; text-decoration: none; 
                              font-size: 13px; font-weight: 500;">
                        Apply →
                    </a>
                </td>
            </tr>
            """

        # Complete HTML email template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5;">
            <div style="max-width: 900px; margin: 0 auto; padding: 20px;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            border-radius: 16px 16px 0 0; padding: 30px 40px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">
                        🚀 AutoHire AI
                    </h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0; font-size: 16px;">
                        Daily Job Alert — {datetime.now().strftime('%B %d, %Y')}
                    </p>
                </div>

                <!-- Summary Card -->
                <div style="background: white; padding: 24px 40px; border-bottom: 1px solid #e8ecf1;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h2 style="margin: 0; color: #1a1a2e; font-size: 20px;">
                                📊 {len(jobs)} New Job{'' if len(jobs) == 1 else 's'} Found
                            </h2>
                            <p style="margin: 6px 0 0; color: #6c757d; font-size: 14px;">
                                {source_summary}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Job Listings Table -->
                <div style="background: white; padding: 0; overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f8f9ff;">
                                <th style="padding: 14px 16px; text-align: left; color: #667eea; 
                                           font-size: 13px; font-weight: 600; text-transform: uppercase; 
                                           letter-spacing: 0.5px; border-bottom: 2px solid #667eea;">
                                    Job Title
                                </th>
                                <th style="padding: 14px 16px; text-align: left; color: #667eea; 
                                           font-size: 13px; font-weight: 600; text-transform: uppercase; 
                                           letter-spacing: 0.5px; border-bottom: 2px solid #667eea;">
                                    Company
                                </th>
                                <th style="padding: 14px 16px; text-align: left; color: #667eea; 
                                           font-size: 13px; font-weight: 600; text-transform: uppercase; 
                                           letter-spacing: 0.5px; border-bottom: 2px solid #667eea;">
                                    Location
                                </th>
                                <th style="padding: 14px 16px; text-align: left; color: #667eea; 
                                           font-size: 13px; font-weight: 600; text-transform: uppercase; 
                                           letter-spacing: 0.5px; border-bottom: 2px solid #667eea;">
                                    Source
                                </th>
                                <th style="padding: 14px 16px; text-align: left; color: #667eea; 
                                           font-size: 13px; font-weight: 600; text-transform: uppercase; 
                                           letter-spacing: 0.5px; border-bottom: 2px solid #667eea;">
                                    Posted
                                </th>
                                <th style="padding: 14px 16px; text-align: center; color: #667eea; 
                                           font-size: 13px; font-weight: 600; text-transform: uppercase; 
                                           letter-spacing: 0.5px; border-bottom: 2px solid #667eea;">
                                    Action
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {job_rows}
                        </tbody>
                    </table>
                </div>

                <!-- Footer -->
                <div style="background: #1a1a2e; border-radius: 0 0 16px 16px; padding: 24px 40px; text-align: center;">
                    <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 13px;">
                        Powered by <strong style="color: #667eea;">AutoHire AI</strong> — 
                        Automated Job Application Tracker
                    </p>
                    <p style="color: rgba(255,255,255,0.5); margin: 8px 0 0; font-size: 12px;">
                        This is an automated email. Jobs are updated every {Config.SCRAPE_INTERVAL_HOURS} hours.
                    </p>
                </div>

            </div>
        </body>
        </html>
        """
        return html

    def send_daily_alert(self):
        """
        Send daily email alert with all unemailed job listings.
        Marks jobs as emailed after successful send.

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        print("\n[EMAIL] Preparing daily job alert...")

        # Get jobs that haven't been emailed yet
        jobs = self.db.get_unemailed_jobs()

        if not jobs:
            print("[EMAIL] No new jobs to send. Skipping email.")
            return True

        print(f"[EMAIL] Found {len(jobs)} new jobs to include in alert")

        try:
            # Create the email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚀 AutoHire AI: {len(jobs)} New Job{'s' if len(jobs) != 1 else ''} Found — {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = f"AutoHire AI <{self.user}>"
            msg['To'] = self.recipient

            # Build HTML email body
            html_body = self._build_html_email(jobs)
            msg.attach(MIMEText(html_body, 'html'))

            # Connect to SMTP server and send
            with smtplib.SMTP(self.host, self.port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.user, self.password)
                server.sendmail(self.user, self.recipient, msg.as_string())

            # Mark all included jobs as emailed
            job_ids = [job['id'] for job in jobs]
            self.db.mark_jobs_as_emailed(job_ids)

            # Log successful email
            self.db.log_email(self.recipient, len(jobs), 'sent')
            print(f"[EMAIL] ✅ Alert sent successfully to {self.recipient}")
            return True

        except smtplib.SMTPAuthenticationError:
            error = "SMTP authentication failed. Check EMAIL_USER and EMAIL_PASSWORD in .env"
            print(f"[EMAIL ERROR] {error}")
            self.db.log_email(self.recipient, len(jobs), 'failed', error)
            return False

        except smtplib.SMTPException as e:
            error = f"SMTP error: {str(e)}"
            print(f"[EMAIL ERROR] {error}")
            self.db.log_email(self.recipient, len(jobs), 'failed', error)
            return False

        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            print(f"[EMAIL ERROR] {error}")
            self.db.log_email(self.recipient, len(jobs), 'failed', error)
            return False


# ============================================
# CLI Entry Point for manual email testing
# ============================================
if __name__ == "__main__":
    print("AutoHire AI - Email Service Test")
    print("-" * 40)

    # Validate email config
    config_errors = Config.validate()
    if config_errors:
        print("⚠️  Configuration errors:")
        for err in config_errors:
            print(f"   - {err}")
        print("\nPlease update your .env file and try again.")
    else:
        service = EmailService()
        service.send_daily_alert()
