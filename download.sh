#!/bin/bash
# download.sh

[ ! -d "data" ] && mkdir data
chmod 755 data

[ ! -d "geodata" ] && mkdir geodata
chmod 755 geodata

# Get the zip code file from the US Census website - this is ~60 MB
[ ! -f "geodata/cb_2017_us_zcta510_500k.zip" ] && curl https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_us_zcta510_500k.zip --output geodata/cb_2017_us_zcta510_500k.zip

# Unzip the file locally. This creates files totalling another ~95 MB
cd geodata
[ ! -f "cb_2017_us_zcta510_500k.shp" ] && unzip cb_2017_us_zcta510_500k.zip

cd ..
eval python3 download_arcos.py -s https://www.deadiversion.usdoj.gov/arcos/retail_drug_summary/ -d data -v
