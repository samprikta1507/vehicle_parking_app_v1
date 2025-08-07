# vehicle_parking_app_v1
# Steps for setup git
1) install git cli on windows
2) Create git account using iitm mail id
3) Create new repository on github.com as private
4) clone the repository to local system
5) use VS code to start implementation

# 🚗 Vehicle Parking App - V1

A smart and user-friendly web application to manage vehicle parking efficiently. Designed for **Admins** to manage lots and **Users** to book spots seamlessly.


---

## 📖 Overview

This application allows admins to create and manage parking lots and lets users book available spots, mark them as occupied or released, and view history. It also automatically calculates parking duration and cost.

There are two types of users:
- **Admin** – Manages parking lots, monitors spot availability, views users and reservations.
- **User** – Books available spots, marks their parking in/out, and views history.

---

## 🚀 Core Features

### 1. 🔐 Login System
- Supports **Admin** and **User** logins.
- **Users can register** and then log in.
- **Admin** uses predefined credentials (no registration required).

### 2. 🛠️ Admin Dashboard
- Add, edit, or delete parking lots.
- **Spots are auto-created** when a lot is added.
- View **spot status** (available/occupied).
- View **user and vehicle info** for occupied spots.
- Access **user details**, **parking history**, and **summary charts**.

### 3. 👤 User Dashboard
- Choose a parking lot; system assigns **first available spot**.
- Mark spot as **occupied** when parking.
- Mark spot as **released** when leaving.
- System calculates **parking cost** based on time.
- View **parking history** and **analytics charts**.

---

## ➕ Additional Features

### ✏️ Edit Profile
- Both **Admin** and **User** can edit profile details.

### 🔍 Search Functionality
- **Admin** can search:
  - By **User ID**
  - By **Location**
  - By **Parking Lot Name**
- **User** can search by:
  - **Location**

---

## 🛠 Tech Stack

### Backend
- Python, Flask, Flask-Login, Flask-RESTful
- Flask-SQLAlchemy & SQLAlchemy ORM
- SQLite (Database)

### Frontend
- HTML5, CSS3, Bootstrap
- Jinja2 Template Engine
- Chart.js (For data visualization)

---

## 🧩 Database Schema

- **User**: name, email, address, pincode, password  
- **Parking_lot**: name, address, pin code, price, max spots  
- **Parking_spot**: status (available/occupied), lot_id  
- **Reservation**: user_id, lot_id, spot_id, car_no, start_time, end_time, cost  

---
## 📁 Project Structure

- ├── backend/
- │ ├── models.py
- │ ├── controllers.py
- │ └── api_controllers.py
- ├── instance/
- │ └── vehicle_parking.sqlite3
- ├── static/
- │ ├── images/
- │ └── styles/
- ├── templates/
- │ └── *.html
- ├── app.py
- ├── requirements.txt
- └── README.md

## 🧩 Entity Relationship Diagram

![ER Diagram](static/images/er%20diagram%20(3).png)

## API Endpoints

### 👥 User APIs

- `GET /api/get_users` – List all users
- `POST /api/add_user` – Add a new user
- `PUT /api/edit_user/<id>` – Edit user details
- `DELETE /api/delete_user/<id>` – Delete a user
- `GET /api/get_user/<id>` – Get single user info

### 🏢 Parking Lot APIs

- `GET /api/get_lots` – List all parking lots
- `POST /api/add_lot` – Add a new parking lot
- `PUT /api/edit_lot/<id>` – Edit parking lot details
- `DELETE /api/delete_lot/<id>` – Delete a parking lot
- `GET /api/search_lot/<id>` – Get a single parking lot

### 🧱 Parking Spot APIs

- `GET /api/get_spots` – List all parking spots
- `POST /api/add_spot` – Add a new spot
- `PUT /api/edit_spot/<id>` – Edit spot
- `DELETE /api/delete_spot/<id>` – Delete spot
- `GET /api/search_spot/<id>` – Get spot by ID

### 📆 Reservation APIs

- `GET /api/get_reservations` – List all reservations
- `POST /api/add_reservation` – Add new reservation
- `DELETE /api/delete_reservation/<id>` – Cancel reservation
- `GET /api/search_reservation/<id>` – View reservation details

---

## 🎥 Project Demo

[Click here to watch the demo video](https://youtu.be/gJlxv_IhPjI?si=Ak3hDGZWHMnbol8N)


