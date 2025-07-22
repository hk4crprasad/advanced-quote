#!/usr/bin/env python3
"""
Database utilities for job management
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from enum import Enum

class JobStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

class JobDatabase:
    """SQLite database for managing story generation jobs"""
    
    def __init__(self, db_path: str = "story_jobs.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS story_jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    story_type TEXT NOT NULL,
                    custom_job TEXT,
                    custom_location TEXT,
                    custom_theme TEXT,
                    language TEXT DEFAULT 'Hindi',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    story_text TEXT,
                    video_url TEXT,
                    audio_filename TEXT,
                    instagram_caption TEXT,
                    youtube_title TEXT,
                    youtube_description TEXT,
                    youtube_tags TEXT,
                    hashtags TEXT,
                    error_message TEXT
                )
            """)
            conn.commit()
    
    def create_job(self, story_type: str, custom_job: Optional[str] = None, 
                   custom_location: Optional[str] = None, custom_theme: Optional[str] = None,
                   language: str = "Hindi") -> str:
        """Create a new job and return job ID"""
        job_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO story_jobs (
                    job_id, status, story_type, custom_job, custom_location, 
                    custom_theme, language
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (job_id, JobStatus.pending, story_type, custom_job, 
                  custom_location, custom_theme, language))
            conn.commit()
        
        return job_id
    
    def update_job_status(self, job_id: str, status: JobStatus, 
                         started_at: Optional[datetime] = None,
                         completed_at: Optional[datetime] = None,
                         error_message: Optional[str] = None):
        """Update job status"""
        with sqlite3.connect(self.db_path) as conn:
            if status == JobStatus.in_progress and started_at:
                conn.execute("""
                    UPDATE story_jobs 
                    SET status = ?, started_at = ?
                    WHERE job_id = ?
                """, (status, started_at, job_id))
            elif status == JobStatus.completed and completed_at:
                conn.execute("""
                    UPDATE story_jobs 
                    SET status = ?, completed_at = ?
                    WHERE job_id = ?
                """, (status, completed_at, job_id))
            elif status == JobStatus.failed:
                conn.execute("""
                    UPDATE story_jobs 
                    SET status = ?, error_message = ?, completed_at = ?
                    WHERE job_id = ?
                """, (status, error_message, datetime.now(), job_id))
            else:
                conn.execute("""
                    UPDATE story_jobs 
                    SET status = ?
                    WHERE job_id = ?
                """, (status, job_id))
            conn.commit()
    
    def update_job_result(self, job_id: str, result: Dict):
        """Update job with generation results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE story_jobs 
                SET story_text = ?, video_url = ?, audio_filename = ?,
                    instagram_caption = ?, youtube_title = ?, youtube_description = ?,
                    youtube_tags = ?, hashtags = ?, status = ?, completed_at = ?
                WHERE job_id = ?
            """, (
                result.get('story_text', ''),
                result.get('video_url', ''),
                result.get('audio_filename', ''),
                result.get('instagram_caption', ''),
                result.get('youtube_title', ''),
                result.get('youtube_description', ''),
                json.dumps(result.get('youtube_tags', [])),
                json.dumps(result.get('hashtags', [])),
                JobStatus.completed if result.get('success') else JobStatus.failed,
                datetime.now(),
                job_id
            ))
            conn.commit()
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job details by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM story_jobs WHERE job_id = ?
            """, (job_id,))
            row = cursor.fetchone()
            
            if row:
                job_data = dict(row)
                # Parse JSON fields
                if job_data['youtube_tags']:
                    job_data['youtube_tags'] = json.loads(job_data['youtube_tags'])
                if job_data['hashtags']:
                    job_data['hashtags'] = json.loads(job_data['hashtags'])
                return job_data
            return None
    
    def get_pending_jobs(self) -> List[Dict]:
        """Get all pending jobs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM story_jobs 
                WHERE status = ? 
                ORDER BY created_at ASC
            """, (JobStatus.pending,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_job_stats(self) -> Dict:
        """Get job statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM story_jobs 
                GROUP BY status
            """)
            stats = dict(cursor.fetchall())
            
            cursor = conn.execute("""
                SELECT COUNT(*) as total 
                FROM story_jobs
            """)
            total = cursor.fetchone()[0]
            
            return {
                "total_jobs": total,
                "pending": stats.get(JobStatus.pending, 0),
                "in_progress": stats.get(JobStatus.in_progress, 0),
                "completed": stats.get(JobStatus.completed, 0),
                "failed": stats.get(JobStatus.failed, 0)
            }
