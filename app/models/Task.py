from app import db

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Text)
    file = db.Column(db.Text)
    problem = db.relationship('Problem', backref='submissions', lazy=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    user = db.relationship('User', backref='submissions', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    maxscore = db.Column(db.Integer)
    maxtests = db.Column(db.Integer)