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
from models import db, Person,Favorite,Character, Vehicle,Planet


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

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/person/<int:id>',methods=['GET'])
def get_person(id):
    person = Person.query.get(id)
    
    if person:
        return jsonify({"Person": person.serialize()})
    else:
        return jsonify({"Error": f"person with {id} was not found"})




@app.route('/persons',methods=["GET"])
def get_all_persons():
    raw_list_persons = Person.query.all()
    list_persons = [persons.serialize_with_relations()
                      for persons in raw_list_persons]
    return jsonify({"list_persons":list_persons})


@app.route('/login/person',methods=['POST'])
def create_person():
    data_request=request.get_json()

    if  not data_request or "person_id" not in data_request:
        return jsonify({"error":"the data: person_ is mandatory"}),400
    if "nickname" not in data_request:
        return jsonify({"Error":"it is necessary to enter a 'nickname'for the new user"}),400
    if "name" not in data_request:
        return jsonify({"Error":"it is necessary to enter a 'name' for the new user"}),400
    if "last_name" not in data_request:
        return jsonify({"Error":"it is necesary to enter a 'last_name' for the new user "}),400
    if "email" not in data_request:
        return jsonify({"Error":"it is necessary to enter a 'email' for the new user"}),400

    person_id=data_request["person_id"]
    person=Person.query.get(person_id)

    if  person:
        return jsonify({"error": f"la persona con el id {person_id} ya exite en nuestra base de datos"}),400
    
    new_person=Person(
        person_id=data_request["person_id"],
        nickname=data_request["nickname"],
        name=data_request["name"],
        last_name=data_request["last_name"],
        email=data_request["email"],
        )
    
    try:
        db.session.add(new_person)
        db.session.commit()
        return jsonify({"message":"Account successfully created"}),200
    except Exception as e:
        db.session.rollback()
        print("Error",e)
        return jsonify({"error":"There was a server error"}),500


@app.route('/favorites',methods=['GET'])
def get_all_favorites():
    raw_list_favorities = Favorite.query.all()
    list_favorite=[favorite.serialize() for favorite in raw_list_favorities]
    return jsonify({'favorites': list_favorite})

@app.route('/favorites/register', methods=['POST'])
def register_favorities():
    data_request = request.get_json()
    
    if not "person_id" in data_request:
        return jsonify({"Error": " los siguientes campos son importantes: person_id"}),400
    
    if not  any(f in data_request for f in ["character_id","planet_id","vehicle_id"]):
        return jsonify({"error": "one of these fields is required:character_id,planet_id,vehicle_id "}),400

    person=Person.query.get(data_request["person_id"])
    if not person:
        return jsonify({"error":"person not found in the database"}),404
    
    character_id = data_request.get("character_id")
    planet_id = data_request.get("planet_id")
    vehicle_id = data_request.get("vehicle_id")

    character=Character.query.get(character_id) if character_id else None
    planet=Planet.query.get(planet_id) if planet_id else None
    vehicle=Vehicle.query.get(vehicle_id) if vehicle_id else None

    if character_id and not character:
        return jsonify({"error":"character not found"}),404
    if planet_id and not planet:
        return jsonify({"error":"planet not found"}),404
    if vehicle_id and not vehicle:
        return jsonify({"error":"vehicle not found"}),404
    

    favorite_existing = Favorite.query.filter_by(
        person_id= person.person_id,
        character_id=character.character_id if character else None,
        planet_id = planet.planet_id if planet else None,
        vehicle_id= vehicle.vehicle_id if vehicle else None,
    ).first()

    if favorite_existing:
        return jsonify({"error":f"successfully added to the user {person.name}"}),409

    favorite = Favorite(
        person_id=person.person_id,
        character_id=character.character_id if character else None,
        planet_id=planet.planet_id if planet else None,
        vehicle_id=vehicle.vehicle_id if vehicle else None
    )

    
    try:
        db.session.add(favorite)
        db.session.commit()

        favorite_data ={
            "peson_id":person.person_id
        }

        if character:
            favorite_data["character"]={
                "id":character.character_id,
                "name":character.character_name
            }
        if planet:
            favorite_data["planet"]={
                "id":planet.planet_id,
                "name":planet.planet_name
            }
        if vehicle:
            favorite_data["vehicle"]={
                "id":vehicle.vehicle_id,
                "name":vehicle.vehicle_name
            }

        return jsonify({"message":f"favorite successfully added t o the user {person.name}",
        "favorite":favorite_data}),200
    except Exception as e:
        db.session.rollback()
        print("Error",e)
        return jsonify({"error":"Sorry, there was a server error"}),500
    
    

@app.route('/favorites', methods=['DELETE'])
def delete_favorite():
    data_request = request.get_json()
    if not data_request or "person_id" not in data_request:
        return jsonify({"error":"The 'person_id' field is mandatory"}),400
    
    person_id= data_request["person_id"]
    character_id= data_request.get("character_id")
    planet_id= data_request.get("planet_id")
    vehicle_id= data_request.get("vehicle_id")

    if not any([character_id,planet_id,vehicle_id]):
        return jsonify({"error": "you must indicate the ID of a character,planet or vehicle"}),400
    
    favorite = Favorite.query.filter_by(
        person_id=person_id,
        character_id=character_id if character_id else None,
        planet_id=planet_id if planet_id else None,
        vehicle_id=vehicle_id if vehicle_id else None,
    ).first()

    if not favorite:
        return jsonify({"error":"Favorite not found with ID provided"}),404
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": f"Favorite deleted from user  with ID # {person_id}"}),200
    except Exception as e:
        db.session.rollback()
        print("Error al eliminar el favorito:",e)
        return jsonify({"error":"Internal server error"}),500




@app.route('/characters',methods=['GET'])
def get_all_character():
    raw_list_character = Character.query.all()
    list_character=[character.serialize() for character in raw_list_character]
    return jsonify({'characters': list_character})

@app.route('/character/<int:id>',methods=['GET'])
def get_character_id(id):
    character = Character.query.get(id)
    print(character)
    if character:
        return jsonify({"character":character.serialize()})
    else:
        return jsonify({"error": "character not found"}),404

@app.route('/vehicles',methods=['GET'])
def get_all_vehicle():
    raw_list_vehicle = Vehicle.query.all()
    list_vehicle=[vehicle.serialize() for vehicle in raw_list_vehicle]
    return jsonify({'vehicles': list_vehicle})

@app.route('/vehicle/<int:id>',methods=['GET'])
def get_vehicle_id(id):
    vehicle = Vehicle.query.get(id)
    print(vehicle)
    if vehicle:
        return jsonify({"vehicle":vehicle.serialize()})
    else:
        return jsonify({"error": "vehicle not found"}),404

@app.route('/planets',methods=['GET'])
def get_all_planet():
    raw_list_planet = Planet.query.all()
    list_planets=[planet.serialize() for planet in raw_list_planet]
    return jsonify({'planets': list_planets})

@app.route('/planet/<int:id>',methods=['GET'])
def get_planet_id(id):
    planet = Planet.query.get(id)
    print(planet)
    if planet:
        return jsonify({"planet": planet.serialize()}),200
    else:
        return jsonify({"error": "planet not found"}),404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


"""
#login usuario
{
  "person_id": 7,
  "nickname": "filip7",
  "name": "felipe7",
  "last_name": "torres7",
  "email": "felipe7@example.com"
}

"""
