from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Hotel(db.Model):
    __tablename__ = 'hotel'
    
    hotel_id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(255), nullable=False)

    # Define relationship with Room and Employee
    rooms = db.relationship('Room', backref='hotel', lazy=True)
    employees = db.relationship('Employee', backref='hotel', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_address = db.Column(db.Text)
    customer_dob = db.Column(db.Date, nullable=False)
    customer_age = db.Column(db.Integer)

    # Define relationship with Payment and Room
    payments = db.relationship('Payment', backref='customer', lazy=True)
    rooms = db.relationship('Room', backref='customer', lazy=True)

class Room(db.Model):
    __tablename__ = 'room'
    
    room_no = db.Column(db.Integer, primary_key=True)
    room_rates = db.Column(db.Integer)
    room_status = db.Column(db.String(255))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))

class Employee(db.Model):
    __tablename__ = 'employee'
    
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(255), nullable=False)
    employee_address = db.Column(db.Text)
    employee_job_desc = db.Column(db.Text)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'))

class Payment(db.Model):
    __tablename__ = 'payment'
    
    payment_no = db.Column(db.Integer, primary_key=True)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(255))
    payment_amount = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
