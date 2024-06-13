from typing import Union
from selenium import webdriver
#from flask import Flask, request
from fastapi import FastAPI, Query
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

#app = Flask(__name__)
app = FastAPI()

def download_selenium():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get('https://www.icarros.com.br/principal/index.jsp')
    title = driver.title
    city = driver.find_element(By.XPATH, '//*[@id="cidadeAbertoTexto"]').text
    data = {'Page Title': title, 'City': city}
    return data


@app.get("/data")
async def get_data():
    return download_selenium()


"""@app.route('/', methods= ['GET','POST'])
def home():
    if (request.method == 'GET'):
        return download_selenium()"""

if __name__ == "__main__":
    app.run(debug=True, port=3000)