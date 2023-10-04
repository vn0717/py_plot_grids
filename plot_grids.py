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
        
        
fig = plt.figure(figsize=(12,9), dpi=300)

proj_s = params["map_proj"][0]

if proj_s == "mercator":
    proj = crs.PlateCarree(central_longitude=float(params["ref_lon"][0]))
elif proj_s == "lambert":
    
    print("REF LAT:", float(params["ref_lat"][0]), "\nREF LON:", float(params["ref_lon"][0]), "\nTRUELAT1:", float(params["truelat1"][0]), "\nTRUELAT2:", float(params["truelat2"][0]))
    
    proj = crs.LambertConformal(central_longitude=float(params["ref_lon"][0]), central_latitude=float(params["ref_lat"][0]), standard_parallels=(float(params["truelat1"][0]), float(params["truelat2"][0])))
elif proj_s == "polar":
    if params["ref_lat"][0] > 0:
        proj = crs.NorthPolarStereo(central_longitude=float(params["ref_lon"][0]))
    else:
        proj = crs.SouthPolarStereo(central_longitude=float(params["ref_lon"][0]))
else:
    raise Exception(f"{proj_s} is not a valid project for WRF")


ax = plt.subplot(projection=proj)

dom_cent = {}


for dom in range(0, int(params["max_dom"][0])):
    
    dom_id = dom+1
    
    if dom_id == 1:
        dom_cent[dom_id] = {"lat" : float(params["ref_lat"][0]), "lon" : float(params["ref_lon"][0]), "x":int(int(params["e_we"][dom]) / 2), "y":int(int(params["e_sn"][dom]) / 2), "dx":int(params["dx"][dom]), "dy":int(params["dy"][dom])}
        
    else:
        parent = int(params["parent_id"][dom])
        
        
        di = (int(params["i_parent_start"][dom]) - dom_cent[parent]["x"]) * dom_cent[parent]["dx"]
        dj = (int(params["j_parent_start"][dom]) - dom_cent[parent]["y"]) * dom_cent[parent]["dy"]
        
        hypot, angle = ut.get_angle_dist(di, dj)
        
        print("ANGLE:", angle)
        
        low_left_lon, low_left_lat = ut.find_lon_lat(hypot, angle, dom_cent[parent]["lat"], dom_cent[parent]["lon"])
        
        
        
        
        new_dx = dom_cent[parent]["dx"] / int(params["parent_grid_ratio"][dom])
        new_dy = dom_cent[parent]["dy"] / int(params["parent_grid_ratio"][dom])
        
        
        dx = int(int(params["e_we"][dom]) / 2) * new_dx
        dy = int(int(params["e_sn"][dom]) / 2) * new_dy
        
        hypot, angle = ut.get_angle_dist(dx, dy)
        
        cent_lon, cent_lat = ut.find_lon_lat(hypot, angle, low_left_lat, low_left_lon)
  
        dom_cent[dom_id] = {"lon" : cent_lon, "lat" : cent_lat, "x":int(int(params["e_we"][dom]) / 2), "y":int(int(params["e_sn"][dom]) / 2), "dx":new_dx, "dy":new_dy}
    
    half_i_dist = int(int(params["e_we"][dom]) / 2) * dom_cent[dom_id]["dx"]
    half_j_dist = int(int(params["e_sn"][dom]) / 2) * dom_cent[dom_id]["dx"]
    
    
    lat = []
    lon = []
    

    for i_adjust, j_adjust in zip([1,1,-1,-1], [1,-1,-1,1]):
        hypot, angle = ut.get_angle_dist(half_i_dist * i_adjust, half_j_dist * j_adjust)
        
        
        lon_p, lat_p = ut.find_lon_lat(hypot, angle, dom_cent[dom_id]["lat"], dom_cent[dom_id]["lon"])


        
        lat.append(lat_p)
        lon.append(lon_p)

    lat.append(lat[0])
    lon.append(lon[0])
    
    print(len(lat))
    print(len(lon))
    
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

plt.legend()

#lat_new = proj.transform_points(crs.PlateCarree(), np.array([dom_cent[1]["lon"], dom_cent[1]["lon"]]),np.array([lat_min, lat_max]))

#plt.ylim(lat_new[1,0], lat_new[1,1])
plt.gca().set_aspect('equal', adjustable='box')
gl = ax.gridlines(crs=crs.PlateCarree(), draw_labels=True, linestyle='--', linewidth=0.5, color='gray')
gl.xlabels_top = False  # Turn off labels at the top
gl.ylabels_right = False  # Turn off labels on the right
plt.title("WRF DOMAINS", size=18, weight='bold')