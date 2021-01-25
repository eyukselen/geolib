from math import radians, cos, sin, asin, sqrt
import csv 
import datetime
import random
import json

time_start = datetime.datetime.now()

# create random users 
users = [] #['userID', 'lat', 'lng'] 
for x in range(1000):
    userId = 10000 + x
    lat = random.uniform(0, 180) - 90
    lng = random.uniform(0, 360) - 180
    users.append([userId, lat, lng])

# get some cities with coords. 
with open('capitals.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader, None) # skip header line
    capitals = list(reader)


def getDistanceFromLatLng(lat1, lng1, lat2, lng2, miles=False): # use decimal degrees
    r = 6371 # radius of the earth in km
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lat_dif = lat2 - lat1
    lng_dif=radians(lng2 - lng1)
    a = sin(lat_dif / 2.0) ** 2 + cos(lat1) * cos(lat2) * sin(lng_dif / 2.0) ** 2
    d = 2 * r * asin(sqrt(a))
    return d # this is by kilometre

# get the closest city for user
user_cities = []
for user in users:
    userid = user[0]
    try:
        lat = user[1]
        lng = user[2]
    except:
        print(user)
        exit()
    dist = []
    for city in capitals:
        clat = float(city[2])
        clng = float(city[3])
        cdist = getDistanceFromLatLng(lat, lng, clat, clng)
        dist.append(cdist)
    index_min = min(range(len(dist)), key=dist.__getitem__)
    user_cities.append(user + capitals[index_min][:2])


def isIntersect(point1, point2, point3, point4):
    con1 = 1 if max(point3[0], point4[0]) > point1[1] else 0 
    con3 = 1 if  min(point3[1], point4[1]) < point1[0] < max(point3[1], point4[1]) else 0
    res = 0
    if con1 + con3 == 2:
        res = 1
    return res


def isInPoly(polygon, point):
    c1 = [point[0], point[1]]
    c2 = [point[0], 180]
    intersects = 0
    for x in range(len(polygon) - 2):
        p1 = polygon[x]
        p2 = polygon[x + 1]
        if isIntersect(c1, c2, p1, p2):
            intersects += 1
    return False if (intersects % 2) == 0 else True

# find the country code for user location
with open('countries.geojson','r') as f:
    data = json.load(f)

def findCountry(point):
    res = None
    multipoly = False
    for country in data['features']:
        name = country['properties']['ISO_A3']
        if country['geometry']['type'] == 'Polygon':
            multipoly = False
        elif country['geometry']['type'] == 'MultiPolygon':
            multipoly = True
        polygon = country['geometry']['coordinates']
        if multipoly:
            for poly in polygon:
                subpoly = poly[0]
                if isInPoly(subpoly, point):
                    res = name
                    break
        else:
            if isInPoly(polygon[0], point):
                res = name
        if res:
            break
    return res

user_cc = []
for user in user_cities:
    userId = user[0]
    point = [user[1], user[2]]
    country = str(findCountry(point))
    user_cc.append( user + [country])

with open('users.csv','w', newline='') as f:
    wr = csv.writer(f, dialect='excel', )
    wr.writerows(user_cc)

time_finish = datetime.datetime.now()
print(time_finish-time_start)
# 0:03:36.237099

