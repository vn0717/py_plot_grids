import numpy as np


def get_data(string):
    start = string.find("=") + 1
    new_string = string[start:]
    new_string = new_string.replace(" ", "")
    new_string = new_string.replace("\'", "")
    new_string = new_string.replace("\"", "")
    new_string = new_string.replace("\n", "")
    
    if new_string.find(",") != -1:
        new_string = new_string.split(",")
        final_data = []
        for i in new_string:
            if i != "":
                final_data.append(i)
                
        
        return final_data
    else:
        return [new_string]
    
def get_var(string):
    start = string.find("=")
    new_string = string[:start]
    new_string = new_string.replace(" ", "")
    return new_string
    
    
def find_lon_lat(distance, direction, center_lat, center_lon):

    direction = np.radians(direction)
    
    center_lat = np.radians(center_lat)
    center_lon = np.radians(center_lon)

    Radius = 6378100

    d_r = distance/Radius

    new_lat = np.arcsin(np.sin(center_lat) * np.cos(d_r) + np.cos(center_lat) * np.sin(d_r) * np.cos(direction))
    new_lon = center_lon + np.arctan2(np.sin(direction) * np.sin(d_r) * np.cos(center_lat), np.cos(d_r)-np.sin(center_lat) * np.sin(new_lat))

    new_lat = np.degrees(new_lat)
    new_lon = np.degrees(new_lon)
    
    return new_lon, new_lat


def get_angle_dist(di, dj):
    hypot = np.sqrt((di**2) + (dj**2))
        
    angle = np.arctan2(dj, di)
    return hypot, np.degrees(angle)

def add_zero(number):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)
    