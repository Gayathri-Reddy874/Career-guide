# database.py - Complete updated version
import sqlite3
import json
import hashlib
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='instance/career_guide.db'):
        # Ensure instance directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                education TEXT,
                stream TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        # Psychometric test results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS psychometric_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                personality TEXT,
                interests TEXT,
                aptitudes TEXT,
                work_styles TEXT,
                value_data TEXT,
                raw_answers TEXT,
                ai_summary TEXT,
                career_matches TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Career quiz results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answers TEXT,
                recommendations TEXT,
                ai_summary TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # IQ Test Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iq_test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                iq_score INTEGER,
                correct_count INTEGER,
                section_scores TEXT,
                answers TEXT,
                time_taken INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Admin logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT,
                target_user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
        if not cursor.fetchone():
            hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password, full_name, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@careerguide.com', hashed_password, 'Administrator', 1))
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    # ============ USER MANAGEMENT ============
    def create_user(self, username, email, password, full_name=None, phone=None, education=None, stream=None):
        """Create new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (username, email, password, full_name, phone, education, stream)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, hashed_password, full_name, phone, education, stream))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {'success': True, 'user_id': user_id}
        except sqlite3.IntegrityError as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?
        ''', (username, username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Update last login
            self.update_last_login(user['id'])
            return dict(user)
        return None
    
    def update_last_login(self, user_id):
        """Update user's last login time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_all_users(self, admin_only=False):
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if admin_only:
            cursor.execute('SELECT * FROM users WHERE is_admin = 1 ORDER BY created_at DESC')
        else:
            cursor.execute('SELECT * FROM users WHERE is_admin = 0 ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        return [dict(user) for user in users]
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['full_name', 'phone', 'education', 'stream', 'email']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields and value:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(user_id)
            cursor.execute(f'''
                UPDATE users SET {', '.join(updates)} WHERE id = ?
            ''', values)
            conn.commit()
        
        conn.close()
        return True
    
    def delete_user(self, user_id):
        """Delete user and all their data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete related records
        cursor.execute('DELETE FROM psychometric_results WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM quiz_results WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM iq_test_results WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    
    # ============ PSYCHOMETRIC TEST RESULTS ============
    def save_psychometric_result(self, user_id, personality, interests, aptitudes, work_styles, value_data, raw_answers, ai_summary, career_matches):
        """Save psychometric test results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO psychometric_results 
            (user_id, personality, interests, aptitudes, work_styles, value_data, raw_answers, ai_summary, career_matches)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            json.dumps(personality),
            json.dumps(interests),
            json.dumps(aptitudes),
            json.dumps(work_styles),
            json.dumps(value_data),
            json.dumps(raw_answers),
            ai_summary,
            json.dumps(career_matches)
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return result_id
    
    def get_psychometric_results(self, user_id, limit=10):
        """Get user's psychometric test results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM psychometric_results 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        formatted_results = []
        for r in results:
            result = dict(r)
            result['personality'] = json.loads(result['personality']) if result['personality'] else {}
            result['interests'] = json.loads(result['interests']) if result['interests'] else {}
            result['aptitudes'] = json.loads(result['aptitudes']) if result['aptitudes'] else {}
            result['work_styles'] = json.loads(result['work_styles']) if result['work_styles'] else {}
            result['value_data'] = json.loads(result['value_data']) if result['value_data'] else {}
            result['career_matches'] = json.loads(result['career_matches']) if result['career_matches'] else []
            formatted_results.append(result)
        
        return formatted_results
    
    # ============ QUIZ RESULTS ============
    def save_quiz_result(self, user_id, answers, recommendations, ai_summary):
        """Save quiz results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quiz_results (user_id, answers, recommendations, ai_summary)
            VALUES (?, ?, ?, ?)
        ''', (user_id, json.dumps(answers), json.dumps(recommendations), ai_summary))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return result_id
    
    def get_quiz_results(self, user_id, limit=10):
        """Get user's quiz results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM quiz_results 
            WHERE user_id = ? 
            ORDER BY test_date DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        formatted_results = []
        for r in results:
            result = dict(r)
            result['answers'] = json.loads(result['answers']) if result['answers'] else {}
            result['recommendations'] = json.loads(result['recommendations']) if result['recommendations'] else []
            formatted_results.append(result)
        
        return formatted_results
    
    # ============ IQ TEST RESULTS ============
    def save_iq_test_result(self, user_id, iq_score, correct_count, section_scores, answers, time_taken):
        """Save IQ test results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO iq_test_results 
                (user_id, iq_score, correct_count, section_scores, answers, time_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 
                iq_score, 
                correct_count, 
                json.dumps(section_scores), 
                json.dumps(answers), 
                time_taken
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ IQ test result saved for user {user_id} - Score: {iq_score}")
            return result_id
            
        except Exception as e:
            print(f"❌ Error saving IQ test result: {e}")
            return None

    def get_iq_test_results(self, user_id, limit=5):
        """Get user's IQ test results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM iq_test_results 
                WHERE user_id = ? 
                ORDER BY test_date DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            formatted_results = []
            for r in results:
                result = dict(r)
                result['section_scores'] = json.loads(result['section_scores']) if result['section_scores'] else {}
                result['answers'] = json.loads(result['answers']) if result['answers'] else {}
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error getting IQ test results: {e}")
            return []

    def get_latest_iq_test_result(self, user_id):
        """Get user's latest IQ test result"""
        results = self.get_iq_test_results(user_id, limit=1)
        return results[0] if results else None

    def get_iq_test_stats(self, user_id):
        """Get IQ test statistics for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_tests,
                    AVG(iq_score) as avg_score,
                    MAX(iq_score) as highest_score,
                    MIN(iq_score) as lowest_score
                FROM iq_test_results 
                WHERE user_id = ?
            ''', (user_id,))
            
            stats = cursor.fetchone()
            conn.close()
            
            return dict(stats) if stats else None
            
        except Exception as e:
            print(f"❌ Error getting IQ test stats: {e}")
            return None
    
    # ============ ADMIN LOGS ============
    def log_admin_action(self, admin_id, action, target_user_id=None):
        """Log admin actions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admin_logs (admin_id, action, target_user_id)
            VALUES (?, ?, ?)
        ''', (admin_id, action, target_user_id))
        conn.commit()
        conn.close()
    
    def get_admin_logs(self, limit=50):
        """Get admin action logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l.*, u.username as admin_name 
            FROM admin_logs l
            JOIN users u ON l.admin_id = u.id
            ORDER BY l.timestamp DESC 
            LIMIT ?
        ''', (limit,))
        logs = cursor.fetchall()
        conn.close()
        return [dict(log) for log in logs]
    
    # ============ STATISTICS ============
    def get_stats(self):
        """Get system statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # User count (non-admin)
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_admin = 0')
        stats['total_users'] = cursor.fetchone()['count']
        
        # Psychometric test count
        cursor.execute('SELECT COUNT(*) as count FROM psychometric_results')
        stats['psychometric_tests'] = cursor.fetchone()['count']
        
        # Quiz test count
        cursor.execute('SELECT COUNT(*) as count FROM quiz_results')
        stats['quiz_tests'] = cursor.fetchone()['count']
        
        # IQ test count
        cursor.execute('SELECT COUNT(*) as count FROM iq_test_results')
        stats['iq_tests'] = cursor.fetchone()['count']
        
        # Admin count
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_admin = 1')
        stats['total_admins'] = cursor.fetchone()['count']
        
        # Recent users
        cursor.execute('SELECT * FROM users WHERE is_admin = 0 ORDER BY created_at DESC LIMIT 5')
        stats['recent_users'] = [dict(u) for u in cursor.fetchall()]
        
        conn.close()
        return stats