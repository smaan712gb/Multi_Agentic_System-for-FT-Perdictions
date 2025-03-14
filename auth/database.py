import sqlite3
import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
import time

class Database:
    def __init__(self, db_path="auth/users.db"):
        """Initialize the database connection"""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create the necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        ''')
        
        # Subscriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            runs_allowed INTEGER NOT NULL,
            runs_used INTEGER DEFAULT 0,
            payment_id TEXT,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Usage logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            subscription_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
        )
        ''')
        
        self.conn.commit()
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create a new user"""
        cursor = self.conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return {"success": False, "message": "Username or email already exists"}
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        created_at = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, email, password_hash, created_at)
        )
        
        # Create free trial subscription
        self.create_free_trial(user_id)
        
        self.conn.commit()
        return {"success": True, "user_id": user_id}
    
    def create_free_trial(self, user_id):
        """Create a free trial subscription for a new user"""
        subscription_id = str(uuid.uuid4())
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=3)).isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO subscriptions (id, user_id, plan_type, start_date, end_date, runs_allowed, runs_used) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (subscription_id, user_id, "free_trial", start_date, end_date, 3, 0)
        )
        self.conn.commit()
        return subscription_id
    
    def authenticate_user(self, username, password):
        """Authenticate a user by username and password"""
        cursor = self.conn.cursor()
        password_hash = self.hash_password(password)
        
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
        user = cursor.fetchone()
        
        if not user:
            return {"success": False, "message": "Invalid username or password"}
        
        # Update last login
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user["id"]))
        self.conn.commit()
        
        # Create session
        session_id = self.create_session(user["id"])
        
        return {"success": True, "user_id": user["id"], "session_id": session_id}
    
    def create_session(self, user_id):
        """Create a new session for a user"""
        session_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=1)).isoformat()  # Sessions expire after 1 day
        
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (session_id, user_id, created_at, expires_at)
        )
        self.conn.commit()
        
        return session_id
    
    def validate_session(self, session_id):
        """Validate a session and return user_id if valid"""
        if not session_id:
            return None
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            return None
        
        # Check if session is expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            # Delete expired session
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            self.conn.commit()
            return None
        
        return session["user_id"]
    
    def get_user(self, user_id):
        """Get user details by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, email, created_at, last_login FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return None
        
        return dict(user)
    
    def get_active_subscription(self, user_id):
        """Get the active subscription for a user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM subscriptions WHERE user_id = ? AND active = 1 ORDER BY end_date DESC LIMIT 1",
            (user_id,)
        )
        subscription = cursor.fetchone()
        
        if not subscription:
            return None
        
        subscription_dict = dict(subscription)
        
        # Check if subscription is expired
        if subscription_dict["end_date"]:
            end_date = datetime.fromisoformat(subscription_dict["end_date"])
            if datetime.now() > end_date:
                # Deactivate subscription
                cursor.execute("UPDATE subscriptions SET active = 0 WHERE id = ?", (subscription_dict["id"],))
                self.conn.commit()
                return None
        
        # Check if all runs are used
        if subscription_dict["runs_used"] >= subscription_dict["runs_allowed"]:
            # Deactivate subscription if all runs are used
            cursor.execute("UPDATE subscriptions SET active = 0 WHERE id = ?", (subscription_dict["id"],))
            self.conn.commit()
            return None
        
        return subscription_dict
    
    def create_subscription(self, user_id, plan_type, payment_id=None):
        """Create a new subscription for a user"""
        subscription_id = str(uuid.uuid4())
        start_date = datetime.now().isoformat()
        
        # Set subscription details based on plan type
        if plan_type == "basic":
            runs_allowed = 10
            end_date = None  # No expiration date for run-based plans
        elif plan_type == "premium":
            runs_allowed = 100
            end_date = (datetime.now() + timedelta(days=30)).isoformat()  # 30-day expiration
        else:
            return {"success": False, "message": "Invalid plan type"}
        
        cursor = self.conn.cursor()
        
        # Deactivate any existing active subscriptions
        cursor.execute("UPDATE subscriptions SET active = 0 WHERE user_id = ? AND active = 1", (user_id,))
        
        # Create new subscription
        cursor.execute(
            "INSERT INTO subscriptions (id, user_id, plan_type, start_date, end_date, runs_allowed, runs_used, payment_id, active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (subscription_id, user_id, plan_type, start_date, end_date, runs_allowed, 0, payment_id, 1)
        )
        self.conn.commit()
        
        return {"success": True, "subscription_id": subscription_id}
    
    def log_usage(self, user_id, subscription_id, symbol):
        """Log usage of the analysis tool"""
        cursor = self.conn.cursor()
        
        # Increment runs_used in subscription
        cursor.execute("UPDATE subscriptions SET runs_used = runs_used + 1 WHERE id = ?", (subscription_id,))
        
        # Log usage
        log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO usage_logs (id, user_id, subscription_id, timestamp, symbol) VALUES (?, ?, ?, ?, ?)",
            (log_id, user_id, subscription_id, timestamp, symbol)
        )
        
        self.conn.commit()
        
        # Get updated subscription
        cursor.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,))
        subscription = cursor.fetchone()
        
        return dict(subscription)
    
    def get_usage_stats(self, user_id):
        """Get usage statistics for a user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT s.plan_type, s.runs_allowed, s.runs_used, s.start_date, s.end_date FROM subscriptions s WHERE s.user_id = ? AND s.active = 1",
            (user_id,)
        )
        subscription = cursor.fetchone()
        
        if not subscription:
            return {"has_subscription": False}
        
        # Get recent usage logs
        cursor.execute(
            "SELECT * FROM usage_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10",
            (user_id,)
        )
        logs = cursor.fetchall()
        
        return {
            "has_subscription": True,
            "plan_type": subscription["plan_type"],
            "runs_allowed": subscription["runs_allowed"],
            "runs_used": subscription["runs_used"],
            "runs_remaining": subscription["runs_allowed"] - subscription["runs_used"],
            "start_date": subscription["start_date"],
            "end_date": subscription["end_date"],
            "recent_usage": [dict(log) for log in logs]
        }
    
    def close(self):
        """Close the database connection"""
        self.conn.close()
