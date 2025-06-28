from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
import sqlite3
from datetime import datetime, timedelta
from main import PasswordGenerator, PasswordManager
import secrets
import string
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize Flask-Session
Session(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            default_password_length INTEGER DEFAULT 12,
            default_include_uppercase BOOLEAN DEFAULT 1,
            default_include_lowercase BOOLEAN DEFAULT 1,
            default_include_digits BOOLEAN DEFAULT 1,
            default_include_symbols BOOLEAN DEFAULT 1,
            theme TEXT DEFAULT 'light',
            auto_logout_minutes INTEGER DEFAULT 30,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_settings(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
    settings = cursor.fetchone()
    conn.close()
    
    if not settings:
        # Create default settings
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_settings (user_id, default_password_length, default_include_uppercase, 
                                     default_include_lowercase, default_include_digits, default_include_symbols, 
                                     theme, auto_logout_minutes)
            VALUES (?, 12, 1, 1, 1, 1, 'light', 30)
        ''', (user_id,))
        conn.commit()
        conn.close()
        
        # Return default settings
        return (1, user_id, 12, 1, 1, 1, 1, 'light', 30)
    
    return settings

def update_user_settings(user_id, **kwargs):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Build update query dynamically
    update_fields = []
    values = []
    for key, value in kwargs.items():
        if key in ['default_password_length', 'default_include_uppercase', 'default_include_lowercase', 
                   'default_include_digits', 'default_include_symbols', 'theme', 'auto_logout_minutes']:
            update_fields.append(f"{key} = ?")
            values.append(value)
    
    if update_fields:
        values.append(user_id)
        query = f"UPDATE user_settings SET {', '.join(update_fields)} WHERE user_id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()

# Initialize database on startup
init_db()

# Initialize password generator and manager
generator = PasswordGenerator()
manager = PasswordManager()

# Add this function at the top level
def is_logged_in():
    return 'username' in session

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user[2], password):  # user[2] is password_hash
            session.permanent = True
            session['username'] = username
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        
        # Check if username already exists
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        # Hash password and save user
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)', 
                      (username, password_hash, email))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    password_count = manager.get_password_count(session['username'])
    return render_template('dashboard.html', 
                         username=session['username'],
                         password_count=password_count)

@app.route('/generate_password', methods=['GET', 'POST'])
def generate_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        include_uppercase = 'uppercase' in request.form
        include_lowercase = 'lowercase' in request.form
        include_digits = 'numbers' in request.form
        include_symbols = 'symbols' in request.form
        
        password = generator.generate_password(
            length=length,
            include_uppercase=include_uppercase,
            include_lowercase=include_lowercase,
            include_digits=include_digits,
            include_symbols=include_symbols
        )
        
        return render_template('generate.html', password=password)
    
    return render_template('generate.html')

@app.route('/generate_multiple', methods=['GET', 'POST'])
def generate_multiple():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            count = int(request.form.get('count', 5))
            length = int(request.form.get('length', 12))
            
            passwords = generator.generate_multiple_passwords(
                count=count,
                length=length
            )
            
            password_strengths = []
            for pwd in passwords:
                strength = generator.check_password_strength(pwd)
                password_strengths.append({
                    'password': pwd,
                    'strength': strength
                })
            
            return render_template('generate_multiple.html', 
                                 passwords=password_strengths,
                                 form_data=request.form)
        except ValueError as e:
            flash(f'Error: {e}', 'error')
    
    return render_template('generate_multiple.html')

@app.route('/check_strength', methods=['GET', 'POST'])
def check_strength():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password:
            strength = generator.check_password_strength(password)
            return render_template('check_strength.html', 
                                 password=password,
                                 strength=strength)
    
    return render_template('check_strength.html')

@app.route('/save_password', methods=['GET', 'POST'])
def save_password():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        password = request.args.get('password', '')
        website = request.args.get('website', '')
        email = request.args.get('email', '')
        notes = request.args.get('notes', '')
        return render_template('save_password.html', password=password, website=website, email=email, notes=notes)
    
    if request.method == 'POST':
        website = request.form['website']
        email = request.form['email']
        password = request.form['password']
        notes = request.form['notes']
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to CSV
        with open('passwords.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([session['username'], website, email, password, created_date, notes])
        
        flash('Password saved successfully!', 'success')
        return redirect(url_for('view_passwords'))

@app.route('/view_passwords')
def view_passwords():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    passwords = manager.get_user_passwords(session['username'])
    return render_template('view_passwords.html', passwords=passwords)

@app.route('/search_passwords')
def search_passwords():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    search_term = request.args.get('search', '')
    if search_term:
        passwords = manager.search_passwords_web(session['username'], search_term)
    else:
        passwords = []
    
    return render_template('search_passwords.html', passwords=passwords, search_term=search_term)

@app.route('/export_passwords')
def export_passwords():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    export_file = manager.export_passwords_web(session['username'])
    if export_file and os.path.exists(export_file):
        return send_file(export_file, as_attachment=True, download_name='passwords.csv')
    else:
        flash('No passwords to export!', 'info')
        return redirect(url_for('view_passwords'))

@app.route('/api/generate_password', methods=['POST'])
def api_generate_password():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        length = data.get('length', 12)
        include_uppercase = data.get('uppercase', True)
        include_lowercase = data.get('lowercase', True)
        include_digits = data.get('digits', True)
        include_symbols = data.get('symbols', True)
        exclude_ambiguous = data.get('exclude_ambiguous', False)
        
        password = generator.generate_password(
            length=length,
            include_uppercase=include_uppercase,
            include_lowercase=include_lowercase,
            include_digits=include_digits,
            include_symbols=include_symbols,
            exclude_ambiguous=exclude_ambiguous
        )
        
        strength = generator.check_password_strength(password)
        
        return jsonify({
            'password': password,
            'strength': strength
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/check_strength', methods=['POST'])
def api_check_strength():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if password:
            strength = generator.check_password_strength(password)
            return jsonify({
                'strength': strength
            })
        else:
            return jsonify({'error': 'No password provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Get current user data
        user = get_user_by_username(session['username'])
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('profile'))
        
        # Verify current password
        if not check_password_hash(user[2], current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('profile'))
        
        # Update database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            # Check if new username already exists (if changing username)
            if new_username != session['username']:
                cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', (new_username, user[0]))
                if cursor.fetchone():
                    flash('Username already exists', 'error')
                    return redirect(url_for('profile'))
            
            # Update user information
            if new_password:
                if new_password != confirm_password:
                    flash('New passwords do not match', 'error')
                    return redirect(url_for('profile'))
                
                if len(new_password) < 8:
                    flash('New password must be at least 8 characters', 'error')
                    return redirect(url_for('profile'))
                
                # Update with new password
                password_hash = generate_password_hash(new_password)
                cursor.execute('UPDATE users SET username = ?, email = ?, password_hash = ? WHERE id = ?',
                             (new_username, new_email, password_hash, user[0]))
            else:
                # Update without changing password
                cursor.execute('UPDATE users SET username = ?, email = ? WHERE id = ?',
                             (new_username, new_email, user[0]))
            
            conn.commit()
            
            # Update session if username changed
            if new_username != session['username']:
                session['username'] = new_username
            
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('profile'))
    
    # GET request - show current profile
    user = get_user_by_username(session['username'])
    if user:
        password_count = manager.get_password_count(session['username'])
        settings = get_user_settings(user[0])
        return render_template('profile.html', 
                             username=user[1], 
                             email=user[3] or '',
                             password_count=password_count,
                             settings=settings)
    else:
        flash('User not found', 'error')
        return redirect(url_for('dashboard'))

@app.route('/update_settings', methods=['POST'])
def update_settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_username(session['username'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('profile'))
    
    try:
        # Get form data
        default_password_length = int(request.form.get('default_password_length', 12))
        default_include_uppercase = 'default_include_uppercase' in request.form
        default_include_lowercase = 'default_include_lowercase' in request.form
        default_include_digits = 'default_include_digits' in request.form
        default_include_symbols = 'default_include_symbols' in request.form
        theme = request.form.get('theme', 'light')
        auto_logout_minutes = int(request.form.get('auto_logout_minutes', 30))
        
        # Validate settings
        if default_password_length < 4 or default_password_length > 128:
            flash('Password length must be between 4 and 128 characters', 'error')
            return redirect(url_for('profile'))
        
        if auto_logout_minutes < 0 or auto_logout_minutes > 480:
            flash('Auto logout must be between 0 and 480 minutes', 'error')
            return redirect(url_for('profile'))
        
        # Update settings
        update_user_settings(user[0], 
                           default_password_length=default_password_length,
                           default_include_uppercase=default_include_uppercase,
                           default_include_lowercase=default_include_lowercase,
                           default_include_digits=default_include_digits,
                           default_include_symbols=default_include_symbols,
                           theme=theme,
                           auto_logout_minutes=auto_logout_minutes)
        
        flash('Settings updated successfully!', 'success')
        
    except ValueError as e:
        flash(f'Invalid setting value: {str(e)}', 'error')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')
    
    return redirect(url_for('profile'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 