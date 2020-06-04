# Django Web Project
This folder contains the Django web project which makes use of the FaiRDy-Py package to run simulations of storage system life cycles.

## accounts Django application
The 'accounts' subdirectory contains the Django application of the same name, used to manage user accounts on the web framework. This functionality is disabled by default in the project's settings.py module.

## fairdy Django application
The 'fairdy' subdirectory contains another Django application, also of the same name as the directory, which processes the storage system simulations storing and displaying the results.

## Running the FaiRDy Web Project locally
1. Clone this repository
2. Prepare and activate a Python virtual environment with Django, Matplotlib, and NumPy installed.
3. Navigate to /fairdy-py/web/ and run the command 'python manage.py runserver'
4. Check out docs.djangoproject.com for further details
