from typing import List
from selenium import webdriver
from fastapi import FastAPI
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

def extract_data(element):
    return {
        "text": element.text,
        "attributes": element.get_attribute("class")
        # Add more attributes as needed
    }

def download_selenium():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-extensions')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://www.icarros.com.br/principal/index.jsp')

    model_input = driver.find_element(By.XPATH, '//*[@id="modelo"]')
    model_input.send_keys("Opala")
    model_input.send_keys(Keys.ENTER)

    driver.implicitly_wait(10)
    elements = driver.find_elements(By.XPATH, '//div[contains(@class, "offer-card__header")]')

    data = [extract_data(element) for element in elements]

    driver.quit()  # Quit the driver to release resources
    return data

@app.get("/data", response_model=List[dict])
async def get_data():
    return download_selenium()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
