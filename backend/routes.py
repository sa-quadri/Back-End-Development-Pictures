from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    if data:
        return jsonify(data), 200
    else:
        return jsonify({"message": "No data found"}), 404

######################################################################
# GET A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    picture = next((item for item in data if item["id"] == id), None)
    
    if picture is not None:
        return jsonify(picture), 200
    else:
        return jsonify({"message": "Picture not found"}), 404


######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():
    request_data = request.get_json()
    if not request_data:
        return jsonify({"message": "Missing required data"}), 400

    required_fields = ["id", "pic_url", "event_country", "event_state", "event_city", "event_date"]
    if not all(field in request_data for field in required_fields):
        return jsonify({"message": "Missing one or more required fields"}), 400

    new_id = request_data["id"]
    if any(picture["id"] == new_id for picture in data):
        return jsonify({"Message": f"picture with id {new_id} already present"}), 302

    new_picture = {
        "id": new_id,
        "pic_url": request_data["pic_url"],
        "event_country": request_data["event_country"],
        "event_state": request_data["event_state"],
        "event_city": request_data["event_city"],
        "event_date": request_data["event_date"]
    }
    data.append(new_picture)
    
    return jsonify(new_picture), 201

######################################################################
# UPDATE A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    request_data = request.get_json()

    if not request_data:
        return jsonify({"message": "Missing required data"}), 400

    picture = next((item for item in data if item["id"] == id), None)

    if picture:
        picture.update(request_data)
        return jsonify(picture), 200
    else:
        return jsonify({"message": "picture not found"}), 404

######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    global data
    picture = next((item for item in data if item["id"] == id), None)
    if picture:
        data[:] = [item for item in data if item["id"] != id]
        return '', 204
    return jsonify({"message": "Picture not found"}), 404
