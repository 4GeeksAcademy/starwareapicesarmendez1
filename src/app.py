"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os, json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planets, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

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

@app.route('/user', methods=['GET'])
def handle_hello():
    users=User.query.all()
    if len (users)<1:
        return jsonify({"msg":"no existe usuario"}),404
    serialized_users=list(map(lambda x:x.serialize(),users))
    return serialized_users 


@app.route('/planets', methods=['GET'])
def get_planets():
    planets=Planets.query.all()
    if len (planets)<1:
        return jsonify({"msg":"no existe planets"}),404
    serialized_planets=list(map(lambda x:x.serialize(),planets))
    return serialized_planets 

@app.route('/character', methods=['GET'])
def get_character():
    character=Character.query.all()
    if len (character)<1:
        return jsonify({"msg":"no existe character"}),404
    serialized_character=list(map(lambda x:x.serialize(),character))
    return serialized_character 

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_oneplanets(planet_id):
    planet=Planets.query.get(planet_id)
    if  planet is None:
        return jsonify({"msg":"no existe planets"}),404
    serialized_planet=planet.serialize()
    return serialized_planet

@app.route('/character/<int:character_id>', methods=['GET'])
def get_onecharacter(character_id):
    character=Character.query.get(character_id)
    if  character is None:
        return jsonify({"msg":"no existe character"}),404
    serialized_character=character.serialize()
    return serialized_character

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user=User.query.get(user_id)
    if  user is None:
        return jsonify({"msg":"no existe user"}),404
    serialized_user=user.serialize()
    return serialized_user

@app.route('/user', methods=['POST'])
def agregaruser():
    body=json.loads(request.data)
    newuser=User(
        email=body["email"],
        password=body["password"],
        is_active=True
    )
    db.session.add(newuser)
    db.session.commit()
    return jsonify({"msg":"usuario creado con exito"}),200

@app.route('/character', methods=['POST'])
def agregarcharacter():
    body=json.loads(request.data)
    newcharacter=Character(
        name=body["name"],
        gender=body["gender"],
        height=body["height"],
        eye_color=body["eye_color"],
        
    )
    db.session.add(newcharacter)
    db.session.commit()
    return jsonify({"msg":"character creado con exito"}),200

@app.route('/planets', methods=['POST'])
def agregarplanets():
    body=json.loads(request.data)
    newplanet=Planets(
        name=body["name"],
        population=body["population"],
        diameter=body["diameter"],
        climate=body["climate"],
        
    )
    db.session.add(newplanet)
    db.session.commit()
    return jsonify({"msg":"planeta creado con exito"}),200

@app.route('/character/<int:character_id>', methods=['DELETE'])
def deleteonecharacter(character_id):
    deletecharacter=Character.query.get(character_id)
    db.session.delete(deletecharacter)
    db.session.commit()
    return jsonify({"msg":"character borrado con exito"}),200

@app.route('/planets/<int:planets_id>', methods=['DELETE'])
def deleteoneplanet(planets_id):
    deleteoneplanet=Planets.query.get(planets_id)
    db.session.delete(deleteoneplanet)
    db.session.commit()
    return jsonify({"msg":"planeta borrado con exito"}),200

@app.route('/user/<int:user_id>/favorite', methods=['GET'])
def favorite(user_id):
    favorite=Favorite.query.filter_by(user_id=user_id).all()
    if len(favorite)<1:
        return jsonify({"msg":"no existe favoritos"}),404
    serialized_favorite=list(map(lambda x:x.serialize(),favorite))
    return serialized_favorite,200
   
@app.route('/user/<int:user_id>/favorite/<int:planets_id>', methods=['POST'])
def addfavorite(planets_id, user_id):
    newfavorite=Favorite(user_id=user_id, planets_id=planets_id)
    db.session.add(newfavorite)
    db.session.commit()
    return jsonify({"msg":"planeta agregado a favoritos"}),200

@app.route('/user/<int:user_id>/favoritecharacter/<int:character_id>', methods=['POST'])
def addfavoritecharacter(character_id, user_id):
    newfavorite=Favorite(user_id=user_id, character_id=character_id)
    db.session.add(newfavorite)
    db.session.commit()
    return jsonify({"msg":"character agregado a favoritos"}),200
   
   
   

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
