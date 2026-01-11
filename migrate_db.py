import sqlite3

def migrate_database():
    conn = sqlite3.connect('job_ai.db')
    c = conn.cursor()

    try:
        # Add role column to users table
        c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'job_seeker'")
        print("✅ Added 'role' column to users table")

        # Create companies table
        c.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recruiter_id INTEGER NOT NULL,
                company_name TEXT NOT NULL,
                industry TEXT,
                website TEXT,
                description TEXT,
                location TEXT,
                logo_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recruiter_id) REFERENCES users (id)
            )
        """)
        print("✅ Created companies table")

        # Create job_postings table
        c.execute("""
            CREATE TABLE IF NOT EXISTS job_postings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                requirements TEXT,
                location TEXT,
                salary_range TEXT,
                job_type TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)
        print("✅ Created job_postings table")

        # Create new job_applications table structure
        c.execute("""
            CREATE TABLE IF NOT EXISTS job_applications_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_posting_id INTEGER,
                status TEXT DEFAULT 'Applied',
                applied_date TEXT DEFAULT CURRENT_TIMESTAMP,
                resume_path TEXT,
                cover_letter TEXT,
                notes TEXT,
                company TEXT,  -- Keep for backward compatibility
                position TEXT, -- Keep for backward compatibility
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (job_posting_id) REFERENCES job_postings (id)
            )
        """)

        # Migrate existing data
        c.execute("""
            INSERT INTO job_applications_new (id, user_id, company, position, status, applied_date, notes)
            SELECT id, user_id, company, position, status, applied_date, notes
            FROM job_applications
        """)
        print("✅ Migrated existing job applications data")

        # Drop old table and rename new one
        c.execute("DROP TABLE job_applications")
        c.execute("ALTER TABLE job_applications_new RENAME TO job_applications")
        print("✅ Updated job_applications table structure")

        conn.commit()
        print("🎉 Database migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()