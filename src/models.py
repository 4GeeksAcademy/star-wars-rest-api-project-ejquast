from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    led_favorites_id = db.Column(db.Integer, db.ForeignKey("favorites.id"))
    favorites = db.relationship("FavoritesList", backref="user")

    def __init__(self):
        db.session.add(self)
        try:
            db.session.commit()
        exception Exception as error:
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
    
class Favorites(db.model):
    id = db.Column(db.Integer, primary_key=True)
    led_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("FavoritesList", backref="favorites")
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

class Characters(db.model):
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(String(250))
    gender = db.Column(db.String(250))
    hair_color = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))

class Planets(db.model):
    id = Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(250))
    climate = db.Column(db.String(250))
    diameter = db.Column(db.String(250))
    gravity = db.Column(db.String(250))