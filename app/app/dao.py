from datetime import datetime, timedelta, date
import random
from random import randint

from jinja2.async_utils import auto_to_list
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, func

from click import password_option
from flask import flash

from app import app, db
from app.models import User, Airport, Airplane, Route, Flight, Passenger,Ticket,Seat,Payment
import hashlib


def add_user(name, username, password, email):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password, email=email)

    db.session.add(u)
    db.session.commit()

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))

    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def add_flights(flight_code,departure_time,arrival_time,route_id,airplane_id):
    f = Flight(flight_code=flight_code, departure_time=departure_time, arrival_time=arrival_time, route_id=route_id, airplane_id=airplane_id)

    db.session.add(f)
    db.session.commit()

def search_airport():
    DepartureAirport = aliased(Airport)
    DestinationAirport = aliased(Airport)

    routes = (
        db.session.query(
            Route.id,
            DepartureAirport.name.label('departure_name'),
            DestinationAirport.name.label('destination_name')
        )
        .join(DepartureAirport, DepartureAirport.id == Route.departure_airport_id)
        .join(DestinationAirport, DestinationAirport.id == Route.destination_airport_id)
        .all()
    )
    return routes

def search_load(departure_air,arrival_air,departure_date,arrival_date):
    try:
        departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
        arrival_date = datetime.strptime(arrival_date, "%Y-%m-%d").date() if arrival_date else None
    except ValueError:
        flash("Invalid", "error")

    # departure_date_start = datetime.combine(departure_date, datetime.time())
    # departure_date_end = departure_date_start + timedelta(days=1)
    query = db.session.query(Flight).join(Route).join(Airport, Route.departure_airport_id == Airport.id).filter(
        and_(
            Route.departure_airport_id == db.session.query(Airport.id).filter_by(code=departure_air).scalar(),
            Route.destination_airport_id == db.session.query(Airport.id).filter_by(code=arrival_air).scalar(),
            func.date(Flight.departure_time) == departure_date
        )
    )

    flights = query.all()

    return flights

def add_passenger(name,phone,email,birth):

    new_passenger = Passenger(name=name,phone=phone,email=email,birthdate=birth)

    db.session.add(new_passenger)
    db.session.commit()

    return new_passenger.id

def add_ticket(price,flight_id,passenger_id):
    new_ticket = Ticket(ticket_number=str(random.randint(10000, 99999)), ticket_booking_date=date.today(),price=price,flight_id=flight_id,passenger_id=passenger_id)

    db.session.add(new_ticket)
    db.session.commit()
    return new_ticket.id

def add_seat(number,ticket_id):
    new_seat = Seat(number=number,ticket_id=ticket_id)

    db.session.add(new_seat)
    db.session.commit()

def add_payment(amount,ticket_id):
    new_payment = Payment(amount=amount,ticket_id=ticket_id)

    db.session.add(new_payment)
    db.session.commit()

def get_passenger_by_phone(phone):
    return db.session.query(Passenger).filter_by(phone=phone).first()

def load_airports():
    return Airport.query.all()

def load_route():
    return Route.query.all()

def load_airplanes():
    return Airplane.query.all()

def load_routes():
    return Route.query.all()
