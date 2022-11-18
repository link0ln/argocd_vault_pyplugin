#!/usr/bin/env python3

import hvac
import sys
import os
import yaml
from yaml.loader import SafeLoader
import re

pinput=""

try:
  sys.argv[1]
except:
  print('ERROR: type "-" or filename')
  sys.exit(0)

if sys.argv[1] == "-":
  for line in sys.stdin:
    pinput = f'{pinput}{line}'
else:
  pinput = open(sys.argv[1], 'r').read()

try:
  vault_addr  = os.environ['ARGOCD_ENV_VAULT_ADDR']
  vault_token = os.environ['ARGOCD_ENV_VAULT_TOKEN']
except:
  print('ERROR: env ARGOCD_ENV_VAULT_ADDR or ARGOCD_ENV_VAULT_TOKEN not found')
  sys.exit(0)

client = hvac.Client(
    url=vault_addr,
    token=vault_token,
)

#read2 = client.secrets.kv.v1.read_secret('inigma/prod/env')['data']

#print(read2)

#sys.exit(0)

if not client.is_authenticated():
  print('ERROR: not authenticated!')
  sys.exit(0)

def kv_wrapper(match_obj):
  return client.secrets.kv.v1.read_secret(match_obj.group(1))['data'][match_obj.group(2)]

def key2value(kv_data):
  podenv = []
  if re.match(r'<path:(.+?)#(.+?)>', kv_data):
    result = re.sub(r'<path:(.+?)#(.+?)>', kv_wrapper, kv_data)
    #kv_split = re.search(r'(.+?)#(.+)', kv_data)
    #result = client.secrets.kv.v1.read_secret(kv_split.group(1))['data'][kv_split.group(2)]
    return result
  else:
    kv_path = re.match(r'<path:(.+?)>', kv_data).group(1)
    result = client.secrets.kv.v1.read_secret(kv_path)['data']
    for k,v in result.items():
      podenv.append({'name': k, 'value': v})
    return podenv

def follow_yaml(data):
  for k, v in data.items():
    if isinstance(v, dict):
      data[k] = follow_yaml(data[k])
    elif isinstance(v, list):
      for i in range(0,len(data[k])):
        data[k] = follow_yaml(data[k][i])
    else:
      try:
        if re.match(r'<path:(.+?)>', v):
          data[k] = key2value(v)
      except Exception as e:
        pass
  return data

docs = yaml.load_all(pinput, yaml.FullLoader)

for data in docs:
  try:
    print('---')
    print(yaml.dump(follow_yaml(data)))
  except:
    pass

