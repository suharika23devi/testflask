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

    print("🔍 INPUT:", name, city, state)  # ✅ Debug log

    try:
        # ✅ Fetch & cache API data
        if cached_schools is None:
            print("📡 Fetching schools from API...")
            response = requests.get(FULL_API_URL, timeout=10)
            cached_schools = response.json()

        results = []

        for s in cached_schools:
            school_name = s.get("schoolName", "").lower()
            address = s.get("address", "").lower()

            # 🔴 STRICT NAME FILTER (MANDATORY)
            if name and name not in school_name:
                continue

            # 🔴 STRICT CITY FILTER
            if city and city not in address:
                continue

            # 🔴 STRICT STATE FILTER
            if state and state not in address:
                continue

            results.append({
                "schoolID": s.get("schoolID"),
                "schoolName": s.get("schoolName", "").strip(),
                "address": s.get("address", "")
            })

        print(f"✅ Found {len(results)} matching schools")

        # ✅ Return top 5 only
        return jsonify(results[:5])

    except Exception as e:
        print("❌ ERROR:", str(e))
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
