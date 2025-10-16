from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    # One user can have many trips
    trips = relationship("Trip", backref="user")
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password}


class Trip(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id
        }

    # One trip can have many explores, stays, eat&drink, essentials, and getting around entries
    explore = relationship("Explore", backref="trip")
    stay = relationship("Stay", backref="trip")
    eat_drink = relationship("EatDrink", backref="trip")
    essentials = relationship("Essentials", backref="trip")
    getting_around = relationship("GettingAround", backref="trip")


class Explore(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    coordinates = Column(String)
    address = Column(String)
    day = Column(Integer, default=1)
    price = Column(String)
    comments = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "coordinates": self.coordinates,
            "address": self.address,
            "day": self.day,
            "price": self.price,
            "comments": self.comments,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


class Stay(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    coordinates = Column(String)
    address = Column(String)
    price = Column(String)
    day = Column(Integer, default=1)
    status = Column(String)
    comments = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "coordinates": self.coordinates,
            "address": self.address,
            "day": self.day,
            "price": self.price,
            "status": self.status,
            "comments": self.comments,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


class EatDrink(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    coordinates = Column(String)
    address = Column(String)
    day = Column(Integer, default=1)
    comments = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "coordinates": self.coordinates,
            "address": self.address,
            "day": self.day,
            "comments": self.comments,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


class Essentials(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    coordinates = Column(String)
    address = Column(String)
    day = Column(Integer, default=1)
    comments = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "coordinates": self.coordinates,
            "address": self.address,
            "day": self.day,
            "comments": self.comments,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


class GettingAround(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    coordinates = Column(String)
    address = Column(String)
    day = Column(Integer, default=1)
    comments = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "coordinates": self.coordinates,
            "address": self.address,
            "day": self.day,
            "comments": self.comments,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


