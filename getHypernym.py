__author__ = 'Esther'
import urllib.request
import json
import random

def getHypernym(word):
    hypernyms = []
    # Set the request URL
    url = 'http://conceptnet5.media.mit.edu/data/5.2/c/en/'+word.lower()
    # Send the GET request
    resp = urllib.request.urlopen(url)
    resp = resp.read()
    # Interpret the JSON response
    info = json.loads(resp.decode('utf8'))
    for edge in info["edges"]:
        if len(edge["uri"].split(",")) == 3:
            relation, hyponym, hypernym = edge["uri"].split(",")
            # hypernym relation is encoded as /r/IsA
            if "/r/IsA/" in relation and word in hyponym and not "_" in hypernym:
                hypernyms.append(hypernym.split("/")[-2])
    if hypernyms != []:
        hypernym = hypernyms[random.randint(0,len(hypernyms)-1)]
        return hypernym
    return ""