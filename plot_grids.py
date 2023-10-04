import matplotlib.pyplot as plt
import cartopy.crs as crs 
import cartopy.feature as cfeature
import numpy as np
import utils as ut


file = open("namelist.wps")
lines = file.readlines()
file.close()

params = {}
for line in lines:
    if line.find("=") != -1:
        params[ut.get_var(line)] = ut.get_data(line)
        
        


proj_s = params["map_proj"][0]

if proj_s == "mercator":
    try:
        params["ref_lon"][0]
    except:
        raise Exception("ref_lon does not exist in your namelist.wps file")
    
    proj = crs.PlateCarree(central_longitude=float(params["ref_lon"][0]))
elif proj_s == "lambert":
    for param in ["ref_lat", "ref_lon", "truelat1", "truelat2"]:
        try:
            params[param][0]
        except:
            raise Exception(f"{param} does not exist in your namelist.wps file")
    

    proj = crs.LambertConformal(central_longitude=float(params["ref_lon"][0]), central_latitude=float(params["ref_lat"][0]), standard_parallels=(float(params["truelat1"][0]), float(params["truelat2"][0])))


elif proj_s == "polar":
    try:
        params["ref_lon"][0]
    except:
        raise Exception("ref_lon does not exist in your namelist.wps file")
    
    if float(params["ref_lat"][0]) > 0:
        proj = crs.NorthPolarStereo(central_longitude=float(params["ref_lon"][0]))
    else:
        proj = crs.SouthPolarStereo(central_longitude=float(params["ref_lon"][0]))
else:
    raise Exception(f"{proj_s} is not a valid project for WRF")

fig = plt.figure(figsize=(5,9), dpi=300)

ax = plt.subplot(projection=proj)

dom_cent = {}


for dom in range(0, int(params["max_dom"][0])):
    dom_id = dom+1
    #check to see if our parameters exist
    for param in ["e_we", "e_sn", "i_parent_start", "j_parent_start", "parent_grid_ratio"]:
        try:
            params[param][dom]
        except IndexError:
            raise Exception(f"The variable {param} does not exist for domain {str(dom_id)}")
    
    
    
    if dom_id == 1:
        dom_cent[dom_id] = {"lat" : float(params["ref_lat"][0]), "lon" : float(params["ref_lon"][0]), "x":int(int(params["e_we"][dom]) / 2), "y":int(int(params["e_sn"][dom]) / 2), "dx":int(params["dx"][dom]), "dy":int(params["dy"][dom])}
        
    else:
        parent = int(params["parent_id"][dom])
        
        
        di = (int(params["i_parent_start"][dom]) - dom_cent[parent]["x"]) * dom_cent[parent]["dx"]
        dj = (int(params["j_parent_start"][dom]) - dom_cent[parent]["y"]) * dom_cent[parent]["dy"]
        
        hypot, angle = ut.get_angle_dist(di, dj)
        
        
        low_left_lon, low_left_lat = ut.find_lon_lat(hypot, angle, dom_cent[parent]["lat"], dom_cent[parent]["lon"])
        
        
        
        
        new_dx = dom_cent[parent]["dx"] / int(params["parent_grid_ratio"][dom])
        new_dy = dom_cent[parent]["dy"] / int(params["parent_grid_ratio"][dom])
        
        
        dx = int(int(params["e_we"][dom]) / 2) * new_dx
        dy = int(int(params["e_sn"][dom]) / 2) * new_dy
        
        hypot, angle = ut.get_angle_dist(dx, dy)
        
        cent_lon, cent_lat = ut.find_lon_lat(hypot, angle, low_left_lat, low_left_lon)
  
        dom_cent[dom_id] = {"lon" : cent_lon, "lat" : cent_lat, "x":int(int(params["e_we"][dom]) / 2), "y":int(int(params["e_sn"][dom]) / 2), "dx":new_dx, "dy":new_dy}
    
    
    start_res = 25
    
    i_length = int(params["e_we"][dom])
    j_length = int(params["e_sn"][dom])
    
    for i_res in range(start_res,0,-1):
        if i_length % i_res == 0:
            break
    
    for j_res in range(start_res,0,-1):
        if j_length % j_res == 0:
            break

    
    
    
    plot_is = (np.arange(0,int(int(params["e_we"][dom])) + i_res, i_res) - dom_cent[dom_id]["x"]) * dom_cent[dom_id]["dx"]
    plot_js = (np.arange(0,int(int(params["e_sn"][dom])) + j_res, j_res) - dom_cent[dom_id]["y"]) * dom_cent[dom_id]["dy"]
    
    
    
    lat = []
    lon = []
    
    
    for i in plot_is:
        hypot, angle = ut.get_angle_dist(i, plot_js[-1])
        
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)
        
    for j in np.flip(plot_js):
        hypot, angle = ut.get_angle_dist(plot_is[-1], j)
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)
    
    for i in np.flip(plot_is):
        hypot, angle = ut.get_angle_dist(i, plot_js[0])
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)
        
    for j in plot_js:
        hypot, angle = ut.get_angle_dist(plot_is[0], j)
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])
        lat.append(lat_p)
        lon.append(lon_p)

    print(len(lat), len(lon))

    
    lat = np.array(lat)
    lon = np.array(lon)
    temp_lat = lat[np.isnan(lat) == False]
    temp_lon = lon[np.isnan(lat) == False]
    lat = temp_lat[np.isnan(temp_lon) == False]
    lon = temp_lon[np.isnan(temp_lon) == False]
    
    
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
    
    ax.add_feature(cfeature.STATES.with_scale('50m'), linewidth=0.4, alpha=0.25)
    ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=0.4, alpha=0.25)
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.4, alpha=0.25)
    ax.add_feature(cfeature.OCEAN.with_scale('50m'))
    ax.add_feature(cfeature.LAND.with_scale('50m'))
    ax.add_feature(cfeature.LAKES.with_scale('50m'))
    
    plt.plot(lon, lat, transform=crs.PlateCarree(), label=f"d{ut.add_zero(dom_id)}")

plt.legend(loc = 1, fontsize = "x-small")

plt.gca().set_aspect('equal', adjustable='box')
gl = ax.gridlines(crs=crs.PlateCarree(), draw_labels=True, linestyle='--', linewidth=0.5, color='gray')
gl.xlabels_top = False  
gl.ylabels_right = False  

gl.xlabel_style = {'size': 6}  
gl.ylabel_style = {'size': 6} 

plt.title("WRF DOMAINS", size=10, weight='bold')
plt.show()