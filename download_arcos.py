
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import requests
from tqdm import tqdm
from urllib.request import urlopen

def download_pdf(pdf_url, chunk_size=1024, verbose=False, DIR=None):

    headers = requests.head(pdf_url).headers
    tformat = "%a, %d %b %Y %H:%M:%S %Z"
    remote_time = datetime.strptime(headers['Last-modified'], tformat).timestamp()

    local_name = pdf_url[pdf_url.rfind("/")+1:]

    if DIR is not None:
        local_name = os.path.join(DIR, local_name)

    if os.path.exists(local_name) and os.path.getmtime(local_name) > remote_time:
        pass
    else:
        if verbose:
            print("Downloading {} to {}".format(pdf_url, local_name))
            t = (int(headers['content-length']) // 1024) + 1
            chunks = lambda x: tqdm(x.iter_content(chunk_size=chunk_size), total=t)
        else:
            chunks = lambda x: x.iter_content(chunk_size=chunk_size)

        r = requests.get(pdf_url, stream = True)
        
        with open(local_name, "wb") as pdf:
            for chunk in chunks(r):
                if chunk:
                    pdf.write(chunk)

    return None


def get_arcos_pdfs(url):
    rpts = re.compile("Reporting Period")

    page = urlopen(url).read()
    soup = BeautifulSoup(page, features="html.parser")
    div = soup.find_all('div', {'class':['page_content']})[0]
    links = [e.parent['href'] for e in div.find_all(text=rpts)]

    pdfs = []

    if len(links) == 0:
        link = div.select('a[href*="rpt1"]')[0]
        pdfs.append(url[:url.rfind("/")+1] + link['href'])
    else:
        # this is the main page, get the years 2016 and onward
        for link in links:
            if link.endswith("pdf"):
                pdfs.append(url[:url.rfind("/")+1] + link)
            else:
                pdfs += get_arcos_pdfs(url + link)

    return pdfs

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get ARCOS data from source.')
    parser.add_argument('-s', '--source', required=True,
                        help='Root URL for to the ARCOS datasets')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Show progress while downloading')
    parser.add_argument('-c', '--chunk_size', type=int, default=1024,
                        help='Chunk size while downloading. Default is `1024`')
    parser.add_argument('-d', '--dir', default=os.getcwd(),
                        help='Chunk size while downloading. Default is the '
                             'current working directory')
    args = parser.parse_args()

    pdfs = get_arcos_pdfs(args.source)

    for pdf in pdfs:
    	download_pdf(pdf, 
                     chunk_size=args.chunk_size, 
                     verbose=args.verbose, 
                     DIR=args.dir)
