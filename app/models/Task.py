from app import db


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    file = db.Column(db.Text)
    problem = db.relationship('Problem', backref='submissions', lazy=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    user = db.relationship('User', backref='submissions', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    max_score = db.Column(db.Integer)
    max_time = db.Column(db.Float)
    test_folder = db.Column(db.Text)
    details = db.Column(db.Text)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
