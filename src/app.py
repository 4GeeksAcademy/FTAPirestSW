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

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/person',methods=['GET'])
def get_all_person():
    raw_list_person = Person.query.all()
    list_person=[person.serialize_with_relations()
                 for person in raw_list_person]
    return jsonify({"list_persons":list_person})



@app.route('/persons',methods=["GET"])
def get_all_accounts():
    raw_list_persons = Person.query.all()
    list_persons = [persons.serialize_with_relations()
                      for persons in raw_list_persons]
    return jsonify({"list_persons":list_persons})


@app.route('/person',methods=['POST'])
def create_person():
    data_request=request.get_json()
    if  not "persons_id" in data_request:
        return jsonify({"error":"los datos: person_id son obligatorios"}),400
    
    person_id=data_request["persons_id"]
    person=Person.query.get(person_id)
    if not person:
        return jsonify({"error": f"la persona con el id {person_id} no esta en la base de datos"}),404
    
    new_person=Person(
        persons_id=data_request["persons_id"]
        )
    
    try:
        db.session.add(new_person)
        db.session.commit()
        return jsonify({"message":"Cuenta creada con exito"})
    except Exception as e:
        db.session.rollback()
        print("Error",e)
        return jsonify({"error":"Hubo un error en el servidor"})



#@app.route('/favorite',methods=['POST'])
#def create_favorities():
#    data_request=request.get_json()
#    if not "name" in data_request or not "name" in data_request  
#    print(data_request)
#    return "ok",200


@app.route('/favorities',methods=['GET'])
def get_all_favorities():
    raw_list_favorities = Favorite.query.all()
    list_favorite=[favorite.serialize() for favorite in raw_list_favorities]
    return jsonify({'favorities': list_favorite})

@app.route('/favorities/register', methods=['POST'])
def register_favorities():
    data_request = request.get_json()
    
    if not "person_id" in data_request:
        return jsonify({"Error": " los siguientes campos son importantes: person_id"}),400
    
    if not  any(f in data_request for f in ["character_id","planet_id","vehicle_id"]):
        return jsonify({"error": "uno de estos campos son obligatorios:character_id,planet_id,vehicle_id "}),400

    person=Person.query.get(data_request["person_id"])
    if not person:
        return jsonify({"error":"persona no  encontrada en la base de datos"}),404
    
    character_id = data_request.get("character_id")
    planet_id = data_request.get("planet_id")
    vehicle_id = data_request.get("vehicle_id")

    character=Character.query.get(character_id) if character_id else None
    planet=Planet.query.get(planet_id) if planet_id else None
    vehicle=Vehicle.query.get(vehicle_id) if vehicle_id else None

    if character_id and not character:
        return jsonify({"error":"character no encontrado"}),404
    if planet_id and not planet:
        return jsonify({"error":"planet no encontrado"}),404
    if vehicle_id and not vehicle:
        return jsonify({"error":"vehicle no encontrado"}),404
    

    favorite_existing = Favorite.query.filter_by(
        person_id= person.person_id,
        character_id=character.character_id if character else None,
        planet_id = planet.planet_id if planet else None,
        vehicle_id= vehicle.vehicle_id if vehicle else None,
    ).first()

    if favorite_existing:
        return jsonify({"error":"este favorito ya esta resgitrado"}),409

    favorite = Favorite(
        person_id=person.person_id,
        character_id=character.character_id if character else None,
        planet_id=planet.planet_id if planet else None,
        vehicle_id=vehicle.vehicle_id if vehicle else None
    )

    
    try:
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"message":"favorito creado  con exito"}),201
    except Exception as e:
        db.session.rollback()
        print("Error",e)
        return jsonify({"error":"Hubo un error en el servidor"}),500

    
    return "ok",200

@app.route('/character',methods=['GET'])
def get_all_character():
    raw_list_character = Character.query.all()
    list_character=[character.serialize() for character in raw_list_character]
    return jsonify({'characters': list_character})

@app.route('/characters/<int:id>',methods=['GET'])
def get_character_id(id):
    character = Character.query.get(id)
    print(character)
    if character:
        return jsonify(character.serialize_with_relations())
    else:
        return jsonify({"error": "character no econtrado"}),404

@app.route('/vehicle',methods=['GET'])
def get_all_vehicle():
    raw_list_vehicle = Vehicle.query.all()
    list_vehicle=[vehicle.serialize() for vehicle in raw_list_vehicle]
    return jsonify({'vehicles': list_vehicle})

@app.route('/planets',methods=['GET'])
def get_all_planet():
    raw_list_planet = Planet.query.all()
    list_planets=[planet.serialize() for planet in raw_list_planet]
    return jsonify({'planets': list_planets})

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
