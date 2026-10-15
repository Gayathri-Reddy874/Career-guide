# app.py - Updated with user system
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash

import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from functools import wraps
import hashlib

from database import Database
from ai_summary import AISummaryGenerator

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')


# Initialize database and AI summary generator
db = Database()
ai_summary = AISummaryGenerator()

# Load career data
career_df = None
vectorizer = None
career_vectors = None

# Add these decorators after the imports in app.py

def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    """Decorator to redirect logged-in users away from login/register pages"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            flash('You are already logged in', 'info')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function



def load_career_data():
    """Load and prepare career data"""
    global career_df, vectorizer, career_vectors
    
    try:
        career_df = pd.read_csv('career.csv')
        print(f"Loaded {len(career_df)} careers")
        
        # Prepare text features
        career_df['combined_features'] = (
            career_df['Category'].fillna('') + ' ' +
            career_df['Career_Name'].fillna('') + ' ' +
            career_df['Key_Technical_Skills'].fillna('') + ' ' +
            career_df['Key_Soft_Skills'].fillna('') + ' ' +
            career_df['Preferred_Stream'].fillna('')
        )
        
        # Parse salary ranges
        career_df['entry_salary_avg'] = career_df['Entry_Salary_LPA'].apply(parse_salary)
        
        # Create TF-IDF vectors
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        career_vectors = vectorizer.fit_transform(career_df['combined_features'].fillna(''))
        
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def parse_salary(salary_str):
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

# Load data on startup
with app.app_context():
    load_career_data()

# ============ AUTHENTICATION DECORATORS ============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.get_user_by_id(session['user_id'])
        if not user or not user.get('is_admin'):
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============ AUTHENTICATION ROUTES ============
@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.authenticate_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            flash('Login successful! Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        education = request.form.get('education')
        stream = request.form.get('stream')
        
        # Validate inputs
        if not username or not email or not password:
            flash('Please fill in all required fields', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        result = db.create_user(username, email, password, full_name, phone, education, stream)
        
        if result['success']:
            flash('Registration successful! Please login to continue.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Registration failed: {result["error"]}', 'error')
    
    return render_template('register.html')

@app.route('/categories')
def all_categories():
    """Show all career categories - Public access"""
    if career_df is None:
        return "Error loading data", 500
    
    categories = sorted(career_df['Category'].unique().tolist())
    return render_template('categories.html', categories=categories)



@app.route('/category/<category>')
def category_page(category):
    """Category page - Public access"""
    if career_df is None:
        return "Error loading data", 500
    
    categories = career_df['Category'].unique().tolist()
    if category not in categories:
        return render_template('404.html'), 404
    
    return render_template('category.html', category=category)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ============ USER DASHBOARD ============
@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = db.get_user_by_id(session['user_id'])
    psychometric_results = db.get_psychometric_results(session['user_id'], limit=1)
    quiz_results = db.get_quiz_results(session['user_id'], limit=1)
    iq_results = db.get_iq_test_results(session['user_id'], limit=1)
    iq_stats = db.get_iq_test_stats(session['user_id'])
    
    return render_template('dashboard.html', 
                         user=user, 
                         psychometric_results=psychometric_results,
                         quiz_results=quiz_results,
                         iq_results=iq_results,
                         iq_stats=iq_stats)
# ============ PUBLIC ROUTES ============
@app.route('/')
def index():
    """Landing page"""
    categories = career_df['Category'].unique().tolist() if career_df is not None else []
    return render_template('index.html', categories=sorted(categories), user_logged_in='user_id' in session)

@app.route('/chatbot')
def chatbot():
    """AI chatbot page"""
    return render_template('chatbot.html')

@app.route('/quiz')
@login_required
def quiz():
    """Career assessment quiz - Login required"""
    return render_template('quiz.html') 

@app.route('/psychometric-test')
@login_required
def psychometric_test():
    """Psychometric assessment test page - Login required"""
    return render_template('psychometric_test.html',
                         personality_questions=PERSONALITY_QUESTIONS,
                         interest_questions=INTEREST_QUESTIONS,
                         aptitude_questions=APTITUDE_QUESTIONS,
                         work_style_questions=WORK_STYLE_QUESTIONS,
                         values_questions=VALUES_QUESTIONS)



@app.route('/results')
@login_required
def results():
    return render_template('results.html')

@app.route('/career/<career_id>')
def career_detail(career_id):
    if career_df is None:
        return "Error loading data", 500
    
    career = career_df[career_df['Career_ID'] == career_id]
    if career.empty:
        return render_template('404.html'), 404
    
    career_data = career.iloc[0].to_dict()
    similar = get_similar_careers(career_id, top_n=4)
    
    return render_template('career.html', career=career_data, similar=similar)

@app.route('/compare')
def compare():
    if career_df is None:
        return "Error loading data", 500
    
    careers = career_df[['Career_ID', 'Career_Name', 'Category']].to_dict('records')
    return render_template('compare.html', careers=careers)

@app.route('/psychometric-results')
@login_required
def psychometric_results():
    """Display psychometric assessment results - Login required"""
    return render_template('psychometric_results.html')







# ============ API ROUTES ============
@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    try:
        data = request.json
        
        # Get recommendations
        recommendations = get_recommendations(data)
        
        # Generate AI summary
        ai_summary_text = ai_summary.generate_quiz_summary(data, recommendations)
        
        # Save to database
        db.save_quiz_result(session['user_id'], data, recommendations, ai_summary_text)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'summary': ai_summary_text
        })
    except Exception as e:
        print(f"Error in submit_quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# In app.py, update the submit_psychometric function:

@app.route('/api/psychometric/submit', methods=['POST'])
@login_required
def submit_psychometric():
    try:
        data = request.json
        
        # Get career matches
        career_matches = get_career_matches_from_psychometric(data)
        
        # Generate AI summary - use value_data instead of values
        ai_summary_text = ai_summary.generate_psychometric_summary(
            data.get('personality', {}),
            data.get('interests', {}),
            data.get('aptitudes', {}),
            data.get('workStyles', {}),
            data.get('value_data', {}),  # Changed from 'values' to 'value_data'
            career_matches
        )
        
        # Save to database
        db.save_psychometric_result(
            session['user_id'],
            data.get('personality', {}),
            data.get('interests', {}),
            data.get('aptitudes', {}),
            data.get('workStyles', {}),
            data.get('value_data', {}),  # Changed from 'values' to 'value_data'
            data.get('raw_answers', {}),
            ai_summary_text,
            career_matches
        )
        
        return jsonify({
            'success': True,
            'personality': data.get('personality', {}),
            'interests': data.get('interests', {}),
            'aptitudes': data.get('aptitudes', {}),
            'workStyles': data.get('workStyles', {}),
            'value_data': data.get('value_data', {}),
            'career_matches': career_matches,
            'summary': ai_summary_text
        })
    except Exception as e:
        print(f"Error in submit_psychometric: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    


# Add Jinja2 filter for JSON parsing
import json

@app.template_filter('from_json')
def from_json_filter(value):
    """Convert JSON string to Python object"""
    if not value:
        return {}
    try:
        return json.loads(value)
    except:
        return {}

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    try:
        data = request.json
        message = data.get('message', '').lower().strip()
        
        response = get_chatbot_response(message)
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({'response': "I'm having trouble processing your request. Please try again later."}), 500

@app.route('/api/all-careers')
def get_all_careers():
    if career_df is None:
        return jsonify([])
    
    careers = career_df.to_dict('records')
    return jsonify(careers)

@app.route('/api/featured-careers')
def get_featured_careers():
    if career_df is None:
        return jsonify([])
    
    featured = career_df[career_df['entry_salary_avg'].notna()].sort_values('entry_salary_avg', ascending=False).head(6)
    return jsonify(featured.to_dict('records'))

@app.route('/api/categories')
def api_categories():
    if career_df is None:
        return jsonify([])
    
    categories = career_df['Category'].unique().tolist()
    return jsonify(sorted(categories))

@app.route('/api/category/<category>')
def api_category(category):
    if career_df is None:
        return jsonify([])
    
    careers = career_df[career_df['Category'] == category].to_dict('records')
    return jsonify(careers)

@app.route('/api/career/<career_id>')
def api_career(career_id):
    if career_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    career = career_df[career_df['Career_ID'] == career_id]
    if career.empty:
        return jsonify({'error': 'Career not found'}), 404
    
    return jsonify(career.iloc[0].to_dict())

@app.route('/api/compare', methods=['POST'])
def api_compare():
    career_ids = request.json.get('career_ids', [])
    careers = []
    for cid in career_ids:
        career = career_df[career_df['Career_ID'] == cid]
        if not career.empty:
            careers.append(career.iloc[0].to_dict())
    
    return jsonify({'careers': careers})

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    query_lower = query.lower()
    mask = (
        career_df['Career_Name'].str.lower().str.contains(query_lower, na=False) |
        career_df['Category'].str.lower().str.contains(query_lower, na=False) |
        career_df['Key_Technical_Skills'].str.lower().str.contains(query_lower, na=False)
    )
    
    results = career_df[mask].head(10).to_dict('records')
    return jsonify(results)

# ============ ADMIN ROUTES ============
@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = db.get_stats()
    users = db.get_all_users()
    admin_logs = db.get_admin_logs()
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         users=users, 
                         logs=admin_logs)

@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_view_user(user_id):
    user = db.get_user_by_id(user_id)
    psychometric_results = db.get_psychometric_results(user_id)
    quiz_results = db.get_quiz_results(user_id)
    
    return render_template('admin_user.html', 
                         user=user, 
                         psychometric_results=psychometric_results,
                         quiz_results=quiz_results)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    db.delete_user(user_id)
    db.log_admin_action(session['user_id'], f'Deleted user {user_id}', user_id)
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

# ============ HELPER FUNCTIONS ============
def get_recommendations(preferences, top_n=12):
    """Generate career recommendations based on preferences"""
    global career_df, career_vectors, vectorizer
    
    if career_df is None or career_vectors is None:
        return []
    
    user_text = []
    
    if preferences.get('stream') and preferences['stream'] != 'Any':
        user_text.append(preferences['stream'])
    
    if preferences.get('interests'):
        if isinstance(preferences['interests'], list):
            user_text.extend(preferences['interests'])
        else:
            user_text.append(preferences['interests'])
    
    if preferences.get('skills'):
        if isinstance(preferences['skills'], list):
            user_text.extend(preferences['skills'])
        else:
            user_text.append(preferences['skills'])
    
    user_profile = ' '.join(user_text)
    
    if not user_profile.strip():
        recommendations = career_df.head(top_n).to_dict('records')
        for i, rec in enumerate(recommendations):
            rec['match_score'] = 50 + np.random.randint(0, 30)
        return recommendations
    
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        user_vector = vectorizer.transform([user_profile])
        similarities = cosine_similarity(user_vector, career_vectors).flatten()
        
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        recommendations = []
        for idx in top_indices:
            career = career_df.iloc[idx].to_dict()
            career['match_score'] = round(similarities[idx] * 100, 1)
            recommendations.append(career)
        
        return recommendations
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        return career_df.head(top_n).to_dict('records')

def get_career_matches_from_psychometric(data):
    """Generate career matches based on psychometric profile"""
    interests = data.get('interests', {})
    aptitudes = data.get('aptitudes', {})
    
    top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:3] if interests else []
    top_aptitudes = sorted(aptitudes.items(), key=lambda x: x[1], reverse=True)[:2] if aptitudes else []
    
    matches = []
    
    # Match based on interests and aptitudes
    if 'investigative' in [i[0] for i in top_interests]:
        matches.append({
            'title': 'Data Scientist / AI Engineer',
            'career_id': 'C049',
            'match': 92,
            'description': 'Combines analytical thinking with investigative interests for cutting-edge technology careers.',
            'reasons': ['Strong analytical aptitude', 'Investigative interest profile', 'High growth potential']
        })
        
        matches.append({
            'title': 'Research Scientist',
            'career_id': 'C280',
            'match': 88,
            'description': 'Research-focused career requiring analytical skills and scientific curiosity.',
            'reasons': ['Strong investigative interests', 'Analytical aptitude', 'Curiosity-driven work']
        })
    
    if 'artistic' in [i[0] for i in top_interests]:
        matches.append({
            'title': 'UX/UI Designer',
            'career_id': 'C169',
            'match': 85,
            'description': 'Creative role combining design with user psychology and technology.',
            'reasons': ['Artistic interests', 'Creative aptitude', 'User-focused work']
        })
        
        matches.append({
            'title': 'Graphic Designer',
            'career_id': 'C168',
            'match': 82,
            'description': 'Visual communication and creative design for various media.',
            'reasons': ['Strong artistic interests', 'Creative skills', 'Visual thinking']
        })
    
    if 'social' in [i[0] for i in top_interests]:
        matches.append({
            'title': 'Clinical Psychologist',
            'career_id': 'C007',
            'match': 88,
            'description': 'Helping profession requiring empathy and understanding of human behavior.',
            'reasons': ['Social interests', 'Interpersonal aptitude', 'Desire to help others']
        })
        
        matches.append({
            'title': 'Social Worker',
            'career_id': 'C256',
            'match': 85,
            'description': 'Community service and social welfare roles making a difference.',
            'reasons': ['Strong social interests', 'Empathetic nature', 'Community focus']
        })
    
    if 'enterprising' in [i[0] for i in top_interests]:
        matches.append({
            'title': 'Entrepreneur / Business Owner',
            'career_id': 'C074',
            'match': 90,
            'description': 'Build and lead your own business venture.',
            'reasons': ['Enterprising interests', 'Leadership potential', 'Risk-taking nature']
        })
        
        matches.append({
            'title': 'Management Consultant',
            'career_id': 'C072',
            'match': 86,
            'description': 'Help organizations improve and grow through strategic advice.',
            'reasons': ['Strategic thinking', 'Problem-solving skills', 'Business acumen']
        })
    
    if 'realistic' in [i[0] for i in top_interests]:
        matches.append({
            'title': 'Mechanical Engineer',
            'career_id': 'C033',
            'match': 84,
            'description': 'Design and build mechanical systems and components.',
            'reasons': ['Hands-on interests', 'Technical aptitude', 'Practical problem-solving']
        })
        
        matches.append({
            'title': 'Robotics Engineer',
            'career_id': 'C055',
            'match': 82,
            'description': 'Create and program robotic systems for various applications.',
            'reasons': ['Technical skills', 'Innovation focus', 'Building things']
        })
    
    if len(matches) < 3:
        matches.extend([
            {
                'title': 'Software Developer',
                'career_id': 'C016',
                'match': 80,
                'description': 'Create software applications and systems for various platforms.',
                'reasons': ['Problem-solving skills', 'Technical aptitude', 'Growing field']
            },
            {
                'title': 'Business Analyst',
                'career_id': 'C061',
                'match': 78,
                'description': 'Bridge business needs with technical solutions.',
                'reasons': ['Analytical skills', 'Communication abilities', 'Strategic thinking']
            }
        ])
    
    return matches[:5]

def get_similar_careers(career_id, top_n=4):
    """Get careers similar to given career"""
    global career_df, career_vectors, vectorizer
    
    if career_df is None or career_vectors is None:
        return []
    
    career_idx = career_df[career_df['Career_ID'] == career_id].index
    if len(career_idx) == 0:
        return []
    
    idx = career_idx[0]
    
    from sklearn.metrics.pairwise import cosine_similarity
    similarities = cosine_similarity(career_vectors[idx], career_vectors).flatten()
    
    top_indices = similarities.argsort()[-top_n-1:][::-1][1:top_n+1]
    
    similar = []
    for i in top_indices:
        career = career_df.iloc[i].to_dict()
        career['match_score'] = round(similarities[i] * 100, 1)
        similar.append(career)
    
    return similar

def get_chatbot_response(message):
    """Generate chatbot response"""
    global career_df
    
    if career_df is None:
        return "I'm having trouble accessing the career data. Please try again later."
    
    # Greetings
    greetings = ['hello', 'hi', 'hey', 'greetings', 'namaste']
    if any(greet in message for greet in greetings):
        return "👋 Hello! I'm your AI Career Assistant. I can help you find careers, understand requirements, compare options, and plan your professional journey. What would you like to know?"
    
    # Career recommendations
    if any(word in message for word in ['recommend', 'suggest', 'career for me']):
        if 'science' in message:
            careers = career_df[career_df['Preferred_Stream'].str.contains('Science', na=False)].head(5)
            response = "🔬 Based on your interest in Science, here are some great career options:\n\n"
            for _, c in careers.iterrows():
                response += f"• **{c['Career_Name']}** - {c['Category']} (Salary: {c['Entry_Salary_LPA']} LPA)\n"
            return response
        elif 'commerce' in message:
            careers = career_df[career_df['Preferred_Stream'].str.contains('Commerce', na=False)].head(5)
            response = "💼 Based on your interest in Commerce, here are some great career options:\n\n"
            for _, c in careers.iterrows():
                response += f"• **{c['Career_Name']}** - {c['Category']} (Salary: {c['Entry_Salary_LPA']} LPA)\n"
            return response
        elif 'arts' in message:
            careers = career_df[career_df['Preferred_Stream'].str.contains('Arts', na=False)].head(5)
            response = "🎨 Based on your interest in Arts, here are some great career options:\n\n"
            for _, c in careers.iterrows():
                response += f"• **{c['Career_Name']}** - {c['Category']} (Salary: {c['Entry_Salary_LPA']} LPA)\n"
            return response
    
    # Search for specific career
    for _, career in career_df.iterrows():
        if career['Career_Name'].lower() in message:
            return get_career_details_text(career)
    
    return get_default_response()


# Add to app.py

@app.route('/iq-test')
@login_required
def iq_test():
    """IQ Test page"""
    return render_template('iq_test.html',
                         logical_questions=IQ_LOGICAL_QUESTIONS,
                         numerical_questions=IQ_NUMERICAL_QUESTIONS,
                         verbal_questions=IQ_VERBAL_QUESTIONS,
                         spatial_questions=IQ_SPATIAL_QUESTIONS,
                         memory_questions=IQ_MEMORY_QUESTIONS)

@app.route('/iq-test-results')
@login_required
def iq_test_results():
    """IQ Test results page"""
    return render_template('iq_test_results.html')

@app.route('/api/iq-test/submit', methods=['POST'])
@login_required
def submit_iq_test():
    """Save IQ test results"""
    try:
        data = request.json
        
        # Save to database
        db.save_iq_test_result(
            session['user_id'],
            data.get('iq_score'),
            data.get('correct_count'),
            data.get('section_scores'),
            data.get('answers'),
            data.get('time_taken')
        )
        
        # Generate AI summary
        ai_summary = generate_iq_summary(data)
        
        return jsonify({
            'success': True,
            'iq_score': data.get('iq_score'),
            'section_scores': data.get('section_scores'),
            'ai_summary': ai_summary
        })
    except Exception as e:
        print(f"Error in submit_iq_test: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_iq_summary(data):
    """Generate AI summary for IQ test results"""
    iq = data.get('iq_score', 100)
    scores = data.get('section_scores', {})
    
    summary = f"""
    Based on your IQ test results, here's a comprehensive analysis:
    
    **Overall Cognitive Ability:**
    Your IQ score of {iq} places you in the {get_percentile_range(iq)}. 
    
    **Strengths:**
    {get_strengths_analysis(scores)}
    
    **Areas for Development:**
    {get_development_analysis(scores)}
    
    **Career Implications:**
    {get_career_implications(iq, scores)}
    
    **Recommended Next Steps:**
    {get_recommended_steps(scores)}
    """
    
    return summary

def get_percentile_range(iq):
    if iq >= 130: return "top 2% of the population"
    if iq >= 115: return "top 16% of the population"
    if iq >= 100: return "top 50% of the population"
    if iq >= 85: return "bottom 16% of the population"
    return "bottom 2% of the population"

def get_strengths_analysis(scores):
    strengths = []
    if scores.get('logical', 0) >= 6:
        strengths.append("• **Logical Reasoning**: Excellent pattern recognition and analytical thinking")
    if scores.get('numerical', 0) >= 6:
        strengths.append("• **Numerical Ability**: Strong mathematical and quantitative skills")
    if scores.get('verbal', 0) >= 6:
        strengths.append("• **Verbal Comprehension**: Excellent vocabulary and language understanding")
    if scores.get('spatial', 0) >= 6:
        strengths.append("• **Spatial Awareness**: Great visualization and spatial reasoning")
    if scores.get('memory', 0) >= 6:
        strengths.append("• **Memory & Recall**: Strong memory retention and recall abilities")
    
    if strengths:
        return "\n".join(strengths)
    return "You have a balanced cognitive profile across all areas."

def get_development_analysis(scores):
    developments = []
    if scores.get('logical', 0) < 4:
        developments.append("• Practice puzzles, Sudoku, and brain teasers to improve logical reasoning")
    if scores.get('numerical', 0) < 4:
        developments.append("• Regular mental math practice can strengthen numerical abilities")
    if scores.get('verbal', 0) < 4:
        developments.append("• Reading widely and learning new vocabulary can enhance verbal skills")
    if scores.get('spatial', 0) < 4:
        developments.append("• Try 3D puzzles, drawing, and visualization exercises")
    if scores.get('memory', 0) < 4:
        developments.append("• Use mnemonic techniques and regular recall exercises")
    
    if developments:
        return "\n".join(developments)
    return "Continue challenging yourself with advanced materials in your areas of interest."

def get_career_implications(iq, scores):
    if iq >= 130:
        return "Your cognitive abilities are exceptional. Consider careers in research, data science, AI engineering, theoretical physics, or neurosurgery where complex problem-solving is key."
    elif iq >= 115:
        return "Your above-average cognitive abilities suit careers in software engineering, financial analysis, architecture, corporate law, or medicine."
    elif iq >= 100:
        return "Your cognitive abilities are well-suited for careers in business analysis, graphic design, education, project management, or marketing."
    else:
        return "Your cognitive profile aligns well with practical careers in skilled trades, sales, administration, customer service, or technical fields."

def get_recommended_steps(scores):
    steps = []
    if scores.get('logical', 0) < 5:
        steps.append("1. Dedicate 15 minutes daily to logic puzzles and brain games")
    if scores.get('numerical', 0) < 5:
        steps.append("2. Practice mental math and numerical reasoning exercises")
    if scores.get('verbal', 0) < 5:
        steps.append("3. Read challenging books and learn 5 new words daily")
    if scores.get('spatial', 0) < 5:
        steps.append("4. Try drawing, 3D modeling, or puzzle games")
    if scores.get('memory', 0) < 5:
        steps.append("5. Use memory techniques like the method of loci")
    
    if not steps:
        steps = ["1. Take advanced courses in your areas of interest",
                 "2. Consider mentoring others to deepen your understanding",
                 "3. Explore interdisciplinary subjects to broaden your skills"]
    
    return "\n".join(steps)

def get_career_details_text(career):
    """Get detailed career information as text"""
    return f"""**{career['Career_Name']}** ({career['Category']})

📚 **Education:** {career['Min_Education']}
🎓 **Preferred Stream:** {career['Preferred_Stream']}
📖 **Required Degree:** {career['Required_Degree']}
⏱️ **Duration:** {career['Duration_Years']} years

💰 **Salary:**
   Entry Level: {career['Entry_Salary_LPA']} LPA
   Mid Level: {career['Mid_Salary_LPA']} LPA
   Senior Level: {career['Senior_Salary_LPA']} LPA

🔧 **Technical Skills:** {career['Key_Technical_Skills']}

🤝 **Soft Skills:** {career['Key_Soft_Skills']}

🏢 **Top Recruiters:** {career['Top_Recruiters_India']}

📈 **Job Outlook:** {career['Job_Outlook']}

Would you like to know about similar careers or compare this with others?"""

def get_default_response():
    """Default response"""
    return """I can help you with career information! You can ask me about:

**Career Discovery:**
• 'Recommend careers for science student'
• 'What are the highest paying careers?'
• 'Best careers for the future'

**Specific Careers:**
• 'Tell me about Data Scientist'
• 'How to become a doctor?'
• 'Software engineer salary'

**Career Information:**
• 'What skills are in demand?'
• 'Government jobs after graduation'
• 'Careers with good work-life balance'

What would you like to explore?"""

# Questions data
PERSONALITY_QUESTIONS = [
    "I enjoy meeting new people and socializing",
    "I prefer to work independently rather than in teams",
    "I pay close attention to details and accuracy",
    "I enjoy solving complex problems and puzzles",
    "I am organized and like structure in my work",
    "I am creative and enjoy thinking outside the box",
    "I remain calm under pressure and stress",
    "I enjoy helping others and providing support",
    "I am curious and love learning new things",
    "I prefer routine and predictable tasks",
    "I am competitive and strive to be the best",
    "I am empathetic and understand others' feelings",
    "I enjoy leading and directing others",
    "I am practical and prefer hands-on work",
    "I am analytical and data-driven in decision making"
]

INTEREST_QUESTIONS = [
    "Conducting scientific research or experiments",
    "Designing and building things with your hands",
    "Teaching or training others",
    "Starting your own business or venture",
    "Creating art, music, or writing stories",
    "Analyzing data and finding patterns",
    "Helping people solve personal problems",
    "Working with computers and technology",
    "Organizing events and managing projects",
    "Working outdoors or with animals",
    "Negotiating and persuading others",
    "Repairing mechanical equipment",
    "Studying history, culture, or languages",
    "Providing medical care to patients",
    "Developing new software or applications"
]

APTITUDE_QUESTIONS = [
    "Mathematical and numerical reasoning",
    "Verbal and written communication",
    "Logical and analytical thinking",
    "Creative and artistic expression",
    "Technical and mechanical understanding",
    "Leadership and people management",
    "Problem-solving under pressure",
    "Attention to detail and precision",
    "Public speaking and presentation",
    "Research and information gathering",
    "Project planning and organization",
    "Multitasking and time management",
    "Adaptability and learning new skills",
    "Empathy and emotional intelligence",
    "Strategic thinking and planning"
]

WORK_STYLE_QUESTIONS = [
    "Flexible working hours and remote work",
    "Collaborative team environment",
    "Fast-paced and dynamic work",
    "Stable and predictable routine",
    "Opportunity for travel",
    "Work-life balance",
    "High salary and financial rewards",
    "Recognition and appreciation",
    "Continuous learning opportunities",
    "Making a positive social impact"
]

VALUES_QUESTIONS = [
    "Financial security and stability",
    "Helping others and making a difference",
    "Prestige and recognition",
    "Creativity and self-expression",
    "Independence and autonomy",
    "Continuous growth and learning",
    "Work-life balance and family time",
    "Innovation and cutting-edge work",
    "Environmental sustainability",
    "Social justice and equality"
]

# Add to app.py after the existing questions

# IQ Test Questions
# app.py - Add these updated question sets

# IQ Test Questions with correct answers
IQ_LOGICAL_QUESTIONS = [
    {'text': 'If all Bloops are Razzies and all Razzies are Lazzies, then all Bloops are definitely Lazzies. This statement is:', 
     'options': ['True', 'False', 'Uncertain', 'Cannot be determined'],
     'correct': 0},
    {'text': 'Complete the series: 2, 6, 12, 20, ?', 
     'options': ['28', '30', '32', '34'],
     'correct': 0},
    {'text': 'Which number is the odd one out? 2, 5, 10, 17, 26, 37, 50', 
     'options': ['2', '26', '37', '50'],
     'correct': 3},
    {'text': 'If A is taller than B, and B is taller than C, then which statement is true?', 
     'options': ['A is shortest', 'C is tallest', 'A is taller than C', 'B is tallest'],
     'correct': 2},
    {'text': 'Find the missing number: 3, 9, 27, 81, ?', 
     'options': ['162', '243', '324', '405'],
     'correct': 1},
    {'text': 'Which word does not belong? Apple, Banana, Orange, Carrot, Mango', 
     'options': ['Apple', 'Banana', 'Carrot', 'Mango'],
     'correct': 2},
    {'text': 'If NOON is coded as 14151414, then what is MORNING coded as?', 
     'options': ['131518149147', '13151814914', '1315189147', '131518914'],
     'correct': 0},
    {'text': 'Which shape completes the pattern? (Pattern recognition question)', 
     'options': ['Circle', 'Square', 'Triangle', 'Hexagon'],
     'correct': 2}
]

IQ_NUMERICAL_QUESTIONS = [
    {'text': 'What is 15% of 200?', 'options': ['25', '30', '35', '40'], 'correct': 1},
    {'text': 'If a train travels 300 km in 5 hours, what is its average speed?', 
     'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'correct': 1},
    {'text': 'Solve: 8 × (5 + 3) - 4 = ?', 'options': ['60', '64', '68', '72'], 'correct': 0},
    {'text': 'What is the square root of 144?', 'options': ['10', '11', '12', '13'], 'correct': 2},
    {'text': 'A shirt costs ₹1200 after a 20% discount. What was the original price?', 
     'options': ['₹1400', '₹1440', '₹1500', '₹1600'], 'correct': 2},
    {'text': 'What is the next number: 1, 4, 9, 16, 25, ?', 'options': ['30', '32', '36', '49'], 'correct': 2},
    {'text': 'If 3 workers can build a wall in 10 days, how many workers are needed to build it in 5 days?', 
     'options': ['5', '6', '7', '8'], 'correct': 1},
    {'text': 'What is 2/3 of 90?', 'options': ['30', '45', '60', '75'], 'correct': 2}
]

IQ_VERBAL_QUESTIONS = [
    {'text': 'Choose the word that is most similar in meaning to "Benevolent":', 
     'options': ['Kind', 'Strict', 'Angry', 'Greedy'], 'correct': 0},
    {'text': 'Complete the analogy: Doctor is to Hospital as Teacher is to ______', 
     'options': ['School', 'Office', 'Library', 'Classroom'], 'correct': 0},
    {'text': 'Choose the word that is opposite in meaning to "Optimistic":', 
     'options': ['Hopeful', 'Positive', 'Pessimistic', 'Cheerful'], 'correct': 2},
    {'text': 'Select the correct spelling:', 
     'options': ['Accommodate', 'Acommodate', 'Accommodate', 'Acommodate'], 'correct': 0},
    {'text': 'Choose the word that best fits: The ________ of the movie left the audience confused.', 
     'options': ['Plot', 'Ending', 'Beginning', 'Title'], 'correct': 1},
    {'text': 'Select the synonym of "Magnificent":', 
     'options': ['Ordinary', 'Splendid', 'Average', 'Mediocre'], 'correct': 1},
    {'text': 'Complete the sentence: She is _______ than her sister.', 
     'options': ['Tall', 'Taller', 'Tallest', 'More tall'], 'correct': 1},
    {'text': 'Choose the antonym of "Fragile":', 
     'options': ['Weak', 'Delicate', 'Strong', 'Breakable'], 'correct': 2}
]

IQ_SPATIAL_QUESTIONS = [
    {'text': 'Which shape would complete the pattern?', 
     'options': ['⬜ Square', '🔺 Triangle', '⬤ Circle', '◼ Rectangle'], 'correct': 1},
    {'text': 'If you rotate the shape 90 degrees clockwise, what do you get?', 
     'options': ['↗ Up-Right', '↘ Down-Right', '↙ Down-Left', '↖ Up-Left'], 'correct': 1},
    {'text': 'Which figure is the mirror image of the given shape?', 
     'options': ['◀ Left Arrow', '▶ Right Arrow', '▲ Up Arrow', '▼ Down Arrow'], 'correct': 1},
    {'text': 'How many cubes are in this 3D structure?', 
     'options': ['4', '5', '6', '7'], 'correct': 1},
    {'text': 'Which of the following is a 3D shape?', 
     'options': ['Circle', 'Square', 'Cube', 'Triangle'], 'correct': 2},
    {'text': 'If a cube is cut into 8 smaller cubes, how many faces are painted?', 
     'options': ['24', '48', '36', '12'], 'correct': 0},
    {'text': 'Which pattern is the odd one out?', 
     'options': ['⬤ Solid Circle', '◯ Hollow Circle', '◉ Circle with Dot', '◎ Double Circle'], 'correct': 3},
    {'text': 'What is the next shape in the sequence: ⬤, ◼, ▲, ⬤, ◼, ?', 
     'options': ['⬤ Circle', '◼ Square', '▲ Triangle', '● Circle'], 'correct': 2}
]

IQ_MEMORY_QUESTIONS = [
    {'text': 'Remember this sequence: 3-7-2-9-5. What was the third number?', 
     'options': ['2', '7', '9', '5'], 'correct': 0},
    {'text': 'In the pattern: Red, Blue, Green, Yellow, Red, ? What comes next?', 
     'options': ['Blue', 'Green', 'Yellow', 'Red'], 'correct': 0},
    {'text': 'What was the first word in the sequence: Apple, Ball, Cat, Dog, Elephant?', 
     'options': ['Apple', 'Ball', 'Cat', 'Dog'], 'correct': 0},
    {'text': 'Remember: 8, 3, 6, 9, 2. What is the sum of the first and last numbers?', 
     'options': ['8', '9', '10', '11'], 'correct': 2},
    {'text': 'In the pattern: Circle, Square, Triangle, Circle, Square, ? What comes next?', 
     'options': ['Circle', 'Square', 'Triangle', 'Rectangle'], 'correct': 2},
    {'text': 'What was the 4th item in: Mouse, Keyboard, Monitor, CPU, Printer?', 
     'options': ['CPU', 'Printer', 'Monitor', 'Keyboard'], 'correct': 0},
    {'text': 'Remember: A, C, E, G, I. What comes next?', 
     'options': ['J', 'K', 'L', 'M'], 'correct': 1},
    {'text': 'In the sequence: 2, 4, 8, 16, ? What is the next number?', 
     'options': ['24', '32', '64', '128'], 'correct': 1}
]






if __name__ == '__main__':
    app.run(debug=True)
