import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

class CareerChatbot:
    def __init__(self, data_processor):
        self.dp = data_processor
        self.context = {}
        
        # Predefined responses
        self.greetings = {
            'hello': 'Hi there! I\'m your career guidance assistant. How can I help you today?',
            'hi': 'Hello! Ready to explore career options?',
            'hey': 'Hey! Let\'s find your perfect career path.',
            'help': 'I can help you discover careers, answer questions about education requirements, salary expectations, and more!'
        }
        
        # Question patterns
        self.patterns = {
            'salary': r'(salary|pay|earn|income|lpa|remuneration)',
            'education': r'(education|qualification|degree|study|college|university)',
            'skills': r'(skill|require|need to know|should learn)',
            'duration': r'(duration|long|years|time)',
            'recruiters': r'(recruiter|company|hire|employer|top companies)',
            'outlook': r'(outlook|future|demand|growth|scope)',
            'category': r'(category|field|domain|area|sector)'
        }
    
    def get_response(self, user_message, user_id='default'):
        """Generate chatbot response based on user message"""
        user_message = user_message.lower().strip()
        
        # Check for greetings
        for greet in self.greetings:
            if greet in user_message:
                return self.greetings[greet]
        
        # Check if asking for recommendations
        if any(word in user_message for word in ['recommend', 'suggest', 'career for me', 'what should i']):
            return self._handle_recommendation_request(user_message)
        
        # Check for specific career questions
        career_mentioned = self._extract_career_mention(user_message)
        if career_mentioned:
            return self._answer_career_question(career_mentioned, user_message)
        
        # Check for category exploration
        categories = self.dp.get_all_categories()
        for category in categories:
            if category.lower() in user_message:
                careers = self.dp.get_careers_by_category(category)
                return self._format_category_response(category, careers[:5])
        
        # Default response
        return self._get_default_response()
    
    def _extract_career_mention(self, message):
        """Extract career name from message"""
        # Check for exact career names
        for career in self.dp.df['Career_Name'].values:
            if career.lower() in message:
                return career
        
        # Check for partial matches
        words = message.split()
        for word in words:
            matches = self.dp.df[
                self.dp.df['Career_Name'].str.lower().str.contains(word)
            ]
            if not matches.empty:
                return matches.iloc[0]['Career_Name']
        
        return None
    
    def _answer_career_question(self, career_name, question):
        """Answer specific question about a career"""
        career = self.dp.df[
            self.dp.df['Career_Name'] == career_name
        ].iloc[0].to_dict()
        
        # Salary questions
        if re.search(self.patterns['salary'], question):
            return f"For {career_name}, entry-level salary is {career['Entry_Salary_LPA']} LPA, mid-level {career['Mid_Salary_LPA']} LPA, and senior-level {career['Senior_Salary_LPA']} LPA."
        
        # Education questions
        if re.search(self.patterns['education'], question):
            edu = f"Minimum education: {career['Min_Education']}. "
            if pd.notna(career['Preferred_Stream']):
                edu += f"Preferred stream: {career['Preferred_Stream']}. "
            if pd.notna(career['Required_Degree']):
                edu += f"Required degree: {career['Required_Degree']}."
            return edu
        
        # Skills questions
        if re.search(self.patterns['skills'], question):
            skills = f"Technical skills: {career['Key_Technical_Skills']}. "
            skills += f"Soft skills: {career['Key_Soft_Skills']}."
            return skills
        
        # Duration
        if re.search(self.patterns['duration'], question):
            return f"It typically takes {career['Duration_Years']} years to become a {career_name}."
        
        # Recruiters
        if re.search(self.patterns['recruiters'], question):
            return f"Top recruiters in India: {career['Top_Recruiters_India']}"
        
        # Outlook
        if re.search(self.patterns['outlook'], question):
            return f"Job outlook: {career['Job_Outlook']}"
        
        # Default career info
        return self._format_career_summary(career)
    
    def _handle_recommendation_request(self, message):
        """Handle requests for career recommendations"""
        # Extract possible preferences from message
        stream = None
        if 'science' in message:
            stream = 'Science'
        elif 'commerce' in message:
            stream = 'Commerce'
        elif 'arts' in message or 'humanities' in message:
            stream = 'Arts'
        
        if stream:
            careers = self.dp.df[
                self.dp.df['Preferred_Stream'].str.contains(stream, na=False)
            ].head(5)
            
            response = f"Based on your interest in {stream}, here are some careers to explore:\n\n"
            for _, career in careers.iterrows():
                response += f"• {career['Career_Name']} - {career['Category']}\n"
            response += "\nWould you like more details about any of these?"
            return response
        
        return "I'd love to help you find careers! Tell me about your interests, education, or preferred stream (Science, Commerce, Arts)."
    
    def _format_career_summary(self, career):
        """Format a career summary"""
        return (
            f"**{career['Career_Name']}** ({career['Category']})\n\n"
            f"📚 Education: {career['Min_Education']} in {career['Preferred_Stream']}\n"
            f"⏱️ Duration: {career['Duration_Years']} years\n"
            f"💰 Entry Salary: {career['Entry_Salary_LPA']} LPA\n"
            f"🔮 Outlook: {career['Job_Outlook']}\n\n"
            f"Want to know about skills, recruiters, or something specific?"
        )
    
    def _format_category_response(self, category, careers):
        """Format category exploration response"""
        response = f"**{category}** careers you might like:\n\n"
        for career in careers:
            response += f"• {career['Career_Name']}\n"
        response += "\nWhich one interests you? I can tell you more!"
        return response
    
    def _get_default_response(self):
        """Default response when no pattern matches"""
        return (
            "I'm here to help you explore careers! You can ask me about:\n"
            "• Specific careers (e.g., 'Tell me about Data Scientist')\n"
            "• Career categories (e.g., 'Healthcare careers')\n"
            "• Education requirements\n"
            "• Salary expectations\n"
            "• Or ask for recommendations!"
        )