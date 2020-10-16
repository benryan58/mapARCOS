

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from fiona.crs import from_epsg

DIR = 'C:/Users/ben_ryan/Documents/Maps/zipcodes'


# Read Spatial Data and aggregate
zipfp = "{}/{}".format(DIR,"cb_2017_us_zcta510_500k.shp")
zipshp = gpd.read_file(zipfp)
zipshp['aggZip'] = zipshp.apply(lambda x: int(x['GEOID10'][0:3]), axis=1)
zipshp = zipshp.dissolve(by='aggZip',aggfunc='sum')
zipshp.to_file("{}/{}".format(DIR,"aggzips.shp"))


# Read ARCOS data and population estimates
arcfp = "{}/{}".format(DIR,"ARCOS_2000_2016.csv")
arcDF = pd.read_csv(arcfp)
zipPop = pd.read_csv("{}/{}".format(DIR,"aggzipPop.csv"))


# Generate shapefiles with specific drug/year data
code = '1100'
amph06DF = arcDF[(arcDF.drugName==code) & (arcDF.rptStart=='2006-01-01')]
amphshp = zipshp.merge(amph06DF,left_index=True,right_on='zipcode')
amphshp = amphshp.merge(zipPop,how='left',left_on='zipcode',right_on='aggZip')
amphshp.to_file("{}/{}".format(DIR,"amphetamines2006.shp"))

# Aggregate all the opioid drug data and make a shapefile for it
opioidDF = arcDF[arcDF.drugCode.str.contains('^9')]
grouped = opioidDF.groupby(['rptStart','zipcode'])
opData = grouped.aggregate({'State':'first','Q1':'sum','Q2':'sum','Q3':'sum','Q4':'sum','Total':'sum'})
opData.reset_index(level=0, inplace=True)
opData.reset_index(level=0, inplace=True)

op16shp = zipshp.merge(opData[opData.rptStart=='2016-01-01'],how='left',left_index=True,right_on='zipcode')
op16shp = op16shp.merge(zipPop,how='left',left_on='zipcode',right_on='aggZip')
op16shp.to_file("{}/{}".format(DIR,"opioids2016.shp"))

