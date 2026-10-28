import requests
import os
import hashlib
import csv

def get_access_token(url, client_id, client_secret):
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    return response.json()["access_token"]

def compute_file_hash(filepath):
    # Read file and append filename
    with open(filepath, "rb") as f:
        file_data = f.read()

    # Append filename as bytes
    file_data += filepath.encode('utf-8')

    # Compute SHA-256
    sha256_hash = hashlib.sha256(file_data).hexdigest()

    return sha256_hash

def compute_folder_hashes(folderName, playlistId):
    hashes = []
    for filename in os.listdir(folderName):
        filepath = os.path.join(folderName, filename)

        if not os.path.isfile(filepath):
            continue;
        hashes.append({"hash": compute_file_hash(filepath), "folder": folderName, "playlistId": playlistId})

    return hashes

def check_and_add_file(hash, headers, playlistId, folderName):
    for filename in os.listdir(folderName):
        filepath = os.path.join(folderName, filename)

        if not os.path.isfile(filepath):
            continue;

        if hash == compute_file_hash(filepath):
            with open(filepath, "rb") as f:
                try:
                    playlistId_int = int(playlistId)
                    requests.post(os.environ["XIBO_URL"] + '/api/library', files={"files": f}, data={"name": hash, "playlistId": playlistId_int}, headers=headers)
                except:
                    print("ERROR! NON-INTEGER PLAYLIST ID")

#Read config, folders stores folderName then playlistId
folders = []
with open('config.csv') as folder_config:
    csv_reader = csv.reader(folder_config, delimiter=',')
    for row in csv_reader:
        folders.append({"folderName": row[0], "playlistId": row[1]})
#Start by getting an access token
access_token = get_access_token(os.environ["XIBO_URL"] + "/api/authorize/access_token", os.environ['XIBO_CLIENT_ID'], os.environ['XIBO_CLIENT_SECRET'])
#Then pull the library
headers = {"Authorization": "Bearer " + access_token}
library = requests.get(os.environ["XIBO_URL"] + "/api/library", params={"length": 100000}, headers=headers)

library_json = library.json()
library_files = [library_file["name"] for library_file in library_json]

#Calculate the hashes for the local directory
hashes = []
for folder in folders:
    hashes += compute_folder_hashes(folder["folderName"], folder["playlistId"])

#If hashes is empty, just remove everything
if hashes == None:
    for hash in library_files:
        #Find the media ID, then remove said media id:
        for library_file in library_json:
            if library_file["name"] == hash and not library_file["name"].startswith("internal"):
                params = {"forceDelete": 1}
                requests.delete(os.environ["XIBO_URL"] + "/api/library/" + str(library_file["mediaId"]), params=params, headers=headers)
    exit(0)

#Compute files to remove and those that don't need to be removed
hashes_to_keep = []
for hash in hashes:
    for library_file in library_files:
        if hash["hash"] == library_file:
            hashes_to_keep.append(hash["hash"])
            library_files.remove(hash["hash"])
#Remove those files
for hash in library_files:
    #Find the media ID, then remove said media id:
    for library_file in library_json:
        if library_file["name"] == hash and not library_file["name"].startswith("internal"):
            params = {"forceDelete": 1}
            requests.delete(os.environ["XIBO_URL"] + "/api/library/" + str(library_file["mediaId"]), params=params, headers=headers)
#Add the new ones
hashes_to_add = [x for x in hashes if x not in hashes_to_keep]
for hash in hashes_to_add:
    for hash_to_keep in hashes_to_keep:
        if hash["hash"] == hash_to_keep:
            continue
    check_and_add_file(hash["hash"], headers, hash["playlistId"], hash["folder"])
