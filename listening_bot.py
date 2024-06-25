import socket
import json
from threading import Thread
from common_functions import change_ip, extract_data_file, select_consulados, process_response
from bot_multithreaded import Bot_visa_dating

# Lista para almacenar los hilos.
hilos = []
# Lista para almacenar respuestas.
response = []

# Bandera para indicar si hay un proceso en ejecución
global proceso_en_ejecucion
proceso_en_ejecucion = False

# Función para manejar las conexiones entrantes
def handle_client(conn, addr):
    global proceso_en_ejecucion
    data = conn.recv(1024).decode()
    #print(data)
    if not proceso_en_ejecucion:
        if(data.strip().isdigit()):
            proceso_en_ejecucion = True
            init_bot(data.strip())
        else:
            print(f"el consulado o los consulados que intentas agendar no contienen un formato valido por ejemplo:'70'")
    else:
        print(f"Recibido mensaje '{data}' desde {addr}, pero ya hay un proceso de bot activo.")
    
    conn.close()

# Función para iniciar el servidor
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5555))
    server_socket.listen(5)
    print("Servidor escuchando en localhost:5555")

    while True:
        conn, addr = server_socket.accept()
        print(f"Nueva conexión desde {addr}")
        execute_bot = Thread(target=handle_client, args=(conn, addr))
        execute_bot.start()

def init_bot(consulados):
    
    global proceso_en_ejecucion
    cuentas = extract_data_file('cuentas.json')
    array_consulados = select_consulados(consulados)
    #print(array_consulados)

    for cuenta in cuentas:
        hilos.append(
            Bot_visa_dating(
                cuenta['email'],
                cuenta['pass'],
                array_consulados['consulados'],
                array_consulados['cas'],
                900
            )
        )

    # Iniciar los hilos
    for hilo in hilos:
        try:
            if not hilo.is_alive():
                hilo.start()
        except RuntimeError:
            print(RuntimeError)
    # Esperar a que terminen los hilos
    for hilo in hilos:
        try:
            if hilo.is_alive():
                hilo.join()
        except RuntimeError:
            print(RuntimeError)
        response.append(hilo.result)

    #print(response)
    process_response(response,"cuentas.json")
    # Cambiar ip con ExpressVPN
    change_ip()
    proceso_en_ejecucion = False
    response = []

if __name__ == "__main__":
    start_server()
