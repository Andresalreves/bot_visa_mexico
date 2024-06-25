from playwright.sync_api import sync_playwright, TimeoutError
from common_functions import search_prev_options, verificar_fecha
from datetime import datetime
import time

def bot(
        nombre_usuario,
        password,
        list_consulados,
        list_cas,
        rango
    ):
    url = "https://ais.usvisa-info.com/es-mx/niv/users/sign_in"
    select_date = False
    global index
    global consulate_xpath
    global time_consulate
    global consulate_date
    global prev_options

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=100)  # Use browser instead of navegador (Spanish for browser)
            context = browser.new_context()

            # Navigate to the URL
            page = context.new_page()  # Create a new Page object
            page.goto(url,timeout=60000)
            #time.sleep(6000)
            # Login section
            username_field = page.locator("#user_email")
            password_field = page.locator("#user_password")
            checkbox = page.locator('//*[@id="sign_in_form"]/div[3]/label/div')

            username_field.fill(nombre_usuario)
            password_field.fill(password)
            checkbox.click()
            page.wait_for_selector('//*[@id="sign_in_form"]/p[1]/input',timeout=10000).click()
            #time.sleep(6000)
            page.wait_for_selector(
                "xpath=//a[starts-with(@href, '/es-mx/niv/schedule/') and substring(@href, string-length(@href) - string-length('/continue_actions') + 1) = '/continue_actions']",
                state="visible",
                timeout=30000
            ).click()
            # Extract visa number from URL
            visa_number = page.url.split("/")[-2]

            # Click program accordion and program link
            page.locator('//*[@id="forms"]/ul/li[1]').click()
            page.locator(f'a[href="/es-mx/niv/schedule/{visa_number}/continue"]').click()
            consulado = page.wait_for_selector('//*[@id="appointments_consulate_appointment_facility_id"]',timeout=10000)
            # Loop through consulates
            for index, consulate_xpath in enumerate(list_consulados):
                prev_options = search_prev_options(consulate_xpath)
                consulado.select_option(prev_options['consulado'])
                url_ajax_fecha = f'https://ais.usvisa-info.com/es-mx/niv/schedule/{visa_number}/appointment/days/{consulate_xpath}.json?appointments[expedite]=false'
                try:
                    with page.expect_response(lambda response: url_ajax_fecha == response.url,timeout=10000) as response_info:
                        consulado.select_option(consulate_xpath)
                    response = response_info.value
                    available_dates = response.json()
                    #print(available_dates)
                    appointment_date = page.wait_for_selector("#appointments_consulate_appointment_date",timeout=10000)
                    appointment_date.evaluate("el => el.removeAttribute('readonly')")
                    if(len(available_dates) > 0):
                        for date in available_dates:
                            consulate_date = date["date"]
                            if not verificar_fecha(consulate_date,rango):
                                return {
                                    "estatus":"Error",
                                    "message":f"No se encontraron fechas disponibles, dentro del rango dado de {rango} dias",
                                    "cuenta":{"email":nombre_usuario,"pass":password},
                                    "fecha" : datetime.now().strftime('%Y-%m-%d'),
                                    "hora" : datetime.now().strftime('%H:%M:%S')
                                    }
                            # La solucion para que no salga el mensaje de seleciono un dia inhabil hace muy lento el script
                            #appointment_date.click()
                            #time.sleep(2)
                            appointment_date.fill(date["date"])
                            #time.sleep(2)
                            #datepicker = page.wait_for_selector("#ui-datepicker-div",timeout=4000)
                            #date_elements = datepicker.query_selector_all('td[data-handler="selectDay"]>a')
                            #if date_elements:
                                #first_date_element = date_elements[0]
                                #first_date_element.click()
                            url_ajax_hora = f'https://ais.usvisa-info.com/es-mx/niv/schedule/{visa_number}/appointment/times/{consulate_xpath}.json?date={consulate_date}&appointments[expedite]=false'
                            try:
                                with page.expect_response(lambda response: url_ajax_hora == response.url,timeout=10000) as response_info2:
                                    appointment_date.press('Enter')
                                appointment_time = page.wait_for_selector("#appointments_consulate_appointment_time",timeout=10000)
                                page.locator('#appointments_consulate_address').click()
                                available_times = response_info2.value.json()
                                #print(available_times)
                                options = appointment_time.query_selector_all("option:not(:first-child)")
                                if((len(available_times["available_times"]) > 0) and (len(options)> 0)):
                                    time_consulate = available_times["available_times"][0]
                                    appointment_time.select_option(time_consulate)
                                else:
                                    continue
                            except TimeoutError:
                                continue
                            break
                    else:
                        continue
                except TimeoutError:
                    continue
                break
            cas = page.wait_for_selector('//*[@id="appointments_asc_appointment_facility_id"]')
            cas.select_option(prev_options['cas'])
            url_ajax_fecha_cas = f'https://ais.usvisa-info.com/es-mx/niv/schedule/{visa_number}/appointment/days/{list_cas[index]}.json?&consulate_id={consulate_xpath}&consulate_date={consulate_date}&consulate_time={time_consulate}&appointments[expedite]=false'
            try:
                with page.expect_response(lambda response: url_ajax_fecha_cas == response.url,timeout=10000) as response_info3:
                    cas.select_option(list_cas[index])
                response = response_info3.value
                available_dates_cas = response.json()
                appointment_date_cas = page.wait_for_selector("#appointments_asc_appointment_date",timeout=10000)
                appointment_date_cas.evaluate("el => el.removeAttribute('readonly')")
                for date in available_dates_cas: 
                    appointment_date_cas.fill(date["date"])
                    url_ajax_hora_cas = f'https://ais.usvisa-info.com/es-mx/niv/schedule/{visa_number}/appointment/times/{list_cas[index]}.json?date={date["date"]}&consulate_id={consulate_xpath}&consulate_date={consulate_date}&consulate_time={time_consulate}&appointments[expedite]=false'
                    try:
                        with page.expect_response(lambda response: url_ajax_hora_cas == response.url,timeout=10000) as response_info4:
                            appointment_date_cas.press('Enter')
                        time.sleep(1)
                        page.locator('#appointments_consulate_address').click()
                        appointment_time_cas = page.wait_for_selector("#appointments_asc_appointment_time",timeout=10000)
                        available_times_cas = response_info4.value.json()
                        options2 = appointment_time_cas.query_selector_all("option:not(:first-child)")
                        if((len(available_times_cas["available_times"]) > 0) and (len(options2) > 0)):
                            #print(available_times_cas)
                            break
                        else:
                            continue
                    except TimeoutError:
                        continue
                appointment_time_cas.select_option(available_times_cas["available_times"][0])
            except TimeoutError:
                return {
                    "estatus":"Error",
                    "message":texto_mensaje,
                    "cuenta":{"email":nombre_usuario,"pass":password},
                    "fecha" : datetime.now().strftime('%Y-%m-%d'),
                    "hora" : datetime.now().strftime('%H:%M:%S')
                }

            #time.sleep(6000)            
            #Submit appointment
            create_appointment = page.wait_for_selector("#appointments_submit",timeout=10000)
            create_appointment.click()
            flash_messages = page.wait_for_selector("#flash_messages .notice", state="visible")
            texto_mensaje = flash_messages.inner_text()
            browser.close()
            if "La programación de su cita se ha realizado correctamente" in texto_mensaje:
                return {
                    "estatus":"ok",
                    "message":texto_mensaje,
                    "cuenta":{"email":nombre_usuario,"pass":password},
                    "fecha" : datetime.now().strftime('%Y-%m-%d'),
                    "hora" : datetime.now().strftime('%H:%M:%S')
                }
            else:
                return {
                    "estatus":"Error",
                    "message":texto_mensaje,
                    "cuenta":{"email":nombre_usuario,"pass":password},
                    "fecha" : datetime.now().strftime('%Y-%m-%d'),
                    "hora" : datetime.now().strftime('%H:%M:%S')
                }
    except Exception as e:
        return {
            "estatus":"Error",
            "message":str(e),
            "cuenta":{"email":nombre_usuario,"pass":password},
            "fecha" : datetime.now().strftime('%Y-%m-%d'),
            "hora" : datetime.now().strftime('%H:%M:%S')
        }
"""
result = bot(
    "mperezcastillo828@gmail.com",
    "),5(Qq>g+v",
    ["70"],
    ["82"],
    930
)
print(result)
"""