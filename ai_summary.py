# ai_summary.py
import json
from datetime import datetime

class AISummaryGenerator:
    """AI-powered summary generator for test results"""
    
    def generate_psychometric_summary(self, personality, interests, aptitudes, work_styles, value_data, career_matches):
        """Generate comprehensive summary from psychometric test results"""
        
        summary = {
            'title': 'Your Psychometric Assessment Report',
            'date': datetime.now().strftime('%B %d, %Y'),
            'sections': []
        }
    
        
        # Personality Section
        personality_desc = self._get_personality_description(personality)
        summary['sections'].append({
            'title': 'Personality Profile',
            'content': personality_desc,
            'type': 'personality'
        })
        
        # Interests Section
        interests_desc = self._get_interests_description(interests)
        summary['sections'].append({
            'title': 'Career Interests',
            'content': interests_desc,
            'type': 'interests'
        })
        
        # Aptitudes Section
        aptitudes_desc = self._get_aptitudes_description(aptitudes)
        summary['sections'].append({
            'title': 'Key Strengths & Aptitudes',
            'content': aptitudes_desc,
            'type': 'aptitudes'
        })
        
        # Work Style Section
        work_style_desc = self._get_work_style_description(work_styles)
        summary['sections'].append({
            'title': 'Work Style Preferences',
            'content': work_style_desc,
            'type': 'work_style'
        })
        
        # Values Section
        values_desc = self._get_values_description(value_data)
        summary['sections'].append({
            'title': 'Core Values',
            'content': values_desc,
            'type': 'values'
        })
        
        # Career Recommendations
        career_desc = self._get_career_recommendations_description(career_matches)
        summary['sections'].append({
            'title': 'Top Career Recommendations',
            'content': career_desc,
            'type': 'careers'
        })
        
        # Overall Summary
        overall_summary = self._get_overall_summary(personality, interests, aptitudes, career_matches)
        summary['sections'].append({
            'title': 'Overall Summary & Next Steps',
            'content': overall_summary,
            'type': 'overall'
        })
        
        return json.dumps(summary, indent=2)
    
    def generate_quiz_summary(self, answers, recommendations):
        """Generate summary from career quiz results"""
        
        summary = {
            'title': 'Your Career Quiz Results',
            'date': datetime.now().strftime('%B %d, %Y'),
            'sections': []
        }
        
        # Profile Summary
        profile_summary = self._get_profile_summary(answers)
        summary['sections'].append({
            'title': 'Your Profile Summary',
            'content': profile_summary,
            'type': 'profile'
        })
        
        # Top Recommendations
        top_recs = recommendations[:5] if recommendations else []
        recs_desc = self._get_recommendations_description(top_recs)
        summary['sections'].append({
            'title': 'Your Top Career Matches',
            'content': recs_desc,
            'type': 'recommendations'
        })
        
        # Action Plan
        action_plan = self._get_action_plan(top_recs)
        summary['sections'].append({
            'title': 'Recommended Next Steps',
            'content': action_plan,
            'type': 'action_plan'
        })
        
        return json.dumps(summary, indent=2)
    
    def _get_personality_description(self, personality):
        """Generate personality description"""
        traits = []
        if personality.get('extraversion', 3) > 3.5:
            traits.append("• **Extraverted**: You thrive in social settings, enjoy collaboration, and gain energy from interacting with others.")
        elif personality.get('extraversion', 3) < 2.5:
            traits.append("• **Introverted**: You prefer independent work, value deep focus, and recharge through solitude.")
        
        if personality.get('agreeableness', 3) > 3.5:
            traits.append("• **Highly Agreeable**: You value harmony, are empathetic, and enjoy helping others succeed.")
        
        if personality.get('conscientiousness', 3) > 3.5:
            traits.append("• **Conscientious**: You are organized, reliable, and goal-oriented with strong attention to detail.")
        
        if personality.get('openness', 3) > 3.5:
            traits.append("• **Open to Experience**: You are creative, curious, and enjoy learning new things.")
        
        return "\n".join(traits) if traits else "Your personality profile shows a balanced mix of traits that can adapt to various work environments."
    
    def _get_interests_description(self, interests):
        """Generate interests description"""
        if not interests:
            return "Your interest profile is being developed. Consider exploring different career fields to discover your passions."
        
        sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
        top_interests = sorted_interests[:3]
        
        descriptions = []
        for interest, score in top_interests:
            if interest == 'realistic':
                descriptions.append(f"• **Realistic** (Score: {score:.1f}): You enjoy hands-on work with tools, machines, and practical applications.")
            elif interest == 'investigative':
                descriptions.append(f"• **Investigative** (Score: {score:.1f}): You enjoy research, analysis, and solving complex problems.")
            elif interest == 'artistic':
                descriptions.append(f"• **Artistic** (Score: {score:.1f}): You enjoy creative expression through art, writing, or design.")
            elif interest == 'social':
                descriptions.append(f"• **Social** (Score: {score:.1f}): You enjoy helping, teaching, and working closely with others.")
            elif interest == 'enterprising':
                descriptions.append(f"• **Enterprising** (Score: {score:.1f}): You enjoy leading, persuading, and influencing others.")
            elif interest == 'conventional':
                descriptions.append(f"• **Conventional** (Score: {score:.1f}): You enjoy organized, structured work with clear procedures.")
        
        return "\n".join(descriptions)
    
    def _get_aptitudes_description(self, aptitudes):
        """Generate aptitudes description"""
        if not aptitudes:
            return "Your aptitude profile is being developed. Focus on building skills in areas that interest you."
        
        sorted_aptitudes = sorted(aptitudes.items(), key=lambda x: x[1], reverse=True)
        top_aptitudes = sorted_aptitudes[:3]
        
        descriptions = []
        for apt, score in top_aptitudes:
            if apt == 'analytical':
                descriptions.append(f"• **Analytical Thinking** (Level: {score:.1f}/5): You excel at data analysis, logical reasoning, and problem-solving.")
            elif apt == 'creative':
                descriptions.append(f"• **Creative Thinking** (Level: {score:.1f}/5): You excel at innovation, design, and thinking outside the box.")
            elif apt == 'technical':
                descriptions.append(f"• **Technical Skills** (Level: {score:.1f}/5): You excel at working with tools, machines, and technology.")
            elif apt == 'interpersonal':
                descriptions.append(f"• **Interpersonal Skills** (Level: {score:.1f}/5): You excel at communication, teamwork, and relationship building.")
            elif apt == 'organizational':
                descriptions.append(f"• **Organizational Skills** (Level: {score:.1f}/5): You excel at planning, coordination, and attention to detail.")
        
        return "\n".join(descriptions)
    
    def _get_work_style_description(self, work_styles):
        """Generate work style description"""
        if not work_styles:
            return "Your work style preferences are diverse. Consider what environment makes you most productive."
        
        sorted_styles = sorted(work_styles.items(), key=lambda x: x[1], reverse=True)
        top_styles = sorted_styles[:4]
        
        descriptions = []
        for style, score in top_styles:
            if style == 'flexibility':
                descriptions.append(f"• **Flexible Work** (Importance: {score:.1f}/5): You value adaptable schedules and remote work options.")
            elif style == 'collaboration':
                descriptions.append(f"• **Team Collaboration** (Importance: {score:.1f}/5): You thrive in team-oriented environments.")
            elif style == 'stability':
                descriptions.append(f"• **Job Stability** (Importance: {score:.1f}/5): You prefer predictable routines and job security.")
            elif style == 'work_life_balance':
                descriptions.append(f"• **Work-Life Balance** (Importance: {score:.1f}/5): You prioritize balance between work and personal life.")
            elif style == 'financial_rewards':
                descriptions.append(f"• **Financial Rewards** (Importance: {score:.1f}/5): You value competitive compensation and growth.")
            elif style == 'learning':
                descriptions.append(f"• **Continuous Learning** (Importance: {score:.1f}/5): You seek growth and development opportunities.")
            elif style == 'social_impact':
                descriptions.append(f"• **Social Impact** (Importance: {score:.1f}/5): You want to make a positive difference in society.")
        
        return "\n".join(descriptions)
    
    def _get_values_description(self, values):
        """Generate values description"""
        if not values:
            return "Understanding your values will help you find fulfilling career paths."
        
        sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
        top_values = sorted_values[:5]
        
        descriptions = []
        for value, score in top_values:
            if value == 'security':
                descriptions.append(f"• **Financial Security** (Importance: {score:.1f}/5): Stability and financial well-being matter to you.")
            elif value == 'altruism':
                descriptions.append(f"• **Helping Others** (Importance: {score:.1f}/5): Making a positive impact drives you.")
            elif value == 'prestige':
                descriptions.append(f"• **Recognition** (Importance: {score:.1f}/5): Achievement and status are important motivators.")
            elif value == 'creativity':
                descriptions.append(f"• **Creativity** (Importance: {score:.1f}/5): Self-expression and innovation fuel your passion.")
            elif value == 'autonomy':
                descriptions.append(f"• **Independence** (Importance: {score:.1f}/5): Freedom and autonomy guide your decisions.")
            elif value == 'growth':
                descriptions.append(f"• **Growth** (Importance: {score:.1f}/5): Continuous learning and development are essential.")
            elif value == 'balance':
                descriptions.append(f"• **Work-Life Balance** (Importance: {score:.1f}/5): Harmony between work and life is key.")
        
        return "\n".join(descriptions)
    
    def _get_career_recommendations_description(self, career_matches):
        """Generate career recommendations description"""
        if not career_matches:
            return "Based on your profile, we recommend exploring a variety of career fields to find your best fit."
        
        descriptions = []
        for i, career in enumerate(career_matches[:5], 1):
            descriptions.append(f"**{i}. {career.get('title', 'Career')}** ({career.get('match', 0)}% Match)")
            descriptions.append(f"   {career.get('description', '')}")
            descriptions.append(f"   *Why it matches:* {', '.join(career.get('reasons', ['Good fit for your profile']))}")
            descriptions.append("")
        
        return "\n".join(descriptions)
    
    def _get_overall_summary(self, personality, interests, aptitudes, career_matches):
        """Generate overall summary"""
        top_interest = max(interests.items(), key=lambda x: x[1])[0] if interests else "various"
        top_aptitude = max(aptitudes.items(), key=lambda x: x[1])[0] if aptitudes else "diverse"
        
        interest_names = {
            'realistic': 'hands-on, practical work',
            'investigative': 'research and analysis',
            'artistic': 'creative expression',
            'social': 'helping and teaching',
            'enterprising': 'leadership and business',
            'conventional': 'organized, structured work'
        }
        
        summary = f"""Based on your comprehensive psychometric assessment, your profile shows strong alignment with {interest_names.get(top_interest, 'various')} interests and {top_aptitude} thinking abilities.

Your top career matches include roles that leverage your natural strengths and align with your values. The careers recommended for you offer:
• Strong alignment with your personality traits
• Opportunities that match your interests
• Work environments that suit your preferences
• Values that resonate with what matters to you

**Recommended Next Steps:**
1. Explore the top career matches in detail using our career explorer
2. Research the education requirements for careers that interest you
3. Connect with professionals in your top fields through networking
4. Consider taking online courses to build relevant skills
5. Schedule informational interviews to learn more about these careers

Remember, career exploration is a journey. Use these insights as a starting point to discover paths that will bring you fulfillment and success."""
        
        return summary
    
    def _get_profile_summary(self, answers):
        """Generate profile summary from quiz answers"""
        education = answers.get('education', 'Not specified')
        stream = answers.get('stream', 'Not specified')
        interests = answers.get('interests', [])
        skills = answers.get('skills', [])
        
        summary = f"""**Education Level:** {education}
**Academic Stream:** {stream}
**Areas of Interest:** {', '.join(interests) if interests else 'Not specified'}
**Key Skills:** {', '.join(skills) if skills else 'Not specified'}

Based on your profile, you have a strong foundation in {stream} with interests in {', '.join(interests[:3]) if interests else 'various fields'}. Your skills in {', '.join(skills[:3]) if skills else 'various areas'} provide a good starting point for several career paths."""
        
        return summary
    
    def _get_recommendations_description(self, recommendations):
        """Generate recommendations description"""
        if not recommendations:
            return "No specific recommendations available. Please retake the quiz for personalized results."
        
        descriptions = []
        for i, rec in enumerate(recommendations, 1):
            descriptions.append(f"**{i}. {rec.get('Career_Name', 'Career')}**")
            descriptions.append(f"   • Category: {rec.get('Category', 'N/A')}")
            descriptions.append(f"   • Match Score: {rec.get('match_score', 0)}%")
            descriptions.append(f"   • Entry Salary: {rec.get('Entry_Salary_LPA', 'N/A')} LPA")
            descriptions.append(f"   • Required Education: {rec.get('Min_Education', 'N/A')}")
            descriptions.append("")
        
        return "\n".join(descriptions)
    
    def _get_action_plan(self, recommendations):
        """Generate action plan based on recommendations"""
        if not recommendations:
            return "Start by exploring different career categories and taking our psychometric test for more detailed insights."
        
        top_career = recommendations[0]
        career_name = top_career.get('Career_Name', 'your chosen career')
        
        action_plan = f"""Based on your interest in {career_name}, here's a recommended action plan:

**Short-term (0-6 months):**
• Research {career_name} career paths and daily responsibilities
• Identify required education and certifications
• Connect with professionals in this field on LinkedIn
• Take introductory courses to build foundational skills

**Medium-term (6-12 months):**
• Enroll in relevant courses or certifications
• Build a portfolio or gain practical experience
• Attend industry events and webinars
• Consider internships or shadowing opportunities

**Long-term (1-3 years):**
• Complete necessary education requirements
• Apply for entry-level positions or further studies
• Build professional network in your chosen field
• Continuously update skills based on industry trends

Remember to regularly reassess your goals and adjust your path as you learn more about the field."""
        
        return action_plan