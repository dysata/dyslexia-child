#version 2023-08-06/02
import requests
import argparse
import json


from datetime import datetime

import logging

import os

logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


parser = argparse.ArgumentParser()

parser.add_argument("-withr", help="download annotated audio with r sound",  action='store_true')

parser.add_argument("-timestart", type=valid_date, help="The Start Date - format YYYY-MM-DD (UTC)")
parser.add_argument("-timeend", type=valid_date, help="The End Date - format YYYY-MM-DD (UTC)")


parser.add_argument("path", type=str, help="Path to store your files")
parser.add_argument("-tags", type=str, nargs = '+', help="Tags (key-words)")
requiredNamedArgs = parser.add_argument_group('required named arguments')
requiredNamedArgs.add_argument("-password", type=str, help="Your HPC2C password", required=True)
requiredNamedArgs.add_argument("-login", type=str, help="Your HPC2C login name", required=True)
#parser.add_argument("-token")

args = parser.parse_args()

print(f'Args:\n\t{args}')

s = requests.Session()
url = "https://hpccloud.ssd.sscc.ru/api/1.0/tokens"
username = args.login # "dyslexia002"
password = args.password # "myTest23"
response = s.get(url, auth=(username, password))
if(response.status_code != 200):
    print('Authorization failed')
    quit()
response_json = response.json()
print(response_json)
token = response_json['tokens'][0]['token']
user_id = response_json['tokens'][0]['user_id']
#print(token)

import os
if(args.path): 
    cwd = os.mkdir(args.path)
    os.chdir(args.path)



def try_download_file(filename):
    url = "https://hpccloud.ssd.sscc.ru/storage/" + filename
    r = s.get(url, allow_redirects=True)
    print(f"\tCouchDB response: Status Code: {r.status_code}, reason: {r.reason}")
    if r.status_code == 200:
        open(filename, 'wb').write(r.content)
    return r.status_code

def download_file(filename):
    flag = 0
    for i in range(10):
        print(f"Attempt {i}")
        status_code = try_download_file(filename)
        if 200 == status_code:
            flag = 1
            break
    if flag == 0:
        print("Could not download this file")
    

import json

def download():
    url = "https://hpccloud.ssd.sscc.ru/couchdb/aka/_find"
    headers = { 'Content-type' :   'application/json; charset=utf-8' }
    query = {
        "selector" : {
            "dataobject": 
             { 
                "$and" : 
                [
                    {
                        "files": {
                            "$elemMatch": {
                                "mime": {
                                   "$regex": "audio*"
                                }
                            }
                        },
                        "meta" : {
                            "annotation" : {
                                "$and" : [
                                 ]
                            }
                        }
                    }
               ]
            }
        },
        "limit" : 1000
    }
    if args.tags:
        tags = {
            "tags": {
                "$all": args.tags
            }
        }
        query["selector"]["dataobject"]["$and"].append(tags)

    if args.withr:
        rexists = {
                     "value": {
                        "$elemMatch": {
                           "$and": [
                              {
                                 "data.rquality": {
                                    "$exists": True
                                 }
                              }
#                              ,
#                              {
#                                 "data.rquality": {
#                                    "$ne": "no-sound"
#                                 }
#                              }
                           ]
                        }
                     }
                  }

        query["selector"]["dataobject"]["$and"][0]["meta"]["annotation"]["$and"].append(rexists)

    if args.timestart:
        ts_stamp = int(args.timestart.strftime("%s")) * 1000
        ts = {
                "timestamp": {
                    "$gte": ts_stamp
                }
             }

        query["selector"]["dataobject"]["$and"][0]["meta"]["annotation"]["$and"].append(ts)
    if args.timeend:
        te_stamp = int(args.timeend.strftime("%s")) * 1000
        
        te = {
                "timestamp": {
                    "$lte": te_stamp
                }
             }

        query["selector"]["dataobject"]["$and"][0]["meta"]["annotation"]["$and"].append(te)

    json_formatted_str = json.dumps(query, indent=2)

    print(json_formatted_str)


    r = s.post(url, json = query, headers = headers)   
    print(f"\tCouchDB response: Status Code: {r.status_code}, reason: {r.reason}")

#    print(r.json())

    records = r.json()['docs']
    total = len(records)
    print(f"Received info about {total} files")

    for idx, o in enumerate(records):
        filename = o['dataobject']['files'][0]['path']

        print(f"Downloading file {idx} of {total}, filename = {filename}")
        metafile = f"{filename}.json"
        with open(metafile, 'w') as mf:
                mf.write(json.dumps(o, indent=4))
        download_file(filename)




download()



