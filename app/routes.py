from flask import Blueprint, jsonify, request

gym_routes = Blueprint("gym_routes", __name__)

members = []


@gym_routes.route("/")
def home():
    return jsonify({"message": "ACEest Fitness & Gym API Running"})


@gym_routes.route("/members", methods=["POST"])
def add_member():
    data = request.json
    member = {
        "id": len(members) + 1,
        "name": data["name"],
        "age": data["age"],
        "membership": data["membership"]
    }
    members.append(member)
    return jsonify(member), 201


@gym_routes.route("/members", methods=["GET"])
def get_members():
    return jsonify(members)