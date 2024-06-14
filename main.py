from typing import Union
from selenium import webdriver
from fastapi import FastAPI, Query
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = FastAPI()

def download_selenium():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://www.icarros.com.br/principal/index.jsp')
    model_input = driver.find_element(By.XPATH, '//*[@id="modelo"]')
    model_input.send_keys("Opala")
    search_button = driver.find_element(By.XPATH, '//*[@id="buscaForm"]/div[2]/button')
    search_button.send_keys(Keys.ENTER)
    driver.implicitly_wait(10)

    results_header = driver.find_elements(By.XPATH, '//div[contains(@class, "offer-card__header")]')
    car_names = []
    car_prices = []

    for result_header in results_header:
        try:
            car_name = result_header.find_element(By.XPATH,
                                                  './/p[contains(@class, "label__onLight ids_textStyle_label_medium_bold")]').text
            car_model = result_header.find_element(By.XPATH,
                                                   './/p[contains(@class, "label__neutral ids_textStyle_label_xsmall_regular")]').text
            price_container = result_header.find_element(By.XPATH,
                                                         '//div[contains(@class, "offer-card__price-container")]')
            car_price = price_container.find_element(By.XPATH,
                                                     './/p[contains(@class, "label__onLight ids_textStyle_label_medium_bold")]').text

            car_names.append(f"{car_name} {car_model}")
            car_prices.append(car_price)

        except Exception as e:
            print(f"An error occurred while processing result header: {e}")

    return car_names, car_prices

@app.get("/data")
async def get_data():
    return {"car_name": download_selenium()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
