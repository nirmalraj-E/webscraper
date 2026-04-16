from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_imdb():
    driver = setup_driver()
    driver.get("https://www.imdb.com/chart/top/")
    time.sleep(5)

    movies = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")
    data = []

    for i, movie in enumerate(movies[:250], start=1):
        try:
            
            title = movie.find_element(By.CSS_SELECTOR, "h3").text

            full_text = movie.text

            year_match = re.search(r"\b(19|20)\d{2}\b", full_text)
            year = year_match.group() if year_match else "N/A"
            try:
                rating = movie.find_element(By.CSS_SELECTOR, ".ipc-rating-star--rating").text
            except:
                rating = "N/A"

            data.append({
                "Rank": i,
                "Title": title,
                "Year": year,
                "Rating": rating
            })

        except:
            continue

    driver.quit()
    return data

def save_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("imdb_top_250.csv", index=False)
    print("CSV file created successfully!")

if __name__ == "__main__":
    print("Scraping started...")
    movies = scrape_imdb()
    save_csv(movies)
    print("Done!")