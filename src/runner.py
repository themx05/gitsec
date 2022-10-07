#! /bin/python3
from yaml import load, SafeLoader
import argparse
import json
import os
from typing import Dict
from requests import request
from nacl import public, encoding
from base64 import b64encode

def secureSecret(value: str, key: Dict):
    publicKey = public.PublicKey(key['key'].encode("utf-8"), encoding.Base64Encoder())
    box = public.SealedBox(publicKey)
    encrypted = box.encrypt(value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def setupSecret(repository: Dict, key: Dict, secret: Dict, config):
    apiUrl="https://api.github.com/repos/{repoName}/actions/secrets/{secret}".format(repoName = repository['name'], secret = secret['name'])

    signed = secureSecret(secret['value'], key)
    req = request(
        method="PUT",
        url = apiUrl, 
        headers= {
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'Authorization': "token {token}".format(token = config['authorization']['token'])
        },
        data= json.dumps({
            'encrypted_value': signed,
            'key_id': key['key_id']
        })
    )

    if req.status_code >= 200 and req.status_code <= 204 :
        print("|--{name}: Configured ✅".format(name = secret['name']))

    return

def setupRepository(repoId: str, repository: Dict, config: Dict):
    print("[{repo}]: Configuring secrets".format(repo = repository['name']))

    getPublicKey = request(
        method="GET",
        url = "https://api.github.com/repos/{repoName}/actions/secrets/public-key".format(repoName = repository['name']), 
        headers= {
            'Accept': 'application/vnd.github+json',
            'Authorization': "token {token}".format(token = config['authorization']['token'])
        },
    )

    key = json.loads(getPublicKey.text)

    for s in repository['secrets']:
        secret = config['secrets'][s]
        setupSecret(repository= repository, secret= secret, key = key, config=config)

    print("[{repo}]: all secrets configured 👐👐👐\n".format(repo = repository['name']))
    return


def processConfig(config: Dict):
    repos: Dict = config['repositories']
    for k in repos.keys():
        repo = repos[k]
        setupRepository(k, repo, config)
    return

parser = argparse.ArgumentParser("Automate Github Action Secrets Deployments")
parser.add_argument("--file", '-f', metavar="file", type=str, help="The configuration file where to read data")


def __main__():
    args = parser.parse_args()
    file = os.path.join(os.getcwd(), args.file)
    with open(file) as f:
        config = load(f, Loader = SafeLoader)
        processConfig(config)
        f.close()
    pass

__main__()