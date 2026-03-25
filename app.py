from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔹 Full schools API
FULL_API_URL = "https://devsmartschoolapi.myclassboard.com/api/SmartSchool/MCBGetAllSchools"

# 🔹 Cache
cached_schools = None


# 🔍 SEARCH SCHOOLS API
@app.route('/search-schools', methods=['GET'])
def search_schools():
    global cached_schools

    # ✅ Get params safely
    name = request.args.get('name')
    city = request.args.get('city')
    state = request.args.get('state')

    # ✅ Normalize (avoid None issues)
    name = name.lower().strip() if name else ""
    city = city.lower().strip() if city else ""
    state = state.lower().strip() if state else ""

    print("🔍 INPUT:", name, city, state)

    try:
        # ✅ Fetch API once (cache)
        if cached_schools is None:
            print("📡 Fetching schools from API...")
            response = requests.get(FULL_API_URL, timeout=10)
            data = response.json()

            # ✅ Handle list or nested structure
            if isinstance(data, dict):
                cached_schools = data.get("data", [])
            else:
                cached_schools = data

        results = []

        for s in cached_schools:
            school_name = str(s.get("schoolName", "")).lower()
            address = str(s.get("address", "")).lower()

            # 🔴 STRICT NAME FILTER (MANDATORY)
            if name:
                if name not in school_name:
                    continue

            # 🔴 STRICT CITY FILTER
            if city:
                if city not in address:
                    continue

            # 🔴 STRICT STATE FILTER
            if state:
                if state not in address:
                    continue

            results.append({
                "schoolID": s.get("schoolID"),
                "schoolName": s.get("schoolName", "").strip(),
                "address": s.get("address", "")
            })

        print(f"✅ Found {len(results)} matching schools")

        # ✅ If nothing found
        if not results:
            return jsonify([])

        # ✅ Return top 5
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
