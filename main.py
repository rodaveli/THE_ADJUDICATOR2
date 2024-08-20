import os
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
from sqlalchemy.sql import func
import uuid
import openai
from openai import OpenAI

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Add this function to handle CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///adjudicator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class AdjudicationSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    opponent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    join_link = db.Column(db.String(36), unique=True, nullable=False)
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'completed'
    all_arguments_submitted = db.Column(db.Boolean, default=False)
    judgment_result = db.Column(db.Text)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_sessions')
    opponent = db.relationship('User', foreign_keys=[opponent_id], backref='joined_sessions')
    winner = db.relationship('User', foreign_keys=[winner_id])

User.created_sessions = db.relationship('AdjudicationSession', foreign_keys=[AdjudicationSession.creator_id], backref='creator', lazy='dynamic')
User.joined_sessions = db.relationship('AdjudicationSession', foreign_keys=[AdjudicationSession.opponent_id], backref='opponent', lazy='dynamic')

class Argument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    is_locked = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer, db.ForeignKey('adjudication_session.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    session = db.relationship('AdjudicationSession', backref=db.backref('arguments', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('arguments', lazy='dynamic'))

@app.route('/')
def hello():
    return jsonify({"message": "Welcome to the Adjudicator App!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello, {current_user}! This is a protected route."}), 200

@app.route('/create_session', methods=['POST'])
@jwt_required()
def create_session():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({"message": "Title is required"}), 400
    
    join_link = str(uuid.uuid4())
    new_session = AdjudicationSession(title=title, creator_id=user.id, join_link=join_link)
    
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({
        "message": "Adjudication session created successfully",
        "session_id": new_session.id,
        "join_link": join_link
    }), 201

@app.route('/join_session/<join_link>', methods=['POST'])
@jwt_required()
def join_session(join_link):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    session = AdjudicationSession.query.filter_by(join_link=join_link).first()
    
    if not session:
        return jsonify({"message": "Invalid join link"}), 404
    
    if session.status != 'open':
        return jsonify({"message": "This session is no longer open"}), 400
    
    if session.creator_id == user.id:
        return jsonify({"message": "You cannot join your own session"}), 400
    
    session.opponent_id = user.id
    session.status = 'in_progress'
    db.session.commit()
    
    return jsonify({"message": "Successfully joined the session"}), 200

@app.route('/user_sessions', methods=['GET'])
@jwt_required()
def user_sessions():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    created_sessions = [{"id": s.id, "title": s.title, "status": s.status} for s in user.created_sessions]
    joined_sessions = [{"id": s.id, "title": s.title, "status": s.status} for s in user.joined_sessions]
    
    return jsonify({
        "created_sessions": created_sessions,
        "joined_sessions": joined_sessions
    }), 200

@app.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    session = AdjudicationSession.query.get(session_id)
    
    if not session:
        return jsonify({"message": "Session not found"}), 404
    
    if session.creator_id != user.id and session.opponent_id != user.id:
        return jsonify({"message": "You don't have access to this session"}), 403
    
    return jsonify({
        "id": session.id,
        "title": session.title,
        "status": session.status,
        "creator": session.creator.username,
        "opponent": session.opponent.username if session.opponent else None,
        "created_at": session.created_at.isoformat(),
        "join_link": session.join_link if session.creator_id == user.id else None
    }), 200

@app.route('/submit_argument/<int:session_id>', methods=['POST'])
@jwt_required()
def submit_argument(session_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    session = AdjudicationSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Session not found"}), 404
    
    if session.status != 'in_progress':
        return jsonify({"message": "This session is not in progress"}), 400
    
    if session.creator_id != user.id and session.opponent_id != user.id:
        return jsonify({"message": "You don't have access to this session"}), 403
    
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({"message": "Argument content is required"}), 400
    
    new_argument = Argument(content=content, session_id=session_id, user_id=user.id)
    db.session.add(new_argument)
    db.session.commit()
    
    return jsonify({"message": "Argument submitted successfully", "argument_id": new_argument.id}), 201

@app.route('/lock_argument/<int:argument_id>', methods=['POST'])
@jwt_required()
def lock_argument(argument_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    argument = Argument.query.get(argument_id)
    if not argument:
        return jsonify({"message": "Argument not found"}), 404
    
    if argument.user_id != user.id:
        return jsonify({"message": "You can only lock your own arguments"}), 403
    
    if argument.is_locked:
        return jsonify({"message": "This argument is already locked"}), 400
    
    argument.is_locked = True
    db.session.commit()
    
    session = argument.session
    if all(arg.is_locked for arg in session.arguments):
        session.all_arguments_submitted = True
        session.status = 'awaiting_judgment'
        db.session.commit()
        
        # Trigger AI judgment
        judgment = get_ai_judgment(session.id)
        if judgment:
            session.judgment_result = judgment
            db.session.commit()
    
    return jsonify({"message": "Argument locked successfully"}), 200

@app.route('/session_arguments/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session_arguments(session_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    session = AdjudicationSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Session not found"}), 404
    
    if session.creator_id != user.id and session.opponent_id != user.id:
        return jsonify({"message": "You don't have access to this session"}), 403
    
    arguments = [
        {
            "id": arg.id,
            "content": arg.content,
            "submitted_at": arg.submitted_at.isoformat(),
            "is_locked": arg.is_locked,
            "user": arg.user.username
        } for arg in session.arguments
    ]
    
    return jsonify({
        "session_id": session_id,
        "arguments": arguments,
        "all_arguments_submitted": session.all_arguments_submitted
    }), 200

def get_ai_judgment(session_id):
    session = AdjudicationSession.query.get(session_id)
    if not session or not session.all_arguments_submitted:
        return None

    arguments = session.arguments.all()
    prompt = f"Adjudicate the following debate. Title: {session.title}\n\n"
    for arg in arguments:
        prompt += f"Participant {arg.user.username}:\n{arg.content}\n\n"
    prompt += "Based on the arguments presented, who is the winner and why? Provide a detailed explanation."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an impartial judge tasked with adjudicating a debate based on the arguments presented."},
                {"role": "user", "content": prompt}
            ]
        )
        judgment = response.choices[0].message.content
        return judgment
    except Exception as e:
        print(f"Error in AI judgment: {str(e)}")
        return None

@app.route('/get_judgment/<int:session_id>', methods=['POST'])
@jwt_required()
def get_judgment(session_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    session = AdjudicationSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Session not found"}), 404
    
    if session.creator_id != user.id and session.opponent_id != user.id:
        return jsonify({"message": "You don't have access to this session"}), 403
    
    if not session.all_arguments_submitted:
        return jsonify({"message": "Not all arguments have been submitted"}), 400
    
    if session.judgment_result:
        return jsonify({"judgment": session.judgment_result}), 200
    
    judgment = get_ai_judgment(session_id)
    if judgment:
        session.judgment_result = judgment
        db.session.commit()
        return jsonify({"judgment": judgment}), 200
    else:
        return jsonify({"message": "Failed to get AI judgment"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)