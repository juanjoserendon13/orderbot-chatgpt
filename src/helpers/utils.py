import json

def transform_to_json(myjson):
  json_dict = {}
  try:
    json_dict = json.loads(myjson)
  except ValueError as e:
    return False
  return json_dict
