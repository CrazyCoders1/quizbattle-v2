from app import db
from datetime import datetime
from sqlalchemy import UniqueConstraint

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    wrong_answers = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)  # in seconds
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure one result per user per challenge
    __table_args__ = (UniqueConstraint('user_id', 'challenge_id', name='unique_user_challenge_result'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_id': self.challenge_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'time_taken': self.time_taken,
            'submitted_at': self.submitted_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
