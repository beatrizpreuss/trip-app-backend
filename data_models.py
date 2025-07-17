from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Float, column
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

    # One trip can have many points of interest, accommodations, and food entries
    points_of_interest = relationship("PointsOfInterest", backref="trip")
    accommodation = relationship("Accommodation", backref="trip")
    food = relationship("Food", backref="trip")


class PointsOfInterest(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    lat_long = Column(Float)
    address = Column(String)
    price = Column(String)
    comment = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))


class Accommodation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    address = Column(String)
    price = Column(String)
    status = Column(String)
    comment = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))


class Food(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    address = Column(String)
    comment = Column(String)
    external_url = Column(String)
    trip_id = Column(Integer, ForeignKey("trip.id"))


# class LocalTransport(db.Model)
# class LongDistanceTransport(db.Model)


