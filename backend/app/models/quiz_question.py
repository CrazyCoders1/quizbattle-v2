from app import db

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)  # List of options
    answer = db.Column(db.Integer, nullable=False)  # Index of correct answer
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, tough
    exam_type = db.Column(db.String(50), nullable=False)  # CBSE 11, JEE Main, etc.
    hint = db.Column(db.Text, nullable=True)  # Optional hint for tough questions
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # For soft delete
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'options': self.options,
            'answer': self.answer,
            'difficulty': self.difficulty,
            'exam_type': self.exam_type,
            'hint': self.hint,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
