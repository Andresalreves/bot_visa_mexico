import asyncio
import openvpn
import playwright
from playwright.async_api import async_playwright

# Configuraciones de OpenVPN
CONFIG_DIR = "/path/to/openvpn/config"
VPNBOOK_USERNAME = "your_username"
VPNBOOK_PASSWORD = "your_password"

# Configuraciones de Playwright
PLAYWRIGHT_HEADLESS = True  # Si quieres ejecutar los navegadores en segundo plano
PLAYWRIGHT_PROXY = {  # Usar proxy de OpenVPN
    "server": "127.0.0.1",
    "port": 8080,
}

async def main():
    # Obtener lista de servidores VPNBook
    servers = await openvpn.get_servers(VPNBOOK_USERNAME, VPNBOOK_PASSWORD)

    # Crear un pool de conexiones a OpenVPN
    async with openvpn.AsyncPool(max_size=50) as pool:
        # Crear un contexto de Playwright para cada servidor
        async with async_playwright() as p:
            contexts = []
            for server in servers:
                # Conectarse a un servidor VPN
                connection = await pool.acquire(server.hostname)

                # Crear un contexto de Playwright con el proxy de OpenVPN
                context = await p.chromium.launch_persistent_context(
                    headless=PLAYWRIGHT_HEADLESS,
                    proxy=PLAYWRIGHT_PROXY,
                )

                contexts.append(context)

            # Abrir una página web en cada navegador
            for context in contexts:
                page = await context.new_page()
                await page.goto("https://www.google.com/")

            # Esperar a que todas las páginas se carguen
            await asyncio.gather(*[page.wait_for_load_state("domcontentloaded") for page in contexts])

            # Desconectarse del servidor VPN
            for connection in pool:
                await connection.close()

            # Cerrar los contextos de Playwright
            for context in contexts:
                await context.close()

if __name__ == "__main__":
    asyncio.run(main())
