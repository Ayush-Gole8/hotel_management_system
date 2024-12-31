from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

# Enumerations for controlled vocabulary
class RoomStatusEnum(Enum):
    VACANT = 'Vacant'
    OCCUPIED = 'Occupied'
    MAINTENANCE = 'Maintenance'

class PaymentMethodEnum(Enum):
    CASH = 'Cash'
    CREDIT_CARD = 'Credit Card'
    DEBIT_CARD = 'Debit Card'
    ONLINE = 'Online'

class BookingStatusEnum(Enum):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'

class Hotel(db.Model):
    __tablename__ = 'hotel'
    
    hotel_id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(255), nullable=False, unique=True)
    
    # Relationships
    rooms = db.relationship('Room', backref='hotel', lazy=True, cascade="all, delete-orphan")
    employees = db.relationship('Employee', backref='hotel', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Hotel {self.hotel_name}>"

class Customer(db.Model):
    __tablename__ = 'customer'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_address = db.Column(db.Text, nullable=True)
    customer_dob = db.Column(db.Date, nullable=False)
    customer_age = db.Column(db.Integer, nullable=True)
    customer_mobile_no = db.Column(db.String(15), nullable=False, unique=True)  # Added mobile number

    # Relationships
    payments = db.relationship('Payment', backref='customer', lazy=True, cascade="all, delete-orphan")
    rooms = db.relationship('Room', backref='customer', lazy=True)  # Allows multiple rooms if needed
    booking_requests = db.relationship('BookingRequest', backref='customer', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer {self.customer_name}>"

class Room(db.Model):
    __tablename__ = 'room'
    
    room_no = db.Column(db.Integer, primary_key=True)
    room_rates = db.Column(db.Integer, nullable=False)
    room_status = db.Column(db.Enum(RoomStatusEnum), nullable=False, default=RoomStatusEnum.VACANT)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=True)  # Nullable for vacant rooms
    
    # Relationships
    booking_requests = db.relationship('BookingRequest', backref='room', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Room {self.room_no} - {self.room_status.value}>"

class Employee(db.Model):
    __tablename__ = 'employee'
    
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(255), nullable=False)
    employee_address = db.Column(db.Text, nullable=True)
    employee_job_desc = db.Column(db.Text, nullable=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'), nullable=False)
    
    def __repr__(self):
        return f"<Employee {self.employee_name}>"

class Payment(db.Model):
    __tablename__ = 'payment'
    
    payment_no = db.Column(db.Integer, primary_key=True)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.Enum(PaymentMethodEnum), nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    
    def __repr__(self):
        return f"<Payment {self.payment_no} - {self.payment_method.value} - {self.payment_amount}>"

class BookingRequest(db.Model):
    __tablename__ = 'booking_request'
    
    request_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)  # Link to Customer
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)
    additional_info = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(BookingStatusEnum), nullable=False, default=BookingStatusEnum.PENDING)  # Possible values: Pending, Accepted, Rejected
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<BookingRequest {self.request_id} - {self.status.value}>"
