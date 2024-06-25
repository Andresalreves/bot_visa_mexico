from playwright.sync_api import sync_playwright
import threading
from evpn import ExpressVpnApi
import random
# Configuración de ExpressVPN
with ExpressVpnApi() as api:
    locations = api.locations  # Obtener ubicaciones disponibles
    # Función para obtener una nueva IP de ExpressVPN
    def get_new_ip():
        # Elegir una ubicación aleatoria
        loc = random.choice(locations)
        try:
            conection = api.connect(loc["id"])
            return conection
        except Exception as e:
            print(f"Error al conectar a ExpressVPN: {e}")
            return None

    # Función para ejecutar en cada hilo
    def run_browser(index):
        new_connection = get_new_ip()
        print(new_connection['info']['connection']['ip'])
        if new_connection['info']['connection']['ip']:
            print("Aqui estoy")
            with sync_playwright() as p:
                browser = p.chromium.launch()
                context = browser.new_context()
                page = context.new_page()

                # Aquí puedes interactuar con el navegador usando Playwright
                page.goto("https://api64.ipify.org?format=json")
                ip_response = page.content()
                print(f"Tu dirección IP es: {ip_response}")

                # Realizar acciones adicionales si es necesario

                browser.close()
        else:
            print(f"Navegador {index+1}: Error al obtener una nueva IP")
    # Crear y ejecutar los hilos
    threads = []
    for i in range(50):
        t = threading.Thread(target=run_browser, args=(i,))
        threads.append(t)
        t.start()

    # Esperar a que todos los hilos terminen
    for t in threads:
        t.join()