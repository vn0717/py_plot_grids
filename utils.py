"""
Plot Gird Utilities

This file contains functions used by the plot grids script

Michael P. Vossen
University of Wisconsin-Milaukee

Date Created: 10/5/2023
Last Updated: 10/20/2023
"""


import numpy as np

def get_data(string):
    """
    Function that takes in a string and finds the paramter value.
    It looks for the = and knows that after that the carachers are the
    paramter values

    Args:
        string (STRING): The string containg the parameter value

    Returns:
        LIST: List of parameter values for each domain
    """
    #find the location of the =.  Add one since python is non inclusive
    start = string.find("=") + 1
    
    #get the useful part of the string with the parameter values
    new_string = string[start:]
    
    #get rid of characters that are extra
    new_string = new_string.replace(" ", "")
    new_string = new_string.replace("\'", "")
    new_string = new_string.replace("\"", "")
    new_string = new_string.replace("\n", "")
    
    #every comma seperates information for a domain.  Here I split
    #the data based on commas so each domain is an index in a list
    
    #if a comma exists seperate data
    if new_string.find(",") != -1:
        new_string = new_string.split(",")
        final_data = []
        for i in new_string:
            if i != "":
                final_data.append(i)
                
        
        return final_data
    
    #if a comma does not exist, we have only one domain worth of data and so we are good to go
    else:
        return [new_string]
    
def get_var(string):
    """
    Function to find parameter name from a string.

    Args:
        string (STRING): string containg a parameter

    Returns:
        STRING: Name of parameter in the string
    """
    #the name of the parameter will be left of = and so
    #we start by finding the =
    start = string.find("=")
    #everything before the = we are intrested in
    new_string = string[:start]
    #there is no need for white space and so here I get rid of it
    new_string = new_string.replace(" ", "")
    return new_string
    
    
def find_lon_lat(distance, direction, center_lat, center_lon):
    """
    Function that takes in a distance, bearing, and center point to find a latitude
    and longitude.

    Args:
        distance (FLOAT): Distance to new point
        direction (FLOAT): Bearing to new point in degrees
        center_lat (FLOAT): Latitude of starting point
        center_lon (FLOAT): Longitude of starting point

    Returns:
        FLOAT : Longitude of new point
        FLOAT : Latitude of new point
    """

    #convert degrees to radians
    direction = np.radians(direction)
    center_lat = np.radians(center_lat)
    center_lon = np.radians(center_lon)

    #the radius of the earth
    Radius = 6378100

    #calculate new lat and lon
    d_r = distance/Radius
    new_lat = np.arcsin(np.sin(center_lat) * np.cos(d_r) + np.cos(center_lat) * np.sin(d_r) * np.cos(direction))
    new_lon = center_lon + np.arctan2(np.sin(direction) * np.sin(d_r) * np.cos(center_lat), np.cos(d_r)-np.sin(center_lat) * np.sin(new_lat))

    #the new lat and lon is in radians and so I convert back to degrees
    new_lat = np.degrees(new_lat)
    new_lon = np.degrees(new_lon)
    
    return new_lon, new_lat


def get_angle_dist(di, dj):
    """
    This function finds the distance and angle of a movement based
    on the i and j components of the movement

    Args:
        di (FLOAT): Distance moved in the x direction
        dj (FLOAT): Distance moved in the y direction

    Returns:
        FLOAT: The total distance of the movement
        FLOAT: The bearing of the movement in degrees
    """
    #we need to convert to double precision to make this calculation
    di = np.float64(di)
    dj = np.float64(dj)
    
    #find distance using the pythagorean theorem
    hypot = np.sqrt((di**2) + (dj**2))
    
    #find the bearing
    angle = np.arctan2(dj, di)
    
    return hypot, np.degrees(angle)

def add_zero(number):
    """
    Function to convert a number to a string.  If the number is
    less than ten a zero is added in the tens place.

    Args:
        number (INTEGER): Number to convert to a string 

    Returns:
        STRING: _Number in string format with zero padding if needed
    """
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)
    