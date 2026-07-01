import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scraper_emails(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
        emails = list(set(emails))
        return emails
    except Exception as e:
        print(f"  ⚠️ Error en {url}: {e}")
        return []

def scraper_multiple(urls):
    resultados = []
    for url in urls:
        print(f"🔍 Scrapeando: {url}")
        emails = scraper_emails(url)
        for email in emails:
            resultados.append({'url': url, 'email': email})
        print(f"  ✅ {len(emails)} emails encontrados")
    
    df = pd.DataFrame(resultados)
    df.to_excel('emails_encontrados.xlsx', index=False)
    print(f"\n🎯 TOTAL: {len(resultados)} emails guardados en emails_encontrados.xlsx")
    return df

# ---- PON AQUÍ LAS URLS DEL CLIENTE ----
urls = [
    'https://httpbin.org',
    'https://example.com',
]

scraper_multiple(urls)