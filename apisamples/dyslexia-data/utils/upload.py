import requests
import argparse
import json

import logging

import os

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)



parser = argparse.ArgumentParser()
parser.add_argument("path", type=dir_path, help="Path to a file tree with audio files")
parser.add_argument("tags", type=str, nargs = '+', help="Tags (key-words)")
requiredNamedArgs = parser.add_argument_group('required named arguments')
requiredNamedArgs.add_argument("-nameprefix", type=str, help="We change file names when storing the files to HPC2C to generated id strings. The strings will start with this prefix", required=True)
requiredNamedArgs.add_argument("-password", type=str, help="Your HPC2C password", required=True)
requiredNamedArgs.add_argument("-login", type=str, help="Your HPC2C login name", required=True)
#parser.add_argument("-token")

args = parser.parse_args()

print(f'Args:\n\t{args}')

s = requests.Session()
url = "http://localhost:3000/tokens"
username = args.login # "user"
print(username)
password = args.password # "password"
print(password)
response = s.get(url, auth=(username, password))
print(response.status_code)
if(response.status_code != 200):
    print('Authorization failed')
    quit()
response_json = response.json()
print(response_json)
token = response_json['tokens'][0]['token']
user_id = response_json['tokens'][0]['user_id']
print(token)

import pathlib

count = 0
failed = []
import os
cwd = os.getcwd()

attempts = 0

def try_upload(file, filename, type):
    global attempts
    global count
    url = "http://localhost:3000/storage/" + filename
    headers = {'Content-type': 'audio/' + type, 'X-Method-Override' : 'PUT'}
    r = s.put(url, data=open(file, 'rb'), headers=headers)
    print(f"\tNextCloud response: Status Code: {r.status_code}, reason: {r.reason}")
    return r
   
import string
import random

def file_rename(f):
    letters = string.ascii_lowercase
    modify = ''.join(random.choice(letters) for i in range(1))
    new_name = f"{f.with_suffix('')}-{modify}{f.suffix}"
    old_name_meta = f"{f.with_suffix('')}.json"
    new_name_meta = f"{f.with_suffix('')}-{modify}.json"
    os.rename(f.as_posix(), new_name)
    os.rename(old_name_meta, new_name_meta)
    log.info(f'\tRenamed to:\n\t{new_name}')
    return pathlib.Path(new_name)


def upload(file, type):
    global count
    global failed
    global attempts
    #filename = pathlib.Path(file).name

    filename = str(user_id) + '-audio-' + args.nameprefix + '-' + str(count) + '.' + type
    count = count + 1

    r = try_upload(file, filename, type)

    if r.status_code == 503:
        while r.status_code == 503 and attempts < 10:
            log.warn("Could not upload a file (error 503), trying to rename")
            file = file_rename(file)
            r = try_upload(file, filename, type)
            attempts += 1

    attempts = 0

    if r.status_code == 201:
        url = "http://localhost:3000/couchdb/dyslexia/"
        headers = { 'Content-type' : 'application/json' }
        meta = {}
        meta_file_path = file.with_suffix('.json')
        print(f"\tMeta file path = {meta_file_path}")
        if(os.path.exists(meta_file_path)):
            meta_file = open(meta_file_path)
            meta = json.load(meta_file)
        else:
            log.warning("could not find meta file for" + file.resolve().as_posix())
        print(f"\tMeta = {meta}")
        couchdb_doc = {'dataobject' : { "files": [{ 'path' : filename, 'mime' : "audio/" + type }], 'user_id': user_id, 'type' : "uploaded", 'original_path' : file.resolve().as_posix(), 'meta' : meta}}
        couchdb_doc['dataobject']['tags'] = args.tags
        print(f"\tSaving to CouchDB: {couchdb_doc}")
        r = s.post(url, json = couchdb_doc, headers = headers)   
        print(f"\tCouchDB response: Status Code: {r.status_code}, reason: {r.reason}")
        print(f"\tcontent: {r.content}")
    else:
        print(f"\tFailed to upload file {file}")
        failed.append({'file' : file, 'code' : r.status_code, 'reason' : r.reason})
 
#    print(meta)



path = pathlib.Path(args.path)


filetypes = ["wav", "ogg", "m4a", "mp3"]
for t in filetypes:
    print('- Processing ' + t + ' files -')
    for f in path.rglob('*.' + t):
        print(f"\tGoing to upload {f}")
        upload(f, t)
    print('- Done -')

print("")
print("Was not able to upload these files:")
print("")
for f in failed:
    print(f"{f['file']}:\n\tstatus code = {f['code']}, reason = {f['reason']}")




