from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def scrape_crypto():
    driver = setup_driver()

    driver.get("https://coinmarketcap.com/")
    time.sleep(5)

    data = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    for i, row in enumerate(rows[:10], start=1):
        try:
            name = row.find_element(By.CSS_SELECTOR, "p[class*='coin-item-symbol']").text
            price = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
            change = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text
            market_cap = row.find_element(By.CSS_SELECTOR, "td:nth-child(7)").text

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data.append({
                "Rank": i,
                "Coin": name,
                "Price": price,
                "24h Change": change,
                "Market Cap": market_cap,
                "Timestamp": timestamp
            })

        except Exception as e:
            print("Row error:", e)

    driver.quit()
    return data
 

def save_csv(data):
    df = pd.DataFrame(data)
    df.to_csv("crypto_prices.csv", mode='a',
              header=not pd.io.common.file_exists("crypto_prices.csv"),
              index=False)
    print("Data saved to crypto_prices.csv!")

def filter_data(data, min_price=None, top_gainers=False):
    df = pd.DataFrame(data)

    # 🔥 FIX START
    if df.empty:
        print("No data scraped da 😑")
        return df

    print("Columns:", df.columns)   # debug
    df.columns = df.columns.str.strip()  # remove space issues
    # 🔥 FIX END

    if min_price:
        df["Price_Clean"] = df["Price"].str.replace("[$,]", "", regex=True).astype(float)
        df = df[df["Price_Clean"] >= min_price]

    if top_gainers:
        df["Change_Clean"] = df["24h Change"].str.replace("%", "").astype(float)
        df = df.sort_values("Change_Clean", ascending=False)

    return df

if __name__ == "__main__":
    print("Scraping started...")
    crypto_data = scrape_crypto()

    save_csv(crypto_data)

    filtered = filter_data(crypto_data, min_price=100)

    print(filtered[["Rank", "Coin", "Price", "24h Change"]])

    print("Done!")