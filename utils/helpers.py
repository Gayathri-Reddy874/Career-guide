# utils/helpers.py
import re
import pandas as pd
from datetime import datetime

def parse_salary_range(salary_str):
    """Parse salary string to average value"""
    if pd.isna(salary_str) or salary_str == 'Varies':
        return None
    try:
        if '-' in str(salary_str):
            low, high = str(salary_str).split('-')
            return (float(low) + float(high)) / 2
        return float(salary_str)
    except:
        return None

def extract_skills_from_text(text):
    """Extract skill keywords from text"""
    if not text:
        return []
    skills = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    return list(set(skills[:10]))

def calculate_experience_years(degree, duration_str):
    """Calculate approximate years of experience needed"""
    if pd.isna(duration_str):
        return 0
    try:
        if '-' in str(duration_str):
            low, high = str(duration_str).split('-')
            return int(high)
        return int(duration_str)
    except:
        return 0

def get_career_path_levels(entry_salary, mid_salary, senior_salary):
    """Get career progression levels"""
    return {
        'entry': parse_salary_range(entry_salary),
        'mid': parse_salary_range(mid_salary),
        'senior': parse_salary_range(senior_salary)
    }

def format_duration(duration_str):
    """Format duration string for display"""
    if pd.isna(duration_str):
        return 'Varies'
    return f"{duration_str} years"

def get_outlook_color(outlook):
    """Get color for job outlook badge"""
    outlook_colors = {
        'Excellent': '#d4edda',
        'Growing': '#d1ecf1',
        'Good': '#fff3cd',
        'Stable': '#cfe2ff',
        'Competitive': '#f8d7da',
        'Cyclical': '#e2e3e5'
    }
    return outlook_colors.get(outlook, '#e9ecef')

def get_education_level_rank(education):
    """Get numeric rank for education level"""
    levels = {
        '10+2': 1,
        'Diploma': 2,
        'Bachelor\'s': 3,
        'Master\'s': 4,
        'PG Degree': 4,
        'PhD': 5
    }
    return levels.get(education, 0)

def generate_career_summary(career):
    """Generate a summary text for a career"""
    summary = f"{career['Career_Name']} is a {career['Category']} career "
    summary += f"requiring {career['Min_Education']} education. "
    summary += f"It offers entry-level salaries of {career['Entry_Salary_LPA']} LPA "
    summary += f"with {career['Job_Outlook']} job outlook."
    return summary

def validate_career_data(career):
    """Validate career data dictionary"""
    required_fields = ['Career_ID', 'Career_Name', 'Category', 'Min_Education']
    for field in required_fields:
        if field not in career or pd.isna(career[field]):
            return False
    return True