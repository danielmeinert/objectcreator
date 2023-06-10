# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 21:21:30 2023

@author: puvlh
"""

import requests

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()

        total_length = int(r.headers.get('content-length'))
        print(total_length)
        with open(local_filename, 'wb') as f:
            i=0
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                f.write(chunk)
                print(i*8192/total_length)
                i += 1
    return local_filename