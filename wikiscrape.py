#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding=utf-8

"""
Created on Tue Jan 23 14:08:55 2018

@author: itclunie
"""

import shapely.geometry, pyproj, requests, json, csv #, sys, time
#reload(sys)
#sys.setdefaultencoding('utf8')

def wikiScrape(inCoord,lang,collect):
    urlStem = "https://" + lang + ".wikipedia.org/w/api.php?format=json&action=query&gsprop=name&list=geosearch&gslimit=500&gsradius=10000&gscoord="
    urlContent = "https://" + lang + ".wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exchars=1200&titles="
    pageUrlstem = "https://" + lang + ".wikipedia.org/?curid="
    url =  urlStem + str(inCoord.y) + "%7C" + str(inCoord.x)  
    
    try:
        r = requests.get(url)
        obj = json.loads(r.text)
        pageLst = obj['query']['geosearch']
        
        for page in pageLst:
            rContent = requests.get(urlContent + page['title']) #grab extract of page text
            objContent = json.loads(rContent.text)
            pageContent = str(objContent['query']['pages'])
            
            pageUrl = pageUrlstem + str(page['pageid'])
            collect.append( [ page['pageid'], page['title'] ,page['lon'],page['lat'],lang, pageUrl, pageContent ] )

    except:
        collect.append([url])
        pass
    
    
def conserveMemory(list_of_lists, csvPathsList):
    with open(csvPathsList, 'a', encoding='utf-8') as output:
        writer = csv.writer(output, lineterminator = '\n')
        [ writer.writerows([item]) for item in list_of_lists ]
    for lisst in list_of_lists:
        lisst[:] = []
    
    
outPath = "/Users/itclunie/Desktop/wikiScrapeGAP.csv"
headers = ['pageid','title','lon','lat','lang','url']
with open(outPath, 'w') as output:
    writer = csv.writer(output, lineterminator = '\n')
    writer.writerows([headers])
    

# Set up projections
p_ll = pyproj.Proj(init='epsg:4326')
p_mt = pyproj.Proj(init='epsg:3857') # metric; same as EPSG:900913

# Create corners of rectangle to be transformed to a grid
nw = shapely.geometry.Point((36.28903,36.54945))   #nw x, se y
se = shapely.geometry.Point((43.57605,38.89124))   #se x, nw y

#nw = shapely.geometry.Point((-3.31212, 55.82068))   #edinburgh test
#se = shapely.geometry.Point((-2.96319, 55.99240))   


stepsize = 5000 # 5 km grid step size

# Project corners to target projection
s = pyproj.transform(p_ll, p_mt, nw.x, nw.y) # Transform NW point to 3857
e = pyproj.transform(p_ll, p_mt, se.x, se.y) # .. same for SE


gridPoints = []
# Iterate over 2D area
x = s[0]
while x < e[0]:
    y = s[1]
    while y < e[1]:
        p = shapely.geometry.Point(pyproj.transform(p_mt, p_ll, x, y))
        gridPoints.append(p)
        y += stepsize
    x += stepsize
    
    
outPathgrid = "/Users/itclunie/Desktop/TurkeyGrid.csv"
with open(outPathgrid, 'w') as output:
    writer2 = csv.writer(output, lineterminator = '\n')
    writer2.writerows([['lon','lat']])
    for point in gridPoints:
        writer2.writerows([[str(point.x), str(point.y)]])


collectPages = []
countr = 0
for point in gridPoints:
    countr += 1
#    print(countr)
    wikiScrape(point,"en",collectPages)
    wikiScrape(point,"tr",collectPages)
    
    if countr % 10 == 0:
        print(countr, len(gridPoints))
        conserveMemory(collectPages,outPath)    
#        sys.exit()

conserveMemory(collectPages,outPath)




#{
#  "batchcomplete": "",
#  "warnings": {
#    "extracts": {
#      "*": "\"exlimit\" was too large for a whole article extracts request, lowered to 1."
#    }
#  },
#  "query": {
#    "pages": {
#      "43178257": {
#        "pageid": 43178257,
#        "ns": 0,
#        "title": "Al-Muhafaza Stadium",
#        "extract": "<p><b>Al-Muhafaza Stadium<\/b> (Arabic: <span lang=\"ar\" dir=\"rtl\" xml:lang=\"ar\">\u0645\u0644\u0639\u0628 \u0627\u0644\u0645\u062d\u0627\u0641\u0638\u0629<\/span>\u200e) is a multi-use all-seater stadium in the Syrian capital Damascus. It is mostly used for football matches and is home to the Syrian Premier League club al-Muhafaza SC. It also hosts local competitions of athletics.<\/p>\n<h2><span id=\"History\">History<\/span><\/h2>\n<p>The stadium was opened in 2011 with a capacity of 1,000 seats in the Kafr Sousa district of Damascus, with a total cost of US$ 2.8 million. It is owned and operated by the Damascus-based al-Muhafaza sports club and is part of a complex that includes an administration building, gymnasium, theatre, restaurants and plazas.<\/p>\n<h2><span id=\"See_also\">See also<\/span><\/h2>\n<ul><li>List of football stadiums in Syria<\/li>\n<\/ul><h2><span id=\"References\">References<\/span><\/h2>\n\n<p><span><\/span><\/p>..."
#      }
#    }
#  }
#}