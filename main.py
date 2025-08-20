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


@app.route('/trips/<int:trip_id>', methods=['GET'])
def open_trip(trip_id):
    """ Retrieves and displays all tables from the trip with the specified ID. """
    trip = data_manager.open_trip(trip_id)
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    pois = data_manager.get_points_of_interest_by_trip(trip_id)
    accommodations = data_manager.get_accommodations_by_trip(trip_id)
    foods = data_manager.get_foods_by_trip(trip_id)
    return jsonify({
        "trip": trip.to_dict(),
        "points_of_interest": [poi.to_dict() for poi in pois],
        "accommodations": [acc.to_dict() for acc in accommodations],
        "foods": [food.to_dict() for food in foods]
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

    # Update or add foods
    for food_data in data.get("foods", []):
        food_id = food_data.get("id")
        if food_id and food_data.get("deleted"): # When the delete button for the row is clicked on the frontend, react will change delete state to true.
            data_manager.delete_food(food_id)
        elif food_id:
            data_manager.update_food(
                food_id=food_id,
                food_type=food_data.get("type"),
                lat_long=food_data.get("lat_long"),
                address=food_data.get("address"),
                comment=food_data.get("comment"),
                external_url=food_data.get("external_url"),
            )
        else:
            data_manager.add_food(
                trip_id=trip_id,
                food_type=food_data.get("type"),
                lat_long=food_data.get("lat_long"),
                address=food_data.get("address"),
                comment=food_data.get("comment"),
                external_url=food_data.get("external_url"),
            )

    # Update or add accommodations
    for acc_data in data.get("accommodations", []):
        acc_id = acc_data.get("id")
        if acc_id and acc_data.get("deleted"): # When the delete button for the row is clicked on the frontend, react will change delete state to true.
            data_manager.delete_accommodation(acc_id)
        elif acc_id:
            data_manager.update_accommodation(
                accommodation_id=acc_id,
                acc_type=acc_data.get("type"),
                lat_long=acc_data.get("lat_long"),
                address=acc_data.get("address"),
                price=acc_data.get("price"),
                status=acc_data.get("status"),
                comment=acc_data.get("comment"),
                external_url=acc_data.get("external_url"),
            )
        else:
            data_manager.add_accommodation(
                trip_id=trip_id,
                acc_type=acc_data.get("type"),
                lat_long=acc_data.get("lat_long"),
                address=acc_data.get("address"),
                price=acc_data.get("price"),
                status=acc_data.get("status"),
                comment=acc_data.get("comment"),
                external_url=acc_data.get("external_url"),
            )

    # Update or add points of interest
    for poi_data in data.get("points_of_interest", []):
        poi_id = poi_data.get("id")
        if poi_id and poi_data.get("deleted"): # When the delete button for the row is clicked on the frontend, react changes delete state to true.
            data_manager.delete_point_of_interest(poi_id)
        if poi_id:
            data_manager.update_point_of_interest(
                point_of_interest_id=poi_id,
                new_name=poi_data.get("name"),
                lat_long=poi_data.get("lat_long"),
                address=poi_data.get("address"),
                price=poi_data.get("price"),
                comment=poi_data.get("comment"),
                external_url=poi_data.get("external_url"),
            )
        else:
            data_manager.add_point_of_interest(
                trip_id=trip_id,
                name=poi_data.get("name"),
                lat_long=poi_data.get("lat_long"),
                address=poi_data.get("address"),
                price=poi_data.get("price"),
                comment=poi_data.get("comment"),
                external_url=poi_data.get("external_url"),
            )

    return jsonify({"message": "Trip and related data updated successfully"})


@app.route('/trips/<int:trip_id>/map', methods=['GET'])
# """" Displays the map of the trip with the specified ID, along with all
# the locations that were added to the map. # """"


@app.route('/destination-ideas', methods=['GET', 'POST'])
# """" On GET, renders the page. On POST, retrieves data from the questionnaire,
# runs the AI with the adapted prompt AND SAVES IT TO A AI-SUGGESTIONS DATABASE?# """"


@app.route('/destination-ideas/suggestions', methods=['GET'])
# """" Renders the page with the AI suggestions# """"


@app.route('/trips/<int:trip_id>/points-of-interest', methods=['GET'])
def get_points_of_interest_of_trip(trip_id):
    pois = data_manager.get_points_of_interest_by_trip(trip_id)
    return jsonify([poi.to_dict() for poi in pois])


@app.route('/trips/<int:trip_id>/accommodations', methods=['GET'])
def get_accommodations_of_trip(trip_id):
    accommodations = data_manager.get_accommodations_by_trip(trip_id)
    return jsonify([accommodation.to_dict() for accommodation in accommodations])


@app.route('/trips/<int:trip_id>/foods', methods=['GET'])
def get_foods_of_trip(trip_id):
    foods = data_manager.get_foods_by_trip(trip_id)
    return jsonify([food.to_dict() for food in foods])


#in the route, when I get a trip, I get everything from that trip (foods, etc)


if __name__ == "__main__":
    app.run(debug=True)