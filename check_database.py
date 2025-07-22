#!/usr/bin/env python3
"""
Debug script to check database entries and recent jobs
"""

import sqlite3
from pathlib import Path
from src.utils.job_database import JobDatabase

def check_database_entries():
    """Check recent job entries in the database"""
    print("🔍 Checking Database Entries")
    print("=" * 50)
    
    job_db = JobDatabase()
    
    # Connect directly to SQLite to check all jobs
    db_path = Path("story_jobs.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        
        # Get all jobs
        cursor = conn.execute("""
            SELECT job_id, status, story_type, video_url, completed_at, created_at 
            FROM story_jobs 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        jobs = cursor.fetchall()
        
        print(f"📊 Found {len(jobs)} recent jobs:")
        print()
        
        for i, job in enumerate(jobs, 1):
            print(f"{i}. Job ID: {job['job_id'][:8]}...")
            print(f"   Status: {job['status']}")
            print(f"   Type: {job['story_type']}")
            print(f"   Video URL: {job['video_url'] or 'None'}")
            print(f"   Created: {job['created_at']}")
            print(f"   Completed: {job['completed_at'] or 'Not completed'}")
            print()
        
        # Check for completed jobs with missing video URLs
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM story_jobs 
            WHERE status = 'completed' AND (video_url IS NULL OR video_url = '')
        """)
        missing_urls = cursor.fetchone()['count']
        
        print(f"⚠️ Completed jobs with missing video URLs: {missing_urls}")
        
        # Check for completed jobs with video URLs
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM story_jobs 
            WHERE status = 'completed' AND video_url IS NOT NULL AND video_url != ''
        """)
        with_urls = cursor.fetchone()['count']
        
        print(f"✅ Completed jobs with video URLs: {with_urls}")

if __name__ == "__main__":
    check_database_entries()
