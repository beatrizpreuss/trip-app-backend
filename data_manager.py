from sqlalchemy.exc import SQLAlchemyError
import uuid
from data_models import db, User, Trip, Stay, Explore, EatDrink, Essentials, GettingAround


class DataManager():

    def create_user(self, username, email, password):
        """Create and save a new user to the database.

        Args:
            username (str): The username of the user.
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            User: The newly created User object if successful.
            None: If an error occurred.
        """
        new_user = User(username=username, email=email, password=password)
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


    def update_user(self, user_id, username, email, password, ):
        """Update an existing user.

        Args:
            user_id (int): The ID of the user.
            username (str): New username to update.
            email (str): New email to update.
            password (str): New password to update.

        Returns:
            User: The updated user object if successful.
            None: If the user is not found or an error occurred.
        """
        user = User.query.get(user_id)
        if not user:
            return None
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = password
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating user: ", str(e))
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
            user_deleted = User.query.filter(User.user_id == user_id).delete()
            db.session.commit()
            return user_deleted > 0 # returns True if a user was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting user: ", str(e))
            return False


    # TRIP FUNCTIONS

    def create_trip(self, name, user_id):
        """Create and save a new trip to the database.

        Args:
            name (str): The name of the trip.

        Returns:
            Trip: The newly created trip object if successful.
            None: If an error occurred.
        """
        new_trip = Trip(id=str(uuid.uuid4()), name=name, user_id=user_id)
        try:
            db.session.add(new_trip)
            db.session.commit()
            return new_trip
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating trip: ", str(e))
            raise


    def get_trips(self, user_id):
        """Retrieve all trips from the database.

        Returns:
            list[Trip]: A list of Trip objects.
            None: If an error occurred.
        """
        try:
            trips = Trip.query.filter_by(user_id=user_id).all()
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


    def update_trip(self, trip_id, name):
        """Update an existing trip's name.

        Args:
            trip_id (int): The ID of the trip to update.
            name (str): New trip name to update.

        Returns:
            Trip: The updated trip object if successful.
            None: If the trip is not found or an error occurred.
        """
        trip = Trip.query.get(trip_id)
        if not trip:
            return None
        if name:
            trip.name = name
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


    # EXPLORE FUNCTIONS
    # Shouldn't they be added/updated all at once everytime instead of one at a time?
    # Should there be a delete option or just update?

    def get_explore(self):
        """Retrieve all places to explore from the database.

        Returns:
            list[Explore]: A list of Explore objects.
            None: If an error occurred.
        """
        try:
            explore = Explore.query.all()
            return explore
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_explore_by_trip(self, trip_id):
        """Retrieve all places to explore from a specific trip in the database.

        Returns:
            list[Explore]: A list of explore objects.
            None: If an error occurred.
        """
        try:
            explore = Explore.query.filter_by(trip_id=trip_id).all()
            return explore
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_explore(self, trip_id, name, coordinates, address, day, price, comments, external_url):
        """Create and save a new place to explore to the database.

        Args:
            name (str): The name of the place to explore.
            coordinates (str): The latitude and longitude of the place to explore.
            address (str): The address of the place to explore.
            day (array): The day(s) on which this point will be used during the trip.
            price (str): The price of the place to explore (e.g. entry fee).
            comments (str): Any comments pertaining that place to explore.
            external_url (str): Link to related website (e.g. buy tickets).

        Returns:
            Explore: The newly created place to explore object if successful.
            None: If an error occurred.
        """
        new_explore = Explore(
            trip_id=trip_id,
            name=name,
            coordinates=coordinates,
            address=address,
            day=day,
            price=price,
            comments=comments,
            external_url=external_url)
        try:
            db.session.add(new_explore)
            db.session.commit()
            return new_explore
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating place to explore: ", str(e))


    def update_explore(self, explore_id, name, coordinates, address, day, price, comments, external_url):
        """Update an existing place to explore details.

        Args:
            explore_id (int): The ID of the explore place to update.
            name (str): New explore place name to update.
            coordinates (str): New latitude and longitude to update.
            address (str): New explore address to update.
            day (array): The day(s) on which this point will be used during the trip.
            price (str): New explore price to update.
            comments (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            Explore: The updated place to explore object if successful.
            None: If the explore place is not found or an error occurred.
        """
        explore = Explore.query.get(explore_id)
        if not explore:
            return None
        if name:
            explore.name = name
        if coordinates:
            explore.coordinates = coordinates
        if address:
            explore.address = address
        if day:
            explore.day = day
        if price:
            explore.price = price
        if comments:
            explore.comments = comments
        if external_url:
            explore.external_url = external_url
        try:
            db.session.commit()
            return explore
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating place to explore: ", str(e))
            return None


    def delete_explore(self, explore_id):
        """
        Deletes a place to explore from the database by its ID.

        Args:
            explore_id (int): The unique identifier of the explore place to delete.

        Returns:
            bool: True if an explore was successfully deleted, False otherwise.
        """
        try:
            explore_deleted = Explore.query.filter(Explore.id == explore_id).delete()
            db.session.commit()
            return explore_deleted > 0 # returns True if an item was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting place to explore: ", str(e))
            return False


    # STAY FUNCTIONS

    def get_stays(self):
        """Retrieve all stays from the database.

        Returns:
            list[Stay]: A list of Stay objects.
            None: If an error occurred.
        """
        try:
            stays = Stay.query.all()
            return stays
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_stays_by_trip(self, trip_id):
        """Retrieve all stays from a specific trip in the database.

        Returns:
            list[Stay]: A list of stay objects.
            None: If an error occurred.
        """
        try:
            stays = Stay.query.filter_by(trip_id=trip_id).all()
            return stays
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_stay(self, trip_id, name, coordinates, address, day, price, status, comments, external_url):
        """Create and save new stay to the database.

        Args:
            name (str): The name of the stay (e.g. hotel..., camping...).
            coordinates (str): The latitude and longitude of the stay.
            address (str): The address of the stay.
            price (str): The price of the stay.
            day (array): The day(s) on which this point will be used during the trip.
            status (str): The status of the stay (e.g. paid, reserved).
            comments (str): Any comments pertaining that stay.
            external_url (str): Link to related website (e.g. reservation confirmation).

        Returns:
            Stay: The newly created stay object if successful.
            None: If an error occurred.
        """
        new_stay = Stay(
            trip_id=trip_id,
            name=name,
            coordinates=coordinates,
            address=address,
            day=day,
            price=price,
            status=status,
            comments=comments,
            external_url=external_url)
        try:
            db.session.add(new_stay)
            db.session.commit()
            return new_stay
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating stay: ", str(e))


    def update_stay(self, stay_id, name, coordinates, address, day, price, status, comments, external_url):
        """Update an existing stay's details.

        Args:
            stay_id (int): The ID of the stay to update.
            name (str): New stay type to update.
            coordinates (str): New latitude and longitude to update.
            address (str): New address to update.
            day (array): The day(s) on which this point will be used during the trip.
            price (str): New price to update.
            status (str): New status to update
            comments (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            Stay: The updated stay object if successful.
            None: If the stay is not found or an error occurred.
        """
        stay = Stay.query.get(stay_id)
        if not stay:
            return None
        if name:
            stay.name = name
        if coordinates:
            stay.coordinates = coordinates
        if address:
            stay.address = address
        if day:
            stay.day = day
        if price:
            stay.price = price
        if status:
            stay.status = status
        if comments:
            stay.comments = comments
        if external_url:
            stay.external_url = external_url
        try:
            db.session.commit()
            return stay
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating stay: ", str(e))
            return None


    def delete_stay(self, stay_id):
        """
        Deletes stay from the database by its ID.

        Args:
            stay_id (int): The unique identifier of the stay to delete.

        Returns:
            bool: True if a stay object was successfully deleted, False otherwise.
        """
        try:
            stay_deleted = Stay.query.filter(Stay.id == stay_id).delete()
            db.session.commit()
            return stay_deleted > 0 # returns True if an item was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting stay: ", str(e))
            return False


    # EAT&DRINK FUNCTIONS

    def get_eat_drink(self):
        """Retrieve all eat&drink objects from the database.

        Returns:
            list[EatDrink]: A list of eat&drink objects.
            None: If an error occurred.
        """
        try:
            eat_drink = EatDrink.query.all()
            return eat_drink
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_eat_drink_by_trip(self, trip_id):
        """Retrieve all eat&drink from a specific trip in the database.

        Returns:
            list[EatDrink]: A list of eat&drink objects.
            None: If an error occurred.
        """
        try:
            eat_drink = EatDrink.query.filter_by(trip_id=trip_id).all()
            return eat_drink
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_eat_drink(self, trip_id, name, coordinates, address, day, comments, external_url):
        """Create and save new eat&drink to the database.

        Args:
            name (str): The name of eat&drink place.
            coordinates(str): The latitude and longitude of the eat&drink place.
            address (str): The address of the eat&drink place.
            day (array): The day(s) on which this point will be used during the trip.
            comments (str): Any comments pertaining that place.
            external_url (str): Link to related website (e.g. restaurant's menu).

        Returns:
            EatDrink: The newly created eat&drink object if successful.
            None: If an error occurred.
        """
        new_eat_drink = EatDrink(
            trip_id=trip_id,
            name=name,
            coordinates=coordinates,
            address=address,
            day=day,
            comments=comments,
            external_url=external_url)
        try:
            db.session.add(new_eat_drink)
            db.session.commit()
            return new_eat_drink
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating eat&drink place: ", str(e))


    def update_eat_drink(self, eat_drink_id, name, coordinates, address, day, comments, external_url):
        """Update an existing eat&drink's details.

        Args:
            eat_drink_id (int): The ID of the eat&drink place to update.
            name (str): New eat&drink name to update.
            coordinates (str): New latitude and longitude to update.
            address (str): New address to update.
            day (array): The day(s) on which this point will be used during the trip.
            comments (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            EatDrink: The updated eat&drink object if successful.
            None: If the eat&drink object is not found or an error occurred.
        """
        eat_drink = EatDrink.query.get(eat_drink_id)
        if not eat_drink:
            return None
        if name:
            eat_drink.name = name
        if coordinates:
            eat_drink.coordinates = coordinates
        if address:
            eat_drink.address = address
        if day:
            eat_drink.day = day
        if comments:
            eat_drink.comment = comments
        if external_url:
            eat_drink.external_url = external_url
        try:
            db.session.commit()
            return eat_drink
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating eat&drink place: ", str(e))
            return None


    def delete_eat_drink(self, eat_drink_id):
        """
        Deletes eat&drink from the database by its ID.

        Args:
            eat_drink_id (int): The unique identifier of the eat&drink to delete.

        Returns:
            bool: True if an eat&drink object was successfully deleted, False otherwise.
        """
        try:
            eat_drink_deleted = EatDrink.query.filter(
                EatDrink.id == eat_drink_id).delete()
            db.session.commit()
            return eat_drink_deleted > 0  # returns True if an item was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting eat&drink: ", str(e))
            return False


# ESSENTIALS FUNCTIONS

    def get_essentials(self):
        """Retrieve all essentials objects from the database.

        Returns:
            list[Essentials]: A list of essentials objects.
            None: If an error occurred.
        """
        try:
            essentials = Essentials.query.all()
            return essentials
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_essentials_by_trip(self, trip_id):
        """Retrieve all essentials from a specific trip in the database.

        Returns:
            list[Essentials]: A list of essentials objects.
            None: If an error occurred.
        """
        try:
            essentials = Essentials.query.filter_by(trip_id=trip_id).all()
            return essentials
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_essentials(self, trip_id, name, coordinates, address, day, comments, external_url):
        """Create and save new essentials to the database.

        Args:
            name (str): The name of essentials place.
            coordinates(str): The latitude and longitude of the essentials place.
            address (str): The address of the essentials place.
            day (array): The day(s) on which this point will be used during the trip.
            comments (str): Any comments pertaining that place.
            external_url (str): Link to related website.

        Returns:
            Essentials: The newly created eat&drink object if successful.
            None: If an error occurred.
        """
        new_essentials = Essentials(
            trip_id=trip_id,
            name=name,
            coordinates=coordinates,
            address=address,
            day=day,
            comments=comments,
            external_url=external_url)
        try:
            db.session.add(new_essentials)
            db.session.commit()
            return new_essentials
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating essentials place: ", str(e))


    def update_essentials(self, essentials_id, name, coordinates, address, day, comments, external_url):
        """Update an existing essentials' details.

        Args:
            essentials_id (int): The ID of the essentials place to update.
            name (str): New essentials name to update.
            coordinates (str): New latitude and longitude to update.
            address (str): New address to update.
            day (array): The day(s) on which this point will be used during the trip.
            comments (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            Essentials: The updated essentials object if successful.
            None: If the essentials object is not found or an error occurred.
        """
        essentials = Essentials.query.get(essentials_id)
        if not essentials:
            return None
        if name:
            essentials.name = name
        if coordinates:
            essentials.coordinates = coordinates
        if address:
            essentials.address = address
        if day:
            essentials.day = day
        if comments:
            essentials.comment = comments
        if external_url:
            essentials.external_url = external_url
        try:
            db.session.commit()
            return essentials
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating essentials place: ", str(e))
            return None


    def delete_essentials(self, essentials_id):
        """
        Deletes essentials from the database by its ID.

        Args:
            essentials_id (int): The unique identifier of the essentials to delete.

        Returns:
            bool: True if an essentials object was successfully deleted, False otherwise.
        """
        try:
            essentials_deleted = Essentials.query.filter(
                Essentials.id == essentials_id).delete()
            db.session.commit()
            return essentials_deleted > 0  # returns True if an item was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting essentials: ", str(e))
            return False


# GETTING AROUND FUNCTIONS

    def get_getting_around(self):
        """Retrieve all getting around objects from the database.

        Returns:
            list[GettingAround]: A list of getting around objects.
            None: If an error occurred.
        """
        try:
            getting_around = GettingAround.query.all()
            return getting_around
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def get_getting_around_by_trip(self, trip_id):
        """Retrieve all getting around objects from a specific trip in the database.

        Returns:
            list[GettingAround]: A list of essentials objects.
            None: If an error occurred.
        """
        try:
            getting_around = GettingAround.query.filter_by(trip_id=trip_id).all()
            return getting_around
        except SQLAlchemyError as e:
            print("A database error occurred:", str(e))
            return None
        except Exception as e:
            print("An unexpected error occurred:", str(e))
            return None


    def add_getting_around(self, trip_id, name, coordinates, address, day, comments, external_url):
        """Create and save new getting_around to the database.

        Args:
            name (str): The name of getting_around place.
            coordinates(str): The latitude and longitude of the getting_around place.
            address (str): The address of the getting_around place.
            day (array): The day(s) on which this point will be used during the trip.
            comments (str): Any comments pertaining that place.
            external_url (str): Link to related website.

        Returns:
            GettingAround: The newly created getting_around object if successful.
            None: If an error occurred.
        """
        new_getting_around = GettingAround(
            trip_id=trip_id,
            name=name,
            coordinates=coordinates,
            address=address,
            day=day,
            comments=comments,
            external_url=external_url)
        try:
            db.session.add(new_getting_around)
            db.session.commit()
            return new_getting_around
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while creating getting around place: ", str(e))


    def update_getting_around(self, getting_around_id, name, coordinates, address, day, comments, external_url):
        """Update an existing getting_around details.

        Args:
            getting_around_id (int): The ID of the place to update.
            name (str): New name to update.
            coordinates (str): New latitude and longitude to update.
            address (str): New address to update.
            day (array): The day(s) on which this point will be used during the trip.
            comments (str): New comment to update.
            external_url (str): New external link to update.

        Returns:
            GettingAround: The updated getting_around object if successful.
            None: If the getting_around object is not found or an error occurred.
        """
        getting_around = GettingAround.query.get(getting_around_id)
        if not getting_around:
            return None
        if name:
            getting_around.name = name
        if coordinates:
            getting_around.coordinates = coordinates
        if address:
            getting_around.address = address
        if day:
            getting_around.day = day
        if comments:
            getting_around.comment = comments
        if external_url:
            getting_around.external_url = external_url
        try:
            db.session.commit()
            return getting_around
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while updating getting around place: ", str(e))
            return None


    def delete_getting_around(self, getting_around_id):
        """
        Deletes getting_around from the database by its ID.

        Args:
            getting_around_id (int): The unique identifier of the getting_around to delete.

        Returns:
            bool: True if a getting_around object was successfully deleted, False otherwise.
        """
        try:
            getting_around_deleted = GettingAround.query.filter(
                GettingAround.id == getting_around_id).delete()
            db.session.commit()
            return getting_around_deleted > 0  # returns True if an item was deleted
        except Exception as e:
            db.session.rollback()
            print("An error has occurred while deleting getting around: ", str(e))
            return False