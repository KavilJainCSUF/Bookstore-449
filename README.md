# Bookstore-449

## Team 7
* Kavil Jain
* Aunj Patel
* Ali Omrani

## Steps to install project in your local (for Windows):
* Download the zip file of this project from the master branch.
* Create a virtual environment in a local folder where the project is extracted. ***(python -m venv venv)***
* Activate the virtualEnv. ***(venv\Scripts\activate)***
* Install all libraries from **requirements.txt** file. ***(pip install -r requirements.txt)***
* Install MongoDB Compass, connect the MongoDB server and add dummy bookstore data. (fields - title, author, description, price, stock)
* Run the project. ***(uvicorn app:app --reload)***
* In your browser, route to **localhost:8000/docs**. Now you can test all the APIs implemented in the project.


