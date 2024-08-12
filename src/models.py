from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship("Favorites", backref="user")

    def __init__(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise Exception(error.args)

    def serialize(self):
        bond_dictionaries = []
        for bond in self.favorites:
            bond_dictionaries.append(
                bond.serialize()
            )
        return {
            "id": self.id,
            "email": self.email,
            "favorites": bond_dictionaries
            # do not serialize the password, its a security breach
        }
    
class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    led_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    led_favorite_characters = db.Column(db.Integer, db.ForeignKey("characters.id"))
    led_favorite_planets = db.Column(db.Integer, db.ForeignKey("planets.id"))

    def __init__(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "favorites_characters": self.led_favorite_characters,
            "favorite_planets": self.led_favorite_planets
        }

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    hair_color = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))

    def __init__(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "character_name": self.character_name,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(250))
    climate = db.Column(db.String(250))
    diameter = db.Column(db.String(250))
    gravity = db.Column(db.String(250))

    def __init__(self):
        db.session.add(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "planet_name": self.planet_name,
            "climate": self.climate,
            "diameter": self.diameter,
            "gravity": self.gravity
        }