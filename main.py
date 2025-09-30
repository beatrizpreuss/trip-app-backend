import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from data_manager import DataManager
from data_models import db

app = Flask(__name__)
CORS(app)

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

# THERE ARE NO USER ROUTES HERE
# @app.route('/', methods=['GET'])
# # """" Renders the home page # """"
# def index():
#     return render_template('index.html')


@app.route('/trips', methods=['GET'])
def get_all_trips():
    """ Retrieves and displays all trips. """
    trips = data_manager.get_trips()
    return jsonify([trip.to_dict() for trip in trips])


@app.route('/trips', methods=['POST'])
def create_trip():
    """Creates a new trip object, with the temporary name of New Trip, and saves it to the database. """
    trip_name = request.json.get("name", "New Trip")
    trip = data_manager.create_trip(trip_name)
    return jsonify({"trip": trip.to_dict()}), 201


@app.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    """Deletes an entire trip from the database. """
    data_manager.delete_trip(trip_id)
    return jsonify({"message": "Trip deleted", "trip_id": trip_id}), 200


@app.route('/trips/<int:trip_id>', methods=['GET'])
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


@app.route('/trips/<int:trip_id>', methods=['PUT'])
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

@app.route('/trips/<int:trip_id>/map', methods=['GET'])
# """" Displays the map of the trip with the specified ID, along with all
# the locations that were added to the map. # """"


@app.route('/destination-ideas', methods=['GET', 'POST'])
# """" On GET, renders the page. On POST, retrieves data from the questionnaire,
# runs the AI with the adapted prompt AND SAVES IT TO A AI-SUGGESTIONS DATABASE?# """"


@app.route('/destination-ideas/suggestions', methods=['GET'])
# """" Renders the page with the AI suggestions# """"


@app.route('/trips/<int:trip_id>/explore', methods=['GET'])
def get_explore_of_trip(trip_id):
    explore = data_manager.get_explore_by_trip(trip_id)
    return jsonify([expl.to_dict() for expl in explore])


@app.route('/trips/<int:trip_id>/stays', methods=['GET'])
def get_stays_of_trip(trip_id):
    stays = data_manager.get_stays_by_trip(trip_id)
    return jsonify([stay.to_dict() for stay in stays])


@app.route('/trips/<int:trip_id>/eat-drink', methods=['GET'])
def get_eat_drink_of_trip(trip_id):
    eat_drink = data_manager.get_eat_drink_by_trip(trip_id)
    return jsonify([eat.to_dict() for eat in eat_drink])


@app.route('/trips/<int:trip_id>/essentials', methods=['GET'])
def get_essentials_of_trip(trip_id):
    essentials = data_manager.get_essentials_by_trip(trip_id)
    return jsonify([essential.to_dict() for essential in essentials])


@app.route('/trips/<int:trip_id>/getting-around', methods=['GET'])
def get_getting_around_of_trip(trip_id):
    getting_around = data_manager.get_getting_around_by_trip(trip_id)
    return jsonify([around.to_dict() for around in getting_around])


@app.route('/trips/<int:trip_id>/suggestions', methods=['POST'])
def get_popup_answers(trip_id):
    """Receive json from the frontend"""
    initial_json = request.get_json()
    print(f"Received json from trip {trip_id}")
    return jsonify(initial_json), 201



if __name__ == "__main__":
    app.run(debug=True)