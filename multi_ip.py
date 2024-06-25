from selenium import webdriver
from fake_useragent import UserAgent
from requests_html import HTMLSession

proxies = []
# Crear una lista de proxies
for i in range(4000,4050):
    proxies.append(f"http://127.0.0.1:{i}")

# Generar user agents
user_agents = [UserAgent().random]

# Crear navegadores con diferentes proxies y user agents
for proxy, user_agent in zip(proxies, user_agents):
    options = webdriver.ChromeOptions()
    options.add_argument("--proxy-server={}".format(proxy))
    options.add_argument("--user-agent={}".format(user_agent))
    driver = webdriver.Chrome(options=options)

# Realizar solicitudes en cada navegador
for driver in drivers:
    driver.get("https://www.google.com")
    print(driver.title)

# Cerrar los navegadores
for driver in drivers:
    driver.quit()


        try:
            consulado = driver.find_element(By.XPATH, '//*[@id="appointments_consulate_appointment_facility_id"]/option[7]')
        except NoSuchElementException:
            print("Element not found. Check the XPath selector.")
            driver.quit()
            exit()

        # Create an ActionChains object to handle the "onchange" event
        actions = ActionChains(driver)

        # Simulate the change of value in the "consulado" element
        actions.move_to_element(consulado).click().perform()

        # Wait for the AJAX response to complete (consider timeout and potential errors)
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(
                lambda driver: driver.execute_script("return jQuery.active == 0")
            )
        except TimeoutException:
            print("AJAX request timed out. Consider adjusting the wait time.")
            driver.quit()
            exit()

        # Get the AJAX response (assuming it's displayed in an element)
        try:
            response = driver.execute_script("return JSON.parse($('.tu_selector_respuesta').text())")
        except NoSuchElementException:
            print("Element containing AJAX response not found. Check the selector.")
            driver.quit()
            exit()

        # Print the AJAX response
        print(response)