from sys import exception

from sqlalchemy.exc import IntegrityError
from app import app, login, db
from flask import render_template, url_for, request, redirect, session, flash, jsonify
import dao
from flask_login import login_user, logout_user
from datetime import date, datetime

from app.models import UserRole


@app.route("/", methods=['get','post'])
def index():
    list_airport = dao.load_airports()
    today = date.today()
    err = ''
    if request.method.__eq__('POST'):
        selected_radio = request.form.get("flight-type")
        departure_air = request.form.get("airport_dep")
        arrival_air = request.form.get("airport_arr")
        departure_date = request.form.get("dateDepart")
        arrival_date = request.form.get("dateArrival")
        passengers_amount = request.form.get("amount")
        print(f"Passengers Amount: {passengers_amount}")
        if departure_air == arrival_air:
            err = 'Same airport !! Please choose another airport to find'
        if not passengers_amount:
            err = 'Amount of passengers must be at least 1 !!'
        else:
            session['passenger_amount'] = int(passengers_amount)
            session['radio_choice'] = selected_radio
            flights = dao.search_load(departure_air, arrival_air, departure_date, arrival_date)
            session['flights'] = [flight.to_dict() for flight in flights]
            if selected_radio == 'Round':
                flights_round = dao.search_round_load(departure_air, arrival_air, departure_date, arrival_date)
                session['flights_round'] = [flight.to_dict() for flight in flights_round]
            return redirect(url_for('result'))

    return render_template('index.html', airports=list_airport, today=today, err=err)

@app.route("/login", methods=['get', 'post'])
def load_login():
    msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)

        # u khac null => chung thuc thanh cong
        if user:
            login_user(user=user)
            return redirect("/")
        else:
            msg = 'Invalid username or password !!'

    return render_template('login.html', err=msg)

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/')

@app.route("/register", methods=['get', 'post'])
def load_register_form():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not password.__eq__(confirm):
            err_msg = 'Invalid confirm password !!'
        else:
            data = request.form.copy()
            del data['confirm']
            dao.add_user(**data)
            return redirect("/login")

    return render_template('register.html', err_msg=err_msg)

@app.route("/result", methods=['POST', 'get'])
def result():
    selected_radio = session.get("radio_choice")
    flights = session.get('flights', [])

    if request.method.__eq__('POST'):
        flight_id = request.form.get('flight_id')
        if flight_id:
            print(flight_id)
            session['flight_id'] = flight_id
            if selected_radio == 'Oneway':
                return redirect("/passenger")
            elif selected_radio == 'Round':
                return redirect("/resultround")


    return render_template("result.html", flights=flights, selected_radio=selected_radio)

@app.route("/schedule", methods=['get', 'post'])
def load_schedule():

    list_airport = dao.load_airports()
    list_airplanes = dao.load_airplanes()
    list_routes = dao.load_route()
    today = datetime.today().strftime('%Y-%m-%dT%H:%M')
    list_routes_airport = dao.search_airport()
    msg = ''
    msg_success = ''
    new_flight = []
    if request.method.__eq__('POST'):
        flight_code = request.form.get("flight_code")
        departure_time = request.form.get("departure_time")
        arrival_time = request.form.get("arrival_time")
        route_id = request.form.get("route")
        airplane_id = request.form.get("airplane")

        if not flight_code:
            msg = 'Flight code must not be empty !!!'
        elif len(flight_code) != 6:
            msg = 'Flight code must be 6 characters !!! '
        else:
            new_flight = dao.add_flights(flight_code, departure_time, arrival_time, route_id, airplane_id)
            msg_success = 'Schedule success !!!'

    return render_template("schedule.html", today=today, airports=list_airport, airplanes =list_airplanes, routes=list_routes,
                           list_routes_airport=list_routes_airport, msg=msg, new_flight=new_flight, msg_success=msg_success)

@app.route("/passenger", methods=['get','post'])
def passenger():
    amount_of_passengers = session.get('passenger_amount')
    selected_radio = session.get("radio_choice")
    if selected_radio == 'Round':
        print(selected_radio)
    err = ''
    passenger_ids = []
    flag = True

    if request.method.__eq__('POST'):
        for i in range(amount_of_passengers):
            passenger_name = request.form.get(f'name_{i}')
            passenger_phone = request.form.get(f'phone_{i}')
            passenger_email = request.form.get(f'email_{i}')
            passenger_birth = request.form.get(f'birthdate_{i}')

            if len(str(passenger_phone)) > 12 or len(str(passenger_phone)) <= 9:
                err = 'Phone must be 10 to 12 number'
                flag = False
            elif '@gmail' not in passenger_email:
                err = 'Email must have the @gmail !!'
                flag = False
            else:
                existing_passenger = dao.get_passenger_by_phone(passenger_phone)
                if existing_passenger:
                    err = f"Phone number {passenger_phone} already exists!"
                    flag = False
                else:
                    try:
                        passenger_add = dao.add_passenger(passenger_name, passenger_phone, passenger_email, passenger_birth)
                        db.session.flush()
                        passenger_ids.append(passenger_add)
                    except IntegrityError:
                        db.session.rollback()
                        err = f"Failed to add passenger: {passenger_name}"
                        flag = False

        if flag:
            db.session.commit()
            session['passenger_ids'] = passenger_ids
            return redirect('/ticketpayment')

    return render_template('passenger.html', amount_of_passengers=amount_of_passengers, err=err)

@app.route("/resultround", methods=['get','post'])
def result_round():
    flights_round = session.get('flights_round',[])
    if request.method.__eq__('POST'):
        flight_id = request.form.get('flight_id')
        session['flight_round_id'] = flight_id
        return redirect(url_for('passenger'))

    return render_template('resultround.html', flights_round=flights_round)

@app.route("/ticketpayment",methods=['get','post'])
def ticket_and_payment():
    tickets = []
    msg_success = ''
    err = ''
    amount_of_passengers = session.get('passenger_amount')
    passengers = session.get('passenger_ids',[])
    flight_id = session.get('flight_id')
    flight_round_id = session.get('flight_round_id')
    selected_radio = session.get("radio_choice")
    if not amount_of_passengers:
        err = 'Not found any passenger'

    if request.method.__eq__('POST'):
        flag = True
        for i in range(amount_of_passengers):
            p = passengers[i]
            price = request.form.get(f'price_{i}')
            seat_number = request.form.get(f"seat_num_{i}")

            checking_seat = dao.search_seats(flight_id, seat_number)
            if checking_seat:
                flag = False
                raise ValueError(
                    f"Seat number {seat_number} is already taken for this Flight no {flight_id} please choose another Seat")

            ticket = dao.add_ticket(price, flight_id, p)

            db.session.flush()
            dao.add_seat(seat_number, ticket)
            db.session.flush()
            dao.add_payment(price, ticket)
            db.session.flush()
            if selected_radio == 'Round':
                checking_seat_round = dao.search_seats(flight_round_id, seat_number)
                if checking_seat_round:
                    flag = False
                    raise ValueError(
                        f"Seat number {seat_number} is already taken for {flight_round_id} please choose another Seat")
                ticket2 = dao.add_ticket(price, flight_round_id, p)

                db.session.flush()
                dao.add_seat(seat_number, ticket2)
                db.session.flush()
                dao.add_payment(price, ticket2)
                db.session.flush()

        if flag:
            msg_success = 'Reserve Success !!! '
            db.session.commit()

    return render_template("ticketpayment.html", err=err,amount_of_passengers=amount_of_passengers, msg_success=msg_success)

@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')

@app.route("/all_flights")
def load_flights():
    flights = dao.all_flights()

    return render_template('flights.html',flights=flights)

@app.route("/tickets_after")
def load_tickets():
    tickets = session.get('tickets', [])
    return render_template('ticket_after.html', tickets=tickets)

@app.context_processor
def inject_user_roles():
    return dict(UserRole=UserRole)

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
