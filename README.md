# API del Network Controller de Packet Tracer con Python – TP4 Redes de Computadoras (3643)

Scripts suministrados por la cátedra (repositorio `redes-computadoras/api-python-redes-cisco`) y el
script propio del grupo para la Actividad 4 del TP4. Consumen la API REST (Northbound API) del
Network Controller de Packet Tracer.

## Scripts

| Script | Qué hace |
|---|---|
| `src/01_get-ticket.py` | Pide un ticket al controlador (`POST /api/v1/ticket`) con usuario y clave, y muestra el código de respuesta y el *service ticket*. |
| `src/02_get-network-device.py` | Lista los equipos de red (`GET /api/v1/network-device`): muestra el JSON y una tabla con hostname, plataforma e IP de administración. |
| `src/03_get-host.py` | Lista los hosts finales (`GET /api/v1/host`): muestra el JSON y una tabla con nombre, IP, MAC e interfaz del switch a la que se conectan. |
| `src/04_tabulate.py` | Pide su propio ticket y muestra con `tabulate` dos tablas: equipos (hostname, número de serie, versión de software) y hosts (nombre, tipo, IP). |
| `src/inventario_custom.py` | **Script propio.** Une equipos y hosts en un solo CSV y muestra un resumen por estado que marca los equipos no administrados. |

### Script propio: `inventario_custom.py`

Pide el ticket, consulta `GET /api/v1/network-device` y `GET /api/v1/host`, y los exporta a un único CSV con las
columnas `origen, nombre, tipo, ip, mac, plataforma, alcance, estado, conectado_a`. Luego muestra cuántos equipos
hay en cada estado y lista los que no quedaron administrados.

`alcance` es el `reachabilityStatus` (*Reachable*/*Unreachable*) y `estado` el `collectionStatus` (*Managed*,
*Wrong credential*, ...). El resumen decide por `estado`: en nuestra topología el ISP figura *Unreachable* porque
falla la autenticación, pero lo relevante es que queda en *Wrong credential*, como pide el diseño.

**Valor agregado:** junta en un archivo lo que los scripts de la cátedra muestran por separado, deja un CSV para el
informe o una planilla, y sirve como chequeo rápido de que el Discovery quedó completo.

```
python src/inventario_custom.py --out inventario.csv
python src/inventario_custom.py --demo --out inventario_demo.csv    # prueba sin controlador
```

Opciones: `--url` (URL del controlador), `--user` (si no se indica la clave, se pide por teclado), `--out`, `--demo`.

### Cambios hechos a los scripts de la cátedra

- **Equipos no administrados:** `02` y `04` terminaban con `KeyError: 'hostname'` al llegar a un equipo en
  *Wrong credential* (el ISP), porque el controlador no devuelve sus datos de inventario. Se agregó una función
  `campo()` que muestra `(sin hostname)`, `(sin platformId)`, etc. cuando falta el dato. Se aplicó también en `03`.
- **Credenciales y ticket fuera del código:** el usuario y la clave se leen de `NC_USER` y `NC_PASS` (`01` y `04`), y
  el ticket de `NC_TICKET` (`02` y `03`). Si no están definidas, se usan los valores originales de la cátedra
  (`cisco` / `cisco123!` y el token de ejemplo), así que los scripts funcionan igual que antes.

## Instalación

1. Clonar el repositorio y entrar a la carpeta:

   ```
   git clone <URL_del_repositorio> api-python-redes-cisco
   cd api-python-redes-cisco
   ```

2. Crear y activar el entorno virtual (en el ejemplo se llama `cisco`):

   ```
   python3 -m venv cisco
   source cisco/bin/activate        # Linux
   cisco\Scripts\activate           # Windows (PowerShell)
   ```

3. Instalar las dependencias: `pip install -r requirements.txt`
4. En VS Code, elegir como intérprete el Python del entorno `cisco`.
5. Para salir del entorno: `deactivate`

La carpeta del entorno virtual, los `.env` y los `.csv` generados no se suben (están en el `.gitignore`).

## Conexión con el Network Controller

En Packet Tracer, en el Network Controller: *Config* → *Controller* (Real World) → marcar *Access Enabled*. El
controlador queda accesible desde la PC en `http://localhost:58000` (el puerto puede variar; la documentación de la
API está en `http://localhost:58000/swagger.html`). Se usan el usuario y la clave creados en el primer ingreso al
dashboard del controlador.

## Variables de entorno

Los scripts no tienen usuarios ni claves reales en el código: los leen de variables de entorno. `.env.example`
muestra cuáles son; se puede copiar como `.env` (no se sube) para tener los valores a mano, pero los scripts **no**
leen ese archivo: hay que cargar las variables en la terminal antes de ejecutarlos.

| Variable | Uso | Si no se define |
|---|---|---|
| `NC_BASE_URL` | URL del controlador (`inventario_custom.py`) | `http://localhost:58000` |
| `NC_USER` | Usuario del controlador | `cisco` (`01`, `04`); se pide por teclado (`inventario_custom.py`) |
| `NC_PASS` | Clave del controlador | `cisco123!` (`01`, `04`); se pide por teclado (`inventario_custom.py`) |
| `NC_TICKET` | Ticket para `02` y `03` | token de ejemplo de la cátedra (no funciona: hay que pedir uno nuevo) |

PowerShell:

```
$env:NC_USER = "usuario"
$env:NC_PASS = "clave"
python src/01_get-ticket.py
$env:NC_TICKET = "NC-...-nbi"      # el ticket que mostró 01
python src/02_get-network-device.py
python src/03_get-host.py
python src/04_tabulate.py
python src/inventario_custom.py --out inventario.csv
```

Linux:

```
export NC_USER=usuario NC_PASS=clave
python src/01_get-ticket.py
export NC_TICKET=NC-...-nbi
python src/02_get-network-device.py
```

El ticket vence (idle 15 minutos, sesión 1 hora): si `02` o `03` responden 401, hay que pedir uno nuevo con `01`.
