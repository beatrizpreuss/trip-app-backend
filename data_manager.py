from sqlalchemy.exc import SQLAlchemyError

from data_models import db, User, Trip, PointOfInterest, Accommodation, Food


class DataManager():

    # USER FUNCTIONS
    # Will user functions be needed after implementation of authentication?

    def create_user(self, email, password):
        """Create and save a new user to the database.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            User: The newly created User object if successful.
            None: If an error occurred.
        """
        new_user = User(email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            print("A database error occurred:", str(e))
        except Exception as e:
            db.session.rollback()
            print("An unexpected error occurred:", str(e))
        return None


    def get_users(self):
        """Retrieve all users from the database.

        Returns:
            list[User]: A list of User objects.
            None: If an error occurred.
        """
        try:
            users = User.query.all()
            return users
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_user(self, user_id):
        """Retrieve a single user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The User object if found.
            None: If the user does not exist or an error occurred.
        """
        try:
            return User.query.get(user_id)
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def delete_user(self, user_id):
        """
        Deletes a user from the database by their user ID.

        Args:
            user_id (int): The unique identifier of the user to delete.

        Returns:
            bool: True if a user was successfully deleted, False otherwise.
        """
        try:
            user_deleted = User.query.filter(User.id == user_id).delete()
            db.session.commit()
            return user_deleted > 0 # returns True if a user was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting user: ", str(e))
            return False


    # TRIP FUNCTIONS

    def create_trip(self, name):
        """Create and save a new trip to the database.

        Args:
            name (str): The name of the trip.

        Returns:
            Trip: The newly created trip object if successful.
            None: If an error occurred.
        """
        new_trip = Trip(name=name)
        try:
            db.session.add(new_trip)
            db.session.commit()
            return new_trip
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating trip: ", str(e))


    def get_trips(self):
        """Retrieve all trips from the database.

        Returns:
            list[Trip]: A list of Trip objects.
            None: If an error occurred.
        """
        try:
            trips = Trip.query.all()
            return trips
        except SQLAlchemyError as e:
            print("A database error occurred: ", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def open_trip(self, trip_id):
        """Retrieve a single trip by its ID.

        Args:
            trip_id (int): The ID of the trip.

        Returns:
            Trip: The Trip object if found.
            None: If the user does not exist or an error occurred.
        """
        try:
            return Trip.query.get(trip_id)
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def update_trip(self, trip_id, new_name):
        """Update an existing trip's name.

        Args:
            trip_id (int): The ID of the trip to update.
            new_name (str): New trip name to update.

        Returns:
            Trip: The updated trip object if successful.
            None: If the trip is not found or an error occurred.
        """
        trip = Trip.query.get(trip_id)
        if not trip:
            return None
        if new_name:
            trip.name = new_name
        try:
            db.session.commit()
            return trip
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating trip: ", str(e))
            return None


    def delete_trip(self, trip_id):
        """
        Deletes a trip from the database by its ID.

        Args:
            trip_id (int): The unique identifier of the trip to delete.

        Returns:
            bool: True if a trip was successfully deleted, False otherwise.
        """
        try:
            trip_deleted = Trip.query.filter(Trip.id == trip_id).delete()
            db.session.commit()
            return trip_deleted > 0 # returns True if a user was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting user: ", str(e))
            return False


    # POINTS OF INTEREST FUNCTIONS
    # Shouldn't they be added/updated all at once everytime instead of one at a time?
    # Should there be a delete option or just update?

    def get_points_of_interest(self):
        """Retrieve all points of interest from the database.

        Returns:
            list[Point of Interest]: A list of Point of Interest objects.
            None: If an error occurred.
        """
        try:
            points_of_interest = PointOfInterest.query.all()
            return points_of_interest
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_points_of_interest_by_trip(self, trip_id):
        """Retrieve all points of interest from a specific trip in the database.

        Returns:
            list[Points of Interest]: A list of point_of_interest objects.
            None: If an error occurred.
        """
        try:
            points_of_interest = PointOfInterest.query.filter_by(trip_id=trip_id).all()
            return points_of_interest
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_point_of_interest(self, trip_id, name, lat_long, address, price, comment, external_url):
        """Create and save a new point of interest to the database.

        Args:
            name (str): The name of the point of interest.
            lat_long (str): The latitude and longitude of the point of interest.
            address (str): The address of the point of interest.
            price (str): The price of the point of interest (e.g. entry fee).
            comment (str): Any comments pertaining that point of interest.
            external_url (str): Link to related website (e.g. buy tickets).

        Returns:
            Point of interest: The newly created point of interest object if successful.
            None: If an error occurred.
        """
        new_point_of_interest = PointOfInterest(
            trip_id=trip_id,
            name=name,
            lat_long=lat_long,
            address=address,
            price=price,
            comment=comment,
            external_url=external_url)
        try:
            db.session.add(new_point_of_interest)
            db.session.commit()
            return new_point_of_interest
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating point of interest: ", str(e))


    def update_point_of_interest(self, point_of_interest_id, new_name, lat_long, address, price, comment, external_url):
        """Update an existing point of interest's details.

        Args:
            point_of_interest_id (int): The ID of the point of interest to update.
            new_name (str): New point of interest name to update.
            lat_long (str): New latitude and longitude to update.
            address (str): New point of interest address to update.
            price (str): New point of interest price to update.
            comment (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            Point of interest: The updated point of interest object if successful.
            None: If the point of interest is not found or an error occurred.
        """
        point_of_interest = PointOfInterest.query.get(point_of_interest_id)
        if not point_of_interest:
            return None
        if new_name:
            point_of_interest.name = new_name
        if lat_long:
            point_of_interest.lat_long = lat_long
        if address:
            point_of_interest.address = address
        if price:
            point_of_interest.price = price
        if comment:
            point_of_interest.comment = comment
        if external_url:
            point_of_interest.external_url = external_url
        try:
            db.session.commit()
            return point_of_interest
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating point of interest: ", str(e))
            return None


    def delete_point_of_interest(self, point_of_interest_id):
        """
        Deletes a point of interest from the database by its ID.

        Args:
            point_of_interest_id (int): The unique identifier of the point of interest to delete.

        Returns:
            bool: True if a point of interest was successfully deleted, False otherwise.
        """
        try:
            point_of_interest_deleted = PointOfInterest.query.filter(PointOfInterest.id == point_of_interest_id).delete()
            db.session.commit()
            return point_of_interest_deleted > 0 # returns True if a movie was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting point of interest: ", str(e))
            return False


    # ACCOMMODATION FUNCTIONS

    def get_accommodations(self):
        """Retrieve all accommodations from the database.

        Returns:
            list[Accommodation]: A list of Accommodation objects.
            None: If an error occurred.
        """
        try:
            accommodations = Accommodation.query.all()
            return accommodations
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_accommodations_by_trip(self, trip_id):
        """Retrieve all accommodations from a specific trip in the database.

        Returns:
            list[Accommodation]: A list of accommodation objects.
            None: If an error occurred.
        """
        try:
            accommodations = Accommodation.query.filter_by(trip_id=trip_id).all()
            return accommodations
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_accommodation(self, trip_id, acc_type, lat_long, address, price, status, comment, external_url):
        """Create and save new accommodation to the database.

        Args:
            acc_type (str): The type of accommodation (e.g. hotel, camping).
            lat_long (str): The latitude and longitude of the accommodation.
            address (str): The address of the accommodation.
            price (str): The price of the accommodation.
            status (str): The status of the accommodation (e.g. paid, reserved).
            comment (str): Any comments pertaining that accommodation.
            external_url (str): Link to related website (e.g. reservation confirmation).

        Returns:
            Point of interest: The newly created point of interest object if successful.
            None: If an error occurred.
        """
        new_accommodation = Accommodation(
            trip_id=trip_id,
            type=acc_type,
            lat_long=lat_long,
            address=address,
            price=price,
            status=status,
            comment=comment,
            external_url=external_url)
        try:
            db.session.add(new_accommodation)
            db.session.commit()
            return new_accommodation
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating accommodation: ", str(e))


    def update_accommodation(self, accommodation_id, acc_type, lat_long, address, price, status, comment, external_url):
        """Update an existing accommodation's details.

        Args:
            accommodation_id (int): The ID of the accommodation to update.
            acc_type (str): New accommodation type to update.
            lat_long (str): New latitude and longitude to update.
            address (str): New address to update.
            price (str): New price to update.
            status (str): New status to update
            comment (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            Accommodation: The updated accommodation object if successful.
            None: If the accommodation is not found or an error occurred.
        """
        accommodation = Accommodation.query.get(accommodation_id)
        if not accommodation:
            return None
        if acc_type:
            accommodation.type = acc_type
        if lat_long:
            accommodation.lat_long = lat_long
        if address:
            accommodation.address = address
        if price:
            accommodation.price = price
        if status:
            accommodation.status = status
        if comment:
            accommodation.comment = comment
        if external_url:
            accommodation.external_url = external_url
        try:
            db.session.commit()
            return accommodation
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating accommodation: ", str(e))
            return None


    def delete_accommodation(self, accommodation_id):
        """
        Deletes accommodation from the database by its ID.

        Args:
            accommodation_id (int): The unique identifier of the accommodation to delete.

        Returns:
            bool: True if an accommodation object was successfully deleted, False otherwise.
        """
        try:
            accommodation_deleted = Accommodation.query.filter(Accommodation.id == accommodation_id).delete()
            db.session.commit()
            return accommodation_deleted > 0 # returns True if a movie was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting accommodation: ", str(e))
            return False


    # FOOD FUNCTIONS

    def get_foods(self):
        """Retrieve all food from the database.

        Returns:
            list[Food]: A list of food objects.
            None: If an error occurred.
        """
        try:
            foods = Food.query.all()
            return foods
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_foods_by_trip(self, trip_id):
        """Retrieve all food from a specific trip in the database.

        Returns:
            list[Food]: A list of food objects.
            None: If an error occurred.
        """
        try:
            foods = Food.query.filter_by(trip_id=trip_id).all()
            return foods
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_food(self, trip_id, food_type, lat_long, address, comment, external_url):
        """Create and save new food to the database.

        Args:
            food_type (str): The type of food place (e.g. restaurant, supermarket).
            lat_long (str): The latitude and longitude of the food place.
            address (str): The address of the food place.
            comment (str): Any comments pertaining that food place.
            external_url (str): Link to related website (e.g. restaurant's menu).

        Returns:
            Food: The newly created food object if successful.
            None: If an error occurred.
        """
        new_food = Food(
            trip_id=trip_id,
            type=food_type,
            lat_long=lat_long,
            address=address,
            comment=comment,
            external_url=external_url)
        try:
            db.session.add(new_food)
            db.session.commit()
            return new_food
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating food: ", str(e))


    def update_food(self, food_id, food_type, lat_long, address, comment, external_url):
        """Update an existing food's details.

        Args:
            food_id (int): The ID of the food to update.
            food_type (str): New food type to update.
            lat_long (str): New latitude and longitude to update.
            address (str): New address to update.
            comment (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            Food: The updated food object if successful.
            None: If the food object is not found or an error occurred.
        """
        food = Food.query.get(food_id)
        if not food:
            return None
        if food_type:
            food.type = food_type
        if lat_long:
            food.lat_long = lat_long
        if address:
            food.address = address
        if comment:
            food.comment = comment
        if external_url:
            food.external_url = external_url
        try:
            db.session.commit()
            return food
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating food: ", str(e))
            return None


    def delete_food(self, food_id):
        """
        Deletes food from the database by its ID.

        Args:
            food_id (int): The unique identifier of the food to delete.

        Returns:
            bool: True if a food object was successfully deleted, False otherwise.
        """
        try:
            food_deleted = Food.query.filter(
                Food.id == food_id).delete()
            db.session.commit()
            return food_deleted > 0  # returns True if a movie was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting food: ", str(e))
            return False