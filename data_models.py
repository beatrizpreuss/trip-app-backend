from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    # One user can have many trips
    trips = relationship("Trip", backref="user")


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

    # One trip can have many points of interest, accommodations, and food entries
    point_of_interest = relationship("PointOfInterest", backref="trip")
    accommodation = relationship("Accommodation", backref="trip")
    food = relationship("Food", backref="trip")


class PointOfInterest(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    lat_long = Column(String)
    address = Column(String)
    price = Column(String)
    comment = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat_long": self.lat_long,
            "address": self.address,
            "price": self.price,
            "comment": self.comment,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


class Accommodation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    lat_long = Column(String)
    address = Column(String)
    price = Column(String)
    status = Column(String)
    comment = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "lat_long": self.lat_long,
            "address": self.address,
            "price": self.price,
            "status": self.status,
            "comment": self.comment,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


class Food(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    lat_long = Column(String)
    address = Column(String)
    comment = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "lat_long": self.lat_long,
            "address": self.address,
            "comment": self.comment,
            "external_url": self.external_url,
            "trip_id": self.trip_id
        }


# class LocalTransport(db.Model)
# class LongDistanceTransport(db.Model)


