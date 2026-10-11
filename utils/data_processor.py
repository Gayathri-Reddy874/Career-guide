import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class CareerDataProcessor:
    def __init__(self, csv_path='career.csv'):
        self.df = pd.read_csv(csv_path)
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.career_vectors = None
        self.prepare_data()
    
    def prepare_data(self):
        # Create combined text for each career for similarity matching
        self.df['combined_features'] = (
            self.df['Category'] + ' ' + 
            self.df['Career_Name'] + ' ' + 
            self.df['Key_Technical_Skills'].fillna('') + ' ' + 
            self.df['Key_Soft_Skills'].fillna('') + ' ' + 
            self.df['Preferred_Stream'].fillna('')
        )
        
        # Convert salary strings to numeric averages
        self.df['entry_salary_avg'] = self.df['Entry_Salary_LPA'].apply(
            self._parse_salary_range
        )
        self.df['mid_salary_avg'] = self.df['Mid_Salary_LPA'].apply(
            self._parse_salary_range
        )
        self.df['senior_salary_avg'] = self.df['Senior_Salary_LPA'].apply(
            self._parse_salary_range
        )
        
        # Create TF-IDF vectors
        self.career_vectors = self.vectorizer.fit_transform(
            self.df['combined_features']
        )
    
    def _parse_salary_range(self, salary_str):
        """Parse salary strings like '3-5' or '8-15' to average"""
        if pd.isna(salary_str) or salary_str == 'Varies':
            return None
        try:
            # Handle ranges like "3-5" or "8-15"
            if '-' in str(salary_str):
                low, high = str(salary_str).split('-')
                return (float(low) + float(high)) / 2
            # Handle single values
            return float(salary_str)
        except:
            return None
    
    def get_career_by_id(self, career_id):
        """Get career details by ID"""
        career = self.df[self.df['Career_ID'] == career_id].to_dict('records')
        return career[0] if career else None
    
    def get_careers_by_category(self, category):
        """Get all careers in a category"""
        return self.df[self.df['Category'] == category].to_dict('records')
    
    def get_all_categories(self):
        """Get unique categories"""
        return sorted(self.df['Category'].unique())
    
    def search_careers(self, query):
        """Search careers by name, skills, etc."""
        query = query.lower()
        mask = (
            self.df['Career_Name'].str.lower().str.contains(query) |
            self.df['Category'].str.lower().str.contains(query) |
            self.df['Key_Technical_Skills'].str.lower().str.contains(query, na=False)
        )
        return self.df[mask].to_dict('records')