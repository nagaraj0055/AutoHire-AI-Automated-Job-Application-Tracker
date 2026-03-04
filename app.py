"""
============================================
AutoHire AI - Main Flask Application
============================================
Entry point for the AutoHire AI web application.
Serves the dashboard, REST API, and manages the scheduler.
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from database import DatabaseManager
from scheduler import JobScheduler
from scraper import JobScraperManager
from email_service import EmailService
from config import Config

# ============================================
# Flask App Initialization
# ============================================
app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY
CORS(app)  # Enable CORS for API access

# Initialize services
db = DatabaseManager()
job_scheduler = JobScheduler()


# ============================================
# Dashboard Routes (HTML Pages)
# ============================================

@app.route('/')
def dashboard():
    """
    Main dashboard page.
    Displays job listings with filter support and statistics.
    """
    # Extract filter parameters from query string
    filters = {
        'company': request.args.get('company', '').strip(),
        'role': request.args.get('role', '').strip(),
        'location': request.args.get('location', '').strip(),
        'source': request.args.get('source', '').strip()
    }

    # Remove empty filters
    filters = {k: v for k, v in filters.items() if v}

    # Get filtered jobs and stats
    jobs = db.get_all_jobs(filters if filters else None)
    stats = db.get_stats()

    return render_template(
        'dashboard.html',
        jobs=jobs,
        stats=stats,
        filters=request.args,
        total_results=len(jobs)
    )


# ============================================
# REST API Routes
# ============================================

@app.route('/api/jobs', methods=['GET'])
def api_get_jobs():
    """
    GET /api/jobs
    Retrieve all job listings with optional filters.

    Query Parameters:
        - company (str): Filter by company name
        - role (str): Filter by job title
        - location (str): Filter by location
        - source (str): Filter by source platform

    Returns:
        JSON response with job listings
    """
    filters = {
        'company': request.args.get('company', '').strip(),
        'role': request.args.get('role', '').strip(),
        'location': request.args.get('location', '').strip(),
        'source': request.args.get('source', '').strip()
    }
    filters = {k: v for k, v in filters.items() if v}

    jobs = db.get_all_jobs(filters if filters else None)

    return jsonify({
        'status': 'success',
        'count': len(jobs),
        'data': jobs
    }), 200


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def api_get_job(job_id):
    """
    GET /api/jobs/<id>
    Retrieve a single job listing by ID.

    Returns:
        JSON response with job details or 404
    """
    job = db.get_job_by_id(job_id)

    if job:
        return jsonify({
            'status': 'success',
            'data': job
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': f'Job with ID {job_id} not found'
        }), 404


@app.route('/api/jobs', methods=['POST'])
def api_add_job():
    """
    POST /api/jobs
    Add a new job listing manually.

    Request Body (JSON):
        - job_title (str, required)
        - company_name (str, required)
        - location (str)
        - job_link (str, required)
        - date_posted (str)
        - source (str)

    Returns:
        JSON response with creation status
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['job_title', 'company_name', 'job_link']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({
            'status': 'error',
            'message': f'Missing required fields: {", ".join(missing)}'
        }), 400

    # Build job data with defaults
    job_data = {
        'job_title': data['job_title'],
        'company_name': data['company_name'],
        'location': data.get('location', 'Not Specified'),
        'job_link': data['job_link'],
        'date_posted': data.get('date_posted', 'Manual Entry'),
        'source': data.get('source', 'manual')
    }

    success, reason = db.insert_job(job_data)

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Job added successfully',
            'data': job_data
        }), 201
    elif reason == 'duplicate':
        return jsonify({
            'status': 'error',
            'message': f'A job with this link already exists in the database.'
        }), 409
    else:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {reason}'
        }), 500


@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def api_delete_job(job_id):
    """
    DELETE /api/jobs/<id>
    Soft delete a job listing by ID.

    Returns:
        JSON response with deletion status
    """
    success = db.delete_job(job_id)

    if success:
        return jsonify({
            'status': 'success',
            'message': f'Job {job_id} deleted successfully'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': f'Job with ID {job_id} not found'
        }), 404


@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """
    GET /api/stats
    Get dashboard statistics.

    Returns:
        JSON response with statistics
    """
    stats = db.get_stats()
    return jsonify({
        'status': 'success',
        'data': stats
    }), 200


# ============================================
# Action Routes (Trigger operations)
# ============================================

@app.route('/api/scrape', methods=['POST'])
def api_trigger_scrape():
    """
    POST /api/scrape
    Trigger an immediate scraping job.

    Optional JSON body:
        - platform (str): Specific platform to scrape (linkedin, indeed, naukri)
        - role (str): Override default search role
        - location (str): Override default search location

    Returns:
        JSON response with scraping results
    """
    data = request.get_json() or {}
    platform = data.get('platform', 'all')
    role = data.get('role')
    location = data.get('location')

    manager = JobScraperManager(role, location)

    if platform == 'all':
        results = manager.run_all()
        total = sum(len(jobs) for jobs in results.values())
        return jsonify({
            'status': 'success',
            'message': f'Scraping complete. Found {total} jobs.',
            'details': {k: len(v) for k, v in results.items()}
        }), 200
    else:
        jobs = manager.run_single(platform)
        return jsonify({
            'status': 'success',
            'message': f'Scraped {len(jobs)} jobs from {platform}',
            'count': len(jobs)
        }), 200


@app.route('/api/email', methods=['POST'])
def api_trigger_email():
    """
    POST /api/email
    Trigger an immediate email alert.

    Returns:
        JSON response with email status
    """
    email_service = EmailService()
    success = email_service.send_daily_alert()

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Email alert sent successfully'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send email alert. Check configuration.'
        }), 500


@app.route('/api/scheduler/status', methods=['GET'])
def api_scheduler_status():
    """
    GET /api/scheduler/status
    Get the current scheduler status and upcoming jobs.

    Returns:
        JSON response with scheduler information
    """
    status = job_scheduler.get_status()
    return jsonify({
        'status': 'success',
        'scheduler_running': job_scheduler.scheduler.running,
        'jobs': status
    }), 200


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found'
        }), 404
    return render_template('dashboard.html', jobs=[], stats=db.get_stats(), filters={}, total_results=0), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    if request.path.startswith('/api/'):
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    return "Internal Server Error", 500


# ============================================
# Application Entry Point
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  🚀 AutoHire AI - Automated Job Application Tracker")
    print("=" * 60)

    # Initialize database on first run
    print("\n[STARTUP] Initializing database...")
    db.initialize_database()

    # Validate configuration
    config_errors = Config.validate()
    if config_errors:
        print("\n⚠️  Configuration warnings:")
        for err in config_errors:
            print(f"   - {err}")
        print("   Some features (email, etc.) may not work without proper config.")
        print("   Copy .env.example to .env and update values.\n")

    # Start the background scheduler
    print("[STARTUP] Starting background scheduler...")
    job_scheduler.start()

    # Start Flask server
    print(f"\n[STARTUP] Starting Flask server on port {Config.FLASK_PORT}...")
    print(f"[STARTUP] Dashboard: http://localhost:{Config.FLASK_PORT}")
    print(f"[STARTUP] API Base:  http://localhost:{Config.FLASK_PORT}/api\n")

    try:
        app.run(
            host='0.0.0.0',
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG,
            use_reloader=False  # Prevent double scheduler initialization
        )
    except KeyboardInterrupt:
        job_scheduler.stop()
        print("\n[SHUTDOWN] AutoHire AI stopped.")
