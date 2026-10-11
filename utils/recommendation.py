import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CareerRecommender:
    def __init__(self, data_processor):
        self.dp = data_processor
    
    def recommend_by_preferences(self, preferences, top_n=10):
        """
        Recommend careers based on user preferences
        preferences: dict with fields like education, stream, skills, salary_expectation, etc.
        """
        # Create user preference vector
        user_text = self._create_user_profile_text(preferences)
        user_vector = self.dp.vectorizer.transform([user_text])
        
        # Calculate similarities
        similarities = cosine_similarity(
            user_vector, self.dp.career_vectors
        ).flatten()
        
        # Get top indices
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        # Prepare recommendations with scores
        recommendations = []
        for idx in top_indices:
            career = self.dp.df.iloc[idx].to_dict()
            career['match_score'] = round(similarities[idx] * 100, 1)
            
            # Filter by education if specified
            if preferences.get('education') and preferences['education'] != 'Any':
                if not self._check_education_match(
                    career['Min_Education'], 
                    preferences['education']
                ):
                    continue
            
            # Filter by stream if specified
            if preferences.get('stream') and preferences['stream'] != 'Any':
                if preferences['stream'] not in str(career['Preferred_Stream']):
                    continue
            
            recommendations.append(career)
        
        return recommendations[:top_n]
    
    def recommend_similar_careers(self, career_id, top_n=5):
        """Find careers similar to a given career"""
        if not self.dp.get_career_by_id(career_id):
            return []
        
        # Get index of the career
        idx = self.dp.df[self.dp.df['Career_ID'] == career_id].index[0]
        
        # Calculate similarities
        similarities = cosine_similarity(
            self.dp.career_vectors[idx], 
            self.dp.career_vectors
        ).flatten()
        
        # Get top indices (excluding itself)
        top_indices = similarities.argsort()[-top_n-1:][::-1][1:top_n+1]
        
        recommendations = []
        for i, idx in enumerate(top_indices):
            career = self.dp.df.iloc[idx].to_dict()
            career['match_score'] = round(similarities[idx] * 100, 1)
            recommendations.append(career)
        
        return recommendations
    
    def _create_user_profile_text(self, prefs):
        """Convert user preferences to text for vector matching"""
        parts = []
        
        # Add education if available
        if prefs.get('education') and prefs['education'] != 'Any':
            parts.append(prefs['education'])
        
        # Add stream if available
        if prefs.get('stream') and prefs['stream'] != 'Any':
            parts.append(prefs['stream'])
        
        # Add skills
        if prefs.get('skills'):
            parts.extend(prefs['skills'])
        
        # Add interests/category
        if prefs.get('interests'):
            parts.append(prefs['interests'])
        
        return ' '.join(parts)
    
    def _check_education_match(self, career_edu, user_edu):
        """Check if user education meets career requirements"""
        edu_levels = {
            '10+2': 1,
            'Diploma': 2,
            'Bachelor\'s': 3,
            'Master\'s': 4,
            'PG Degree': 4,
            'PhD': 5
        }
        
        career_level = edu_levels.get(career_edu, 0)
        user_level = edu_levels.get(user_edu, 0)
        
        return user_level >= career_level