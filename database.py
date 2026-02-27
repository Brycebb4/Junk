# Database Module for CincyJunkBot
# SQLite database for lead storage and management

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from config import Config

class LeadDatabase:
    """SQLite database for managing leads"""

    def __init__(self):
        self.config = Config()
        self.db_path = self.config.DATABASE_PATH
        self._init_db()

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize database schema"""
        # Create data directory if needed
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = self._get_connection()
        cursor = conn.cursor()

        # Create leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                source_url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT,
                keywords_detected TEXT,
                estimated_value TEXT,
                priority_score INTEGER,
                posted_time TEXT,
                discovered_time TEXT,
                status TEXT DEFAULT 'new',
                notes TEXT DEFAULT '',
                contact_attempts TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads(priority_score DESC)
        ''')

        conn.commit()
        conn.close()

    def add_lead(self, lead_data):
        """Add a new lead to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO leads (
                    source, source_url, title, description, location,
                    keywords_detected, estimated_value, priority_score,
                    posted_time, discovered_time, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead_data.get('source', 'unknown'),
                lead_data.get('source_url', ''),
                lead_data.get('title', ''),
                lead_data.get('description', ''),
                lead_data.get('location', ''),
                json.dumps(lead_data.get('keywords_detected', [])),
                lead_data.get('estimated_value', 'Unknown'),
                lead_data.get('priority_score', 0),
                lead_data.get('posted_time', datetime.now().isoformat()),
                lead_data.get('discovered_time', datetime.now().isoformat()),
                lead_data.get('status', 'new'),
                lead_data.get('notes', '')
            ))

            lead_id = cursor.lastrowid
            conn.commit()
            return lead_id

        except sqlite3.IntegrityError:
            # Duplicate URL
            return None
        finally:
            conn.close()

    def get_leads(self, status='all', source='all', limit=50):
        """Get leads with optional filters"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = 'SELECT * FROM leads WHERE 1=1'
        params = []

        if status != 'all':
            query += ' AND status = ?'
            params.append(status)

        if source != 'all':
            query += ' AND source = ?'
            params.append(source)

        query += ' ORDER BY priority_score DESC, discovered_time DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert to list of dicts
        leads = []
        for row in rows:
            lead = dict(row)
            lead['keywords_detected'] = json.loads(lead['keywords_detected'])
            lead['contact_attempts'] = json.loads(lead['contact_attempts'])
            leads.append(lead)

        return leads

    def get_lead(self, lead_id):
        """Get a single lead by ID"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM leads WHERE id = ?', (lead_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            lead = dict(row)
            lead['keywords_detected'] = json.loads(lead['keywords_detected'])
            lead['contact_attempts'] = json.loads(lead['contact_attempts'])
            return lead
        return None

    def update_status(self, lead_id, new_status):
        """Update lead status"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE leads
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_status, lead_id))

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_notes(self, lead_id, notes):
        """Update lead notes"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE leads
                SET notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (notes, lead_id))

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def add_contact_attempt(self, lead_id, attempt_type, content):
        """Add a contact attempt to lead history"""
        lead = self.get_lead(lead_id)
        if not lead:
            return False

        attempts = lead.get('contact_attempts', [])
        attempts.append({
            'type': attempt_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE leads
                SET contact_attempts = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (json.dumps(attempts), lead_id))

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def is_duplicate(self, source_url):
        """Check if URL already exists"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM leads WHERE source_url = ?', (source_url,))
        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def delete_lead(self, lead_id):
        """Delete a lead"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM leads WHERE id = ?', (lead_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_stats(self):
        """Get dashboard statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Total leads
        cursor.execute('SELECT COUNT(*) FROM leads')
        total = cursor.fetchone()[0]

        # By status
        cursor.execute('SELECT status, COUNT(*) as count FROM leads GROUP BY status')
        status_counts = dict(cursor.fetchall())

        # Today's leads
        cursor.execute('''
            SELECT COUNT(*) FROM leads
            WHERE date(discovered_time) = date('now')
        ''')
        today = cursor.fetchone()[0]

        # Hot leads (priority >= 75)
        cursor.execute('SELECT COUNT(*) FROM leads WHERE priority_score >= 75')
        hot = cursor.fetchone()[0]

        # Won leads
        won_count = status_counts.get('won', 0)

        conn.close()

        return {
            'total': total,
            'today': today,
            'hot': hot,
            'won': won_count,
            'by_status': status_counts
        }

    def get_leads_by_value_range(self):
        """Get leads grouped by estimated value"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT estimated_value, COUNT(*) as count
            FROM leads
            GROUP BY estimated_value
        ''')

        result = dict(cursor.fetchall())
        conn.close()

        return result

    def search_leads(self, query):
        """Search leads by keyword"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM leads
            WHERE title LIKE ? OR description LIKE ? OR location LIKE ?
            ORDER BY priority_score DESC
            LIMIT 50
        ''', (search_term, search_term, search_term))

        rows = cursor.fetchall()
        conn.close()

        leads = []
        for row in rows:
            lead = dict(row)
            lead['keywords_detected'] = json.loads(lead['keywords_detected'])
            lead['contact_attempts'] = json.loads(lead['contact_attempts'])
            leads.append(lead)

        return leads
