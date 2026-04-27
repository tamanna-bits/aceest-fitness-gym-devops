from flask import Blueprint, jsonify, request

gym_routes = Blueprint("gym_routes", __name__)

members = []

VALID_MEMBERSHIPS = {"Basic", "Premium", "VIP"}

programs = {
    "Fat Loss (FL)": {
        "calorie_factor": 22,
        "description": "HIIT + Deficit Diet",
        "allowed_memberships": {"Premium", "VIP"},
    },
    "Muscle Gain (MG)": {
        "calorie_factor": 35,
        "description": "Strength + Surplus Diet",
        "allowed_memberships": {"VIP"},
    },
    "Beginner (BG)": {
        "calorie_factor": 26,
        "description": "Full Body Circuit + Balanced Diet",
        "allowed_memberships": {"Basic", "Premium", "VIP"},
    },
}


def get_available_programs(membership: str) -> dict:
    """Return programs accessible to a given membership tier."""
    if membership not in VALID_MEMBERSHIPS:
        raise ValueError(f"Invalid membership: '{membership}'. Must be one of {VALID_MEMBERSHIPS}")
    return {
        name: details
        for name, details in programs.items()
        if membership in details["allowed_memberships"]
    }


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

    required = ["name", "age", "membership", "program"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    if not isinstance(data["age"], int) or data["age"] <= 0:
        return jsonify({"error": "Age must be a positive integer"}), 400

    if data["membership"] not in VALID_MEMBERSHIPS:
        return jsonify({"error": f"Invalid membership. Must be one of: {sorted(VALID_MEMBERSHIPS)}"}), 400

    if data["program"] not in programs:
        return jsonify({"error": f"Invalid program. Must be one of: {list(programs.keys())}"}), 400

    if data["membership"] not in programs[data["program"]]["allowed_memberships"]:
        return jsonify({"error": f"'{data['program']}' is not available for {data['membership']} members"}), 403

    calorie_factor = programs[data["program"]]["calorie_factor"]
    weight = data.get("weight", 70)

    member = {
        "id": len(members) + 1,
        "name": data["name"],
        "age": data["age"],
        "weight": weight,
        "membership": data["membership"],
        "program": data["program"],
        "calories": int(weight * calorie_factor),
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

# ── Programs ─────────────────────────────────────────────────────────────
def get_available_programs(membership: str) -> dict:
    """Return programs accessible to a given membership tier."""
    if membership not in VALID_MEMBERSHIPS:
        raise ValueError(f"Invalid membership: '{membership}'. Must be one of {VALID_MEMBERSHIPS}")
    return {
        name: details
        for name, details in programs.items()
        if membership in details["allowed_memberships"]
    }


@gym_routes.route("/programs/<program_name>/calories", methods=["GET"])
def calc_calories(program_name):
    weight = request.args.get("weight", type=float)
    if not weight or weight <= 0:
        return jsonify({"error": "Provide valid ?weight= (kg)"}), 400
    if program_name not in programs:
        return jsonify({"error": "Program not found"}), 404

    program = programs[program_name]
    calories = int(weight * program["calorie_factor"])

    return jsonify({
        "program": program_name,
        "description": program["description"],
        "weight_kg": weight,
        "calories_kcal": calories,
        "allowed_memberships": sorted(program["allowed_memberships"]),
    }), 200