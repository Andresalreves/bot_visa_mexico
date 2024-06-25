import threading
from playwright.sync_api import sync_playwright
import openvpn_client
import vpnbook_connector

# Configuración de OpenVPN
openvpn_client.init_process(0)
vpnbook = vpnbook_connector.VPNBookConnector()

# Función para obtener una nueva IP de VPNBook
def get_new_ip():
    vpnbook.disconnect_from_vpn()
    new_code = vpnbook.get_new_code()
    vpnbook.connect_to_vpn(new_code)
    return vpnbook.get_ip()

# Función para ejecutar en cada hilo
def run_browser(index):
    new_ip = get_new_ip()
    print(f"Navegador {index+1}: IP {new_ip}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        
        # Aquí puedes interactuar con el navegador usando Playwright
        page.goto("https://api64.ipify.org?format=json")
        
        # Realizar acciones adicionales si es necesario
        
        browser.close()

# Crear y ejecutar los hilos
threads = []
for i in range(50):
    t = threading.Thread(target=run_browser, args=(i,))
    threads.append(t)
    t.start()

# Esperar a que todos los hilos terminen
for t in threads:
    t.join()

# Cerrar la conexión OpenVPN
openvpn_client.quit_process()