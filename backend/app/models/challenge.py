from app import db
from datetime import datetime
import random
import string

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    question_count = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, nullable=False)  # in minutes
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, **kwargs):
        super(Challenge, self).__init__(**kwargs)
        if not self.code:
            self.code = self.generate_code()
    
    def generate_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'exam_type': self.exam_type,
            'difficulty': self.difficulty,
            'question_count': self.question_count,
            'time_limit': self.time_limit,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
