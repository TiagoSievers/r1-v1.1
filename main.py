from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from fastapi import FastAPI, Query, HTTPException
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_icarros(driver: webdriver.Chrome, car_name: str) -> List[dict]:
    max_retries = 5
    attempt = 0

    while attempt < max_retries:
        try:
            driver.get('https://www.icarros.com.br/principal/index.jsp')
            model_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="modelo"]'))
            )
            model_input.send_keys(car_name)
            search_button = driver.find_element(By.XPATH, '//*[@id="buscaForm"]/div[2]/button')
            search_button.send_keys(Keys.ENTER)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "offer-card__header")]'))
            )

            results_header = driver.find_elements(By.XPATH, '//div[contains(@class, "offer-card__header")]')
            price_containers = driver.find_elements(By.XPATH, '//div[contains(@class, "offer-card__price")]')

            car_names = []
            car_prices = []

            while results_header and price_containers:
                try:
                    result_header = results_header.pop(0)
                    car_name_element = result_header.find_element(By.XPATH,
                                                                  './/p[contains(@class, "label__onLight ids_textStyle_label_medium_bold")]')
                    car_name = car_name_element.text.strip()
                    if car_name:
                        car_model_element = result_header.find_element(By.XPATH,
                                                                       './/p[contains(@class, "label__neutral ids_textStyle_label_xsmall_regular")]')
                        car_model = car_model_element.text.strip()
                        car_names.append(f"{car_name} {car_model}")
                except Exception as e:
                    logger.error(f"Error processing result header: {e}")

                try:
                    price_container = price_containers.pop(0)
                    car_price_element = price_container.find_element(By.XPATH,
                                                                     './/p[contains(@class, "label__onLight ids_textStyle_label_medium_bold")]')
                    car_price = car_price_element.text.strip()
                    if car_price:
                        car_prices.append(car_price)
                except Exception as e:
                    logger.error(f"Error processing price container: {e}")

            result_list = []
            for name, price in zip(car_names, car_prices):
                result_list.append({"name": name, "price": price})

            return result_list

        except NoSuchElementException as e:
            logger.error(f"Element not found: {e}")
        except TimeoutException as e:
            logger.error(f"Timeout while waiting for elements: {e}")
        except Exception as e:
            logger.error(f"Error in search_icarros attempt {attempt}: {e}")

        attempt += 1
        logger.info(f"Retrying... Attempt {attempt}/{max_retries}")
        time.sleep(5)  # Espera antes de tentar novamente

    return []

def search_napista(driver: webdriver.Chrome, car_name: str, car_model: str) -> List[dict]:
    max_retries = 5
    attempt = 0

    while attempt < max_retries:
        try:
            url = f'https://napista.com.br/busca/{car_model}-{car_name}'

            driver.get(url)
            time.sleep(3)

            car_names = []
            car_prices = []

            while True:
                try:
                    results_napista = driver.find_elements(By.XPATH, '//div[contains(@class, "iRYCmh")]')

                    if results_napista:
                        for napista_result in results_napista:
                            try:
                                napista_car_name = napista_result.find_element(By.XPATH,
                                                                               './/h2[contains(@class, " hXsWso")]').text
                                napista_car_price = napista_result.find_element(By.XPATH,
                                                                                './/div[contains(@class, " klMQDM")]').text

                                car_names.append(napista_car_name)
                                car_prices.append(napista_car_price)

                            except StaleElementReferenceException:
                                logger.error("Encountered StaleElementReferenceException. Retrying...")
                                break

                            except Exception as e:
                                logger.error(f"Error processing napista result: {e}")

                        return [{"name": name, "price": price} for name, price in zip(car_names, car_prices)]

                    else:
                        logger.info("No results found. Retrying...")
                        time.sleep(2)

                except StaleElementReferenceException:
                    logger.error("Encountered StaleElementReferenceException outside. Retrying...")
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Error in search_napista: {e}")
                    time.sleep(2)

        except NoSuchElementException as e:
            logger.error(f"Element not found: {e}")
        except Exception as e:
            logger.error(f"Error in search_napista attempt {attempt}: {e}")

        attempt += 1
        logger.info(f"Retrying... Attempt {attempt}/{max_retries}")
        time.sleep(5)  # Espera antes de tentar novamente

    return []

def search_autoline(driver: webdriver.Chrome, car_name: str, car_model: str) -> List[dict]:
    max_retries = 5
    attempt = 0

    while attempt < max_retries:
        try:
            url = f'https://www.autoline.com.br/comprar/carros/novos-seminovos-usados/todos-os-estados/todas-as-cidades/{car_model}/{car_name}/todas-as-versoes/todos-os-anos/todas-as-cores/todos-os-precos?geofilter=0'

            driver.get(url)
            time.sleep(3)
            """search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/app-root/app-search-result-vehicles/div/div[2]/div[2]/div[1]/app-filter-field/div/div[2]/app-collapsible-field[2]/div/div[2]/div/div[3]/input-select/div/input'))
            )
            search_input.send_keys(search_term)
            search_input.send_keys(Keys.ENTER)"""

            time.sleep(2)

            car_names = []
            car_prices = []

            while True:
                try:
                    results_autoline = driver.find_elements(By.XPATH, '//div[contains(@class, "card-vehicle ng-star-inserted")]')

                    if results_autoline:
                        for autoline_result in results_autoline:
                            try:
                                autoline_car_name = autoline_result.find_element(By.XPATH,
                                                                                 './/div[contains(@class, "text-maker")]').text
                                autoline_car_price = autoline_result.find_element(By.XPATH,
                                                                                  './/div[contains(@class, "text-value")]').text

                                car_names.append(autoline_car_name)
                                car_prices.append(autoline_car_price)

                            except StaleElementReferenceException:
                                logger.error("Encountered StaleElementReferenceException. Retrying...")
                                break

                            except Exception as e:
                                logger.error(f"Error processing autoline result: {e}")

                        return [{"name": name, "price": price} for name, price in zip(car_names, car_prices)]

                    else:
                        logger.info("No results found. Retrying...")
                        time.sleep(2)

                except StaleElementReferenceException:
                    logger.error("Encountered StaleElementReferenceException outside. Retrying...")
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Error in search_autoline: {e}")
                    time.sleep(2)

        except NoSuchElementException as e:
            logger.error(f"Element not found: {e}")
        except Exception as e:
            logger.error(f"Error in search_autoline attempt {attempt}: {e}")

        attempt += 1
        logger.info(f"Retrying... Attempt {attempt}/{max_retries}")
        time.sleep(5)  # Espera antes de tentar novamente

    return []

@app.get("/data")
async def get_data(car_model: str = Query(..., description="Modelo do carro"),car_name: str = Query(..., description="Nome do carro")):
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        while True:
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

            icarros_results = search_icarros(driver, car_model)
            napista_results = search_napista(driver, car_model, car_name)
            autoline_results = search_autoline(driver, car_model, car_name)

            driver.quit()

            if icarros_results and napista_results and autoline_results:
                return {
                    "icarros_results": icarros_results,
                    "napista_results": napista_results,
                    "autoline_results": autoline_results
                }
            else:
                logger.info("Retrying data retrieval as not all results are present.")
                time.sleep(5)

    except Exception as e:
        logger.error(f"Error in get_data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
