#Módulos que se usarán
import requests #Para entender solicitudes
import json #Para reconocer el formato json
import os #Para leer usuario y clave de variables de entorno
from tabulate import * #Para crear tablas

baseUri = "http://localhost:58000/api/v1" #URL de PT

def campo(d, clave):
    # Equipos no administrados (el ISP, en "Wrong credential") vienen sin hostname
    # y con otros campos vacios: se muestra "(sin <campo>)".
    return d.get(clave) or "(sin %s)" % clave

# Llamada al API por el ticket
headers = {"Content-Type": "application/json"} #Headers
data = json.dumps({"username": os.getenv("NC_USER", "cisco"), "password": os.getenv("NC_PASS", "cisco123!")}) #Credenciales (NC_USER / NC_PASS)
resp = requests.post(baseUri+"/ticket", data=data, headers=headers) #URL específica

print("Status de Solicitud:")
print(resp.status_code)
result = resp.json()
# print(result)

ticket = result["response"]["serviceTicket"] #Printing ticket
print("\nEl Service Ticket es:")
print(ticket)


# Llamada al API para recibir los dispositivos de red
headers = {"X-Auth-Token": ticket}
resp = requests.get(baseUri+"/network-device", headers=headers) #URL específica

# print (resp.status_code)
result = resp.json()
#print (json.dumps(result, indent=4))
print("\nDispositivos de Red:")
host_list=[]
i=0
for item in result["response"]:
    i+=1
    host_list.append([i,campo(item, "hostname"),campo(item, "serialNumber"),campo(item, "softwareVersion")])
    #print(campo(item, "hostname")+" "+campo(item, "serialNumber")+" "+campo(item, "softwareVersion")) #Lista completa

print(tabulate(host_list,headers=["Hostname","Serial Number","Software Version"],tablefmt='rst')) #Tabla ordenada 

# Llamada al API para recibir los host
headers = {"X-Auth-Token": ticket }
resp = requests.get(baseUri+"/host", headers=headers) #URL específica

# print (resp.status_code)
result = resp.json()
#print (json.dumps(result, indent=4))
print("\nHosts de la Red:")
host_list=[]
i=0
for item in result["response"]:
    i+=1
    host_list.append([i,campo(item, "hostName"),campo(item, "hostType"),campo(item, "hostIp")])
    #print(campo(item, "hostName")+" "+campo(item, "hostType")+" "+campo(item, "hostIp")) #Lista completa

print(tabulate(host_list,headers=["Hostname","Tipo","IP"],tablefmt='rst')) #Tabla ordenada 