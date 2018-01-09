# django-AMS

## Background Information

An assignment management system system built with Django

## Features

- Users can sign in and sign up
- Lecturers can create, edit and delete assignments
- Students can submit assignments
- Students cand edit and delete submissions as long as the due date for the assignment hasn't passed
- Lecturers can grade submitted assignments
- Lecturers can comment on submitted assignments

## Why is this project useful

- Manual assignment management has proven to be inconvenient, inefficient and error-prone especially when working with a large number of students. The process becomes very time consuming and tedious.
- The Assignment Management System will assist lecturers and students in managing the assignment creation and submission process.

## How users can get started with the project

- By cloning this repository

## Dependencies

- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/) 
- [Coverage](https://coverage.readthedocs.io/en/coverage-4.4.2/)


## Installation and Setup

- Navigate to directory of choice on terminal.
- Clone this repository on that directory.

   - Using SSH;

     > git clone git@github.com:Del-sama/django-AMS.git
   - Using HTTP;

     > https://github.com/Del-sama/django-AMS.git
- Navigate  to the repo's folder on your computer.

     > cd django-AMS/

- Ensure you have Python installed.
- Install the app's dependencies using pip
 
     > pip install -r requirements.txt

- Run tests in your terminal.

     > python manage.py test

- Start the application.

     > python manage.py runserver

- This launches the app on your default browser on http://localhost:8000

## How to run tests

- In your terminal, run 
   > python manage.py test

## Limitations of the project

- N/A
