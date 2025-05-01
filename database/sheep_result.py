from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SheepResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    input_file = db.Column(db.String(150), nullable=False)
    output_file = db.Column(db.String(150), nullable=False)
    sheep_count = db.Column(db.Integer, nullable=False)