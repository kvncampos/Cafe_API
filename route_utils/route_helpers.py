from flask import jsonify, request


def get_cafe_response(cafe):
  """
  This function transforms a Cafe object into a dictionary representation
  suitable for JSON response in the API.

  Args:
      cafe: A Cafe object presumably from your database model.

  Returns:
      A dictionary containing cafe information for the API response.
  """
  response_dict = {
      "name": cafe.name,
      "map_url": cafe.map_url or "N/A",  # Handle missing map_url
      "img_url": cafe.img_url or "N/A",   # Handle missing img_url
      "location": cafe.location,
      "seats": cafe.seats,
      "has_toilet": cafe.has_toilet,
      "has_wifi": cafe.has_wifi,
      "has_sockets": cafe.has_sockets,
      "can_take_calls": cafe.can_take_calls,
      "coffee_price": cafe.coffee_price, 
  }
  return response_dict

def many_responses(all_cafes):
    if not all_cafes:  # Check if list is empty
        return jsonify(error={"Not Found": "No cafes found in the database"}), 404
    else:
        response = [get_cafe_response(cafe) for cafe in all_cafes]
        # Use Response Model for GET Request Output
        return jsonify(cafes=response), 200
    
def new_cafe_check(Cafe_Model):
    new_cafe = Cafe_Model(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    return new_cafe