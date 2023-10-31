"""  
PLOT GRIDS

A program to plot what a WPS domain looks like using the namelist parameters


Michael P. Vossen
University of Wisconsin-Milaukee

Date Created: 10/5/2023
Last Updated: 10/20/2023

"""


import matplotlib.pyplot as plt
import cartopy.crs as crs 
import cartopy.feature as cfeature
import numpy as np
import utils as ut


################################
# Find Paramters
################################

#open the namelist and read it's contents into memory
file = open("namelist.wps")
lines = file.readlines()
file.close()

#create blank dictonary to hold our namelist parameters
params = {}

#for each line in the file
for line in lines:
    #if the line has an = then it is a paramter to save
    if line.find("=") != -1:
        params[ut.get_var(line)] = ut.get_data(line)
        

##############################
# Error Checking
##############################
        
#get a list of paramters found so we can loop through and do some error checking
keys = list(params.keys())

#for each parameter found
for key in keys:
    
    #get the parameter value
    value = params[key][0]
    
    #if it is one of the single numeric value parameters, check to see if it is numeric.  If not
    #throw a useful error
    if key.find("lon") != -1 or key.find("lat") != -1 or key.find("max_dom") != -1:
        if value.replace(".", "").replace("-","").isnumeric() == False:
            raise ValueError(f"{value} in not a number and thus cannot be used for {key}")
        
    #if we are looking at a longitude parameter, make sure the longitude value is appropriate.  If not
    #throw a useful error
    if key.find("lon") != -1:
        value = float(value)
        if value > 180 or value <= -180:
            raise ValueError(f"{str(value)} cannot be used for a longitude in {key}.  Be sure to use values between -180 and 180")
        
    #if we are looking at a latitude parameter, make sure the latitude value is appropriate.  If not
    #throw a useful error    
    elif key.find("lat") != -1:
        value = float(value)
        
        if value > 90 or value < -90:
            raise ValueError(f"{str(value)} cannot be used for a latitude in {key}.  Be sure to use values between -90 and 90")
 
    

####################################
# Setup map projection
####################################

#pull out the map projection parameter
proj_s = params["map_proj"][0]

#if projection is mercator
if proj_s == "mercator":
    #make sure the approprate parameters exist.  If they don't throw a useful error
    try:
        params["ref_lon"][0]
    except:
        raise Exception("ref_lon does not exist in your namelist.wps file")
    
    #setup cartopy projection
    proj = crs.PlateCarree(central_longitude=float(params["ref_lon"][0]))
    
#if map projection is lambert conformal conic
elif proj_s == "lambert":
    #make sure the approprate parameters exist.  If they don't throw a useful error
    for param in ["ref_lat", "ref_lon", "truelat1", "truelat2"]:
        try:
            params[param][0]
        except:
            raise Exception(f"{param} does not exist in your namelist.wps file")
    
    #setup cartopy projection
    proj = crs.LambertConformal(central_longitude=float(params["ref_lon"][0]), central_latitude=float(params["ref_lat"][0]), standard_parallels=(float(params["truelat1"][0]), float(params["truelat2"][0])))

#if map projection is polar
elif proj_s == "polar":
    #make sure the approprate parameters exist.  If they don't throw a useful error
    try:
        params["ref_lon"][0]
    except:
        raise Exception("ref_lon does not exist in your namelist.wps file")
    
    #cartopy has two polar projections, one for the NH and one for SH.  Using the latitude 
    #I find which one to use and set the appropriate setting with parameters from the namelist
    if float(params["ref_lat"][0]) > 0:
        proj = crs.NorthPolarStereo(central_longitude=float(params["ref_lon"][0]))
    else:
        proj = crs.SouthPolarStereo(central_longitude=float(params["ref_lon"][0]))
        
#if the projection does not match any of the previous, WRF and WPS do not support that projection.
#So if we reach this point throw an error.
else:
    raise Exception(f"{proj_s} is not a valid project for WRF")


##############################################
# Create Blank Plot
##############################################

#setup figue
fig = plt.figure(figsize=(5,9), dpi=300)

#set projection to what we defined earlier
ax = plt.subplot(projection=proj)



#####################################
# Find Domain Info
#####################################


#Blank dictornary to hold domain information
dom_cent = {}

#for each domain
for dom in range(0, int(params["max_dom"][0])):
    #python starts at 0, but wrf domains start at 1.  So I make the adjustment
    dom_id = dom+1
    #check to see if our parameters exist for the domain.  If they don't throw a useful error
    for param in ["e_we", "e_sn", "i_parent_start", "j_parent_start", "parent_grid_ratio"]:
        try:
            params[param][dom]
        except IndexError:
            raise Exception(f"The variable {param} does not exist for domain {str(dom_id)}")
        
    
    #if this is the first domain we need to initalize the domain dictonary
    if dom_id == 1:
        dom_cent[dom_id] = {"lat" : float(params["ref_lat"][0]), "lon" : float(params["ref_lon"][0]), "x":int(int(params["e_we"][dom]) / 2), "y":int(int(params["e_sn"][dom]) / 2), "dx":int(params["dx"][dom]), "dy":int(params["dy"][dom])}
      
    #if this is not the first domain, lets calculate the information for the domain relative to it's parent.  
    else:
        #find the parent domain for this domain
        parent = int(params["parent_id"][dom])
        
        
        """
        To find the edge of the current domain we need to find the center of the domain so we can
        calculate the edges of the domain.  
        
        """
        #find how may grid points the lower left of the domain we are on is away from the parent domain center
        #number of i grids
        di = (int(params["i_parent_start"][dom]) - dom_cent[parent]["x"]) * dom_cent[parent]["dx"]
        #number of j grids
        dj = (int(params["j_parent_start"][dom]) - dom_cent[parent]["y"]) * dom_cent[parent]["dy"]
        
        #calculate the distance and angle the lower left of the current domain is from the center of the parent domain
        hypot, angle = ut.get_angle_dist(di, dj)
        
        #calculate lower left corner's lat and lon
        low_left_lon, low_left_lat = ut.find_lon_lat(hypot, angle, dom_cent[parent]["lat"], dom_cent[parent]["lon"])
        
        #find the resolution of the domain
        new_dx = dom_cent[parent]["dx"] / int(params["parent_grid_ratio"][dom])
        new_dy = dom_cent[parent]["dy"] / int(params["parent_grid_ratio"][dom])
        
        #find the x and y distance to the center of the domain
        dx = int(int(params["e_we"][dom]) / 2) * new_dx
        dy = int(int(params["e_sn"][dom]) / 2) * new_dy
        
        #find the distance and angle to the center of the domain
        hypot, angle = ut.get_angle_dist(dx, dy)
        
        #get lat and lon of the center of the domain
        cent_lon, cent_lat = ut.find_lon_lat(hypot, angle, low_left_lat, low_left_lon)

        #add parametrs to the domain
        dom_cent[dom_id] = {"lon" : cent_lon, "lat" : cent_lat, "x":int(int(params["e_we"][dom]) / 2), "y":int(int(params["e_sn"][dom]) / 2), "dx":new_dx, "dy":new_dy}
    
    
    ########################################
    # Build Plotting Point
    ########################################
    
    
    #the number of points to plot on each edge of the domain.  The total number of ploting points is ((start_res * 4) + 1).
    #this is not the final number of points and the number will be optimized later.
    start_res = 25
    
    #get the number of grid points in each direction for the domain
    i_length = int(params["e_we"][dom])
    j_length = int(params["e_sn"][dom])
    
    #make sure the number of points to plot on the edge of the domain is divisible by the resolution.  If not optimize to make it so
    for i_res in range(start_res,0,-1):
        if i_length % i_res == 0:
            break
    
    for j_res in range(start_res,0,-1):
        if j_length % j_res == 0:
            break

    
    
    #create list of is and js that should be plotted
    plot_is = (np.arange(0,int(int(params["e_we"][dom])) + i_res, i_res) - dom_cent[dom_id]["x"]) * dom_cent[dom_id]["dx"]
    plot_js = (np.arange(0,int(int(params["e_sn"][dom])) + j_res, j_res) - dom_cent[dom_id]["y"]) * dom_cent[dom_id]["dy"]
    
    
    #latitude and longitude of point
    lat = []
    lon = []
    
    #for the top edge of the domain find the latitude and longitude points
    for i in plot_is:
        hypot, angle = ut.get_angle_dist(i, plot_js[-1])
        
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)
        
    #for the right edge of the domain find the latitude and longtidue points
    for j in np.flip(plot_js):
        hypot, angle = ut.get_angle_dist(plot_is[-1], j)
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)
    
    #for the bottom edge of the domain find the latitude and longitude points
    for i in np.flip(plot_is):
        hypot, angle = ut.get_angle_dist(i, plot_js[0])
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)
    #for the left edge of the domain find the latitude and longitude points
    for j in plot_js:
        hypot, angle = ut.get_angle_dist(plot_is[0], j)
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)

    #convert latitude and longitude lists to numpy arrays to make it easy to remove nans    
    lat = np.array(lat)
    lon = np.array(lon)
    temp_lat = lat[np.isnan(lat) == False]
    temp_lon = lon[np.isnan(lat) == False]
    lat = temp_lat[np.isnan(temp_lon) == False]
    lon = temp_lon[np.isnan(temp_lon) == False]
    
    ##############################
    # Plot the Domain
    ##############################
    
    
    #find the maximum and minimum latitude to set the plot extent
    if dom_id == 1:
        lat_min = np.nanmin(np.array(lat))
        lat_max = np.nanmax(np.array(lat))
       
    else:
        new_lat_min = np.nanmin(np.array(lat))
        new_lat_max = np.nanmax(np.array(lat))
        
        if lat_min > new_lat_min:
            lat_min = new_lat_min
        if lat_max < new_lat_max:
            lat_max = new_lat_max    
    
   
    #plot domain edge    
    plt.plot(lon, lat, transform=crs.PlateCarree(), label=f"d{ut.add_zero(dom_id)}")


#add useful geographic features
ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.4, alpha=0.25)
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.4, alpha=0.25)
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.4, alpha=0.25)
ax.add_feature(cfeature.OCEAN.with_scale('50m'))
ax.add_feature(cfeature.LAND.with_scale('50m'))
ax.add_feature(cfeature.LAKES.with_scale('50m'))
    
#add domain legend
plt.legend(loc = 1, fontsize = "x-small")

#create latitude and longtide grid
plt.gca().set_aspect('equal', adjustable='box')
gl = ax.gridlines(crs=crs.PlateCarree(), draw_labels=True, linestyle='--', linewidth=0.5, color='gray')
gl.top_labels = False  
gl.right_labels = False  
gl.xlabel_style = {'size': 6}  
gl.ylabel_style = {'size': 6} 

#add plot title
plt.title("WRF DOMAINS", size=10, weight='bold')

#show the plot
plt.show()