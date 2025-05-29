from application.database import db
from flask_security import UserMixin, RoleMixin

class RolesUsers(db.Model):
    __tablename__ = 'RolesUsers'
    ru_id = db.Column(db.Integer(), primary_key=True)
    ru_user_id = db.Column('user_id', db.Integer(), db.ForeignKey('User.id'))
    ru_role_id = db.Column('role_id', db.Integer(), db.ForeignKey('Role.id'))

class Role(db.Model, RoleMixin):
    __tablename__ = "Role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    description = db.Column(db.String(255), unique=True, nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(25), unique=True, nullable=False)
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String(25), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='RolesUsers', backref=db.backref('users', lazy='dynamic'))

    # One-to-many: User -> SymptomOutcome
    symptoms = db.relationship('SymptomOutcome', backref='user', lazy=True, cascade="all, delete-orphan")
    # One-to-many: User -> FoodIntake
    food_intakes = db.relationship('FoodIntake', backref='user', lazy=True, cascade="all, delete-orphan")

class SymptomOutcome(db.Model):
    __tablename__ = 'SymptomOutcome'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    stool_consistency = db.Column(db.Integer)
    pain_while_passing_stool = db.Column(db.Boolean)
    stool_colour = db.Column(db.String(25))
    stool_frequency = db.Column(db.Integer)
    mucous_in_stool = db.Column(db.Boolean)
    blood_in_stool = db.Column(db.Boolean)
    pain_location = db.Column(db.String(50))
    fever = db.Column(db.Boolean)
    nausea = db.Column(db.Boolean)
    flatulence = db.Column(db.Boolean)

class FoodIntake(db.Model):
    __tablename__ = 'FoodIntake'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    water = db.Column(db.Integer)
    stress = db.Column(db.Integer)

    # One-to-many: FoodIntake -> Meal
    meals = db.relationship('Meal', backref='food_intake', lazy=True, cascade="all, delete-orphan")

class Meal(db.Model):
    __tablename__ = 'Meal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    food_intake_id = db.Column(db.Integer, db.ForeignKey('FoodIntake.id'), nullable=False)
    meal_type = db.Column(db.String(10), nullable=False)  # 'breakfast', 'lunch', 'dinner', 'snack'
    item = db.Column(db.String(50), nullable=False)