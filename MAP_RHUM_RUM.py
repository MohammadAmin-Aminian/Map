#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 16:16:05 2023

@author: mohammadamin

Map RHUM-RUM 
Pygmt 

conda activate env spin-ml
"""
import pygmt
import numpy as np
from obspy.clients.fdsn import Client
ridge_data = pygmt.datasets.load_sample_data(name="ocean_ridge_points")
client = Client("RESIF")
# start =UTCDateTime("2012-10-12")
net = "YV"
sta = "RR28,RR29,RR34,RR36,RR38,RR40,RR50,RR52"


invz = client.get_stations(
    network=net,
    station=sta,
    channel="BHZ",
    location="*",
    level="response"
)

invz_RR41 = client.get_stations(
    network=net,
    station="RR41",
    channel="BHZ",
    location="*",
    level="response"
)


lats = np.zeros(len(invz[0]))
lons = np.zeros(len(invz[0]))
labels = []
for i in range(0, len(invz[0])):
    lats[i] = invz[0][i][0].latitude
    lons[i] = invz[0][i][0].longitude
    labels.append(invz[0][i].code)

minlon, maxlon = 45, 75
minlat, maxlat = -35, -15

# define etopo data file
# topo_data = 'path_to_local_data_file'
# 30 arc second global relief (SRTM15+V2.1 @ 1.0 km)
topo_data = '@earth_relief_30s'
# topo_data = '@earth_relief_15s' #15 arc second global relief (SRTM15+V2.1)
# topo_data = '@earth_relief_03s' #3 arc second global relief (SRTM3S)
fig = pygmt.Figure()
# make color pallets
pygmt.makecpt(
    cmap='topo',
    series='-8000/8000/1000',
    continuous=True
)

fig.grdimage(
    grid=topo_data,
    region=[minlon, maxlon, minlat, maxlat],
    projection='M4i',
    shading=True,
    frame=True
)

fig.plot(
    data=ridge_data,
    style='c0.05c',  # Small circle marker
    color='red',
    pen='black',    
)

# Add label for Madagascar
# fig.text(
#     x=45,
#     y=-20,
#     text="Madagascar",
#     offset="0.2c",
#     font="14p,Helvetica-Bold,black",
#     justify="LM"
# )

# Add label for La Réunion Island
fig.text(
    x=49,
    y=-21,
    text="La Réunion",
    offset="0.2c",
    font="10p,Times-Bold,black",
    justify="LM",
)

fig.text(
    x= 66,
    y= -18,
    text="CIR",
    offset="0.2c",
    font="10p,Times-Bold,blue",
    justify="LM",
    angle = -65,
    fill="lightorange",  # Background fill color
)

fig.text(
    x= 60,
    y= -29,
    text="SWIR",
    offset="0.2c",
    font="10p,Times-Bold,blue",
    justify="LM",
    angle = 35,
    fill="lightorange",  # Background fill color
)

fig.text(
    x= 72,
    y= -27,
    text="SEIR",
    offset="0.2c",
    font="10p,Times-Bold,blue",
    justify="LM",
    angle = -40,
    fill="lightorange",  # Background fill color
)

#Tectornic plates

fig.text(
    x= 53,
    y= -27,
    text="Somali Plate",
    offset="0.2c",
    font="10p,Times-Bold,purple",
    justify="LM",
    angle = 0,
    fill="lightyellow",  # Background fill color
    pen="1p,black",
)
fig.text(
    x= 70.5,
    y= -16.5,
    text="Australian Plate",
    offset="0.2c",
    font="10p,Times-Bold,purple",
    justify="LM",
    angle = -65,
    fill="lightyellow",  # Background fill color
    pen="1p,black",
)
fig.text(
    x= 60,
    y= -35,
    text="Antarctic Plate",
    offset="0.2c",
    font="10p,Times-Bold,purple",
    justify="LM",
    angle = 45,
    fill="lightyellow",  # Background fill color
    pen="1p,black",
)

with fig.inset(position="jBR+w2c+o0.5c/0.2c", box="+pgrey+p3p,black"):
    # Use a plotting function to create a figure inside the inset
    fig.coast(
        region=[5, 140, -40,80],
        projection="M3c",
        borders=[1, 2],
        shorelines="1/thin",
        water="white",
        land = 'gray',
        # Use dcw to selectively highlight an area,
    )
    
    # Plot a rectangle ("r") in the inset map to show the area of the main
    # figure. "+s" means that the first two columns are the longitude and
    # latitude of the bottom left corner of the rectangle, and the last two
    # columns the longitude and latitude of the upper right corner.
    rectangle = [90, -15, 130,10],
    fig.plot(data=rectangle, style="r+s", pen="1p,red")
fig.plot(
    x=lons,
    y=lats,
    style='t0.10i',  # Triangle marker with size 0.15 inches
    color='red',
    pen='black',
    label='Broadband OBS',
)

fig.colorbar(
    frame='+l"Topography"'
)

# Add labels for each station
for label, lon, lat in zip(labels, lons, lats):
    if label == "RR40":
        fig.text(
            x=lon,
            y=lat-1,
            text=label,
            offset="0.2c",
            font="10p,Times-Bold,black",
            justify="LM",
            no_clip=True,
            fill="lightblue",
        )
    else:    
        fig.text(
        x=lon,
        y=lat,
        text=label,
        offset="0.2c",
        font="10p,Times-Bold,black",
        justify="LM",
        no_clip=True,
        fill="lightblue",
        )


fig.plot(
    x=invz_RR41[0][0][0].longitude,
    y=invz_RR41[0][0][0].latitude,
    style='a0.3c',  # Triangle marker with size 0.15 inches
    color='yellow',
    pen='black',
    label='Active Seamount',
)

fig.legend(
    position="JTL+jTL+o0.1c",  # Place legend at Top Right corner inside the map, with a slight offset
    box="+gwhite+p1p", # White background with a black outline of 1 point thickness
)
fig.show(dpi=300)
fig.savefig(dpi=300, fname="MAP_RHUM1.jpg")



