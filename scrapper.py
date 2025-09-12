from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.occamsadvisory.com/"

def scrape_occams():
    
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    
    
    driver.get(BASE_URL)
    time.sleep(5)  

    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    data = []

    
    selectors = [
        "div.et_pb_text_inner",      # main text blocks
        "section.et_pb_section p",   # paragraph inside sections
        "h1, h2, h3"                 # headings
    ]

    seen_text = set()  # avoid duplicates

    for sel in selectors:
        for tag in soup.select(sel):
            text = tag.get_text(strip=True)
            # Skip very short or boilerplate text
            if text and len(text) > 30 and text not in seen_text:
                seen_text.add(text)
                data.append({"content": text, "url": BASE_URL})

    # Save to JSON
    with open("knowledge.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Scraping complete! {len(data)} meaningful items saved to knowledge.json")

if __name__ == "__main__":
    scrape_occams()
