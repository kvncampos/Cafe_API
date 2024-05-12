from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Integer, String, Boolean, func, select
from icecream import ic
from os import getenv
from route_utils.route_helpers import get_cafe_response, many_responses, new_cafe_check
from dotenv import load_dotenv, dotenv_values 
'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
# loading variables from .env file
load_dotenv() 

SECRET_API = getenv('SECRET_API')

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    """
    A class representing a Cafe.

    Attributes:
        id (int): The unique identifier of the cafe.
        name (str): The name of the cafe.
        map_url (str): The URL of the cafe's location on a map.
        img_url (str): The URL of the cafe's image.
        location (str): The location of the cafe.
        seats (str): The seating capacity of the cafe.
        has_toilet (bool): Indicates if the cafe has a toilet.
        has_wifi (bool): Indicates if the cafe has WiFi.
        has_sockets (bool): Indicates if the cafe has power sockets.
        can_take_calls (bool): Indicates if the cafe can take phone calls.
        coffee_price (str): The price range of the coffee served in the cafe.
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/api/random', methods=['GET'])
def random_cafe():
    """
    Get a random cafe from the database.

    Returns:
        - If a random cafe is found in the database, returns a JSON response with the cafe details.
        - If no cafes are found in the database, returns a JSON response with an error message and a 404 status code.
    """
    random_cafe = db.session.execute(db.select(Cafe).order_by(db.func.random())).scalars().first()
    if random_cafe is None:
        return jsonify(error={"Not Found": "No cafes found in the database"}), 404
    else:
        # Use Response Model for GET Request Output
        return jsonify(cafe=get_cafe_response(random_cafe)), 200
    
# HTTP GET - Read All Records
@app.route('/api/all', methods=['GET'])
def all_cafes():
    """
    Get all cafes from the database.

    Returns:
        A JSON response containing information about all cafes.
    """
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars()
    return many_responses(all_cafes)

# HTTP GET - Find A Record
@app.route('/api/search', methods=['GET'])
def search_cafe():
    """
    Searches for cafes based on the provided location.

    Parameters:
    - loc (str): The location to search for cafes.

    Returns:
    - str: A JSON response containing information about the cafes found.

    Example:
        >>> search_cafe()
        {
            "cafes": [
                {
                    "id": 1,
                    "name": "Cafe A",
                    "map_url": "https://maps.google.com/cafeA",
                    "img_url": "https://cafeA.com/image.jpg",
                    "location": "City A",
                    "seats": "50",
                    "has_toilet": true,
                    "has_wifi": true,
                    "has_sockets": true,
                    "can_take_calls": false,
                    "coffee_price": "$3.50"
                },
                {
                    "id": 2,
                    "name": "Cafe B",
                    "map_url": "https://maps.google.com/cafeB",
                    "img_url": "https://cafeB.com/image.jpg",
                    "location": "City A",
                    "seats": "30",
                    "has_toilet": true,
                    "has_wifi": true,
                    "has_sockets": true,
                    "can_take_calls": true,
                    "coffee_price": "$4.00"
                }
            ]
        }
    """
    loc = request.args.get('loc')
    all_cafes = Cafe.query.filter_by(location = loc).order_by(Cafe.name).all()
    return many_responses(all_cafes)

# HTTP POST - Create Record
@app.route('/api/add', methods=['POST'])
def add_cafe():
    """
    Add a new cafe to the database.

    This function is a Flask route that handles the POST request to add a new cafe to the database. It expects the following parameters in the request form data:
    - name (str): The name of the cafe.
    - map_url (str): The URL of the cafe's location on a map.
    - img_url (str): The URL of an image representing the cafe.
    - loc (str): The location of the cafe.
    - sockets (bool): Whether the cafe has sockets or not.
    - toilet (bool): Whether the cafe has a toilet or not.
    - wifi (bool): Whether the cafe has WiFi or not.
    - calls (bool): Whether the cafe can take calls or not.
    - seats (str): The number of seats available in the cafe.
    - coffee_price (str): The price of coffee in the cafe.

    Returns:
    - If the cafe is successfully added to the database, returns a JSON response with a success message and a status code of 200.
    - If there is an error adding the cafe to the database, returns a JSON response with an error message and a status code of 400. The specific error message depends on the type of error encountered:
    - If there are missing input parameters, the error message will indicate that.
    - If there is a duplicate entry, the error message will indicate that.
    - If there is a general error writing to the database, the error message will indicate that.

    Note:
    - This function uses the SQLAlchemy ORM to interact with the database.
    - It catches any exceptions or integrity errors that occur during the database operations and returns appropriate error messages.
    - It also performs a rollback if an error occurs and closes the database session.
    """
    try:
        new_cafe = new_cafe_check(Cafe)
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(success={"success": "Successfully added the new cafe"}), 200
    
    except (Exception, IntegrityError) as error:
        db.session.rollback()
        error_string = repr(error)

        if "NOT NULL constraint failed" in error_string:
            return jsonify(error={"error": "Missing input parameters"}), 400

        elif "UNIQUE constraint failed" in error_string:
            return jsonify(error={"error": "Duplicate entry"}), 400
        else:
            return jsonify(error={'error': 'Error writing to database'}), 400
    finally:
        # Optional: Close DB connection or perform cleanup actions
        db.session.close()
        
# HTTP PUT/PATCH - Update Record
@app.route('/api/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id: int):
    """
    Update the coffee price for a specific cafe.

    Parameters:
    - cafe_id (int): The ID of the cafe to update the price for.

    Returns:
    - JSON response: A JSON response indicating the success or failure of the update operation.

    """
    # Check if new_price is null
    if not request.args.get('new_price'):
        return jsonify(error={"error": "coffee_price cannot be null."}), 400
    
    # Query cafe_id return 404 with message if not found.
    cafe_query = db.get_or_404(Cafe, cafe_id, description='This ID Does not Exist.')
    if cafe_query:
        # Update coffee_price and commit
        try:
            cafe_query.coffee_price = request.args.get('new_price')
            db.session.commit()
            return jsonify(success={"success": "Successfully added the new cafe"}), 200
        
        # Check for Exceptions if any
        except (Exception, IntegrityError) as error:
            db.session.rollback()
            error_string = repr(error)

            if "NOT NULL constraint failed" in error_string:
                return jsonify(error={"error": "Missing input parameters"}), 400

            elif "UNIQUE constraint failed" in error_string:
                return jsonify(error={"error": "Duplicate entry"}), 400
            else:
                return jsonify(error={'error': 'Error writing to database'}), 400
        finally:
            # Close DB connection or perform cleanup actions
            db.session.close()
            
# HTTP DELETE - Delete Record
@app.route('/api/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id: int):
    # Check if new_price is null
    api_key = request.args.get('api-key')
    if not api_key or api_key != SECRET_API:
        return jsonify(error={"error": "Not Authorized to perform this action."}), 403
    
    # Query cafe_id return 404 with message if not found.
    cafe_query = db.get_or_404(Cafe, cafe_id, description='This ID Does not Exist.')
    if cafe_query:
        # Update coffee_price and commit
        db.session.delete(cafe_query)
        db.session.commit()
        # Close DB connection or perform cleanup actions
        db.session.close()
        return jsonify(success={"success": "Successfully added the new cafe"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
