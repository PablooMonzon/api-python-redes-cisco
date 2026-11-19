"""inventario_custom.py - script propio del grupo (TP4, Redes de Computadoras 3643).

Pide un ticket al Network Controller de Packet Tracer (POST /api/v1/ticket), consulta los
equipos de red (GET /api/v1/network-device) y los hosts (GET /api/v1/host), los une en un
solo CSV y muestra un resumen por estado que marca los equipos que el controlador no
administra (por diseno, el ISP queda en "Wrong credential").

Uso:
    python src/inventario_custom.py --out inventario.csv
    python src/inventario_custom.py --demo --out inventario_demo.csv   (sin controlador)

Usuario y clave: variables de entorno NC_USER y NC_PASS (o --user, y la clave se pide por
teclado). URL: --url o NC_BASE_URL (por defecto http://localhost:58000).
"""
import argparse
import csv
import getpass
import os
import sys
from collections import Counter

try:
    import requests
except ImportError:  # permite usar --demo sin dependencias instaladas
    requests = None

API = "/api/v1"
TICKET_PATH = API + "/ticket"
DEVICE_PATH = API + "/network-device"
HOST_PATH = API + "/host"

FIELDS = ["origen", "nombre", "tipo", "ip", "mac", "plataforma", "alcance", "estado", "conectado_a"]


def first(d, *keys):
    """Devuelve el primer campo no vacio de d entre keys (la API de PT varia segun version)."""
    for k in keys:
        v = d.get(k)
        if v not in (None, "", []):
            return v if not isinstance(v, list) else ", ".join(map(str, v))
    return ""


def get_config(args):
    base = (args.url or os.getenv("NC_BASE_URL") or "http://localhost:58000").rstrip("/")
    user = args.user or os.getenv("NC_USER") or input("Usuario del controlador: ")
    pwd = os.getenv("NC_PASS") or getpass.getpass("Clave del controlador: ")
    return base, user, pwd


def get_ticket(base, user, pwd):
    r = requests.post(base + TICKET_PATH,
                      json={"username": user, "password": pwd},
                      headers={"Content-Type": "application/json"},
                      timeout=15)
    r.raise_for_status()
    resp = r.json().get("response", {})
    ticket = resp.get("serviceTicket") if isinstance(resp, dict) else None
    if not ticket:
        raise RuntimeError("La API no devolvio serviceTicket: %s" % r.text)
    return ticket


def api_get(base, path, ticket):
    r = requests.get(base + path, headers={"X-Auth-Token": ticket}, timeout=20)
    r.raise_for_status()
    data = r.json().get("response", [])
    return data if isinstance(data, list) else [data]


def device_rows(devices):
    return [{
        "origen": "equipo",
        "nombre": first(d, "hostname", "name") or "(sin hostname)",
        "tipo": first(d, "type", "family"),
        "ip": first(d, "managementIpAddress", "ipAddress", "ip"),
        "mac": first(d, "macAddress"),
        "plataforma": first(d, "platformId", "model"),
        # Son dos datos distintos: "alcance" = reachabilityStatus (Reachable/Unreachable);
        # "estado" = collectionStatus, si el NC lo administra (Managed / Wrong credential / ...).
        # Se decide por "estado": el ISP figura Unreachable por fallar la autenticacion,
        # pero lo que importa es que no quedo administrado (Wrong credential).
        "alcance": first(d, "reachabilityStatus"),
        "estado": first(d, "collectionStatus", "status"),
        "conectado_a": "",
    } for d in devices if isinstance(d, dict)]


def host_rows(hosts):
    return [{
        "origen": "host",
        "nombre": first(h, "hostName", "hostname", "name"),
        "tipo": first(h, "hostType", "type"),
        "ip": first(h, "hostIp", "ipAddress"),
        "mac": first(h, "hostMac", "macAddress"),
        "plataforma": "",
        "alcance": "",
        "estado": "",
        "conectado_a": first(h, "connectedNetworkDeviceName", "connectedNetworkDeviceIpAddress"),
    } for h in hosts if isinstance(h, dict)]


def export_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig: Excel lo abre bien
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("Inventario exportado a: %s (%d filas)" % (path, len(rows)))


def resumen(rows):
    equipos = [r for r in rows if r["origen"] == "equipo"]
    hosts = [r for r in rows if r["origen"] == "host"]
    print("\nEquipos de red: %d | Hosts: %d" % (len(equipos), len(hosts)))
    for estado, n in Counter(r["estado"] or "(sin dato)" for r in equipos).most_common():
        print("  %-22s %d" % (estado, n))
    no_ok = [r for r in equipos if no_administrado(r)]
    if no_ok:
        print("\nEquipos que NO quedaron administrados:")
        for r in no_ok:
            print("  - %-12s %-15s %s" % (r["nombre"], r["ip"], r["estado"] or r["alcance"]))
    else:
        print("\nTodos los equipos quedaron administrados (Managed).")


def no_administrado(r):
    """Managed segun collectionStatus; si la API no lo trae, se usa el alcance."""
    if r["estado"]:
        return r["estado"].strip().lower() != "managed"
    return bool(r["alcance"]) and r["alcance"].strip().lower() != "reachable"


DEMO_DEVICES = [
    {"hostname": "BORDE", "type": "Router", "managementIpAddress": "10.1.1.2", "platformId": "ISR4331", "reachabilityStatus": "Reachable", "collectionStatus": "Managed"},
    {"hostname": "ED-A", "type": "MultiLayerSwitch", "managementIpAddress": "10.1.1.1", "platformId": "3650", "reachabilityStatus": "Reachable", "collectionStatus": "Managed"},
    {"hostname": "SW-A", "type": "Switch", "managementIpAddress": "172.16.99.10", "platformId": "2960", "reachabilityStatus": "Reachable", "collectionStatus": "Managed"},
    {"hostname": "ISP", "type": "Router", "managementIpAddress": "198.51.100.1", "platformId": "", "reachabilityStatus": "Unreachable", "collectionStatus": "Wrong credential"},
]
DEMO_HOSTS = [
    {"hostName": "PC0", "hostIp": "172.16.10.1", "hostMac": "0001.0001.0001", "connectedNetworkDeviceName": "SW-A"},
    {"hostName": "PC4", "hostIp": "172.16.60.1", "hostMac": "0004.0004.0004", "connectedNetworkDeviceName": "SW-SRV"},
]


def main():
    ap = argparse.ArgumentParser(description="Inventario del Network Controller de PT -> CSV")
    ap.add_argument("--out", default="inventario.csv", help="archivo CSV de salida")
    ap.add_argument("--url", help="URL base del controlador (def. http://localhost:58000)")
    ap.add_argument("--user", help="usuario del controlador")
    ap.add_argument("--demo", action="store_true", help="usar datos de ejemplo, sin controlador")
    args = ap.parse_args()

    if args.demo:
        rows = device_rows(DEMO_DEVICES) + host_rows(DEMO_HOSTS)
    else:
        if requests is None:
            sys.exit("Falta instalar dependencias: pip install -r requirements.txt")
        base, user, pwd = get_config(args)
        print("Conectando a %s ..." % base)
        try:
            ticket = get_ticket(base, user, pwd)
            rows = device_rows(api_get(base, DEVICE_PATH, ticket)) + \
                host_rows(api_get(base, HOST_PATH, ticket))
        except (requests.exceptions.RequestException, RuntimeError, ValueError) as e:
            print("ERROR: %s" % e)
            sys.exit("Revisa: Packet Tracer abierto, acceso real HTTP habilitado en el NC, "
                     "URL/puerto, usuario y clave.")
        if not rows:
            sys.exit("La API respondio pero no devolvio equipos: hiciste el Discovery?")

    export_csv(rows, args.out)
    resumen(rows)


if __name__ == "__main__":
    main()
