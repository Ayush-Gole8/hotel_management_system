from flask import Flask, request, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newpassword@localhost/hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model definitions
class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String, nullable=False)
    customer_address = db.Column(db.String, nullable=False)
    customer_dob = db.Column(db.Date, nullable=False)
    customer_age = db.Column(db.Integer, nullable=False)
    customer_mobile_no = db.Column(db.String, nullable=False)

class Room(db.Model):
    room_no = db.Column(db.Integer, primary_key=True)
    room_rates = db.Column(db.Integer, nullable=False)
    room_status = db.Column(db.String, nullable=False)

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String, nullable=False)
    employee_address = db.Column(db.String, nullable=False)
    employee_mobile_no = db.Column(db.String, nullable=False)
    employee_job_desc = db.Column(db.String, nullable=False)

# Set index.html as the homepage with role selection
@app.route('/')
def index():
    return render_template('index.html')

# Handle role selection and redirect to the appropriate role page
@app.route('/select_role', methods=['POST'])
def select_role():
    selected_role = request.form['role']
    
    # Redirect based on selected role
    if selected_role == 'manager':
        return redirect(url_for('manager'))
    elif selected_role == 'receptionist':
        return redirect(url_for('receptionist'))
    elif selected_role == 'housekeeping':
        return redirect(url_for('housekeeping'))
    elif selected_role == 'user':
        return redirect(url_for('user'))
    else:
        flash('Invalid role selected!', 'error')
        return redirect(url_for('index'))

# Manager page
@app.route('/manager')
def manager():
    rooms = Room.query.all()  # Get all existing rooms
    employees = Employee.query.all()  # Get all existing employees
    return render_template('Manager.html', rooms=rooms, employees=employees)

# Receptionist page
@app.route('/receptionist')
def receptionist():
    customers = Customer.query.all()  # Get all existing customers for display
    return render_template('Receptionist.html', customers=customers)

# Housekeeping staff page
@app.route('/housekeeping')
def housekeeping():
    return render_template('HouseKeeping_Staff.html')

# User page
@app.route('/user')
def user():
    return render_template('User.html')

# Add Customer (for Receptionist)
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_address = request.form['customer_address']
        customer_dob = request.form['customer_dob']
        customer_age = request.form['customer_age']
        customer_mobile_no = request.form['customer_mobile_no']

        if not all([customer_name, customer_address, customer_dob, customer_age, customer_mobile_no]):
            flash('All fields are required!', 'error')
            return redirect(url_for('add_customer'))

        try:
            customer_dob = datetime.strptime(customer_dob, '%Y-%m-%d').date()
            customer_age = int(customer_age)
        except ValueError:
            flash('Invalid input for date or age!', 'error')
            return redirect(url_for('add_customer'))

        new_customer = Customer(
            customer_name=customer_name,
            customer_address=customer_address,
            customer_dob=customer_dob,
            customer_age=customer_age,
            customer_mobile_no=customer_mobile_no
        )
        
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')

        return redirect(url_for('receptionist'))

    return render_template('add_customer.html')  # Render add_customer.html for GET request

# Add Room (for Manager)
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_no = request.form['room_no']
        room_rates = request.form['room_rates']
        room_status = request.form['room_status']

        if not all([room_no, room_rates, room_status]):
            flash('All fields are required!', 'error')
            return redirect(url_for('manager'))

        new_room = Room(
            room_no=room_no,
            room_rates=room_rates,
            room_status=room_status
        )
        
        db.session.add(new_room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('manager'))

    return redirect(url_for('manager'))

# Add Employee (for Manager)
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        employee_name = request.form['employee_name']
        employee_address = request.form['employee_address']
        employee_mobile_no = request.form['employee_mobile_no']
        employee_job_desc = request.form['employee_job_desc']

        if not all([employee_name, employee_address, employee_mobile_no, employee_job_desc]):
            flash('All fields are required!', 'error')
            return redirect(url_for('manager'))

        new_employee = Employee(
            employee_name=employee_name,
            employee_address=employee_address,
            employee_mobile_no=employee_mobile_no,
            employee_job_desc=employee_job_desc
        )
        
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('manager'))

    return redirect(url_for('manager'))

if __name__ == '__main__':
    app.run(debug=True)
