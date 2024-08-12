"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Favorites
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

jwt = JWTManager(app)

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={"id": user.id})
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Incorrect email or password"}), 401

def get_current_user():
    identity = get_jwt_identity()
    if identity:
        return User.query.get(identity['id'])
    return None

@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/characters', methods=['GET'])
def handle_get_characters():
    characters = Characters.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/characters/<int:id>', methods=['GET'])
def handle_get_character(id):
    character = Characters.query.get(id)
    if character:
        return jsonify(character.serialize()), 200
    else:
        return jsonify({"error": "Character not found"}), 404

@app.route('/planets', methods=['GET'])
def handle_get_planets():
    planets = Planets.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:id>', methods=['GET'])
def handle_get_planet(id):
    planet = Planets.query.get(id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({"error": "Planet not found"}), 404

@app.route('/users/favorites', methods=['GET'])
def handle_get_favorites():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not authenticated"}), 401
    
    favorites = Favorites.query.filter_by(led_user_id=current_user.id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

# Add a favorite characters for the current user
@app.route('/favorites/characters/<int:characters_id>', methods=['POST'])
def add_favorite_characters(characters_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not authenticated"}), 401
    
    new_favorite = Favorites(led_user_id=current_user.id, led_favorite_characters=characters_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"done": True}), 201

# Add a favorite planet for the current user
@app.route('/favorites/planets/<int:planets_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not authenticated"}), 401
    
    new_favorite = Favorites(led_user_id=current_user.id, led_favorite_planets=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"done": True}), 201

# Delete a favorite characters
@app.route('/favorites/characters/<int:characters_id>', methods=['DELETE'])
def delete_favorite_characters(characters_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "User not authenticated"}), 401
    
    favorite = Favorites.query.filter_by(led_user_id=current_user.id, led_favorite_characters=characters_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"done": True}), 200
    else:
        return jsonify({"error": "Favorite not found"}), 404
    
# Delete a favorite planet
@app.route('/favorites/planets/<int:planets_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user = get_current_user()  # Placeholder function
    if not current_user:
        return jsonify({"error": "User not authenticated"}), 401
    
    favorite = Favorites.query.filter_by(led_user_id=current_user.id, led_favorite_planets=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"done": True}), 200
    else:
        return jsonify({"error": "Favorite not found"}), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
