import math
from datetime import datetime

from math import radians, cos, sin, asin, sqrt
from datetime import datetime
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))



# ⏰ Time Features
def extract_time_features(timestamp):
    dt = datetime.fromisoformat(timestamp)
    hour = dt.hour
    is_night = 1 if hour >= 23 or hour <= 6 else 0
    return hour, is_night
