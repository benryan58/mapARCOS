
from ARCOS.process_arcdata import aggregate_zips

import argparse
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
import re

from fiona.crs import from_epsg


def get_paths(path):
    if os.path.isabs(path):
        DIR = os.path.dirname(path)
    else:
        DIR = os.getcwd()
        path = os.path.join(DIR, path)

    return DIR, path

def list_drugs(args):
    datDIR, arc_path = get_paths(args.data):
    arcDF = pd.read_csv(arc_path)

    drugs = arcDF[['drug_code', 'drug_name']].copy()
    drugs = drugs.sort_values("drug_name").drop_duplicates().reset_index(drop=True)

    print(drugs.reset_index(drop=True))

    return None


def run(args)
    geoDIR, zip_path = get_paths(args.geo):
    datDIR, arc_path = get_paths(args.data):

    # Read Spatial Data and aggregate
    zipshp = gpd.read_file(zip_path)

    if "aggZip" not in zipshp.columns:
        zipshp = aggregate_zips(zipshp, zip_path)

    # Read ARCOS data and population estimates
    arcDF = pd.read_csv(arc_path)

    # zipPop = pd.read_csv("{}/{}".format(datDIR,"aggzipPop.csv"))

    if args.drug:
        arcDF = arcDF[arcDF.drug_code == args.drug]
    else:
        args.drug = 'all'

    if args.year:
        arcDF = arcDF[pd.to_datetime(arcDF.end).apply(lambda x: x.year)==args.year]
    else:
        args.year = 'all'


    arc_data = arcDF.groupby('zipcode').agg(sum).reset_index()

    zip_data = zipshp.merge(arc_data, left_on='aggZip',right_on='zipcode')
    zip_data.plot(column=args.time)

    plt.savefig('arcos_'+args.drug+'_'+str(args.year)+'_'+args.time+'_'+'.svg',
                bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Map ARCOS data.')
    parser.add_argument('-d', '--data', required=True,
                        help='Path to the ARCOS datafile')
    parser.add_argument('-g', '--geo', default='aggzips.shp',
                        help='Path to the geospatial file for mapping the ARCOS'
                             ' data. Default: `aggzips.shp` in '
                             'the working directory.')
    parser.add_argument('-D', '--drug', 
                        help='Drug code to select. Use `-D ?` for a list of drugs and their codes.')
    parser.add_argument('-Y', '--year', type=int,
                        help='Year to select. Currently 2000 - 2019')
    parser.add_argument('-T', '--time', choices=['Q1','Q2','Q3','Q4','Total'],
                        default='Total',
                        help='Time frame to select. choices=[Q1, Q2, Q3, Q4, Total]')


    args = parser.parse_args()

    if args.drug == '?':
        list_drugs(args)
    else:
        run(args)
