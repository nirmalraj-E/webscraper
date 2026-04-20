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
    # Headless mode - browser window open aagaama background-la run aagum
    # chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_crypto():
    driver = setup_driver()
    driver.get("https://coinmarketcap.com/")
    time.sleep(5)  # Page load aagura varaiku wait

    data = []

    # Top 10 coins find panrom
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    for i, row in enumerate(rows[:10], start=1):
        try:
            # Coin name
            name = row.find_element(By.CSS_SELECTOR, "p.coin-item-name").text

            # Price
            price = row.find_element(By.CSS_SELECTOR, "div.sc-a0353bbc-0").text

            # 24h change
            change = row.find_element(By.CSS_SELECTOR, "span.sc-a0353bbc-0").text

            # Market cap
            market_cap = row.find_elements(By.CSS_SELECTOR, "td")[6].text

            # Timestamp - historical logging ku
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data.append({
                "Rank": i,
                "Coin": name,
                "Price": price,
                "24h Change": change,
                "Market Cap": market_cap,
                "Timestamp": timestamp
            })

        except:
            continue

    driver.quit()
    return data

def save_csv(data):
    df = pd.DataFrame(data)
    # Append mode - historical logging ku existing file-la add aagum
    df.to_csv("crypto_prices.csv", mode='a', 
              header=not pd.io.common.file_exists("crypto_prices.csv"),
              index=False)
    print("Data saved to crypto_prices.csv!")

def filter_data(data, min_price=None, top_gainers=False):
    df = pd.DataFrame(data)
    
    # Price threshold filter
    if min_price:
        df["Price_Clean"] = df["Price"].str.replace("[$,]", "", regex=True).astype(float)
        df = df[df["Price_Clean"] >= min_price]
    
    # Top gainers filter - highest 24h change
    if top_gainers:
        df["Change_Clean"] = df["24h Change"].str.replace("%", "").astype(float)
        df = df.sort_values("Change_Clean", ascending=False)
    
    return df

if __name__ == "__main__":
    print("Scraping started...")
    crypto_data = scrape_crypto()
    
    # Save to CSV
    save_csv(crypto_data)
    
    # Filter example - $100 above price coins
    filtered = filter_data(crypto_data, min_price=100)
    print(filtered[["Rank", "Coin", "Price", "24h Change"]])
    
    print("Done!")