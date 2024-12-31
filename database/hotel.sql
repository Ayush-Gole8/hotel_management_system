-- Drop existing tables
DROP TABLE IF EXISTS Pickup_Drop_Service CASCADE;
DROP TABLE IF EXISTS Lost_Item CASCADE;
DROP TABLE IF EXISTS Staff_Performance CASCADE;
DROP TABLE IF EXISTS Feedback CASCADE;
DROP TABLE IF EXISTS Room_Service CASCADE;
DROP TABLE IF EXISTS Housekeeping CASCADE;
DROP TABLE IF EXISTS Receptionist CASCADE;
DROP TABLE IF EXISTS Manager CASCADE;
DROP TABLE IF EXISTS Employee CASCADE;
DROP TABLE IF EXISTS Payment CASCADE;
DROP TABLE IF EXISTS Room CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;
DROP TABLE IF EXISTS Hotel CASCADE;

-- Create ENUM type for Room Status
CREATE TYPE room_status AS ENUM ('Vacant', 'Occupied', 'Cleaning');
CREATE TYPE request_type AS ENUM ('Pickup', 'Drop');
CREATE TYPE request_status AS ENUM ('Pending', 'Accepted', 'Rejected');
CREATE TYPE service_type_enum AS ENUM ('Room Cleaning', 'Food Delivery', 'Laundry', 'Wake-up Call');

-- Hotel table
CREATE TABLE Hotel (
  Hotel_id SERIAL PRIMARY KEY,
  Hotel_name VARCHAR(255) NOT NULL,
  Hotel_location VARCHAR(200) NOT NULL
);

-- Customer table
CREATE TABLE Customer (
  Customer_id SERIAL PRIMARY KEY,
  Customer_name VARCHAR(255) NOT NULL,
  Customer_Address TEXT,
  Customer_DOB DATE NOT NULL,
  Customer_Age INT,
  Customer_Mobile_no VARCHAR(15) NOT NULL
);

-- Employee table
CREATE TABLE Employee (
  Employee_id SERIAL PRIMARY KEY,
  Employee_name VARCHAR(255) NOT NULL,
  Employee_Address TEXT,
  Employee_Job_Desc TEXT,
  Employee_mobile_no VARCHAR(15) NOT NULL,
  Hotel_id INT,
  CONSTRAINT fk_hotel FOREIGN KEY (Hotel_id) REFERENCES Hotel (Hotel_id) ON DELETE SET NULL
);

-- Manager table inherits from Employee
CREATE TABLE Manager (
  Manager_id SERIAL PRIMARY KEY,
  Manager_Department VARCHAR(255),
  Employee_id INT UNIQUE,
  CONSTRAINT fk_employee FOREIGN KEY (Employee_id) REFERENCES Employee (Employee_id) ON DELETE CASCADE
);

-- Receptionist table inherits from Employee
CREATE TABLE Receptionist (
  Receptionist_id SERIAL PRIMARY KEY,
  Receptionist_Staff_timing TIME,
  Employee_id INT UNIQUE,
  CONSTRAINT fk_employee FOREIGN KEY (Employee_id) REFERENCES Employee (Employee_id) ON DELETE CASCADE
);

-- Housekeeping table inherits from Employee
CREATE TABLE Housekeeping (
  Housekeeping_id SERIAL PRIMARY KEY,
  Housekeeping_roomassigned INT,
  Employee_id INT UNIQUE,
  CONSTRAINT fk_employee FOREIGN KEY (Employee_id) REFERENCES Employee (Employee_id) ON DELETE CASCADE
);

-- Room table with ENUM for Room status
CREATE TABLE Room (
  Room_no SERIAL PRIMARY KEY,
  Room_rates INT,
  Room_status room_status NOT NULL,
  Hotel_id INT,
  Customer_id INT,
  Receptionist_id INT,
  Housekeeping_id INT,
  Manager_id INT,
  CONSTRAINT fk_hotel FOREIGN KEY (Hotel_id) REFERENCES Hotel (Hotel_id) ON DELETE CASCADE,
  CONSTRAINT fk_customer FOREIGN KEY (Customer_id) REFERENCES Customer (Customer_id) ON DELETE SET NULL,
  CONSTRAINT fk_receptionist FOREIGN KEY (Receptionist_id) REFERENCES Receptionist (Receptionist_id) ON DELETE SET NULL,
  CONSTRAINT fk_housekeeping FOREIGN KEY (Housekeeping_id) REFERENCES Housekeeping (Housekeeping_id) ON DELETE SET NULL,
  CONSTRAINT fk_manager FOREIGN KEY (Manager_id) REFERENCES Manager (Manager_id) ON DELETE SET NULL
);

-- Payment table
CREATE TABLE Payment (
  Payment_no SERIAL PRIMARY KEY,
  Payment_Date DATE NOT NULL,
  Payment_method VARCHAR(255),
  Payment_Amount INT,
  Customer_id INT,
  CONSTRAINT fk_customer FOREIGN KEY (Customer_id) REFERENCES Customer (Customer_id) ON DELETE CASCADE
);

-- Room Service table
CREATE TABLE Room_Service (
  Service_id SERIAL PRIMARY KEY,
  Service_Type VARCHAR(50) NOT NULL,  -- Changed from ENUM to VARCHAR
  Customer_id INT,
  Receptionist_id INT,
  Room_no INT,
  Status VARCHAR(50) NOT NULL,
  CONSTRAINT fk_customer FOREIGN KEY (Customer_id) REFERENCES Customer (Customer_id) ON DELETE CASCADE,
  CONSTRAINT fk_receptionist FOREIGN KEY (Receptionist_id) REFERENCES Receptionist (Receptionist_id) ON DELETE CASCADE,
  CONSTRAINT fk_room FOREIGN KEY (Room_no) REFERENCES Room (Room_no) ON DELETE CASCADE
);


-- Feedback table
CREATE TABLE Feedback (
  Feedback_id SERIAL PRIMARY KEY,
  Customer_id INT,
  Feedback_type VARCHAR(255),
  Manager_id INT,
  CONSTRAINT fk_customer FOREIGN KEY (Customer_id) REFERENCES Customer (Customer_id) ON DELETE CASCADE,
  CONSTRAINT fk_manager FOREIGN KEY (Manager_id) REFERENCES Manager (Manager_id) ON DELETE SET NULL
);

-- Staff Performance table
CREATE TABLE Staff_Performance (
  Staff_id SERIAL PRIMARY KEY,
  Staff_name VARCHAR(255) NOT NULL,
  Staff_grade CHAR(1),
  Manager_id INT,
  CONSTRAINT fk_manager FOREIGN KEY (Manager_id) REFERENCES Manager (Manager_id) ON DELETE SET NULL
);

-- Lost Item table
CREATE TABLE Lost_Item (
    Item_id SERIAL PRIMARY KEY,
    Item_Name VARCHAR(255) NOT NULL,
    Room_no INT,
    Customer_id INT,
    Status VARCHAR(50) DEFAULT 'Reported',
    CONSTRAINT fk_customer FOREIGN KEY (Customer_id) REFERENCES Customer (Customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_room FOREIGN KEY (Room_no) REFERENCES Room (Room_no) ON DELETE CASCADE
);


-- Pickup Drop Service table
-- Pickup Drop Service table
CREATE TABLE Pickup_Drop_Service (
  Pickup_Drop_Service_id SERIAL PRIMARY KEY,
  Pickup_location VARCHAR(255) NOT NULL,
  Drop_Service_location VARCHAR(255) NOT NULL,
  Pickup_Drop_Service_time TIME NOT NULL,
  Customer_id INT NOT NULL,
  Receptionist_id INT,
  status VARCHAR(20) NOT NULL DEFAULT 'Pending',  -- Changed to VARCHAR
  timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_customer_pickupdrop FOREIGN KEY (Customer_id) REFERENCES Customer (Customer_id) ON DELETE CASCADE,
  CONSTRAINT fk_receptionist_pickupdrop FOREIGN KEY (Receptionist_id) REFERENCES Receptionist (Receptionist_id) ON DELETE CASCADE
);

CREATE TABLE booking_request (
    request_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_mobile VARCHAR(15),
    room_no VARCHAR(10),
    status VARCHAR(20), -- Change this to ENUM if using ENUM in PostgreSQL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Sample Insertions
BEGIN;

-- Hotel data
INSERT INTO Hotel (Hotel_name, Hotel_location)
VALUES ('Hotel California', 'Mumbai'),
       ('Grand Palace', 'Delhi');

-- Customer data
INSERT INTO Customer (Customer_name, Customer_Address, Customer_DOB, Customer_Age, Customer_Mobile_no)
VALUES ('Alice', '123 Main St', '2000-01-01', 24, '9999888822'),
       ('Bob', '456 Elm St', '2001-02-02', 23, '9999777766');

-- Employee data
INSERT INTO Employee (Employee_name, Employee_Address, Employee_Job_Desc, Employee_mobile_no, Hotel_id)
VALUES ('John Doe', '789 Pine St', 'Receptionist', '9999666655', 1),
       ('Jane Smith', '321 Oak St', 'Housekeeper', '9999555544', 1);

COMMIT;
-- Insert sample employees
INSERT INTO Employee (Employee_id,Employee_name, Employee_Address, Employee_Job_Desc, Employee_mobile_no, Hotel_id)
VALUES 
(1,'John Smith', '123 Main St, City', 'Oversees hotel operations', '555-1234', 1),   -- Manager
(2,'Emily Brown', '456 Oak St, City', 'Front desk receptionist', '555-5678', 1);     -- Receptionist

-- Insert a manager
INSERT INTO Manager (Manager_Department, Employee_id)
VALUES ('Hotel Operations', 1);  -- Employee_id 1 is John Smith

-- Insert a receptionist
INSERT INTO Receptionist (Receptionist_Staff_timing, Employee_id)
VALUES ('09:00:00', 2);  -- Employee_id 2 is Emily Brown


-- Truncate Room table
TRUNCATE TABLE Room;

-- Select from Room table
SELECT * FROM Room_Service;
SELECT * FROM Pickup_Drop_Service;
select * from Manager;
select * from Receptionist;
select * from Employee;
-- Update Room rates to be no more than 20000
UPDATE Room
SET Room_rates = 20000
WHERE Room_rates > 20000;
SELECT unnest(enum_range(NULL::service_type_enum));
DROP TYPE IF EXISTS service_type_enum cascade;
CREATE TYPE service_type_enum AS ENUM ('Room Cleaning', 'Food Delivery', 'Laundry', 'Wake-up Call');
select * from Lost_Item;
SELECT * FROM Customer;

select * from Room;
select * from Receptionist;
select * from Employee;
insert into employee (employee_id,employee_name,employee_address)