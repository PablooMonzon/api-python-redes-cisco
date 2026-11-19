import json
import os
import requests
api_url = "http://localhost:58000/api/v1/host"

# Ticket: variable de entorno NC_TICKET (lo devuelve 01_get-ticket.py) o pegarlo aca.
headers={"X-Auth-Token": os.getenv("NC_TICKET", "NC-144-d131174a867340c3a5a8-nbi")}


def campo(d, clave):
    # Un equipo que el controlador no administra (el ISP, en "Wrong credential")
    # no trae hostname y viene con otros campos vacios: se muestra "(sin <campo>)".
    return d.get(clave) or "(sin %s)" % clave

resp = requests.get(api_url, headers=headers, verify=False)

print("Request status: ", resp.status_code)

response_json = resp.json()
print (response_json)
print()
print()
hosts = response_json["response"]

for host in hosts:
    print(campo(host, "hostName"), "\t", campo(host, "hostIp"), "\t", campo(host, "hostMac"), "\t", campo(host, "connectedInterfaceName"))