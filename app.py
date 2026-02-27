# CincyJunkBot - Flask Web Application
# Junk Removal Lead Generation System for Cincinnati/Northern Kentucky
# Version with embedded HTML - no templates folder needed

from flask import Flask, send_file, jsonify, request
from flask_socketIO import SocketIO
import threading
import time
import json
from datetime import datetime
import os

from bot.scraper import CincinnatiCraigslistScraper
from bot.filters import LeadFilter
from bot.notifier import NotificationManager
from bot.database import LeadDatabase

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cincy-junk-bot-secret-key-2024'
app.config['JSON_SORT_KEYS'] = False

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize components
db = LeadDatabase()
lead_filter = LeadFilter()
notifier = NotificationManager()
scraper = CincinnatiCraigslistScraper()

# Bot control variables
bot_running = False
bot_thread = None

# HTML Dashboard - embedded directly
DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CincyJunkBot - Cincinnati/NKY Junk Removal Leads</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0f1419; color: #e7e9ea; min-height: 100vh; }

        .header { background: #1a1f26; padding: 20px 30px; border-bottom: 1px solid #2f3940; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: 700; color: #00d4aa; }
        .logo span { color: #fff; }
        .bot-status { display: flex; align-items: center; gap: 15px; }
        .status-badge { padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 500; }
        .status-running { background: #00d4aa20; color: #00d4aa; border: 1px solid #00d4aa40; }
        .status-stopped { background: #ff6b6b20; color: #ff6b6b; border: 1px solid #ff6b6b40; }
        .btn { padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s; }
        .btn-start { background: #00d4aa; color: #0f1419; }
        .btn-start:hover { background: #00e6b8; }
        .btn-stop { background: #ff6b6b; color: #fff; }
        .btn-stop:hover { background: #ff8585; }

        .main-content { padding: 30px; max-width: 1600px; margin: 0 auto; }

        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #1a1f26; border-radius: 12px; padding: 24px; border: 1px solid #2f3940; }
        .stat-label { font-size: 14px; color: #8b98a5; margin-bottom: 8px; }
        .stat-value { font-size: 32px; font-weight: 700; }
        .stat-value.hot { color: #ff6b6b; }
        .stat-value.new { color: #00d4aa; }
        .stat-value.quoted { color: #ffd93d; }

        .filters-bar { background: #1a1f26; padding: 20px; border-radius: 12px; border: 1px solid #2f3940; margin-bottom: 20px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }
        .filter-group { display: flex; align-items: center; gap: 10px; }
        .filter-label { font-size: 14px; color: #8b98a5; }
        .filter-select { background: #0f1419; border: 1px solid #2f3940; color: #e7e9ea; padding: 10px 16px; border-radius: 8px; font-size: 14px; }
        .search-input { background: #0f1419; border: 1px solid #2f3940; color: #e7e9ea; padding: 10px 16px; border-radius: 8px; font-size: 14px; width: 300px; }

        .leads-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }
        .lead-card { background: #1a1f26; border-radius: 12px; border: 1px solid #2f3940; overflow: hidden; transition: transform 0.2s, border-color 0.2s; }
        .lead-card:hover { transform: translateY(-2px); border-color: #00d4aa40; }
        .lead-card.hot { border-left: 4px solid #ff6b6b; }

        .lead-header { padding: 20px; border-bottom: 1px solid #2f3940; display: flex; justify-content: space-between; align-items: flex-start; }
        .lead-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; color: #fff; }
        .lead-location { font-size: 14px; color: #8b98a5; display: flex; align-items: center; gap: 6px; }
        .priority-badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .priority-high { background: #ff6b6b20; color: #ff6b6b; }
        .priority-medium { background: #ffd93d20; color: #ffd93d; }
        .priority-low { background: #00d4aa20; color: #00d4aa; }

        .lead-body { padding: 20px; }
        .lead-description { font-size: 14px; color: #8b98a5; line-height: 1.6; margin-bottom: 15px; }
        .lead-meta { display: flex; gap: 20px; margin-bottom: 15px; }
        .meta-item { font-size: 13px; color: #8b98a5; }
        .meta-item strong { color: #e7e9ea; }

        .lead-actions { display: flex; gap: 10px; flex-wrap: wrap; }
        .btn-action { padding: 8px 16px; border-radius: 6px; border: 1px solid #2f3940; background: #0f1419; color: #e7e9ea; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.2s; }
        .btn-action:hover { background: #2f3940; border-color: #00d4aa; }
        .btn-call { background: #00d4aa20; border-color: #00d4aa40; color: #00d4aa; }
        .btn-call:hover { background: #00d4aa30; }
        .btn-quote { background: #ffd93d20; border-color: #ffd93d40; color: #ffd93d; }

        .source-tag { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; background: #3b82f620; color: #3b82f6; text-transform: uppercase; }

        .empty-state { text-align: center; padding: 60px; color: #8b98a5; }
        .empty-icon { font-size: 48px; margin-bottom: 20px; }

        /* Modal */
        .modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 1000; }
        .modal-overlay.active { display: flex; }
        .modal { background: #1a1f26; border-radius: 16px; padding: 30px; width: 90%; max-width: 500px; border: 1px solid #2f3940; }
        .modal-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; }
        .modal-textarea { width: 100%; background: #0f1419; border: 1px solid #2f3940; color: #e7e9ea; padding: 15px; border-radius: 8px; font-size: 14px; min-height: 120px; resize: vertical; margin-bottom: 20px; }
        .modal-buttons { display: flex; gap: 10px; justify-content: flex-end; }

        .last-check { font-size: 12px; color: #8b98a5; margin-top: 10px; text-align: right; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Cincy<span>Junk</span>Bot</div>
        <div class="bot-status">
            <span id="statusBadge" class="status-badge status-stopped">Bot Stopped</span>
            <button id="startBtn" class="btn btn-start" onclick="startBot()">Start Bot</button>
            <button id="stopBtn" class="btn btn-stop" onclick="stopBot()" style="display:none;">Stop Bot</button>
        </div>
    </div>

    <div class="main-content">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Leads</div>
                <div class="stat-value" id="totalLeads">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Hot Leads (75+)</div>
                <div class="stat-value hot" id="hotLeads">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">New Leads</div>
                <div class="stat-value new" id="newLeads">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Quoted/Contacted</div>
                <div class="stat-value quoted" id="quotedLeads">0</div>
            </div>
        </div>

        <div class="filters-bar">
            <div class="filter-group">
                <span class="filter-label">Status:</span>
                <select class="filter-select" id="statusFilter" onchange="loadLeads()">
                    <option value="all">All Status</option>
                    <option value="new">New</option>
                    <option value="contacted">Contacted</option>
                    <option value="quoted">Quoted</option>
                    <option value="closed">Closed</option>
                </select>
            </div>
            <div class="filter-group">
                <span class="filter-label">Source:</span>
                <select class="filter-select" id="sourceFilter" onchange="loadLeads()">
                    <option value="all">All Sources</option>
                    <option value="craigslist">Craigslist</option>
                    <option value="facebook">Facebook</option>
                    <option value="nextdoor">Nextdoor</option>
                </select>
            </div>
            <input type="text" class="search-input" placeholder="Search leads..." id="searchInput" oninput="loadLeads()">
        </div>

        <div class="leads-grid" id="leadsGrid">
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>No leads found. Start the bot to begin searching!</p>
            </div>
        </div>

        <div class="last-check" id="lastCheck">Last check: Never</div>
    </div>

    <!-- Quick Reply Modal -->
    <div class="modal-overlay" id="replyModal">
        <div class="modal">
            <div class="modal-title">Quick Reply</div>
            <select class="filter-select" style="width:100%; margin-bottom:15px;" id="templateSelect" onchange="selectTemplate()">
                <option value="">Select a template...</option>
                <option value="1">Quick Quote</option>
                <option value="2">Availability Check</option>
                <option value="3">Same Day Service</option>
                <option value="4">Professional Inquiry</option>
            </select>
            <textarea class="modal-textarea" id="replyText" placeholder="Type your message..."></textarea>
            <div class="modal-buttons">
                <button class="btn btn-action" onclick="closeModal()">Cancel</button>
                <button class="btn btn-start" onclick="sendReply()">Send Message</button>
            </div>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        let currentLeadId = null;

        // Demo leads for initial load
        const demoLeads = [
            {
                id: 1,
                source: 'craigslist',
                source_url: 'https://cincinnati.craigslist.org/hsh/d/mason-garage-cleanout-full/123456.html',
                title: 'Garage Cleanout - Full House Move Out',
                description: 'Moving out of my house in Mason. Need help cleaning out the garage, basement, and attic. Everything must go. Heavy furniture, boxes, old appliances.',
                location: 'Mason, OH 45040',
                estimated_value: '$300-$500',
                priority_score: 92,
                posted_time: new Date().toISOString(),
                status: 'new'
            },
            {
                id: 2,
                source: 'craigslist',
                source_url: 'https://cincinnati.craigslist.org/hsh/d/cincinnati-estate-cleanout/234567.html',
                title: 'Estate Cleanout Needed - Professional Service',
                description: 'Need junk removal service for estate cleanout. 4 bedroom home with furniture, clothing, and household items. Second floor has heavy furniture.',
                location: 'Hyde Park, Cincinnati OH 45208',
                estimated_value: '$500+',
                priority_score: 88,
                posted_time: new Date().toISOString(),
                status: 'contacted'
            },
            {
                id: 3,
                source: 'facebook',
                source_url: 'https://facebook.com/marketplace/123456',
                title: 'Hot Tub Removal - Need Help ASAP',
                description: 'Removing an old hot tub from backyard. Need someone with a truck and trailer. It\'s in the backyard, need to go through gate.',
                location: 'Union, KY 41091',
                estimated_value: '$175-$300',
                priority_score: 78,
                posted_time: new Date().toISOString(),
                status: 'new'
            },
            {
                id: 4,
                source: 'craigslist',
                source_url: 'https://cincinnati.craigslist.org/hsh/d/covington-construction-debris/345678.html',
                title: 'Construction Debris Removal',
                description: 'Just finished a renovation project. Have about a truck load of construction debris - drywall, lumber, flooring materials.',
                location: 'Covington, KY 41011',
                estimated_value: '$175-$300',
                priority_score: 71,
                posted_time: new Date().toISOString(),
                status: 'quoted'
            },
            {
                id: 5,
                source: 'nextdoor',
                source_url: 'https://nextdoor.com/123456',
                title: 'Need junk removal for shed demo',
                description: 'Looking for someone to demolish and remove an old shed in my backyard. About 10x12 wooden shed.',
                location: 'Maineville, OH 45039',
                estimated_value: '$300-$500',
                priority_score: 82,
                posted_time: new Date().toISOString(),
                status: 'new'
            }
        ];

        let leads = [...demoLeads];

        function getPriorityClass(score) {
            if (score >= 75) return 'priority-high';
            if (score >= 50) return 'priority-medium';
            return 'priority-low';
        }

        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }

        function renderLeads(leadsToRender) {
            const grid = document.getElementById('leadsGrid');

            if (leadsToRender.length === 0) {
                grid.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><p>No leads match your filters.</p></div>';
                return;
            }

            grid.innerHTML = leadsToRender.map(lead => `
                <div class="lead-card ${lead.priority_score >= 75 ? 'hot' : ''}">
                    <div class="lead-header">
                        <div>
                            <div class="lead-title">${lead.title}</div>
                            <div class="lead-location">📍 ${lead.location}</div>
                        </div>
                        <span class="priority-badge ${getPriorityClass(lead.priority_score)}">${lead.priority_score}</span>
                    </div>
                    <div class="lead-body">
                        <p class="lead-description">${lead.description}</p>
                        <div class="lead-meta">
                            <span class="meta-item"><strong>Value:</strong> ${lead.estimated_value}</span>
                            <span class="meta-item"><strong>Posted:</strong> ${formatDate(lead.posted_time)}</span>
                        </div>
                        <div class="lead-meta">
                            <span class="source-tag">${lead.source}</span>
                            <span class="meta-item">Status: <strong style="color: ${lead.status === 'new' ? '#00d4aa' : '#ffd93d'}">${lead.status}</strong></span>
                        </div>
                        <div class="lead-actions">
                            <button class="btn-action btn-call" onclick="callLead(${lead.id})">📞 Call Now</button>
                            <button class="btn-action btn-quote" onclick="openReply(${lead.id})">💬 Quick Reply</button>
                            <button class="btn-action" onclick="showSourceInfo('${lead.source_url}')">🔗 View Post</button>
                            <button class="btn-action" onclick="updateStatus(${lead.id}, 'contacted')">Mark Contacted</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function loadLeads() {
            const status = document.getElementById('statusFilter').value;
            const source = document.getElementById('sourceFilter').value;
            const search = document.getElementById('searchInput').value.toLowerCase();

            let filtered = leads;

            if (status !== 'all') {
                filtered = filtered.filter(l => l.status === status);
            }
            if (source !== 'all') {
                filtered = filtered.filter(l => l.source === source);
            }
            if (search) {
                filtered = filtered.filter(l =>
                    l.title.toLowerCase().includes(search) ||
                    l.description.toLowerCase().includes(search) ||
                    l.location.toLowerCase().includes(search)
                );
            }

            renderLeads(filtered);
            updateStats();
        }

        function updateStats() {
            document.getElementById('totalLeads').textContent = leads.length;
            document.getElementById('hotLeads').textContent = leads.filter(l => l.priority_score >= 75).length;
            document.getElementById('newLeads').textContent = leads.filter(l => l.status === 'new').length;
            document.getElementById('quotedLeads').textContent = leads.filter(l => l.status === 'contacted' || l.status === 'quoted').length;
        }

        function startBot() {
            document.getElementById('statusBadge').textContent = 'Bot Running';
            document.getElementById('statusBadge').className = 'status-badge status-running';
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-block';
            document.getElementById('lastCheck').textContent = 'Last check: ' + new Date().toLocaleTimeString();

            // Simulate finding a new lead
            setTimeout(() => {
                const newLead = {
                    id: leads.length + 1,
                    source: 'craigslist',
                    source_url: 'https://cincinnati.craigslist.org/hsh/d/new-lead-' + Date.now() + '.html',
                    title: 'New Lead Found - Basement Cleanout',
                    description: 'Fresh lead from Craigslist in the West Chester area.',
                    location: 'West Chester, OH 45069',
                    estimated_value: '$250-$400',
                    priority_score: 85,
                    posted_time: new Date().toISOString(),
                    status: 'new'
                };
                leads.unshift(newLead);
                loadLeads();
            }, 3000);
        }

        function stopBot() {
            document.getElementById('statusBadge').textContent = 'Bot Stopped';
            document.getElementById('statusBadge').className = 'status-badge status-stopped';
            document.getElementById('startBtn').style.display = 'inline-block';
            document.getElementById('stopBtn').style.display = 'none';
        }

        function callLead(leadId) {
            const lead = leads.find(l => l.id === leadId);
            if (confirm('Calling lead: ' + lead.location + '\\n\\nThis will mark them as contacted. Continue?')) {
                updateStatus(leadId, 'contacted');
                alert('Lead marked as contacted! In production, this would initiate a phone call.');
            }
        }

        function updateStatus(leadId, newStatus) {
            const lead = leads.find(l => l.id === leadId);
            if (lead) {
                lead.status = newStatus;
                loadLeads();
            }
        }

        function openReply(leadId) {
            currentLeadId = leadId;
            document.getElementById('replyModal').classList.add('active');
        }

        function closeModal() {
            document.getElementById('replyModal').classList.remove('active');
            document.getElementById('replyText').value = '';
            document.getElementById('templateSelect').value = '';
        }

        function selectTemplate() {
            const templates = {
                '1': 'Hi! I saw your post about junk removal in {location}. I can help with this today! Can you tell me more about what needs to be removed?',
                '2': 'Hello! Interested in your junk removal needs in {location}. I have availability this week. What days work for you?',
                '3': 'Hey! I can do same-day service for your junk removal in {location}. I have a truck available now. Would you like me to come give you a quote?',
                '4': 'Hi there, I came across your listing for junk removal. I run a professional junk removal service in the Cincinnati area. Would you like a free estimate?'
            };

            const lead = leads.find(l => l.id === currentLeadId);
            const template = templates[document.getElementById('templateSelect').value];
            if (template && lead) {
                document.getElementById('replyText').value = template.replace('{location}', lead.location);
            }
        }

        function sendReply() {
            alert('Message sent! In production, this would send an SMS/email to the lead.');
            closeModal();
        }

        function showSourceInfo(url) {
            alert('Demo Mode: In production, this would open: ' + url);
        }

        // Initial load
        loadLeads();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    """Main dashboard page - serves embedded HTML"""
    return DASHBOARD_HTML

@app.route('/api/leads')
def get_leads():
    """Get all leads with optional filters"""
    status = request.args.get('status', 'all')
    source = request.args.get('source', 'all')
    limit = int(request.args.get('limit', 50))

    leads = db.get_leads(status=status, source=source, limit=limit)
    return jsonify({
        'success': True,
        'leads': leads,
        'count': len(leads)
    })

@app.route('/api/leads/<lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Get a specific lead by ID"""
    lead = db.get_lead(lead_id)
    if lead:
        return jsonify({'success': True, 'lead': lead})
    return jsonify({'success': False, 'error': 'Lead not found'}), 404

@app.route('/api/leads/<lead_id>/status', methods=['PUT'])
def update_lead_status(lead_id):
    """Update lead status"""
    data = request.get_json()
    new_status = data.get('status')

    if db.update_status(lead_id, new_status):
        socketio.emit('lead_updated', {'lead_id': lead_id, 'status': new_status})
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to update'}), 400

@app.route('/api/leads/<lead_id>/notes', methods=['PUT'])
def update_lead_notes(lead_id):
    """Update lead notes"""
    data = request.get_json()
    notes = data.get('notes', '')

    if db.update_notes(lead_id, notes):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Failed to update'}), 400

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    stats = db.get_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/bot/status')
def bot_status():
    """Get bot running status"""
    global bot_running
    return jsonify({
        'success': True,
        'running': bot_running,
        'last_check': scraper.last_check_time if hasattr(scraper, 'last_check_time') else None
    })

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the lead generation bot"""
    global bot_running, bot_thread

    if not bot_running:
        bot_running = True
        bot_thread = threading.Thread(target=bot_worker, daemon=True)
        bot_thread.start()
        return jsonify({'success': True, 'message': 'Bot started'})
    return jsonify({'success': False, 'error': 'Bot already running'}), 400

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the lead generation bot"""
    global bot_running

    if bot_running:
        bot_running = False
        return jsonify({'success': True, 'message': 'Bot stopped'})
    return jsonify({'success': False, 'error': 'Bot not running'}), 400

@app.route('/api/templates')
def get_templates():
    """Get quick response templates"""
    templates = [
        {
            'id': 1,
            'name': 'Quick Quote',
            'content': 'Hi! I saw your post about {service} in {location}. I can help with this today! Can you tell me more about what needs to be removed?',
            'type': 'sms'
        },
        {
            'id': 2,
            'name': 'Availability Check',
            'content': 'Hello! Interested in your junk removal needs in {location}. I have availability this week. What days work for you?',
            'type': 'sms'
        },
        {
            'id': 3,
            'name': 'Same Day Service',
            'content': 'Hey! I can do same-day service for your {service} in {location}. I have a truck available now. Would you like me to come give you a quote?',
            'type': 'sms'
        },
        {
            'id': 4,
            'name': 'Professional Inquiry',
            'content': 'Hi there, I came across your listing for {service}. I run a professional junk removal service in the Cincinnati area. Would you like a free estimate?',
            'type': 'email'
        }
    ]
    return jsonify({'success': True, 'templates': templates})

@app.route('/api/export', methods=['GET'])
def export_leads():
    """Export leads to CSV format"""
    leads = db.get_leads(status='all', limit=1000)

    csv_data = "ID,Source,Title,Location,Estimated Value,Status,Posted Time,Discovered Time\n"
    for lead in leads:
        csv_data += f"{lead['id']},{lead['source']},{lead['title']},{lead['location']},{lead['estimated_value']},{lead['status']},{lead['posted_time']},{lead['discovered_time']}\n"

    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=leads.csv'
    }

def bot_worker():
    """Background worker that scrapes for leads"""
    global bot_running

    check_interval = 60  # Check every 60 seconds

    while bot_running:
        try:
            # Scrape Cincinnati Craigslist
            new_leads = scraper.fetch_leads()

            for raw_lead in new_leads:
                # Filter the lead
                filtered_lead = lead_filter.process(raw_lead)

                if filtered_lead:
                    # Check for duplicates
                    if not db.is_duplicate(filtered_lead['source_url']):
                        # Save to database
                        lead_id = db.add_lead(filtered_lead)
                        filtered_lead['id'] = lead_id

                        # Emit to connected clients
                        socketio.emit('new_lead', filtered_lead)

                        # Send notification for hot leads
                        if filtered_lead.get('priority_score', 0) >= 75:
                            notifier.send_alert(filtered_lead)

            # Update last check time
            scraper.last_check_time = datetime.now().isoformat()

        except Exception as e:
            print(f"Bot error: {e}")

        # Sleep before next check
        time.sleep(check_interval)

# Demo data for initial testing
def init_demo_data():
    """Initialize with some demo leads for testing"""
    demo_leads = [
        {
            'source': 'craigslist',
            'source_url': 'https://cincinnati.craigslist.org/hsh/d/mason-garage-cleanout-full/123456.html',
            'title': 'Garage Cleanout - Full House Move Out',
            'description': 'Moving out of my house in Mason. Need help cleaning out the garage, basement, and attic. Everything must go. Heavy furniture, boxes, old appliances. Looking for someone who can take everything.',
            'location': 'Mason, OH 45040',
            'keywords_detected': ['garage cleanout', 'full house', 'basement', 'attic', 'heavy furniture', 'appliances'],
            'estimated_value': '$300-$500',
            'priority_score': 92,
            'posted_time': datetime.now().isoformat(),
            'status': 'new'
        },
        {
            'source': 'craigslist',
            'source_url': 'https://cincinnati.craigslist.org/hsh/d/cincinnati-estate-cleanout/234567.html',
            'title': 'Estate Cleanout Needed - Professional Service',
            'description': 'Need junk removal service for estate cleanout. 4 bedroom home with furniture, clothing, and household items. Second floor has heavy furniture that needs to be carried down. Immediate availability preferred.',
            'location': 'Hyde Park, Cincinnati OH 45208',
            'keywords_detected': ['estate cleanout', 'furniture', 'heavy', 'immediate'],
            'estimated_value': '$500+',
            'priority_score': 88,
            'posted_time': datetime.now().isoformat(),
            'status': 'contacted'
        },
        {
            'source': 'facebook',
            'source_url': 'https://facebook.com/marketplace/123456',
            'title': 'Hot Tub Removal - Need Help ASAP',
            'description': 'Removing an old hot tub from backyard. Need someone with a truck and trailer. It\'s in the backyard, need to go through gate. Will pay well for quick service.',
            'location': 'Union, KY 41091',
            'keywords_detected': ['hot tub removal', 'truck', 'trailer', 'backyard'],
            'estimated_value': '$175-$300',
            'priority_score': 78,
            'posted_time': datetime.now().isoformat(),
            'status': 'new'
        },
        {
            'source': 'craigslist',
            'source_url': 'https://cincinnati.craigslist.org/hsh/d/covington-construction-debris/345678.html',
            'title': 'Construction Debris Removal',
            'description': 'Just finished a renovation project. Have about a truck load of construction debris - drywall, lumber, flooring materials. Need someone to haul it away.',
            'location': 'Covington, KY 41011',
            'keywords_detected': ['construction debris', 'renovation', 'truck load'],
            'estimated_value': '$175-$300',
            'priority_score': 71,
            'posted_time': datetime.now().isoformat(),
            'status': 'quoted'
        },
        {
            'source': 'nextdoor',
            'source_url': 'https://nextdoor.com/123456',
            'title': 'Need junk removal for shed demo',
            'description': 'Looking for someone to demolish and remove an old shed in my backyard. About 10x12 wooden shed. Can handle removal?',
            'location': 'Maineville, OH 45039',
            'keywords_detected': ['shed demo', 'demolish', 'wooden'],
            'estimated_value': '$300-$500',
            'priority_score': 82,
            'posted_time': datetime.now().isoformat(),
            'status': 'new'
        }
    ]

    # Add demo leads if database is empty
    existing = db.get_leads(limit=1)
    if not existing:
        for lead in demo_leads:
            db.add_lead(lead)

# Initialize demo data on startup
with app.app_context():
    init_demo_data()

if __name__ == '__main__':
    # Run with SocketIO support
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
