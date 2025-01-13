# Online Bookstore

An ecommerce platform for buying and selling books online. Built with Django and deployed using AWS EC2, Gunicorn, and Nginx.

## Features

### User Management
- Registration, login, and profile management.

### Book Catalog
- Browse books by category, author, or title.

### Search Functionality
- Search books by keywords.

### Shopping Cart
- Add, update, or remove books from the cart.

### Order Management
- Place orders and view order history.

### Payment Gateway
- Secure payment integration via Razorpay.

### Admin Panel
- Manage books, orders, and users.

---

## Tech Stack

- **Backend:** Django
- **Frontend:** Django Templates, HTML, CSS, JavaScript
- **Database:** PostgreSQL
- **Deployment:** AWS EC2, Gunicorn, Nginx

---

## Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.8
- PostgreSQL
- AWS EC2 instance
- Nginx
- Gunicorn

---

## Installation

### 2. Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate


### 1. Clone the Repository

```bash
git clone https://github.com/rahulxqmoz/ECommerce-Ebookstore.git
cd estore

### 2. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
###3. Install Dependencies
```bash
pip install -r requirements.txt
###4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
###5. Create a Superuser
```bash
python manage.py createsuperuser
###6. Collect Static Files
```bash
python manage.py collectstatic

##Deployment
###1. Set Up AWS EC2 Instance
Launch an EC2 instance (Ubuntu).
Configure security groups to allow HTTP (port 80) and SSH (port 22).
###2. Install Required Software
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
###3. Transfer Project Files to EC2
Clone the Git repository to transfer project files to the EC2 instance.
###4. Set Up Gunicorn
Install Gunicorn:

```bash
pip install gunicorn
Run Gunicorn:
```bash
gunicorn --bind 0.0.0.0:8000 projectname.wsgi:application
###5. Configure Nginx
Create a new Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/online-bookstore
###6. Start Gunicorn as a Service
Create a systemd service file for Gunicorn:
```bash
sudo nano /etc/systemd/system/online-bookstore.service
##Usage
Access the website via the domain or public IP of your EC2 instance.
Admin panel: /admin_home
Start exploring the bookstore!
