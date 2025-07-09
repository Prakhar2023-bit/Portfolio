from flask import Flask, render_template, url_for, request, redirect, jsonify,session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'portfolio.db')
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        content = request.form.get('content', '').strip()

        if name and email and content:
            new_msg = Message(name=name, email=email, content=content)
            db.session.add(new_msg)
            db.session.commit()
            return redirect(url_for('contact', success=True))

        return render_template('contact.html', success=False)

    return render_template('contact.html', success=None)
  

@app.route('/api/messages')
def api_messages():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return jsonify([m.to_dict() for m in messages])

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':  # CHANGE THIS PASSWORD!
            session['admin_logged_in'] = True
            return redirect(url_for('admin_messages'))
        else:
            flash('Incorrect password', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/messages')
def admin_messages():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    messages = Message.query.order_by(Message.id.desc()).all()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
