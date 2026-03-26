from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔹 Your full schools API
FULL_API_URL = "https://devsmartschoolapi.myclassboard.com/api/SmartSchool/MCBGetAllSchools"

# 🔹 Cache
cached_schools = None

# 🔍 SEARCH SCHOOLS API (by name only)
@app.route('/search-schools', methods=['GET'])
def search_schools():
    global cached_schools

    name = request.args.get('name', '').lower().strip()
    if not name:
        return jsonify({"error": "School name is required"}), 400

    try:
        # ✅ Fetch & cache API data
        if cached_schools is None:
            response = requests.get(FULL_API_URL, timeout=10)
            cached_schools = response.json()

        results = []

        for s in cached_schools:
            school_name = s.get("schoolName", "").lower()
            if name in school_name:
                results.append({
                    "schoolID": s.get("schoolID"),
                    "schoolName": s.get("schoolName", "").strip(),
                    "address": s.get("address", "").strip()
                })

        # ✅ Return all matching schools
        return jsonify(results)

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch schools",
            "details": str(e)
        }), 500

# ❤️ Health check
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "School Middleware is running"})

# 🚀 Run server
if __name__ == '__main__':
    app.run(port=4000, debug=True)
