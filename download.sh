#!/bin/bash
# download.sh

# Get the zip code file from the US Census website - this is ~60 MB
curl https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_zcta510_500k.zip --output cb_2017_us_zcta510_500k.zip

# Unzip the file locally. This creates files totalling another ~95 MB
unzip cb_2017_us_zcta510_500k.zip
