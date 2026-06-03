import requests
import math
from collections import defaultdict

# ---------------------------------------------------------
# 1. Load all routes from ZwiftHub
# ---------------------------------------------------------
routes_url = "https://zwifthub.com/api/routes"
routes = requests.get(routes_url).json()

# Find Downtown Titans
route = next(r for r in routes if r["name"].lower() == "downtown titans")
world = route["world"]
road_ids = route["roads"]

print(f"Route: {route['name']}")
print(f"World: {world}")
print(f"Road segments: {len(road_ids)}")

# ---------------------------------------------------------
# 2. Load all worlds (contains road geometry)
# ---------------------------------------------------------
worlds_url = "https://zwifthub.com/api/worlds"
worlds = requests.get(worlds_url).json()

# Find the world object
world_obj = next(w for w in worlds if w["slug"] == world)

# Build lookup: road_id → list of points
# Each point contains: lat, lng, elevation (meters)
road_lookup = {r["id"]: r["points"] for r in world_obj["roads"]}

# ---------------------------------------------------------
# 3. Build full elevation profile for the route
# ---------------------------------------------------------
profile = []

for rid in road_ids:
    if rid not in road_lookup:
        continue
    for p in road_lookup[rid]:
        profile.append((p["lat"], p["lng"], p["elevation"]))

print(f"Total points in elevation profile: {len(profile)}")

# ---------------------------------------------------------
# 4. Convert lat/lng → distance using haversine
# ---------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

dist = [0.0]
elev = [profile[0][2]]

for i in range(1, len(profile)):
    lat1, lon1, z1 = profile[i-1]
    lat2, lon2, z2 = profile[i]
    d = haversine(lat1, lon1, lat2, lon2)
    dist.append(dist[-1] + d)
    elev.append(z2)

# Convert distance to km
dist_km = [d / 1000.0 for d in dist]

# ---------------------------------------------------------
# 5. Compute gradients
# ---------------------------------------------------------
gradients = []

for i in range(1, len(dist_km)):
    dx = (dist_km[i] - dist_km[i-1]) * 1000  # meters
    dy = elev[i] - elev[i-1]
    if dx > 0:
        gradients.append((dy / dx) * 100)

# ---------------------------------------------------------
# 6. Build 1% gradient histogram
# ---------------------------------------------------------
hist = defaultdict(float)

for g in gradients:
    bucket = int(round(g))
    hist[bucket] += 1

# ---------------------------------------------------------
# 7. Print histogram
# ---------------------------------------------------------
print("\nGradient Histogram (1% bins):")
for b in sorted(hist.keys()):
    print(f"{b:+d}% : {hist[b]} samples")
