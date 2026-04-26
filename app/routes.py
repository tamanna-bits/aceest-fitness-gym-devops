from flask import Blueprint, jsonify, request

gym_routes = Blueprint("gym_routes", __name__)

members = []

VALID_MEMBERSHIPS = {"Basic", "Premium", "VIP"}

# ── Health ──────────────────────────────────────────────────────────────
@gym_routes.route("/")
def home():
    return jsonify({"message": "ACEest Fitness & Gym API Running", "version": "1.0"})


@gym_routes.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


# ── Members ──────────────────────────────────────────────────────────────
@gym_routes.route("/members", methods=["POST"])
def add_member():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["name", "age", "membership"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if not isinstance(data["age"], int) or data["age"] <= 0:
        return jsonify({"error": "Age must be a positive integer"}), 400

    if data["membership"] not in VALID_MEMBERSHIPS:
        return jsonify({"error": f"Invalid membership type. Must be one of: {sorted(VALID_MEMBERSHIPS)}"}), 400

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
    return jsonify(members), 200


@gym_routes.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = next((m for m in members if m["id"] == member_id), None)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(member), 200


@gym_routes.route("/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = next((m for m in members if m["id"] == member_id), None)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    member.update({k: v for k, v in data.items() if k != "id"})
    return jsonify(member), 200


@gym_routes.route("/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    global members
    before = len(members)
    members = [m for m in members if m["id"] != member_id]

    if len(members) == before:
        return jsonify({"error": "Member not found"}), 404

    return jsonify({"message": f"Member {member_id} deleted"}), 200
