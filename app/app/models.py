
from sqlalchemy.orm import relationship
from app import db, app
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Date, Time, Enum
import hashlib
from enum import Enum as StatusSeat
from enum import Enum as StatusPayment
from enum import Enum as StatusClass
from enum import Enum as StatusRole
from flask_login import UserMixin


class UserRole(StatusRole):
    ADMIN = 1
    EMPLOYEE = 2
    USER = 3

class ClassStatus(StatusClass):
    ECONOMY = "Economy"
    BUSINESS = "Business"


class SeatStatus(StatusSeat):
    AVAILABLE = "Available"
    RESERVED = "Reserved"

class PaymentStatus(StatusPayment):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAILED = "Failed"

class User(db.Model, UserMixin):


    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.USER)

    def __str__(self):
        return self.name

class Airline(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    airplanes = relationship('Airplane', backref='airline', lazy=True)

class Airplane(db.Model):

    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    airline_id = Column(Integer, ForeignKey(Airline.id), nullable=False)

    flights = relationship('Flight', backref='airplane', lazy=True)

    def __str__(self):
        return self.name

class Airport(db.Model):

    id = Column(Integer,primary_key=True, autoincrement=True)
    code = Column(String(3), unique=True, nullable=False)
    name = Column(String(50), nullable=True)
    city = Column(String(30), nullable=True)
    country = Column(String(50), nullable=True)

    departure_routes = db.relationship('Route', foreign_keys='Route.departure_airport_id', backref='departure_airport',lazy=True)
    destination_routes = db.relationship('Route', foreign_keys='Route.destination_airport_id',
                                         backref='destination_airport', lazy=True)

    def __str__(self):
        return self.code

class Route(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    departure_airport_id = db.Column(db.Integer, db.ForeignKey(Airport.id), nullable=False)
    destination_airport_id = db.Column(db.Integer, db.ForeignKey(Airport.id), nullable=False)

    flights = relationship('Flight', backref='route', lazy=True)

class Flight(db.Model):

    id = Column(Integer,primary_key=True, autoincrement=True)
    flight_code = Column(String(10), nullable=False, unique=True)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)

    route_id = Column(Integer, ForeignKey(Route.id), nullable=False)
    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)

    tickets = relationship('Ticket', backref='flight', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "flight_code": self.flight_code,
            "departure_time": self.departure_time.strftime("%I:%M:%p"),
            "arrival_time": self.arrival_time.strftime("%I:%M:%p")
        }

class Passenger(db.Model):

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(12), nullable=False, unique=True)
    email = Column(String(50), nullable=True)
    birthdate = Column(Date, nullable=False)

    tickets = relationship('Ticket', backref='passenger', lazy=True)

class Ticket(db.Model):

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(String(10), nullable=False)
    ticket_booking_date = Column(Date, nullable=False)
    class_type = Column(Enum(ClassStatus), default=ClassStatus.ECONOMY)
    price = Column(Float, nullable=False)

    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)
    passenger_id = Column(Integer, ForeignKey(Passenger.id), nullable=False)

    seats = relationship('Seat', backref='ticket', uselist=False)
    payments = relationship('Payment', backref='ticket', uselist=False)

class Seat(db.Model):

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(5), nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE)

    ticket_id = Column(Integer, ForeignKey(Ticket.id), nullable=False)


class Payment(db.Model):

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.SUCCESS)

    ticket_id = Column(Integer, ForeignKey(Ticket.id), nullable=False)

if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        # db.session.remove()
        # airports = [
        #     # Airport(code="JFK", name="John F. Kennedy International Airport", city="New York", country="USA"),
        #     # Airport(code="LAX", name="Los Angeles International Airport", city="Los Angeles", country="USA"),
        #     # Airport(code="LHR", name="Heathrow Airport", city="London", country="United Kingdom"),
        #     # Airport(code="DXB", name="Dubai International Airport", city="Dubai", country="UAE"),
        #     # Airport(code="NRT", name="Narita International Airport", city="Tokyo", country="Japan"),
        #     # Airport(code="HNA", name="Noi Bai Airport", city="Ha Noi", country="Vietnam"),
        #     # Airport(code="SGN", name="Tan Son Nhat Airport", city="Ho Chi Minh", country="Vietnam"),
        #     # Airport(code="DLI", name="Lien Khuong Airport", city="Duc Trong", country="Vietnam"),
        #     # Airport(code="VCA", name="Can Tho Airport", city="Can Tho", country="Vietnam"),
        #     # Airport(code="DAD", name="Da Nang Airport", city="Da Nang", country="Vietnam"),
        #     # Airport(code="CXR", name="Cam Ranh Airport", city="Cam Ranh", country="Vietnam"),
        #     # Airport(code="PQC", name="Phu Quoc Airport", city="Phu Quoc", country="Vietnam"),
        #     # Airport(code="HPH", name="Cat Bi Airport", city="Hai Phong", country="Vietnam"),
        #     # Airport(code="HUI", name="Phu Bai Airport", city="Hue", country="Vietnam"),
        #     # Airport(code="VDO", name="Van Don Airport", city="Van Don", country="Vietnam"),
        #     # Airport(code="VII", name="Vinh Airport", city="Vinh", country="Vietnam"),
        #     # Airport(code="PXU", name="Pleiku Airport", city="Pleiku", country="Vietnam"),
        #     # Airport(code="THD", name="Tho Xuan Airport", city="Thanh Hoa", country="Vietnam"),
        #     # Airport(code="VKG", name="Rach Gia Airport", city="Rach Gia", country="Vietnam"),
        # ]

        # list_airport = [
        #     Airport(code="DMK", name="Don Mueang Airport", city="Bangkok", country="Thailand"),
        #     Airport(code="BKK", name="Suvarnabhumi Airport", city="Bangkok", country="Thailand"),
        #     Airport(code="HKT", name="Phuket Airport", city="Phuket", country="Thailand"),
        #     Airport(code="CNX", name="Chiang Mai Airport", city="Chiang Mai", country="Thailand"),
        #     Airport(code="SIN", name="Changi Airport", city="Changi", country="Singapore"),
        #     Airport(code="KUL", name="Kuala Lumpur Airport", city="Selangor", country="Malaysia"),
        #     Airport(code="KCH", name="Kuching Airport", city="Sarawak", country="Malaysia"),
        #     Airport(code="PEN", name="Penang Airport", city="Penang", country="Malaysia"),
        #     Airport(code="DPS", name="I Gusti Ngurah Rai Airport", city="Bali", country="Indonesia"),
        #     Airport(code="SUB", name="Juanda Rai Airport", city="Surabaya", country="Indonesia"),
        #     Airport(code="CRK", name="Clark Airport", city="Mabalacat", country="Phillipines"),
        #     Airport(code="DVO", name="Francisco Bangoy Airport", city="Davao", country="Phillipines"),
        #     Airport(code="AOU", name="Attapeu Airport", city="Attapeu", country="Laos"),
        # ]

        # airlines = [
        #     Airline(name="Pacific Airlines"),
        #     Airline(name="Vietnam Airlines"),
        #     Airline(name="Vietravel Airlines"),Airline(name="VietJet Air"),Airline(name="Bangkok Airway"),
        #     Airline(name="Cebu Pacific"),Airline(name="JetStar Asia Airways"),Airline(name="Singapore Airlines"),
        #     Airline(name="Nok Air"),Airline(name="Philippine Airlines"),Airline(name="Lion Air"),
        #     Airline(name="Garuda Indonesia")
        #
        # ]

        # airplanes = [
        #     Airplane(name="Boeing 737", model="737-800", airline_id=1),
        #     Airplane(name="Boeing 767", model="767", airline_id=2),
        #     Airplane(name="Boeing 777", model="777", airline_id=3),
        #     Airplane(name="Boeing 787", model="787", airline_id=4)
        # ]

        # routes = [
        #     Route(departure_airport_id=14,destination_airport_id=17),
        #     Route(departure_airport_id=14,destination_airport_id=16),Route(departure_airport_id=14,destination_airport_id=18),Route(departure_airport_id=14,destination_airport_id=19),
        #     Route(departure_airport_id=14,destination_airport_id=20),Route(departure_airport_id=14,destination_airport_id=21),
        #     Route(departure_airport_id=14,destination_airport_id=22),Route(departure_airport_id=14,destination_airport_id=23),Route(departure_airport_id=14,destination_airport_id=24),
        #     Route(departure_airport_id=14,destination_airport_id=25),Route(departure_airport_id=14,destination_airport_id=26),Route(departure_airport_id=14,destination_airport_id=27),Route(departure_airport_id=14,destination_airport_id=28),
        #     Route(departure_airport_id=14,destination_airport_id=29),Route(departure_airport_id=14,destination_airport_id=30),Route(departure_airport_id=14,destination_airport_id=31),Route(departure_airport_id=14,destination_airport_id=32),
        #     Route(departure_airport_id=14,destination_airport_id=33),Route(departure_airport_id=14,destination_airport_id=34),Route(departure_airport_id=14,destination_airport_id=35),Route(departure_airport_id=14,destination_airport_id=36),
        #     Route(departure_airport_id=14,destination_airport_id=37),Route(departure_airport_id=14,destination_airport_id=9),Route(departure_airport_id=14,destination_airport_id=10),Route(departure_airport_id=14,destination_airport_id=11),
        #     Route(departure_airport_id=15,destination_airport_id=9), Route(departure_airport_id=15,destination_airport_id=10),Route(departure_airport_id=15,destination_airport_id=11),Route(departure_airport_id=15,destination_airport_id=12),
        #     Route(departure_airport_id=15,destination_airport_id=13),Route(departure_airport_id=15,destination_airport_id=14),Route(departure_airport_id=15,destination_airport_id=14),Route(departure_airport_id=15,destination_airport_id=16),
        #     Route(departure_airport_id=15,destination_airport_id=17),Route(departure_airport_id=15,destination_airport_id=18),Route(departure_airport_id=15,destination_airport_id=19),Route(departure_airport_id=15,destination_airport_id=20),
        #     Route(departure_airport_id=15,destination_airport_id=21),Route(departure_airport_id=15,destination_airport_id=22),Route(departure_airport_id=15,destination_airport_id=23),
        #     Route(departure_airport_id=15,destination_airport_id=24),Route(departure_airport_id=15,destination_airport_id=25),Route(departure_airport_id=15,destination_airport_id=26),Route(departure_airport_id=15,destination_airport_id=27),
        #     Route(departure_airport_id=15,destination_airport_id=28),Route(departure_airport_id=15,destination_airport_id=29),Route(departure_airport_id=15,destination_airport_id=30),Route(departure_airport_id=15,destination_airport_id=31),
        #     Route(departure_airport_id=15,destination_airport_id=32)
        # ]
        # db.session.add_all(routes)
        # db.session.commit()
        # s = User(name='employee1', username='employee1', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
        #          email='employee1@gmail.com', user_role=UserRole.EMPLOYEE)
        u = User(name='admin', username='admin', password=str(hashlib.md5('12345'.encode('utf-8')).hexdigest()),
                 email='admin123@gmail.com', user_role=UserRole.ADMIN)
        #
        db.session.add(u)
        # db.session.add(s)
        db.session.commit()
