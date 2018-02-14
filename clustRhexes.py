#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import hdbscan groups
import hexgrid over aoi
find how many grids have consistant fires & groups
"""

#import shapely, csv, shapefile
#
#with open("VIIRSfiresCLPD.csv", "r") as csvIn: 
#    reader = csv.reader(csvIn, lineterminator = '\n')
#    VIIRS = list(reader)
    


import shapefile, shapely, rtree, csv, os, sys
from collections import Counter
from shapely.geometry import Point
from shapely.geometry import Polygon
#script to count up how many points fall within each hexigon. outputs csv you can attribute join back to hexigon feature class

csvHexCount = r"/Users/itclunie/Desktop/ECON/find industry/csvHexCount.csv" #outcsv
pointfeat = r"/Users/itclunie/Desktop/ECON/find industry/VIIRScluster_points/VIIRSclustRd.shp"     #points
polyfeat = r"/Users/itclunie/Desktop/ECON/find industry/hexes/grid4.shp"        #hex polygons

#print(csvHexCount)
#print(pointfeat)
#print(polyfeat)
#sys.exit()

#A Load the shapefile of polygons and convert it to shapely polygon objects
polygons_sf = shapefile.Reader(polyfeat)
polygon_shapes = polygons_sf.shapes()
polygon_points = [q.points for q in polygon_shapes ]
polygons = [Polygon(q) for q in polygon_points]
poly_records = polygons_sf.records()

#B Load the shapefile of points and convert it to shapely point objects
points_sf = shapefile.Reader(pointfeat)

help(points_sf. shapes())
#sys.exit()

point_shapes = points_sf.shapes()
point_coords= [q.points[0] for q in point_shapes ]
points = [Point(q.points[0]) for q in point_shapes ]

#C Build a spatial index based on the bounding boxes of the polygons
from rtree import index
idx = index.Index()
count = -1
for q in polygon_shapes:
	count +=1
	idx.insert(count, q.bbox)

#D Assign one or more matching polygons to each point
tallyHO = []
count = 0
countThou = 0
for i in range(len(points)): #Iterate through each point
    count += 1
    countThou += 1
    if countThou == 10000:
        countThou = 0
        print('processed ' + str(count) + ' points')

    #Iterate only through the bounding boxes which contain the point 
    for j in idx.intersection(point_coords[i]):
        #Verify that point is within the polygon itself not just the bounding box
        if points[i].within(polygons[j]):       
            tallyHO.append(poly_records[j][0]) 
            break 

#E this tallies up the repeats and give us the point count for each polygon
resultDict = dict([ (i,tallyHO.count(i)) for i in set(tallyHO) ])

#F output the final tally
headers = ['Hex_ID','Count']
with open(csvHexCount, 'w') as output:
    writer = csv.writer(output, lineterminator = '\n')
    writer.writerows([headers])
    
    for key,value in resultDict:
        templist = []
        templist.append(key)
        templist.append(value)
        writer.writerows([templist])
