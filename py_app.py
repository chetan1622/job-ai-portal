import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

# ------------------ DATABASE CONFIG ------------------
DB_NAME = "job_ai.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'job_seeker',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
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
    c.execute(
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_posting_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Applied',
            applied_date TEXT DEFAULT CURRENT_TIMESTAMP,
            resume_path TEXT,
            cover_letter TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (job_posting_id) REFERENCES job_postings (id)
        )
    """)
    conn.commit()
    conn.close()

# ------------------ SECURITY FUNCTIONS ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# ------------------ AUTH FUNCTIONS ------------------
def create_user(name, email, password, role='job_seeker'):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if user and verify_password(password, user[3]):
        return user
    return None

# ------------------ JOB APPLICATION FUNCTIONS ------------------
def add_job_application(user_id, company, position, notes=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO job_applications (user_id, company, position, notes) VALUES (?, ?, ?, ?)",
        (user_id, company, position, notes)
    )
    conn.commit()
    conn.close()

def get_user_applications(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM job_applications WHERE user_id = ? ORDER BY applied_date DESC", (user_id,))
    apps = c.fetchall()
    conn.close()
    return apps

# ------------------ COMPANY FUNCTIONS ------------------
def get_company_by_recruiter(recruiter_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM companies WHERE recruiter_id = ?", (recruiter_id,))
    company = c.fetchone()
    conn.close()
    return company

def save_company_profile(recruiter_id, company_name, industry, website, description, location):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Check if company profile already exists
        existing = get_company_by_recruiter(recruiter_id)
        if existing:
            # Update existing
            c.execute("""
                UPDATE companies 
                SET company_name=?, industry=?, website=?, description=?, location=? 
                WHERE recruiter_id=?
            """, (company_name, industry, website, description, location, recruiter_id))
        else:
            # Create new
            c.execute("""
                INSERT INTO companies (recruiter_id, company_name, industry, website, description, location) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (recruiter_id, company_name, industry, website, description, location))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving company profile: {e}")
        return False
    finally:
        conn.close()

# ------------------ INIT DB (RUN ONCE) ------------------
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# ------------------ STREAMLIT CONFIG ------------------
st.set_page_config(
    page_title="🚀 Job AI Portal",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(45deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1em;
    }
    .card {
        background: white;
        padding: 2em;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1em 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5em;
        border-radius: 10px;
        text-align: center;
        margin: 0.5em;
    }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ------------------ UI ------------------
st.markdown('<h1 class="main-header">🚀 Job AI Portal</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #4CAF50; margin-top: -10px;">Smart Job Hunting Made Simple</h2>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Your AI-powered job application tracker</p>', unsafe_allow_html=True)

# Sidebar Navigation
if not st.session_state.logged_in:
    # Add logo to sidebar - try local first, then sandbox path
    logo_displayed = False
    try:
        st.sidebar.image("logo.png", width=80, caption="Hire Hunt")
        logo_displayed = True
    except:
        try:
            st.sidebar.image("sandbox:/mnt/data/A_3D-rendered_logo_displays_the_text_ERI_H_HUNT_.png", width=80, caption="Hire Hunt")
            logo_displayed = True
        except:
            st.sidebar.markdown("🚀 **Hire Hunt**  \n*AI-Powered Job Tracking*")
    
    menu = st.sidebar.selectbox("Menu", ["🔐 Login", "✨ Signup"])
else:
    # Add logo to sidebar - try local first, then sandbox path
    logo_displayed = False
    try:
        st.sidebar.image("logo.png", width=100, caption="Hire Hunt")
        logo_displayed = True
    except:
        try:
            st.sidebar.image("sandbox:/mnt/data/A_3D-rendered_logo_displays_the_text_ERI_H_HUNT_.png", width=100, caption="Hire Hunt")
            logo_displayed = True
        except:
            st.sidebar.markdown("🚀 **Hire Hunt**  \n*AI-Powered Job Tracking*")
    
    # Dynamic menu based on user role
    user = st.session_state.user
    user_role = user[4] if len(user) > 4 else 'job_seeker'  # role is at index 4
    
    if user_role == 'recruiter':
        menu = st.sidebar.selectbox("Menu", ["🏠 Dashboard", "🏢 Company Profile", "📋 Job Postings", "👥 Applications", "👤 Profile"])
    else:  # job_seeker
        menu = st.sidebar.selectbox("Menu", ["🏠 Dashboard", "➕ Add Application", "📊 My Applications", "🔍 Browse Jobs", "👤 Profile"])

# ------------------ SIGNUP ------------------
if menu == "✨ Signup":
    st.subheader("📝 Create Your Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name", placeholder="Enter your full name")
        with col2:
            email = st.text_input("📧 Email", placeholder="your.email@example.com")
        
        role = st.radio("🎯 I am a:", ["👨‍💼 Job Seeker", "🏢 Recruiter"], horizontal=True)
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        
        if st.form_submit_button("🎉 Create Account", use_container_width=True):
            role_value = "job_seeker" if role == "👨‍💼 Job Seeker" else "recruiter"
            if not all([name, email, password, confirm_password]):
                st.error("❌ All fields are required!")
            elif password != confirm_password:
                st.error("❌ Passwords don't match!")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters!")
            else:
                if create_user(name, email, password, role_value):
                    st.success("🎉 Account created successfully! Please login.")
                    st.balloons()
                else:
                    st.error("❌ Email already exists. Try logging in instead.")

# ------------------ LOGIN ------------------
elif menu == "🔐 Login":
    st.subheader("🔓 Welcome Back")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="your.email@example.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        if st.form_submit_button("🚀 Login", use_container_width=True):
            user = login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"🎉 Welcome back, {user[1]}!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password")

# ------------------ DASHBOARD ------------------
elif menu == "🏠 Dashboard" and st.session_state.logged_in:
    user = st.session_state.user
    st.subheader(f"🏠 Welcome to your Dashboard, {user[1]}!")
    
    # Stats
    applications = get_user_applications(user[0])
    total_apps = len(applications)
    pending_apps = len([app for app in applications if app[4] == 'Applied'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_apps}</h3>
            <p>Total Applications</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{pending_apps}</h3>
            <p>Pending Review</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_apps - pending_apps}</h3>
            <p>With Updates</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Applications
    st.subheader("📋 Recent Applications")
    if applications:
        for app in applications[:5]:  # Show last 5
            with st.container():
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1em; border-radius: 8px; margin: 0.5em 0; border-left: 4px solid #007bff;">
                    <h4>{app[3]} at {app[2]}</h4>
                    <p><strong>Status:</strong> {app[4]} | <strong>Applied:</strong> {app[5]}</p>
                    {f'<p><strong>Notes:</strong> {app[6]}</p>' if app[6] else ''}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 No applications yet. Add your first job application!")

# ------------------ ADD APPLICATION ------------------
elif menu == "➕ Add Application" and st.session_state.logged_in:
    st.subheader("➕ Add New Job Application")
    
    with st.form("application_form"):
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("🏢 Company Name", placeholder="e.g. Google, Microsoft")
            position = st.text_input("🎯 Position", placeholder="e.g. Software Engineer")
        with col2:
            status = st.selectbox("📊 Status", ["Applied", "Interview Scheduled", "Rejected", "Offer Received", "Accepted"])
        
        notes = st.text_area("📝 Notes", placeholder="Add any additional details about this application...")
        
        if st.form_submit_button("💾 Save Application", use_container_width=True):
            if company and position:
                add_job_application(st.session_state.user[0], company, position, notes)
                st.success("✅ Application added successfully!")
                st.balloons()
            else:
                st.error("❌ Company and Position are required!")

# ------------------ MY APPLICATIONS ------------------
elif menu == "📊 My Applications" and st.session_state.logged_in:
    st.subheader("📊 My Job Applications")
    
    applications = get_user_applications(st.session_state.user[0])
    
    if applications:
        # Filters
        status_filter = st.selectbox("Filter by Status", ["All", "Applied", "Interview Scheduled", "Rejected", "Offer Received", "Accepted"])
        
        filtered_apps = applications if status_filter == "All" else [app for app in applications if app[4] == status_filter]
        
        st.write(f"Showing {len(filtered_apps)} application(s)")
        
        for app in filtered_apps:
            with st.expander(f"{app[3]} at {app[2]} - {app[4]}"):
                st.write(f"**Applied Date:** {app[5]}")
                if app[6]:
                    st.write(f"**Notes:** {app[6]}")
                
                # Status update
                new_status = st.selectbox(
                    "Update Status",
                    ["Applied", "Interview Scheduled", "Rejected", "Offer Received", "Accepted"],
                    index=["Applied", "Interview Scheduled", "Rejected", "Offer Received", "Accepted"].index(app[4]),
                    key=f"status_{app[0]}"
                )
                
                if new_status != app[4]:
                    if st.button("Update Status", key=f"update_{app[0]}"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute("UPDATE job_applications SET status = ? WHERE id = ?", (new_status, app[0]))
                        conn.commit()
                        conn.close()
                        st.success("✅ Status updated!")
                        st.rerun()
    else:
        st.info("📭 No applications yet. Add your first job application!")

# ------------------ COMPANY PROFILE (RECRUITER) ------------------
elif menu == "🏢 Company Profile" and st.session_state.logged_in:
    user = st.session_state.user
    if user[4] != 'recruiter':
        st.error("❌ Access denied. This section is for recruiters only.")
    else:
        st.subheader("🏢 Company Profile Management")
        
        # Check if company profile exists
        company = get_company_by_recruiter(user[0])
        
        if company:
            st.success(f"✅ Company profile found: **{company[2]}**")
            
            # Display current company info
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Industry:** {company[3] or 'Not specified'}")
                st.write(f"**Website:** {company[4] or 'Not specified'}")
            with col2:
                st.write(f"**Location:** {company[6] or 'Not specified'}")
            
            if company[5]:  # description
                st.write(f"**Description:** {company[5]}")
            
            if st.button("✏️ Edit Company Profile"):
                st.session_state.edit_company = True
        else:
            st.info("📝 You haven't set up your company profile yet.")
            st.session_state.edit_company = True
        
        # Edit/Create company profile
        if st.session_state.get('edit_company', False):
            st.subheader("🏢 Setup/Edit Company Profile")
            
            with st.form("company_form"):
                company_name = st.text_input("🏢 Company Name", value=company[2] if company else "")
                industry = st.text_input("🏭 Industry", value=company[3] if company else "")
                website = st.text_input("🌐 Website", value=company[4] if company else "", placeholder="https://www.company.com")
                location = st.text_input("📍 Location", value=company[6] if company else "")
                description = st.text_area("📝 Description", value=company[5] if company else "", height=100)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Company Profile", use_container_width=True):
                        if save_company_profile(user[0], company_name, industry, website, description, location):
                            st.success("✅ Company profile saved successfully!")
                            st.session_state.edit_company = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to save company profile.")
                
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.edit_company = False
                        st.rerun()

# ------------------ PROFILE ------------------
elif menu == "👤 Profile" and st.session_state.logged_in:
    user = st.session_state.user
    st.subheader("👤 My Profile")
    
    st.write(f"**Name:** {user[1]}")
    st.write(f"**Email:** {user[2]}")
    st.write(f"**Member since:** {user[4] if len(user) > 4 else 'N/A'}")
    
    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("👋 Logged out successfully!")
        st.rerun()

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #666;">🚀 Powered by Job AI | Track your career journey</p>', unsafe_allow_html=True)