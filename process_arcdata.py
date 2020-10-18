
import argparse
import os
import pandas as pd
import re
import subprocess
from tqdm import tqdm

def clean_line(line):
    # normalize formatting for the line for further parsing
    line = re.sub(r"\s+", " ", line)
    line = line.replace(",","")

    return line.strip().upper()

def get_drug_info(line):
    # extract drug code and drug name from line
    line = re.sub(r"^DRUG\s*(CODE)*:","",line)

    if "DELETE THIS RECORD" in line:
        line = line[:line.index("DRUG NAME:")]
        drugCode = line.strip()
        drugName = ""
    else:
        line = re.sub(r"DRUG\s*(NAME)*:"," - ",line)
        drugCode, drugName = line.split(" - ")
        drugCode = drugCode.strip()
        drugName = drugName.strip()

    return drugCode, drugName

def get_periods(line):
    # extract start and end dates for reporting period from line

    line = re.findall(r"\d{2}/\d{2}/\d{4} TO \d{2}/\d{2}/\d{4}", line)[-1]

    return line.split(" TO ")

def get_state(line):
    # extract State name/code from line

    state = line.replace("STATE:", "")

    if "-" in line:
        state = state.split("-")[1]

    return state.strip()

def line_to_row(line, *args):
    # convert line to series for insertion into the report DataFrame as a row

    row =  [pd.to_datetime(args[0]), pd.to_datetime(args[1])] + list(args[2:]) 
    row += [pd.to_numeric(x, errors='coerce') for x in line.split()]

    return row

def parse_pdf(arc_text, verbose=True):
    # Read PDF line by line and fill a DataFrame with 
    # the extracted data. 

    cols = ['start','end','drug_code','drug_name','state','zipcode',
            'Q1','Q2','Q3','Q4','Total']
    rows = []

    start = ""
    end = ""
    code = ""
    name = ""
    state = ""

    if verbose:
        iterator = lambda x: tqdm(x)
    else:
        iterator = lambda x: x

    for line in iterator(arc_text.split("\n")):
        line = clean_line(line)

        if len(line) == 0:
            continue
        elif re.match(r"^\d{3}( \d+\.?\d{2}){5}", line):
            # This is a data row, so let's add it to the list
            rows.append(line_to_row(line, start, end, code, name, state))
        elif re.match(r".*ARCOS.+REPORT 0?2", line):
            # Some years have all the different reports together, so if we 
            # hit "Report 2" then stop processing
            break
        elif re.match(r"^STATE:", line):
            # This contains the state for the following rows
            state = get_state(line)
        elif re.match(r"^DRUG\s*(CODE)*:", line):
            # This contains the drug information for the following rows
            code, name = get_drug_info(line)
        elif re.match(r".*\d{2}/\d{2}/\d{4} TO \d{2}/\d{2}/\d{4}", line):
            # This contains the reporting period start and end dates
            try:
                start, end = get_periods(line)
            except ValueError:
                print(line)
                raise

    report_df = pd.DataFrame(rows, columns=cols)

    return report_df

def get_pdf_text(pdf_path, *args):

    if len(args) == 0:
        args = ('-table','-enc','UTF-8')

    process_call = ['pdftotext'] + [str(a) for a in args] + [pdf_path, '-']

    pdf = subprocess.run(process_call, capture_output=True)

    return pdf.stdout.decode()

def run(args):
    verbose = args.verbose
    files = args.files
    outfile = args.outfile
    DIR = os.getcwd()

    if len(files) == 1:
        if os.path.isdir(files[0]):
            DIR = files[0]
            files = [os.path.join(DIR, x) for x in os.listdir(DIR) \
                     if x.lower().endswith('.pdf')]

    if not os.path.isabs(outfile):
        outfile = os.path.join(DIR,outfile)

    dfs = []

    for file in files:
        if verbose:
            print("Extracting from " + file)
        txt = get_pdf_text(file)
        dfs.append(parse_pdf(txt, verbose))

    df = pd.concat(dfs)
    df.to_csv(outfile, index=False)

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process ARCOS data.')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Report processing progress.')
    parser.add_argument('-o', '--outfile', default="ARCOS_datasets.csv",
                        help='File name for writing out combined DataFrame.')
    parser.add_argument('files', nargs="+", default='aggzips.shp',
                        help='Path to the geospatial file for mapping the ARCOS'
                             ' data. Default: `aggzips.shp` in '
                             'the working directory.')

    args = parser.parse_args()

    run(args)
