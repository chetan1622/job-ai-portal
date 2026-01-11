# 🚀 Hire Hunt

A modern, AI-powered job application tracking system built with Streamlit and SQLite.

## ✨ Features

- **🔐 Secure Authentication**: User registration and login with password hashing
- **📊 Dashboard**: Overview of your job application statistics
- **➕ Application Tracking**: Add and manage job applications
- **📈 Status Updates**: Track application progress from Applied to Accepted
- **🎨 Modern UI**: Beautiful, responsive interface with custom styling
- **💾 Local Database**: SQLite database for data persistence

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd job-ai-portal
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run py_app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## � Deployment

### Streamlit Cloud (Recommended)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository and deploy

### Heroku
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-job-ai-portal`
4. Deploy: `git push heroku main`

### Docker
```bash
docker build -t job-ai-portal .
docker run -p 8501:8501 job-ai-portal
```

### Local Network Deployment
```bash
streamlit run py_app.py --server.address 0.0.0.0 --server.port 8501
```

## �📱 Usage

1. **Sign Up**: Create your account with name, email, and password
2. **Login**: Access your personalized dashboard
3. **Add Applications**: Record new job applications with company and position
4. **Track Progress**: Update application statuses and add notes
5. **View Statistics**: Monitor your job search progress on the dashboard

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `name`: User's full name
- `email`: Unique email address
- `password`: Hashed password
- `role`: User role (job_seeker or employer)

### Jobs Table
- `id`: Primary key
- `employer_id`: Foreign key to users
- `company`: Company name
- `title`: Job title
- `description`: Job description
- `location`: Job location
- `salary`: Salary information
- `tags`: Skills/tags

### Applications Table
- `id`: Primary key
- `job_id`: Foreign key to jobs
- `seeker_id`: Foreign key to users
- `resume_path`: Path to uploaded resume
- `status`: Application status
- `applied_at`: Application timestamp

## 🔒 Security

- Passwords are hashed using SHA256
- Email uniqueness enforced
- Session-based authentication
- Input validation and sanitization

## 🎨 Customization

The app uses custom CSS for styling. Modify the `<style>` section in `py_app.py` to customize the appearance.

## 📝 License

This project is open source. Feel free to use and modify as needed.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit**