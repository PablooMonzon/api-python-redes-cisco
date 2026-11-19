import json
import os
import requests
api_url = "http://localhost:58000/api/v1/network-device"

# Ticket: variable de entorno NC_TICKET (lo devuelve 01_get-ticket.py) o pegarlo aca.
headers={"X-Auth-Token": os.getenv("NC_TICKET", "NC-144-d131174a867340c3a5a8-nbi")}


def campo(d, clave):
    # Un equipo que el controlador no administra (el ISP, en "Wrong credential")
    # no trae hostname y viene con otros campos vacios: se muestra "(sin <campo>)".
    return d.get(clave) or "(sin %s)" % clave

resp = requests.get(api_url, headers=headers)

print("Request status: ", resp.status_code)

response_json = resp.json()
print()
print()
print (response_json)
print()
print()
networkDevices = response_json["response"]

for networkDevice in networkDevices:
    print(campo(networkDevice, "hostname"), "\t", campo(networkDevice, "platformId"), "\t", campo(networkDevice, "managementIpAddress"))
