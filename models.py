from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, DateTime
from flask_migrate import Migrate

database_path = "postgresql://postgres:temppass@localhost:5432/hackthis"

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    zip_code = db.Column(db.String)
    interests = db.Column(db.String)
    qualifications = db.Column(db.String)

    def format(self):
        return {
            "id": self.id,
            "name": self.title,
            "email": self.release_date,
            "zip_code": self.zip_code,
            "interests": self.interests,
            "qualifications": self.qualifications
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Business(db.Model):
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    zip_code = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)
    website = db.Column(db.String)
    address = db.Column(db.String)
    description = db.Column(db.String)
    skills = db.Column(db.String)

    def format(self):
        return {
            "id": self.id,
            "name": self.title,
            "email": self.release_date,
            "zip_code": self.zip_code,
            "goals": self.goals,
            "website": self.website,
            "address": self.address,
            "description": self.description,
            "skills": self.skills
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
