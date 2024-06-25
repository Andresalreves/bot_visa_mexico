from datetime import datetime, date, timedelta
from evpn import ExpressVpnApi
import random
import json
import os

def change_ip():
    with ExpressVpnApi() as api:
        locations = api.locations # get available locations
        loc = random.choice(locations)
        api.connect(loc["id"])

def extract_data_file(file):
    # Verificar si el archivo existe
    if os.path.exists(file):
        with open(file, 'r') as archivo:
            datos = json.load(archivo)
    else:
        # Si el archivo no existe, crearlo con una lista vacía
        datos = []
        with open(file, 'w') as archivo:
            json.dump(datos, archivo, indent=4)
        print(f"El archivo {file} no existía y fue creado.")
    return datos

def select_consulados(consulado):
    """
    nombre_consulados = [
        'Mexico City', #70
        'Guadalajara', #66
        'Monterrey', #71
        'Ciudad Juarez', #65
        'Hermosillo', #67
        'Matamoros', #68
        'Merida', #69
        'Nogales', #72
        'Nuevo Laredo', #73
        'Tijuana' #74
    ]
    """
    consulados = []
    cas = []
    list_consulados = ['70','66','71','65','67','68','69','72','73','74']
    list_cas = ['82','77','83','76','78','79','81','84','85','88']
    # Recorre la lista original usando enumerate()
    for indice, elemento in enumerate(list_consulados):
        # Agrega el índice a la lista de índices
        if consulado == elemento:
            consulados.append(str(elemento))
            # Agrega el elemento a la lista de elementos
            cas.append(list_cas[indice])
    return {"consulados":consulados,"cas":cas}

def search_prev_options(consulado):
    list_consulados = ['70','66','71','65','67','68','69','72','73','74']
    list_cas = ['82','77','83','76','78','79','81','84','85','88']
    index_option = list_consulados.index(consulado)
    if index_option > 0:
        prev_consulado = list_consulados[(index_option-1)]
        prev_cas = list_cas[(index_option-1)]
    else:
        prev_consulado = list_consulados[(index_option+1)]
        prev_cas = list_cas[(index_option+1)]
    return {"consulado":prev_consulado,"cas":prev_cas}

def verificar_fecha(fecha_texto,rango):
    fecha_a_verificar = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
    fecha_actual = date.today()
    fecha_limite = fecha_actual + timedelta(days=rango)
    if fecha_a_verificar >= fecha_actual and fecha_a_verificar <= fecha_limite:
        return True
    else:
        return False

def escribir_json(nombre_archivo, datos):
    with open(nombre_archivo, 'w') as archivo:
        json.dump(datos, archivo, indent=4)

def process_response(results,archivo_original):
    fecha = datetime.now().strftime('%Y-%m-%d')
    ruta_agendadas = f"./agendadas/cuentas_completadas_{fecha}.json"
    ruta_logs = f"./logs/logs_{fecha}.json"
    # Leer los datos del archivo JSON original
    cuentas = extract_data_file(archivo_original)
    agendadas = extract_data_file(ruta_agendadas)
    logs = extract_data_file(ruta_logs)
    for result in results:
        if result['estatus'] == 'ok':
            agendadas.append(result)
        else:
            logs.append(result)
    escribir_json(ruta_agendadas,agendadas)
    escribir_json(ruta_logs,logs)
    for agendada in agendadas: 
        for cuenta in cuentas:
            if cuenta['email'] == agendada['cuenta']['email']:
                cuentas.remove(cuenta)

    escribir_json(archivo_original, cuentas)