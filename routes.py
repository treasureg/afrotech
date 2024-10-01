from flask import render_template, request, jsonify, session, redirect, url_for, flash
from models import User, Resume, Job, Application
from app import db
from resume_parser import parse_resume
from job_matcher import match_jobs
from auto_applier import apply_to_job
from job_scraper import scrape_jobs
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging

def init_routes(app):
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            if user:
                flash('Username already exists')
                return redirect(url_for('register'))
            
            new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            return redirect(url_for('dashboard'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            try:
                user = User.query.filter_by(username=username).first()
                if user and check_password_hash(user.password_hash, password):
                    session['user_id'] = user.id
                    
                    # Check if the new columns exist, if not, add default values
                    if not hasattr(user, 'job_title_preference'):
                        user.job_title_preference = ''
                    if not hasattr(user, 'job_type_preference'):
                        user.job_type_preference = ''
                    if not hasattr(user, 'industry_preference'):
                        user.industry_preference = ''
                    if not hasattr(user, 'location_preference'):
                        user.location_preference = ''
                    if not hasattr(user, 'salary_min'):
                        user.salary_min = None
                    if not hasattr(user, 'experience_level'):
                        user.experience_level = ''
                    
                    db.session.commit()
                    
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password')
                    app.logger.warning(f"Failed login attempt for username: {username}")
            except Exception as e:
                app.logger.error(f"Error during login: {str(e)}")
                flash('An error occurred during login. Please try again.')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))

    @app.route('/upload_resume', methods=['POST'])
    def upload_resume():
        if 'user_id' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        if 'resume' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            try:
                file_path = os.path.join('/tmp', file.filename)
                file.save(file_path)
                
                parsed_data = parse_resume(file_path)
                
                if parsed_data is None:
                    return jsonify({'error': 'Failed to parse resume'}), 400
                
                user = User.query.get(session['user_id'])
                resume = Resume(user_id=user.id, content=str(parsed_data))
                db.session.add(resume)
                db.session.commit()
                
                os.remove(file_path)
                
                return jsonify({'message': 'Resume uploaded and parsed successfully'}), 200
            except Exception as e:
                return jsonify({'error': f'Error processing resume: {str(e)}'}), 500

    @app.route('/set_preferences', methods=['POST'])
    def set_preferences():
        if 'user_id' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.job_title_preference = request.form.get('job_title', '')
        user.job_type_preference = request.form.get('job_type', '')
        user.industry_preference = request.form.get('industry', '')
        user.location_preference = request.form.get('location', '')
        user.salary_min = request.form.get('salary_min', type=int)
        user.experience_level = request.form.get('experience_level', '')
        
        db.session.commit()
        
        return jsonify({'message': 'Preferences updated successfully'}), 200

    @app.route('/find_and_apply', methods=['POST'])
    def find_and_apply():
        if 'user_id' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        user = User.query.get(session['user_id'])
        
        new_jobs = scrape_jobs()
        for job in new_jobs:
            db.session.add(Job(**job))
        db.session.commit()
        
        matched_jobs = match_jobs(user.id)
        
        applied_jobs = 0
        for job in matched_jobs:
            success = apply_to_job(user, job)
            if success:
                application = Application(user_id=user.id, job_id=job.id, status='Applied')
                db.session.add(application)
                applied_jobs += 1
        
        db.session.commit()
        
        return jsonify({'message': f'Applied to {applied_jobs} jobs'}), 200

    @app.route('/get_applications', methods=['GET'])
    def get_applications():
        if 'user_id' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        applications = Application.query.filter_by(user_id=user.id).all()
        return jsonify([{
            'job_title': app.job.title,
            'company': app.job.company,
            'status': app.status,
            'applied_date': app.applied_date.strftime('%Y-%m-%d')
        } for app in applications]), 200