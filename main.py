import os
from flask import Flask
from data_models import db

app = Flask(__name__)

# Build absolute path to database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)

db.init_app(app)

# Used only to create the tables
# with app.app_context():
#     db.create_all()


@app.route('/', methods=['GET'])
""" Renders the home page """


@app.route('/plan-trips', methods=['GET', 'POST'])
""" On GET retrieves and displays all trips. On POST creates a new trip
 instance, with the temporary name of New Trip, and saves it to the database. """


@app.route('/plan-trips/<int:trip_id>', methods=['GET', 'POST', 'PUT'])
""" On GET retrieves and displays all tables from the trip with the specified ID.
On POST, retrieves new data from the forms, creates new instances for each table,
and saves them to the database. On PUT, updates all edited instances. 
HOW DOES IT ADD STUFF TO THE MAP?"""


@app.route('/plan-trips/<int:trip_id>/map', methods=['GET'])
""" Displays the map of the trip with the specified ID, along with all
the locations that were added to the map. """


@app.route('/destination-ideas', methods=['GET', 'POST'])
""" On GET, renders the page. On POST, retrieves data from the questionnaire,
runs the AI with the adapted prompt AND SAVES IT TO A AI-SUGGESTIONS DATABASE?"""


@app.route('/destination-ideas/suggestions', methods=['GET'])
""" Renders the page with the AI suggestions"""

