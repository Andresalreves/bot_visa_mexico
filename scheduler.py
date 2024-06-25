from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import chromedriver_binary  # Importa chromedriver_binary
import time

def search_date(driver,xpath_next):
    next = driver.find_element(By.XPATH,xpath_next)
    next.click()
    # DATEPICKER
    wait = WebDriverWait(driver, 10)
    datepicker = wait.until(EC.presence_of_element_located((By.ID, "ui-datepicker-div")))
    available_dates = datepicker.find_elements(By.XPATH, '//td[@data-handler="selectDay"]')
    if(len(available_dates) == 0):
        datepicker_year = datepicker.find_element(By.XPATH,'//*[@id="ui-datepicker-div"]/div[1]/div/div/span[2]').text
        date_now = datetime.now()
        year_now = date_now.year
        if((year_now + 3) == int(datepicker_year)):
            return False
        else:
            return search_date(driver,xpath_next)
    else:
        available_dates[0].find_element(By.TAG_NAME,'a').click()
        return True

# Información de la página web
url = "https://ais.usvisa-info.com/es-mx/niv/users/sign_in"
username_field = "user_email"
password_field = "user_password"
select_date = False
global index
# Datos de inicio de sesión
username = "nuevaver055@outlook.com"
password = "/dunA(=,u."
list_consulados = [
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[7]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[3]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[8]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[2]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[4]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[5]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[6]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[9]',
    '//*[@id="appointments_consulate_appointment_facility_id"]/option[11]'
    ]
list_cas = [
    '//*[@id="appointments_asc_appointment_facility_id"]/option[7]',
    '//*[@id="appointments_asc_appointment_facility_id"]/option[3]', 
    '//*[@id="appointments_asc_appointment_facility_id"]/option[8]',
    '//*[@id="appointments_asc_appointment_facility_id"]/option[2]',
    '//*[@id="appointments_asc_appointment_facility_id"]/option[4]',
    '//*[@id="appointments_asc_appointment_facility_id"]/option[5]',
    '//*[@id="appointments_asc_appointment_facility_id"]/option[6]',
    '//*[@id="appointments_asc_appointment_facility_id"]/option[9]',
    '//*[@id="appointments_asc_appointment_facility_id"]/option[11]'
]
# Opciones del navegador (opcional)
try:
    options = webdriver.ChromeOptions()
    #options.add_argument("--disable-images")
    #options.add_argument("--disable-css")
    #options.add_argument("--disable-javascript")
except Exception as e:
    print(e)
# Iniciar el navegador y acceder a la página web
with webdriver.Chrome(options=options) as driver:
    # Port ya no es necesario, ya que chromedriver_binary se encarga de la ubicación
    driver.get(url)
    # Encontrar los campos de inicio de sesión
    username_input = driver.find_element(By.ID, username_field)
    password_input = driver.find_element(By.ID, password_field)

    # Introducir los datos de inicio de sesión
    username_input.send_keys(username)
    password_input.send_keys(password)

    checkbox = driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/div[3]/label/div')

    # Selecciona el checkbox
    checkbox.click()
    # Enviar la solicitud de inicio de sesión
    driver.find_element(By.XPATH,'//*[@id="sign_in_form"]/p[1]/input').click()
    start_time = time.time()
    wait = WebDriverWait(driver, 10)
    # Espera hasta que el boton sea visible
    button_continue = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[4]/main/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/ul/li/a")))
    button_continue.click()
    current_url = driver.current_url
    # Extraer el número de visa
    visa_number = current_url.split('/')[-2]
    #print(visa_number)
    wait = WebDriverWait(driver, 10)
    # Espera hasta que el boton sea visible
    acordeon = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="forms"]/ul/li[1]')))
    acordeon.click()
    wait = WebDriverWait(driver, 10)
    program = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'a[href="/es-mx/niv/schedule/{visa_number}/continue"]')))
    program.click()
    time.sleep(1)
    wait = WebDriverWait(driver, 10)
    # Espera hasta que los consulados sean visibles
    wait.until(EC.visibility_of_element_located((By.XPATH,'//*[@id="appointments_consulate_appointment_facility_id"]/option[11]')))
    
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CITA EN LA SECCIÓN CONSULAR <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    for index, consulado_xpath in enumerate(list_consulados):
        consulado = driver.find_element(By.XPATH,consulado_xpath)
        time.sleep(1)
        consulado.click()
        try:
            time.sleep(1)
            wait = WebDriverWait(driver,8)
            fecha_cita = wait.until(EC.visibility_of_element_located((By.ID, 'appointments_consulate_appointment_date')))
        except TimeoutException:
            continue 
        if fecha_cita.is_displayed():
            time.sleep(1)
            fecha_cita.click()
            select_date = search_date(driver,'//*[@id="ui-datepicker-div"]/div[2]/div/a')
        print(select_date)
        if select_date:
            time.sleep(1)
            wait = WebDriverWait(driver,8)
            select_times = wait.until(EC.visibility_of_element_located((By.ID, 'appointments_consulate_appointment_time')))
            options = select_times.find_elements(By.TAG_NAME,'option')
            if(len(options)>1):
                options[1].click()
            else:
                continue
            break

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CITA EN EL CAS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    cas = driver.find_element(By.XPATH,list_cas[index])
    cas.click()
    time.sleep(1)
    wait = WebDriverWait(driver, 8)
    fecha_cas = wait.until(EC.visibility_of_element_located((By.ID, 'appointments_asc_appointment_date'))) 
    if fecha_cas.is_displayed():
        time.sleep(2)
        fecha_cas.click()
        select_date_cas = search_date(driver,'//*[@id="ui-datepicker-div"]/div[2]/div/a/span')
    #print(select_date)
    if select_date:
        time.sleep(1)
        wait = WebDriverWait(driver, 8)
        select_times = wait.until(EC.visibility_of_element_located((By.ID, 'appointments_asc_appointment_time')))
        options_cas = select_times.find_elements(By.TAG_NAME,'option')
        options_cas[1].click()
    wait = WebDriverWait(driver, 2)    
    create_appointment = wait.until(EC.visibility_of_element_located((By.ID, 'appointments_submit')))
    create_appointment.click()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(elapsed_time)