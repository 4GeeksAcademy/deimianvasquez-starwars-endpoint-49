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
from models import db, User, People, Planet, Favorite
import requests
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route("/people", methods=["GET"])
def get_people():
    people = People.query.all()

    return jsonify([item.serialize() for item in people]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_one_person(people_id=None):
    person = People.query.filter_by(id=people_id).first()

    if person is None:
        return jsonify("Users not found"), 404
    else:
        return jsonify(person.serialize()), 200


@app.route("/planet", methods=["GET"])
def get_planet():
    planet = Planet.query.all()

    return jsonify([item.serialize() for item in planet]), 200


@app.route("/planet/<int:planet_id>", methods=["GET"])
def get_one_planet(planet_id=None):
    planet = People.query.filter_by(id=planet_id).first()

    if planet is None:
        return jsonify("Users not found"), 404
    else:
        return jsonify(planet.serialize()), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()

    return jsonify(list(map(lambda item: item.serialize(), users))), 200


@app.route("/users/<int:user_id>",  methods=["GET"])
def get_favorites_user(user_id=None):
    # favorites = Favorite.query.filter_by(user_id=user_id).first()
    favorites = User.query.get(user_id)

    return jsonify(favorites.serialize()), 200


@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_planet(planet_id=None):
    body = request.json
    print(body)

    fav = Favorite()
    fav.user_id = body["user_id"]
    fav.planet_id = planet_id

    db.session.add(fav)
    try:
        db.session.commit()
        return jsonify("user saved succefull"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"message": f"Error: {error.args}"}), 500


@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_people(people_id=None):
    body = request.json
    print(body)

    fav = Favorite()
    fav.user_id = body["user_id"]
    fav.people_id = people_id

    db.session.add(fav)
    try:
        db.session.commit()
        return jsonify("user saved succefull"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"message": f"Error: {error.args}"}), 500


@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    """
    Elimina un favorito de tipo 'people' con el id especificado.
    """
    favorite = Favorite.query.filter_by(people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return {"message": "Favorite people deleted successfully"}, 200
    return {"message": "Favorite people not found"}, 404


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    """
    Elimina un favorito de tipo 'planet' con el id especificado.
    """
    favorite = Favorite.query.filter_by(planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return {"message": "Favorite planet deleted successfully"}, 200

    return {"message": "Favorite planet not found"}, 404


@app.route("/people-population", methods=["GET"])
def get_people_population():
    """
        Trae los people de swapi y a guarda en la base de datos
    """

    URL_PEOPLE = "https://www.swapi.tech/api/people?page=1&limit=30"
    response = requests.get(URL_PEOPLE)
    data = response.json()
    for item in data["results"]:
        response = requests.get(item["url"])
        person_data = response.json()
        person_data = person_data["result"]["properties"]
        person = People()
        person.name = person_data["name"]
        db.session.add(person)
    try:
        db.session.commit()
        return jsonify({"message": "People data saved successfully"}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"message": f"Error: {error.args}"}), 500

    return jsonify({"message": "This endpoint is not implemented yet"}), 501

    # this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

{'properties':
    {'created': '2025-06-06T06:15:57.809Z',
     'edited': '2025-06-06T06:15:57.809Z',
     'name': 'Luke Skywalker',
     'gender': 'male',
     'skin_color': 'fair', 'hair_color': 'blond', 'height': '172', 'eye_color': 'blue', 'mass': '77',
                'homeworld': 'https://www.swapi.tech/api/planets/1', 'birth_year': '19BBY', 'url': 'https://www.swapi.tech/api/people/1'}, '_id': '5f63a36eee9fd7000499be42', 'description': 'A person within the Star Wars universe', 'uid': '1', '__v': 2}
