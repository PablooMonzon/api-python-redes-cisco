import json
import os
import requests
api_url = "http://localhost:58000/api/v1/ticket"

headers = {
    "content-type": "application/json"
}

# Usuario y clave del controlador: se toman de las variables de entorno NC_USER y NC_PASS
# (asi no quedan escritos en el repositorio); si no estan, se usan los de la catedra.
body_json = {
    "username": os.getenv("NC_USER", "cisco"),
    "password": os.getenv("NC_PASS", "cisco123!")
}

resp = requests.post(api_url, json.dumps(body_json), headers=headers)

print("Ticket request status: ", resp.status_code)
response_json = resp.json()
print (response_json)
serviceTicket = response_json["response"]["serviceTicket"]

print("The service ticket number is: ", serviceTicket) 