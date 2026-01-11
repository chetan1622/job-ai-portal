from setuptools import setup, find_packages

setup(
    name="job-ai-portal",
    version="1.0.0",
    description="AI-powered job application tracking system",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "beautifulsoup4>=4.12.0"
    ],
    python_requires=">=3.8",
)