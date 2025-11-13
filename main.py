import os, json
import re
from datetime import timedelta

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from functools import wraps  # Importing wraps

from data_manager import DataManager
from data_models import db, User

from services.overpass_service import fetch_overpass_results
from services.overpass_queries import (
    query_places_explore_outdoor,
    query_places_explore_indoor,
    query_stays,
    query_eat_drink,
    query_essentials,
    query_getting_around
)
from services.openai_service import get_selection_via_openai, \
    get_destination_suggestion, get_openai_tips

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
# Set access token expiration to 1 hour
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# Set refresh token expiration to 30 days
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)


# Build absolute path to database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)

db.init_app(app)

data_manager = DataManager()

# Used only to create the tables
# with app.app_context():
#     db.create_all()

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'admin':
            return jsonify(msg='You are not allowed to see this, you are not an admin!'), 403
        return fn(*args, **kwargs)
    return wrapper


@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()
    if user:
        user_dictionary = user.to_dict()
        if not user_dictionary or user_dictionary['password'] != password:
            return jsonify(msg="Bad email or password"), 401
    else:
        return jsonify({ 'msg': 'This user does not exist.'}), 500

    access_token = create_access_token(identity=str(user.user_id), additional_claims={"role": "user"})
    refresh_token = create_refresh_token(identity=str(user.user_id))
    return jsonify({"access_token": access_token, "refresh_token": refresh_token})


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if not username or not email or not password:
        return jsonify({'msg': 'Username, email and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'msg': 'Email already registered'}), 400

    new_user = data_manager.create_user(username, email, password)
    if not new_user:
        return jsonify({'msg': 'Error creating user'}), 500

    return jsonify({'msg': 'User created successfully'}), 201


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=str(user_id))
    return {"access_token": access_token}, 200


@app.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())  # this comes from the token
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({"error": "User not found"}), 404


@app.route("/me", methods=["PUT"])
@jwt_required()
def update_current_user():
    user_id = int(get_jwt_identity())  # this comes from the token
    user = User.query.get(user_id)
    if user:
        data = request.get_json()
        new_username = data.get("username")
        new_email = data.get("email")
        new_password = data.get("password")

        updated_user = data_manager.update_user(user_id, new_username, new_email, new_password)
        return jsonify(updated_user.to_dict())

    return jsonify({"error": "User not found"}), 404


@app.route('/trips', methods=['GET'])
@jwt_required()
def get_all_trips():
    """ Retrieves and displays all trips. """
    user_id = int(get_jwt_identity())
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify(msg="This user doesn't exist"), 401

    user_dictionary = user.to_dict()

    trips = data_manager.get_trips(user_dictionary["user_id"])
    return jsonify([trip.to_dict() for trip in trips])


@app.route('/trips', methods=['POST'])
@jwt_required()
def create_trip():
    """Creates a new trip object, with the temporary name of New Trip, and saves it to the database. """
    user_id = get_jwt_identity()
    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify(msg="Invalid user"), 401

    trip_name = request.json.get("name", "New Trip")
    trip = data_manager.create_trip(trip_name, user.user_id)
    return jsonify({"trip": trip.to_dict()}), 201


@app.route('/trips/<trip_id>', methods=['DELETE'])
@jwt_required()
def delete_trip(trip_id):
    """Deletes an entire trip from the database. """
    data_manager.delete_trip(trip_id)
    return jsonify({"message": "Trip deleted", "trip_id": trip_id}), 200


@app.route('/trips/<trip_id>', methods=['GET'])
@jwt_required()
def open_trip(trip_id):
    """ Retrieves and displays all tables from the trip with the specified ID. """
    trip = data_manager.open_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    explore = data_manager.get_explore_by_trip(trip_id)
    stays = data_manager.get_stays_by_trip(trip_id)
    eat_drink = data_manager.get_eat_drink_by_trip(trip_id)
    essentials = data_manager.get_essentials_by_trip(trip_id)
    getting_around = data_manager.get_getting_around_by_trip(trip_id)
    return jsonify({
        "trip": trip.to_dict(),
        "explore": [expl.to_dict() for expl in explore],
        "stays": [stay.to_dict() for stay in stays],
        "eat_drink": [eat.to_dict() for eat in eat_drink],
        "essentials": [essential.to_dict() for essential in essentials],
        "getting_around": [around.to_dict() for around in getting_around]
    })


@app.route('/trips/<trip_id>', methods=['PUT'])
@jwt_required()
def update_trip(trip_id):
    """Updates all data from the forms."""
    data = request.get_json()

    # Update trip name if provided
    new_name = data.get("name")
    trip = data_manager.update_trip(trip_id, new_name)
    if not trip:
        return jsonify({"error": "Trip not found or update failed"}), 404

    # Update or add eat&drink
    for eat_drink_data in data.get("eat_drink", []):
        eat_drink_id = eat_drink_data.get("id")
        if eat_drink_data.get("deleted"): # When the delete button for the row is clicked on the frontend, react will change delete state to true.
            data_manager.delete_eat_drink(eat_drink_id)
        elif eat_drink_id:
            data_manager.update_eat_drink(
                eat_drink_id=eat_drink_id,
                name=eat_drink_data.get("name"),
                coordinates=eat_drink_data.get("coordinates"),
                address=eat_drink_data.get("address"),
                day=eat_drink_data.get("day"),
                comments=eat_drink_data.get("comments"),
                external_url=eat_drink_data.get("external_url"),
            )
        else:
            data_manager.add_eat_drink(
                trip_id=trip_id,
                name=eat_drink_data.get("name"),
                coordinates=eat_drink_data.get("coordinates"),
                address=eat_drink_data.get("address"),
                day=eat_drink_data.get("day"),
                comments=eat_drink_data.get("comments"),
                external_url=eat_drink_data.get("external_url"),
            )

    # Update or add stays
    for stay_data in data.get("stays", []):
        stay_id = stay_data.get("id", None)
        if stay_data.get("deleted"): # When the delete button for the row is clicked on the frontend, react will change delete state to true.
            data_manager.delete_stay(stay_id)
        elif stay_id:
            data_manager.update_stay(
                stay_id=stay_id,
                name=stay_data.get("name"),
                coordinates=stay_data.get("coordinates"),
                address=stay_data.get("address"),
                day=stay_data.get("day"),
                price=stay_data.get("price"),
                status=stay_data.get("status"),
                comments=stay_data.get("comments"),
                external_url=stay_data.get("external_url"),
            )
        else:
            data_manager.add_stay(
                trip_id=trip_id,
                name=stay_data.get("name"),
                coordinates=stay_data.get("coordinates"),
                address=stay_data.get("address"),
                day=stay_data.get("day"),
                price=stay_data.get("price"),
                status=stay_data.get("status"),
                comments=stay_data.get("comments"),
                external_url=stay_data.get("external_url"),
            )

    # Update or add explore
    for explore_data in data.get("explore", []):
        explore_id = explore_data.get("id")
        if explore_data.get("deleted"): # When the delete button for the row is clicked on the frontend, react changes delete state to true.
            data_manager.delete_explore(explore_id)
        elif explore_id:
            data_manager.update_explore(
                explore_id=explore_id,
                name=explore_data.get("name"),
                coordinates=explore_data.get("coordinates"),
                address=explore_data.get("address"),
                day=explore_data.get("day"),
                price=explore_data.get("price"),
                comments=explore_data.get("comments"),
                external_url=explore_data.get("external_url"),
            )
        else:
            data_manager.add_explore(
                trip_id=trip_id,
                name=explore_data.get("name"),
                coordinates=explore_data.get("coordinates"),
                address=explore_data.get("address"),
                day=explore_data.get("day"),
                price=explore_data.get("price"),
                comments=explore_data.get("comments"),
                external_url=explore_data.get("external_url"),
            )

    # Update or add essentials
    for essentials_data in data.get("essentials", []):
        essentials_id = essentials_data.get("id")
        if essentials_data.get("deleted"):  # When the delete button for the row is clicked on the frontend, react changes delete state to true.
            data_manager.delete_essentials(essentials_id)
        elif essentials_id:
            data_manager.update_essentials(
                essentials_id=essentials_id,
                name=essentials_data.get("name"),
                coordinates=essentials_data.get("coordinates"),
                address=essentials_data.get("address"),
                day=essentials_data.get("day"),
                comments=essentials_data.get("comments"),
                external_url=essentials_data.get("external_url"),
            )
        else:
            data_manager.add_essentials(
                trip_id=trip_id,
                name=essentials_data.get("name"),
                coordinates=essentials_data.get("coordinates"),
                address=essentials_data.get("address"),
                day=essentials_data.get("day"),
                comments=essentials_data.get("comments"),
                external_url=essentials_data.get("external_url"),
            )

    # Update or add getting_around
    for getting_around_data in data.get("getting_around", []):
        getting_around_id = getting_around_data.get("id")
        if getting_around_data.get("deleted"):  # When the delete button for the row is clicked on the frontend, react changes delete state to true.
            data_manager.delete_getting_around(getting_around_id)
        elif getting_around_id:
            data_manager.update_getting_around(
                getting_around_id=getting_around_id,
                name=getting_around_data.get("name"),
                coordinates=getting_around_data.get("coordinates"),
                address=getting_around_data.get("address"),
                day=getting_around_data.get("day"),
                comments=getting_around_data.get("comments"),
                external_url=getting_around_data.get("external_url"),
            )
        else:
            data_manager.add_getting_around(
                trip_id=trip_id,
                name=getting_around_data.get("name"),
                coordinates=getting_around_data.get("coordinates"),
                address=getting_around_data.get("address"),
                day=getting_around_data.get("day"),
                comments=getting_around_data.get("comments"),
                external_url=getting_around_data.get("external_url"),
            )

    explore = data_manager.get_explore_by_trip(trip_id)
    stays = data_manager.get_stays_by_trip(trip_id)
    eat_drink = data_manager.get_eat_drink_by_trip(trip_id)
    essentials = data_manager.get_essentials_by_trip(trip_id)
    getting_around = data_manager.get_getting_around_by_trip(trip_id)

    return jsonify({
        "trip": trip.to_dict(),
        "explore": [expl.to_dict() for expl in explore],
        "stays": [stay.to_dict() for stay in stays],
        "eat_drink": [eat.to_dict() for eat in eat_drink],
        "essentials": [essential.to_dict() for essential in essentials],
        "getting_around": [around.to_dict() for around in getting_around]
        })

@app.route('/trips/<trip_id>/map', methods=['GET'])
# """" Displays the map of the trip with the specified ID, along with all
# the locations that were added to the map. # """"


@app.route('/find-destination', methods=['POST'])
def get_destination():
    """ On GET, renders the page. On POST, retrieves data from the questionnaire,
     runs the AI with the adapted prompt AND SAVES IT TO A AI-SUGGESTIONS DATABASE?# """

    # Step 1: Get JSON from frontend
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input received"}), 400

    # Step 2: Extract key fields
    location = data.get("location")
    goal = data.get("goal")
    interests = data.get("interests")
    length = data.get("length")
    fame = data.get("type")
    transport = data.get("transport")
    preferred = data.get("preferred")
    avoid = data.get("avoid")
    season = data.get("season")
    acc = data.get("acc")

    # Step 3: Call AI function to get suggestions of destinations
    try:
        destinations = get_destination_suggestion(location, goal, interests, fame, length, transport, preferred, avoid, season, acc)
        print("AI destinations suggestions:", destinations)
    except Exception as e:
        print("Error reaching OpenAI:", str(e))
        return jsonify({"error": "openai_unreachable"}), 502

    try:
        destination_suggestions = json.loads(destinations)
    except json.JSONDecodeError:
        # If GPT response isn't valid JSON, return it as-is for debugging
        return jsonify({"error": "Invalid JSON from OpenAI",
                        "raw": destinations}), 500

    return jsonify(destination_suggestions), 200


# DON'T NEED THIS ROUTE HERE IN THE BACKEND
# @app.route('/find-destination/suggestions', methods=['GET'])
# # """" Renders the page with the AI suggestions# """"


@app.route('/trips/<trip_id>/explore', methods=['GET'])
@jwt_required()
def get_explore_of_trip(trip_id):
    explore = data_manager.get_explore_by_trip(trip_id)
    return jsonify([expl.to_dict() for expl in explore])


@app.route('/trips/<trip_id>/stays', methods=['GET'])
@jwt_required()
def get_stays_of_trip(trip_id):
    stays = data_manager.get_stays_by_trip(trip_id)
    return jsonify([stay.to_dict() for stay in stays])


@app.route('/trips/<trip_id>/eat-drink', methods=['GET'])
@jwt_required()
def get_eat_drink_of_trip(trip_id):
    eat_drink = data_manager.get_eat_drink_by_trip(trip_id)
    return jsonify([eat.to_dict() for eat in eat_drink])


@app.route('/trips/<trip_id>/essentials', methods=['GET'])
@jwt_required()
def get_essentials_of_trip(trip_id):
    essentials = data_manager.get_essentials_by_trip(trip_id)
    return jsonify([essential.to_dict() for essential in essentials])


@app.route('/trips/<trip_id>/getting-around', methods=['GET'])
@jwt_required()
def get_getting_around_of_trip(trip_id):
    getting_around = data_manager.get_getting_around_by_trip(trip_id)
    return jsonify([around.to_dict() for around in getting_around])


@app.route('/trips/<trip_id>/suggestions', methods=['POST'])
@jwt_required()
def get_suggestions(trip_id):

    # Step 1: Get JSON from frontend
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input received"}), 400

    # Step 2: Extract key fields
    category = data.get("category")
    activity_type = data.get("activityType") # optional for places to explore
    cuisine = data.get("cuisine")  # optional for eat & drink
    style = data.get("style") # optional for stays
    type_answer = data.get("type") # optional for essentials and getting around
    lat = data.get("lat")
    lon = data.get("lon")
    radius = data.get("radius", 2000)  # default to 2km if not provided
    # print("Lat: ", lat, "Lon: ", lon, "Radius: ", radius)

    # Step 3: Select correct query function
    if category == "explore" and activity_type == "Outdoor":
        my_query = query_places_explore_outdoor(lat, lon, radius)
    elif category == "explore" and activity_type == "Indoor":
        my_query = query_places_explore_indoor(lat, lon, radius)
    elif category == "stays":
        my_query = query_stays(lat, lon, radius, style)
    elif category == "eatDrink":
        my_query = query_eat_drink(lat, lon, radius, cuisine)
    elif category == "essentials":
        my_query = query_essentials(lat, lon, radius, type_answer)
    elif category == "gettingAround":
        my_query = query_getting_around(lat, lon, radius, type_answer)
    else:
        return jsonify({"error": "No matching query found"}), 400

    # Step 4: Fetch results from overpass
    try:
        print("Query:" , my_query)
        results = fetch_overpass_results(my_query)

    except Exception as e:
        app.logger.exception("Overpass fetch failed")
        return jsonify({"error": str(e)}), 500

    # if results come back empty, return the error message
    if "elements" not in results:
        error_msg = results.get("error", "No elements returned")
        return jsonify({"error": error_msg}), 502

    # Step 5: Fetch all existing places for this trip
    explore = data_manager.get_explore_by_trip(trip_id)
    stays = data_manager.get_stays_by_trip(trip_id)
    eat_drink = data_manager.get_eat_drink_by_trip(trip_id)
    essentials = data_manager.get_essentials_by_trip(trip_id)
    getting_around = data_manager.get_getting_around_by_trip(trip_id)

    # Combine into a single list of dicts with name + lat/lon
    existing_markers = []
    for item_list in [explore, stays, eat_drink, essentials, getting_around]:
        for item in item_list:
            if item.coordinates is not None:
                existing_markers.append({
                    "name": item.name,
                    "lat": float(item.coordinates.split(",")[0].strip()),
                    "lon": float(item.coordinates.split(",")[1].strip())
            })

    # Simple filtering of results based on existing markers (so I don't get suggested what's already in my trip)
    precision = 6  # rounding to avoid tiny floating point differences

    existing_coordinates = {(round(marker['lat'], precision), round(marker['lon'], precision)) for marker in existing_markers}

    filtered_elements = []

    # make sure the element has lat and lon (even when it has a center - which is displayed differently)
    print(len(results["elements"])) # see how many elements overpass returned
    for el in results['elements']:
        if el.get("nodes"):
            del el["nodes"]
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat and lon:
            if (round(lat, precision), round(lon, precision)) not in existing_coordinates: # check if is already existent in my markers
                el["lat"] = lat
                el["lon"] = lon
                filtered_elements.append(el)
    print("Filtered elements: ", filtered_elements)
        # else:
            # print(f"Skipping element with missing coordinates: {el}")

    # Step 6: Call AI function to make the selection of the most relevant results
    try:
        top_selection_text = get_selection_via_openai(data, filtered_elements)

    except Exception as e:
        print("Error reaching OpenAI:", str(e))
        return jsonify({"error": "openai_unreachable"}), 502

    try:
        clean_text = re.sub(r"^```(?:json)?|```$", "", top_selection_text.strip(), flags=re.MULTILINE)
        top_selection = json.loads(clean_text)

        print("AI selection:", len(top_selection))

    except json.JSONDecodeError:
        # If GPT response isn't valid JSON, return it as-is for debugging
        return jsonify(
            {"error": "Invalid JSON from OpenAI", "raw": clean_text}), 500

    return jsonify(top_selection), 200


@app.route('/trips/<trip_id>/tips', methods=['GET'])
@jwt_required()
def get_travel_tips(trip_id):

    # Step 1: Fetch all existing places for this trip
    explore = data_manager.get_explore_by_trip(trip_id)
    stays = data_manager.get_stays_by_trip(trip_id)
    eat_drink = data_manager.get_eat_drink_by_trip(trip_id)
    essentials = data_manager.get_essentials_by_trip(trip_id)
    getting_around = data_manager.get_getting_around_by_trip(trip_id)

    # Combine into a single list of dicts with name + lat/lon
    existing_markers = []
    for item_list in [explore, stays, eat_drink, essentials, getting_around]:
        for item in item_list:
            if item.coordinates is not None:
                existing_markers.append({
                    "name": item.name,
                    "lat": float(item.coordinates.split(",")[0].strip()),
                    "lon": float(item.coordinates.split(",")[1].strip())
            })

    # Step 2: Call AI function to create tips based on existing markers
    try:
        trip_tips = get_openai_tips(existing_markers)

    except Exception as e:
        print("Error reaching OpenAI:", str(e))
        return jsonify({"error": "openai_unreachable"}), 502

    try:
        clean_text = re.sub(r"^```(?:json)?|```$", "", trip_tips.strip(), flags=re.MULTILINE)
        tips = json.loads(clean_text)

    except json.JSONDecodeError:
        # If GPT response isn't valid JSON, return it as-is for debugging
        return jsonify(
            {"error": "Invalid JSON from OpenAI", "raw": clean_text}), 500

    return jsonify(tips), 200


if __name__ == "__main__":
    app.run(debug=True)