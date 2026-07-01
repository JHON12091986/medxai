import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de ejemplo: Laptops en Mercado Libre Perú
url = "https://listado.mercadolibre.com.pe/computacion/laptops-accesorios/laptops/_NoIndex_True"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

print("Iniciando cacería de precios...")

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Buscamos todos los contenedores de productos
productos = soup.find_all('div', class_='ui-search-result__wrapper')

data = []

for p in productos:
    titulo = p.find('h2', class_='ui-search-item__title').text.strip()
    precio = p.find('span', class_='andes-money-amount__fraction').text.strip()
    link = p.find('a', class_='ui-search-link')['href']
    
    data.append({'Producto': titulo, 'Precio_Soles': precio, 'Link': link})

# Guardar en archivo para vender
df = pd.DataFrame(data)
df.to_csv('precios_laptops_peru.csv', index=False, encoding='utf-8-sig')

print(f"¡LISTO! {len(data)} productos extraídos y guardados en 'precios_laptops_peru.csv'.")