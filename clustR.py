#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
http://nbviewer.jupyter.org/github/lmcinnes/hdbscan/blob/master/notebooks/How%20HDBSCAN%20Works.ipynb

break into months
hexify, then cluster within hexes? # of groups within hexes?

"""
import hdbscan, sys, csv
import numpy as np


def append2csv(inLst, csvPathName):
    with open(csvPathName, 'a') as output:
        writer = csv.writer(output, lineterminator = '\n')
        [ writer.writerows([i]) for i in inLst ]
    for j in inLst:
        j[:] = []
        
with open("VIIRSfiresCLPD.csv", "r") as csvIn:
    reader = csv.reader(csvIn, lineterminator = '\n')
    VIIRS = list(reader)
    
with open("VIIRSmonthClusters.csv", "w") as csvOut:
    writer = csv.writer(csvOut, lineterminator = '\n')
    writer.writerows([['group','date','x','y']])
    
    
VIIRSdict = {}
for i in VIIRS[1:]:
    VIIRSdict[i[2]] = [] #monthYear

for i in VIIRS[1:]:
    lon = float(i[1])
    lat = float(i[0])
    VIIRSdict[i[2]].append([lon,lat]) #key monthYear, value x,y
    

cont = 0
for key in VIIRSdict:
    print(key, cont)
    
    mnthArray = np.array(VIIRSdict[key])    
    rads = np.radians(mnthArray)

    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, 
                            metric='haversine', 
                            algorithm='prims_balltree').fit(rads)
    labels = clusterer.labels_

    outPut = []
    [outPut.append( [ labels[i], key, mnthArray[i][0], mnthArray[i][1] ] ) for i in range(len(labels))]
    
    append2csv(outPut,"VIIRSmonthClusters.csv")
    
    cont += 1
#    if cont == 4:
#        break