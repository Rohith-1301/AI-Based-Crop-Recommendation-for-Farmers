from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    mobile = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), default='en')
    farm_size = db.Column(db.Float, nullable=False)
    
    predictions = db.relationship('CropPrediction', backref='farmer', lazy=True)
    diseases = db.relationship('DiseaseHistory', backref='farmer', lazy=True)
    chats = db.relationship('ChatHistory', backref='farmer', lazy=True)

class CropPrediction(db.Model):
    __tablename__ = 'crop_predictions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    n = db.Column(db.Float, nullable=False)
    p = db.Column(db.Float, nullable=False)
    k = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    soil_type = db.Column(db.String(50))
    district = db.Column(db.String(50))
    season = db.Column(db.String(50))
    recommended_crop = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    report_data = db.Column(db.Text)  # Stores detailed payload strings

class DiseaseHistory(db.Model):
    __tablename__ = 'disease_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    image_path = db.Column(db.String(256), nullable=False)
    detected_disease = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    farm_area = db.Column(db.Float, nullable=False)
    area_unit = db.Column(db.String(20), nullable=False)
    calculations_json = db.Column(db.Text, nullable=False)

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'model'
    message = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='en')