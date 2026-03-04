/**
 * ============================================
 * AutoHire AI - Neumorphic Dashboard Logic
 * ============================================
 */

// ============================================
// Toast Notification System
// ============================================

function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        info: 'info'
    };

    const toast = document.createElement('div');
    toast.className = `stat-card-neo toast toast-${type}`;
    toast.style.cssText = `
        display: flex; align-items: center; gap: 15px; 
        padding: 15px 25px; margin-bottom: 10px;
        background: white; min-width: 300px;
        animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    `;
    
    toast.innerHTML = `
        <i data-lucide="${icons[type] || 'info'}" style="width:20px; color:${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#4a69bd'}"></i>
        <span style="font-size: 13px; font-weight: 600;">${message}</span>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// ============================================
// Modal Management
// ============================================

const addJobModal = document.getElementById('addJobModal');
const btnAddJob = document.getElementById('btnAddJob');
const modalClose = document.getElementById('modalClose');
const btnCancelAdd = document.getElementById('btnCancelAdd');

function openModal() {
    addJobModal.classList.add('active');
}

function closeModal() {
    addJobModal.classList.remove('active');
    document.getElementById('addJobForm').reset();
}

if (btnAddJob) btnAddJob.addEventListener('click', openModal);
if (modalClose) modalClose.addEventListener('click', closeModal);
if (btnCancelAdd) btnCancelAdd.addEventListener('click', closeModal);

// ============================================
// Sidebar Navigation & Portal Filtering
// ============================================

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        // Update active state
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');

        const portalName = item.innerText.split('\n')[0].trim().toLowerCase();
        const cards = document.querySelectorAll('.job-item-neo');

        cards.forEach(card => {
            const source = card.querySelector('.source-pill-neo').innerText.toLowerCase();
            if (portalName === 'all jobs' || source === portalName) {
                card.style.display = 'flex';
                setTimeout(() => card.style.opacity = '1', 50);
            } else {
                card.style.opacity = '0';
                setTimeout(() => card.style.display = 'none', 300);
            }
        });
    });
});

// ============================================
// Add Job Form
// ============================================

const addJobForm = document.getElementById('addJobForm');
if (addJobForm) {
    addJobForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerText;

        submitBtn.innerText = 'Creating...';
        submitBtn.disabled = true;

        const jobData = {
            job_title: document.getElementById('addTitle').value.trim(),
            company_name: document.getElementById('addCompany').value.trim(),
            location: document.getElementById('addLocation').value.trim() || 'Not Specified',
            job_link: document.getElementById('addLink').value.trim(),
            source: 'manual'
        };

        try {
            const response = await fetch('/api/jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(jobData)
            });

            if (response.ok) {
                showToast('Opportunity logged successfully', 'success');
                closeModal();
                setTimeout(() => window.location.reload(), 800);
            } else {
                const err = await response.json();
                showToast(err.message || 'Validation failed', 'error');
            }
        } catch (error) {
            showToast('System offline', 'error');
        } finally {
            submitBtn.innerText = originalText;
            submitBtn.disabled = false;
        }
    });
}

// ============================================
// Delete Job
// ============================================

async function deleteJob(jobId) {
    if (!confirm('Archive this opportunity?')) return;

    try {
        const response = await fetch(`/api/jobs/${jobId}`, { method: 'DELETE' });
        if (response.ok) {
            const card = document.querySelector(`.job-item-neo[data-id="${jobId}"]`);
            if (card) {
                card.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '0';
                card.style.transform = 'translateX(100px) scale(0.9)';
                setTimeout(() => card.remove(), 400);
            }
            showToast('listing archived', 'success');
        }
    } catch (e) {
        showToast('Operation failed', 'error');
    }
}

// ============================================
// Scrape Trigger
// ============================================

async function triggerScrape() {
    const btn = document.getElementById('btnScrape');
    const original = btn.innerHTML;
    
    btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Scraping...';
    btn.disabled = true;
    lucide.createIcons();
    
    showToast('Engine started — scanning LinkedIn & Naukri', 'info');

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({platform: 'all'})
        });
        
        if (response.ok) {
            showToast('Sync complete! New jobs found.', 'success');
            setTimeout(() => window.location.reload(), 1500);
        }
    } catch (e) {
        showToast('Connection error', 'error');
    } finally {
        btn.innerHTML = original;
        btn.disabled = false;
        lucide.createIcons();
    }
}

const btnScrapeManual = document.getElementById('btnScrape');
if (btnScrapeManual) btnScrapeManual.addEventListener('click', triggerScrape);

// ============================================
// Animations & Initialization
// ============================================

function animateCounter(el, target) {
    let count = 0;
    const duration = 1500;
    const startTime = performance.now();

    function update(time) {
        const progress = Math.min((time - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.innerText = Math.floor(eased * target);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

document.addEventListener('DOMContentLoaded', () => {
    // Counters
    document.querySelectorAll('.stat-value-neo').forEach(el => {
        const val = parseInt(el.innerText) || 0;
        el.innerText = '0';
        setTimeout(() => animateCounter(el, val), 300);
    });

    // Staggered Entrance
    document.querySelectorAll('.job-item-neo').forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(() => {
            el.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 400 + (i * 60));
    });
});

// Shortcut Ctrl+N
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        openModal();
    }
});
