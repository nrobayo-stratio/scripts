#!/usr/bin/env python
# outputs curl commands to delete images from docker registry
# https://stratio.atlassian.net/wiki/spaces/MUT/pages/485523555/Mantenimiento+docker+registry

# USAGE:
# 1: run this from the bootstrap, not its container
# 2: you have to set the docker registry url
# 3: registry must been started with "-e REGISTRY_STORAGE_DELETE_ENABLED=true"
#    you can check it on /etc/systemd/system/docker-registry.service
# 4: after launching the DELETE curls, you must run this in order to free up the space:
#    docker exec -it registry bin/registry garbage-collect /etc/docker/registry/config.yml



import requests

# to avoid ssl insecure errors
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import urllib3
#urllib3.disable_warnings()

import json


# docker registry
URL = "http://localhost:5001/"


r = requests.get(url = URL + "/v2/_catalog?n=1000", verify=False) 
catalog = r.json() 
#print(json.dumps(data, indent=2))

# loop through all apps
for app in catalog['repositories']:
    r = requests.get(url = URL + "/v2/" + app + "/tags/list", verify=False)
    dataApp = r.json()

    if 'errors' in dataApp.keys():
        print("ERROR!!! " + dataApp['errors'][0]['detail']['name'] + " WTF!!!: " + str(dataApp))
    elif dataApp['tags']:
        # loop through all tags
        tagNum = 0
        while tagNum < len(dataApp['tags']):
            URLSHA = URL + "/v2/" + dataApp['name'] + "/manifests/" + dataApp['tags'][tagNum]
            HEADERS = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
            r = requests.get(url = URLSHA, verify=False, headers=HEADERS)
            if 'Docker-Content-Digest' in r.headers.keys():
                #SHA256 = r.headers['Docker-Content-Digest']
                # write, but not execute, the curl to delete the app
                #CURL = 'curl -v -s -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X DELETE '
                #print(dataApp['name'] + ":" + dataApp['tags'][tagNum] + "\t" + CURL + URL + "/v2/" + dataApp['name'] + "/manifests/" + SHA256)
                print("if1 " + str(URL) + dataApp['name'] + ":" + dataApp['tags'][tagNum])
            elif 'docker-content-digest' in r.headers.keys():
                SHA256 = r.headers['docker-content-digest']

                # write, but not execute, the curl to delete the app
                #CURL = 'curl -v -s -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X DELETE '
                #print(dataApp['name'] + ":" + dataApp['tags'][tagNum] + "\t" + CURL + URL + "/v2/" + dataApp['name'] + "/manifests/" + SHA256)
                print("if2 " + str(URL) + dataApp['name'] + ":" + dataApp['tags'][tagNum])
            else:
                print("ERROR!!! " + dataApp['name'] + ":" + dataApp['tags'][tagNum] + " has no SHA256!!!: " + str(r.headers))

            tagNum += 1
    else:
        print("ERROR!!! " + dataApp['name'] + " has no tags!!!: " + str(dataApp))
