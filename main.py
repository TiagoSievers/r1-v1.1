from typing import List
from selenium import webdriver
from fastapi import FastAPI, Query
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = FastAPI()

def download_selenium(model: str) -> List[dict]:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://www.icarros.com.br/principal/index.jsp')
    model_input = driver.find_element(By.XPATH, '//*[@id="modelo"]')
    model_input.send_keys(model)
    search_button = driver.find_element(By.XPATH, '//*[@id="buscaForm"]/div[2]/button')
    search_button.send_keys(Keys.ENTER)
    driver.implicitly_wait(10)

    results_header = driver.find_elements(By.XPATH, '//div[contains(@class, "offer-card__header")]')
    price_containers = driver.find_elements(By.XPATH, '//div[contains(@class, "offer-card__price")]')

    car_names = []
    car_prices = []

    while results_header and price_containers:
        try:
            result_header = results_header.pop(0)
            car_name_element = result_header.find_element(By.XPATH,
                                                          './/p[contains(@class, "label__onLight ids_textStyle_label_medium_bold")]')
            car_name = car_name_element.text.strip()  # Remove espaços em branco extras
            if car_name:
                car_model_element = result_header.find_element(By.XPATH,
                                                               './/p[contains(@class, "label__neutral ids_textStyle_label_xsmall_regular")]')
                car_model = car_model_element.text.strip()
                car_names.append(f"{car_name} {car_model}")
        except Exception as e:
            print(f"An error occurred while processing result header: {e}")

        try:
            price_container = price_containers.pop(0)
            car_price_element = price_container.find_element(By.XPATH,
                                                            './/p[contains(@class, "label__onLight ids_textStyle_label_medium_bold")]')
            car_price = car_price_element.text.strip()  # Remove espaços em branco extras
            if car_price:
                car_prices.append(car_price)
        except Exception as e:
            print(f"An error occurred while processing price container: {e}")

    driver.quit()

    # Verifica se o número de nomes de carros é o mesmo que o número de preços
    # Isso garante que cada carro tenha um preço correspondente
    if len(car_names) != len(car_prices):
        print("Número de nomes de carros não corresponde ao número de preços")

    # Cria a lista de dicionários com os resultados válidos
    result_list = []
    for name, price in zip(car_names, car_prices):
        result_list.append({"name": name, "price": price})

    return result_list

@app.get("/data")
async def get_data(model: str = Query(..., description="Modelo do carro")):
    return download_selenium(model)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
