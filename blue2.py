import requests

#BASE = "http://127.0.0.1:8000/"
#dict = {"distance": "A", "time": "B", "direction" : "C"}
#response = requests.post(BASE + "/Motor", data = dict, verify = False)
#print(response.json())
#response = requests.get(BASE + "shutdown")

BASE = "http://127.0.0.1:8000/"
diction = {"distance" : "A", "time": "B", "direction": "C"}
response = requests.post(url=BASE + "items/", json=diction)
print(response.json())