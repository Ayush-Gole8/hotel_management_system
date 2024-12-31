from flask import Flask, request, redirect, url_for, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import enum
from sqlalchemy import Enum as PgEnum
from sqlalchemy import Enum as SQLAlchemyEnum
from flask import session
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Time, ForeignKey, TIMESTAMP
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
from flask import Flask, render_template
from models import BookingRequest # Import your model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Replace with a strong secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost/hotel'  # Update as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = create_engine('postgresql://postgres:newpassword@localhost/hotel')
Session = sessionmaker(bind=engine)
# Initialize Flask-Migrate
migrate = Migrate(app, db)

ROLE_PASSWORDS = {
    'customer': 'customerpass',
    'receptionist': 'receptionistpass',
    'housekeeping': 'housekeepingpass'
}
# Define ENUM types
class RoomStatusEnum(enum.Enum):
    Vacant = 'Vacant'
    Occupied = 'Occupied'
    Cleaning = 'Cleaning'

class RequestTypeEnum(enum.Enum):
    Pickup = 'Pickup'
    Drop = 'Drop'

class RequestStatusEnum(PyEnum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
    Completed = "Completed"


class ServiceTypeEnum(enum.Enum):
    RoomCleaning = 'Room Cleaning'
    FoodDelivery = 'Food Delivery'
    Laundry = 'Laundry'
    WakeupCall = 'Wake-up Call'

# Model Definitions
class Hotel(db.Model):
    __tablename__ = 'hotel'  
    hotel_id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(255), nullable=False)
    hotel_location = db.Column(db.String(200), nullable=False)
    
    # Use back_populates for bidirectional relationship
    employees = db.relationship('Employee', back_populates='hotel', lazy=True)
    rooms = db.relationship('Room', back_populates='hotel', lazy=True)

class Employee(db.Model):
    __tablename__ = 'employee'
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(255), nullable=False)
    employee_address = db.Column(db.Text)
    employee_job_desc = db.Column(db.Text)
    employee_mobile_no = db.Column(db.String(15), nullable=False, unique=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'), nullable=True)
    
    # Use back_populates to define the other side of the relationship
    hotel = db.relationship('Hotel', back_populates='employees')

class Customer(db.Model):
    __tablename__ = 'customer'  
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_address = db.Column(db.Text)
    customer_dob = db.Column(db.Date, nullable=False)
    customer_age = db.Column(db.Integer)
    customer_mobile_no = db.Column(db.String(15), nullable=False, unique=True)
    
    payments = db.relationship('Payment', backref='customer', lazy=True)
    room = db.relationship('Room', back_populates='customer', uselist=False)  # One-to-One Relationship
    pickup_drop_services = db.relationship('PickupDropService', back_populates='customer')

class Manager(db.Model):
    __tablename__ = 'manager'
    manager_id = db.Column(db.Integer, primary_key=True)
    manager_department = db.Column(db.String(255))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), unique=True)
    
    employee = db.relationship('Employee', backref=db.backref('manager', uselist=False))

class Receptionist(db.Model):
    __tablename__ = 'receptionist'
    receptionist_id = db.Column(db.Integer, primary_key=True)
    receptionist_staff_timing = db.Column(db.Time)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), unique=True)
    
    employee = db.relationship('Employee', backref=db.backref('receptionist', uselist=False))
    pickup_drop_services = db.relationship('PickupDropService', back_populates='receptionist')

class Housekeeping(db.Model):
    __tablename__ = 'housekeeping'
    housekeeping_id = db.Column(db.Integer, primary_key=True)
    housekeeping_roomassigned = db.Column(db.Integer)  # Room number assigned
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), unique=True)
    
    employee = db.relationship('Employee', backref=db.backref('housekeeping', uselist=False))

class Room(db.Model):
    __tablename__ = 'room'  
    room_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_rates = db.Column(db.Float, nullable=False)
    room_status = db.Column(PgEnum(RoomStatusEnum), nullable=False, default=RoomStatusEnum.Vacant)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.hotel_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=True)
    receptionist_id = db.Column(db.Integer, db.ForeignKey('receptionist.receptionist_id'), nullable=True)
    housekeeping_id = db.Column(db.Integer, db.ForeignKey('housekeeping.housekeeping_id'), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.manager_id'), nullable=True)
    
    hotel = db.relationship('Hotel', back_populates='rooms')
    customer = db.relationship('Customer', back_populates='room')

    @property
    def status_display(self):
        if self.room_status == RoomStatusEnum.Vacant:
            return 'Available'
        elif self.room_status == RoomStatusEnum.Occupied:
            return 'Occupied'
        elif self.room_status == RoomStatusEnum.Cleaning:
            return 'Cleaning'
        else:
            return self.room_status.value

class Payment(db.Model):
    __tablename__ = 'payment'
    payment_no = db.Column(db.Integer, primary_key=True)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(255))
    payment_amount = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)

class RoomService(db.Model):
    __tablename__ = 'room_service'
    service_id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)  # Changed from enum to string
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    receptionist_id = db.Column(db.Integer, db.ForeignKey('receptionist.receptionist_id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')  # To track the status of the service

    # Relationships
    room = db.relationship('Room', backref='services')
    customer = db.relationship('Customer', backref='services')
    receptionist = db.relationship('Receptionist', backref='services')

class LostItem(db.Model):
    __tablename__ = 'lost_item'
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    room_no = db.Column(db.Integer, db.ForeignKey('room.room_no'), nullable=False)  # Add room_no
    status = db.Column(db.String(50), default='Reported')  # Add status field

    # Relationships
    customer = db.relationship('Customer', backref='lost_items')
    room = db.relationship('Room', backref='lost_items')  # Add relationship for room


class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    feedback_id = db.Column(db.Integer, primary_key=True)
    feedback_text = db.Column(db.Text, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.manager_id'), nullable=True)

    customer = db.relationship('Customer', backref='feedbacks')
    manager = db.relationship('Manager', backref='feedbacks')  # Assuming Manager model exists

class PickupDropService(db.Model):
    __tablename__ = 'pickup_drop_service'  # Use lowercase for table name

    pickup_drop_service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pickup_location = db.Column(db.String(255), nullable=False)
    drop_service_location = db.Column(db.String(255), nullable=False)
    pickup_drop_service_time = db.Column(db.Time, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id', ondelete='CASCADE'), nullable=False)  # Correct foreign key
    receptionist_id = db.Column(db.Integer, db.ForeignKey('receptionist.receptionist_id', ondelete='CASCADE'))  # Use lowercase for table name
    status = db.Column(db.String(20), nullable=False, default='Pending')  # New status field

    # Relationships
    customer = db.relationship('Customer', back_populates='pickup_drop_services')  # Correct relationship
    receptionist = db.relationship('Receptionist', back_populates='pickup_drop_services')  # Ensure this relationship exists

    def __repr__(self):
        return f'<PickupDropService {self.pickup_drop_service_id}>'

    
Base = declarative_base()
class BookingRequest(Base):
    __tablename__ = 'booking_request'
    
    request_id = Column(Integer, primary_key=True)
    customer_name = Column(String(100))
    customer_mobile = Column(String(15))
    room_no = Column(String(10))
    status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.Pending)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    def __repr__(self):
        return f"<BookingRequest(request_id={self.request_id}, customer_name='{self.customer_name}', " \
               f"customer_mobile='{self.customer_mobile}', room_no='{self.room_no}', status='{self.status}', " \
               f"created_at='{self.created_at}')>"

# Routes
@app.route('/')
def login():
    return render_template('login.html')  # Ensure 'login.html' exists in 'templates'
# @app.route('/login')
# def login():
#     return render_template('login.html') 
@app.route('/select_role', methods=['POST'])
def select_role():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    role = request.form.get('role')

    # Define a common password for simplicity
    common_password = 'allpassword'

    if password != common_password:
        flash('Invalid password. Please try again.', 'error')
        return redirect(url_for('login'))

    if role == 'user':
        customer = Customer.query.get(user_id)
        if customer:
            session['user_id'] = user_id
            return redirect(url_for('user_page', customer_id=user_id))
    
    elif role == 'receptionist':
        receptionist = Employee.query.get(user_id)
        if receptionist:
            session['user_id'] = user_id
            return redirect(url_for('receptionist'))

    elif role == 'housekeeping':
        housekeeping_staff = Employee.query.get(user_id)
        if housekeeping_staff:
            session['user_id'] = user_id
            return redirect(url_for('housekeeping'))

    elif role == 'manager':
        manager = Manager.query.get(user_id)
        if manager:
            session['user_id'] = user_id
            return redirect(url_for('manager'))  # Assuming you want to redirect to manager_page

    flash('Invalid credentials. Please check your User ID and role.', 'error')
    return redirect(url_for('login'))

# Manager Page
@app.route('/manager')
def manager():
    # Fetch all necessary data
    rooms = Room.query.order_by(Room.room_no.asc()).all()  
    employees = Employee.query.order_by(Employee.employee_id.asc()).all()  
    hotels = Hotel.query.order_by(Hotel.hotel_name.asc()).all()  # Fetch all hotels
    feedbacks = db.session.query(Feedback).join(Customer).all()  # Join with Customer to get customer names

    # Prepare feedback data to pass to the template
    feedback_data = []
    for feedback in feedbacks:
        feedback_data.append({
            'customer_id': feedback.customer.customer_id,  # Accessing the customer ID
            'customer_name': feedback.customer.customer_name,  # Accessing the customer name
            'feedback_text': feedback.feedback_text,
        })

    # Fetch other necessary data (this is redundant since you already fetched above)
    # Uncomment the following lines if you need unique data for employees and rooms elsewhere
    # employees = Employee.query.all()
    # rooms = Room.query.all()

    # Default hotel ID logic
    default_hotel_id = hotels[0].hotel_id if hotels else None  # Assuming at least one hotel exists

    # Render the template with all the required data
    return render_template(
        'Manager.html',
        rooms=rooms,
        employees=employees,
        hotels=hotels,
        default_hotel_id=default_hotel_id,
        feedbacks=feedback_data  # Pass feedback data to the template
    )

@app.route('/add_employee', methods=['POST'])
def add_employee():
    try:
        employee_name = request.form.get('employee_name')
        employee_address = request.form.get('employee_address')
        employee_mobile_no = request.form.get('employee_mobile_no')
        employee_job_desc = request.form.get('employee_job_desc')

        # Check for mandatory fields
        if not all([employee_name, employee_address, employee_mobile_no, employee_job_desc]):
            flash('All fields are required!', 'error')
            return redirect(url_for('manager'))

        # Check for duplicate employee by mobile number
        existing_employee = Employee.query.filter_by(employee_mobile_no=employee_mobile_no).first()
        if existing_employee:
            flash('An employee with this mobile number already exists.', 'error')
            return redirect(url_for('manager'))

        # Create the new employee without the hotel_id (since it's not compulsory)
        new_employee = Employee(
            employee_name=employee_name,
            employee_address=employee_address,
            employee_mobile_no=employee_mobile_no,
            employee_job_desc=employee_job_desc,
            hotel_id=None  # Optional if you want to keep it for future use
        )
        db.session.add(new_employee)
        db.session.commit()

        flash('Employee added successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error adding employee: {str(e)}', 'error')

    return redirect(url_for('manager'))

@app.route('/remove_employee/<int:employee_id>', methods=['POST'])
def remove_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee removed successfully!', 'success')
    return redirect(url_for('manager'))  # Ensure this redirects correctly to the manager page

from sqlalchemy.exc import SQLAlchemyError
from flask import flash, redirect, render_template, request, url_for

@app.route('/receptionist', methods=['GET', 'POST']) 
def receptionist():
    session = Session()  # Create a session

    try:
        # Fetch booking requests and available rooms
        booking_requests = session.query(BookingRequest).filter_by(status=RequestStatusEnum.Pending).all()
        available_rooms = session.query(Room).filter_by(room_status=RoomStatusEnum.Vacant).order_by(Room.room_no.asc()).all()
        customers = session.query(Customer).options(joinedload(Customer.room)).order_by(Customer.customer_id.asc()).all()

        if request.method == 'POST':
            request_id = request.form.get('request_id')
            action = request.form.get('action')  
            request_type = request.form.get('request_type')  

            if not all([request_id, action, request_type]):
                flash('Missing form data!', 'error')
                return redirect(url_for('receptionist'))

            # Handle Booking Requests
            if request_type == 'Booking':
                booking_request = session.query(BookingRequest).get(request_id)
                if booking_request and booking_request.status == RequestStatusEnum.Pending:
                    if action == 'Accept':
                        room = session.query(Room).filter_by(room_no=booking_request.room_no, room_status=RoomStatusEnum.Vacant).first()
                        if room:
                            customer = session.query(Customer).filter_by(customer_mobile_no=booking_request.customer_mobile).first()
                            if not customer:
                                customer_address = 'N/A'
                                customer_dob = datetime.today().date()
                                customer_age = 0
                                customer = Customer(
                                    customer_name=booking_request.customer_name,
                                    customer_address=customer_address,
                                    customer_dob=customer_dob,
                                    customer_age=customer_age,
                                    customer_mobile_no=booking_request.customer_mobile
                                )
                                session.add(customer)
                                session.commit()

                            room.customer_id = customer.customer_id  
                            room.room_status = RoomStatusEnum.Occupied
                            booking_request.status = RequestStatusEnum.Accepted
                            session.commit()
                            flash(f'Booking for {customer.customer_name} accepted and room {room.room_no} booked!', 'success')
                        else:
                            flash('Room not available for booking!', 'error')
                    elif action == 'Reject':
                        booking_request.status = RequestStatusEnum.Rejected
                        session.commit()
                        flash(f'Booking request {request_id} rejected.', 'error')
                else:
                    flash('Invalid booking request!', 'error')

    except SQLAlchemyError as e:
        session.rollback()
        flash(f'Error processing request: {str(e)}', 'error')
    finally:
        session.close()  # Ensure the session is closed even if an error occurs

    return render_template('Receptionist.html', 
                           booking_requests=booking_requests, 
                           available_rooms=available_rooms, 
                           customers=customers)

@app.route('/pickup_drop', methods=['GET', 'POST'])
def pickup_drop():
    pickup_drop_requests = []  # Initialize variable

    try:
        # Fetch all pickup/drop requests
        pickup_drop_requests = db.session.query(PickupDropService).all()

        # If form is submitted (for Accept/Reject requests)
        if request.method == 'POST':
            request_id = request.form.get('request_id')
            action = request.form.get('action')

            if not all([request_id, action]):
                flash('Missing form data!', 'error')
                return redirect(url_for('pickup_drop'))

            # Handle Pickup/Drop Requests
            pickup_drop_request = db.session.query(PickupDropService).get(request_id)
            if pickup_drop_request:
                pickup_drop_request.status = 'Accepted' if action == 'Accept' else 'Rejected'
                db.session.commit()
                flash(f'Request {request_id} has been {pickup_drop_request.status.lower()}ed.', 'success')
            else:
                flash('Invalid pickup/drop request!', 'error')

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error processing request: {str(e)}', 'error')

    # Render the template with the fetched requests
    return render_template('PickupDrop.html', pickup_drop_requests=pickup_drop_requests)

import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/housekeeping')
def housekeeping():
    try:
        room_service_requests = RoomService.query.order_by(RoomService.service_id.asc()).all()
        lost_items = LostItem.query.all()  # Fetch all lost items

        # Log the retrieved requests to see if any issues are arising
        for request in room_service_requests:
            logging.debug(f"Service ID: {request.service_id}, Service Type: {request.service_type}")

    except Exception as e:
        logging.error(f"Error fetching room service requests or lost items: {e}")
        return "An error occurred while fetching data."

    return render_template('Housekeeping_Staff.html', room_service_requests=room_service_requests, lost_items=lost_items)

@app.route('/mark_service_done/<int:service_id>', methods=['POST'])
def mark_service_done(service_id):
    try:
        room_service_request = RoomService.query.get(service_id)
        if room_service_request:
            room_service_request.status = 'Done'
            db.session.commit()
            flash('Service request marked as done!', 'success')
        else:
            flash('Service request not found!', 'error')
    except Exception as e:
        logging.error(f"Error marking service as done: {e}")
        flash('An error occurred while updating the service request.', 'error')

    return redirect(url_for('housekeeping'))
@app.route('/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    try:
        # Fetch the room service request by ID
        service_request = RoomService.query.get(service_id)
        if service_request:
            db.session.delete(service_request)
            db.session.commit()
            flash('Service request deleted successfully!', 'success')
        else:
            flash('Service request not found.', 'error')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting service request: {e}")
        flash('An error occurred while deleting the service request.', 'error')
    
    return redirect(url_for('housekeeping'))


# Add Customer Route
@app.route('/add_customer/<int:room_no>', methods=['GET', 'POST'])
def add_customer(room_no):
    # Fetch the room details
    room = Room.query.get(room_no)
    if not room:
        flash(f'Room {room_no} does not exist.', 'error')
        return redirect(url_for('receptionist'))

    if request.method == 'POST':
        # Retrieve form data
        customer_name = request.form.get('customer_name')
        customer_address = request.form.get('customer_address')
        customer_dob = request.form.get('customer_dob')
        customer_age = request.form.get('customer_age')
        customer_mobile_no = request.form.get('customer_mobile_no')

        # Validate input
        if not all([customer_name, customer_address, customer_dob, customer_age, customer_mobile_no]):
            flash('All fields are required!', 'error')
            return redirect(url_for('add_customer', room_no=room_no))

        try:
            # Check if mobile number already exists
            existing_customer = Customer.query.filter_by(customer_mobile_no=customer_mobile_no).first()
            if existing_customer:
                flash('A customer with this mobile number already exists.', 'error')
                return redirect(url_for('add_customer', room_no=room_no))

            # Create a new customer
            new_customer = Customer(
                customer_name=customer_name,
                customer_address=customer_address,
                customer_dob=datetime.strptime(customer_dob, '%Y-%m-%d').date(),
                customer_age=int(customer_age),
                customer_mobile_no=customer_mobile_no
            )
            db.session.add(new_customer)
            db.session.commit()

            # Update the room status to occupied
            room.room_status = RoomStatusEnum.Occupied
            room.customer_id = new_customer.customer_id  
            db.session.commit()

            flash('Customer added successfully!', 'success')
            return redirect(url_for('receptionist'))  # Redirect to receptionist page
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding customer: {str(e)}', 'error')
            return redirect(url_for('add_customer', room_no=room_no))

    return render_template('add_customer.html', room=room)

# User Page Route
@app.route('/user_page', methods=['GET', 'POST'])
def user_page():
    # Fetch the customer_id from the session or form data
    customer_id = session.get('user_id')  # Assuming customer_id is stored in the session after login
    
    try:
        # Fetch customer details based on customer_id
        customer = Customer.query.get(customer_id)
        
        if not customer:
            flash('Customer not found.', 'error')
            return redirect(url_for('login'))
        
        # Fetch booked room details for the customer
        booked_room = Room.query.filter_by(customer_id=customer_id).first()  # Assuming room has a customer_id field
        
        # Fetch pickup/drop requests for the customer
        pickup_drop_requests = PickupDropService.query.filter_by(customer_id=customer_id).all()

        return render_template('User.html', customer=customer, booked_room=booked_room, pickup_drop_requests=pickup_drop_requests)
    except SQLAlchemyError as e:
        flash(f'Error fetching data: {str(e)}', 'error')
        return redirect(url_for('login'))



# Delete Customer Route
@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    try:
        # Fetch the customer using the provided ID
        customer = Customer.query.get(customer_id)
        
        if customer:
            # Fetch the room associated with this customer, if any
            room = Room.query.filter_by(customer_id=customer.customer_id).first()
            
            if room:
                # Mark the room as vacant and remove the customer association
                room.room_status = 'Vacant'  # Update to your RoomStatusEnum value if needed
                room.customer_id = None  # Clear the customer association
            
            # Delete the customer record from the database
            db.session.delete(customer)
            
            # Commit the changes to the database
            db.session.commit()
            
            # Display success message
            flash('Customer record deleted and room vacated.', 'success')
        else:
            # If customer is not found, display error message
            flash('Customer not found.', 'error')
    
    except SQLAlchemyError as e:
        # Rollback the transaction in case of an error
        db.session.rollback()
        flash(f'Error deleting customer: {str(e)}', 'error')
    
    # Redirect back to the receptionist page after the action is completed
    return redirect(url_for('receptionist'))

@app.route('/request_pickup_drop', methods=['POST'])
def request_pickup_drop():
    customer_id = request.form.get('customerId')  # Accept customer_id directly
    pickup_location = "Hotel Name"  # Static
    drop_location = "Wadala Station"  # Static

    # Fetch customer based on the provided customer ID
    customer = Customer.query.get(customer_id)

    if not customer:
        flash('Customer not found. Please check the customer ID.', 'error')
        return redirect(url_for('user_page'))

    new_request = PickupDropService(
        pickup_location=pickup_location,  # Use lowercase attribute name
        drop_service_location=drop_location,  # Use lowercase attribute name
        pickup_drop_service_time=datetime.now().time(),  # Use lowercase attribute name
        customer_id=customer.customer_id  # Use lowercase attribute name
    )
    
    try:
        db.session.add(new_request)
        db.session.commit()
        flash('Pickup/Drop request submitted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating pickup/drop request: {e}")
        flash('Error submitting request. Please try again.', 'error')

    return redirect(url_for('user_page'))

@app.route('/accept_pickup_request/<int:request_id>', methods=['POST'])
def accept_pickup_request(request_id):
    request_to_accept = PickupDropService.query.get(request_id)
    if request_to_accept:
        request_to_accept.status = 'Accepted'
        db.session.commit()
        flash('Request accepted!', 'success')
    else:
        flash('Request not found!', 'error')
    
    return redirect(url_for('receptionist_page'))

@app.route('/reject_pickup_request/<int:request_id>', methods=['POST'])
def reject_pickup_request(request_id):
    request_to_reject = PickupDropRequest.query.get(request_id)
    if request_to_reject:
        request_to_reject.status = 'Rejected'
        db.session.commit()
        flash('Request rejected!', 'success')
    else:
        flash('Request not found!', 'error')
    
    return redirect(url_for('receptionist_page'))

@app.route('/request_room_service', methods=['POST'])
def request_room_service():
    customer_id = request.form['customerId']
    room_no = request.form['roomNo']
    service_type = request.form['serviceType']

    # Create a new RoomService request
    room_service_request = RoomService(
        service_type=service_type,
        room_no=room_no,
        customer_id=customer_id,  # Assuming you have customer_id in the RoomService model
    )

    db.session.add(room_service_request)
    db.session.commit()

    flash('Room service request submitted successfully!', 'success')
    return redirect(url_for('user_page'))  


@app.route('/report_lost_item', methods=['POST'])
def report_lost_item():
    item_name = request.form['item_name']
    customer_id = request.form['customer_id']
    room_no = request.form['room_no']
    
    # Here, you can add logic to save this information to the database
    new_lost_item = LostItem(item_name=item_name, customer_id=customer_id)
    db.session.add(new_lost_item)
    db.session.commit()
    
    flash('Lost item reported successfully!', 'success')
    return redirect(url_for('user_page'))

@app.route('/delete_lost_item/<int:item_id>', methods=['POST'])
def delete_lost_item(item_id):
    lost_item = LostItem.query.get(item_id)
    if lost_item:
        db.session.delete(lost_item)
        db.session.commit()
        flash('Lost item record deleted successfully!', 'success')
    else:
        flash('Lost item not found!', 'error')

    return redirect(url_for('housekeeping'))  # Redirect to the housekeeping page or another appropriate location


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    customer_id = request.form['customer_id']
    feedback_text = request.form['feedback']

    # Ensure the customer exists before adding feedback
    customer = Customer.query.filter_by(customer_id=customer_id).first()

    if customer:
        feedback = Feedback(
            feedback_text=feedback_text,
            customer_id=customer.customer_id,
            # Assuming Manager_id is set to a specific value or fetched from the session
            manager_id=None  # or fetch accordingly
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
    else:
        flash('Customer not found.', 'error')

    return redirect(url_for('user_page'))  # Redirect back to the manager page

# Define the /book_room route
@app.route('/book_room', methods=['POST'])
def book_room():
    data = request.get_json()
    
    # Extract data from the request
    room_no = data.get('room_no')
    customer_name = data.get('customer_name')
    customer_address = data.get('customer_address')
    customer_dob = data.get('customer_dob')
    customer_age = data.get('customer_age')
    customer_mobile_no = data.get('customer_mobile_no')

    # Validate incoming data
    if not all([room_no, customer_name, customer_address, customer_dob, customer_age, customer_mobile_no]):
        return jsonify(success=False, message="All fields are required."), 400

    # Perform your booking logic here
    try:
        customer_id = insert_customer_and_book_room(
            room_no, customer_name, customer_address, customer_dob, customer_age, customer_mobile_no
        )
        return jsonify(success=True, message="Room booked successfully!", customer_id=customer_id), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

def insert_customer_and_book_room(room_no, customer_name, customer_address, customer_dob, customer_age, customer_mobile_no):
    # Check if the room exists and is available
    room = Room.query.filter_by(room_no=room_no).first()
    if not room:
        raise Exception("Room not found.")

    if room.room_status != RoomStatusEnum.Vacant:
        raise Exception("Room is already booked.")

    # Parse and validate customer_dob
    try:
        customer_dob_parsed = datetime.strptime(customer_dob, '%Y-%m-%d').date()
    except ValueError:
        raise Exception("Invalid date format. Please use YYYY-MM-DD.")

    # Create a new customer object
    new_customer = Customer(
        customer_name=customer_name,
        customer_address=customer_address,
        customer_dob=customer_dob_parsed,
        customer_age=int(customer_age),
        customer_mobile_no=customer_mobile_no
    )

    try:
        # Start a database transaction
        db.session.add(new_customer)
        db.session.flush()  # Flush to assign customer_id

        # Update the room status to 'Occupied' and associate it with the customer
        room.room_status = RoomStatusEnum.Occupied
        room.customer_id = new_customer.customer_id

        db.session.commit()  # Commit changes to the database
        return new_customer.customer_id
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception("Error inserting customer or booking room: " + str(e))


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
