from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔹 Your full schools API
FULL_API_URL = "https://devsmartschoolapi.myclassboard.com/api/SmartSchool/MCBGetAllSchools"

# 🔹 Cache
cached_schools = None


# 🔍 SEARCH SCHOOLS API
@app.route('/search-schools', methods=['GET'])
def search_schools():
    global cached_schools

    name = request.args.get('name', '').lower().strip()
    city = request.args.get('city', '').lower().strip()
    state = request.args.get('state', '').lower().strip()

    try:
        # ✅ Fetch & cache API data
        if cached_schools is None:
            response = requests.get(FULL_API_URL, timeout=10)
            cached_schools = response.json()

        results = []

        for s in cached_schools:
            school_name = s.get("schoolName", "").lower()
            address = s.get("address", "").lower()

            # ✅ Matching logic
            name_match = name in school_name if name else True
            city_match = city in address if city else True
            state_match = state in address if state else True

            if name_match and city_match and state_match:
                results.append({
                    "schoolID": s.get("schoolID"),
                    "schoolName": s.get("schoolName", "").strip(),
                    "address": s.get("address", "")
                })

        # ✅ Limit results to 5
        return jsonify(results[:30])

    except Exception as e:
        return jsonify({
            "error": "Failed to fetch schools",
            "details": str(e)
        }), 500


# Health check
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "School Middleware is running"})


# 🚀 Run server
if __name__ == '__main__':
    app.run(port=4000, debug=True)