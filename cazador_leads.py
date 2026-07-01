from googlesearch import search
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def es_candidato_valido(url):
    """Verifica si la web tiene un formulario de contacto o palabras clave de gestión."""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text().lower()
        # Buscamos indicadores de que necesitan gestión documental
        keywords = ['factura', 'registro', 'envío', 'documentos', 'contacto', 'cv']
        return any(key in text for key in keywords)
    except:
        return False

def buscar_empresas(query, num_resultados=10):
    print(f"🚀 Iniciando caza para: {query}")
    resultados = []
    
    for url in search(query, num_results=num_resultados, stop=num_resultados, pause=2):
        print(f"🔍 Analizando: {url}")
        candidato = es_candidato_valido(url)
        resultados.append({
            'url': url,
            'necesidad_gestion': candidato
        })
        time.sleep(1) # Respetamos el servidor
        
    return pd.DataFrame(resultados)

if __name__ == "__main__":
    # Tu nicho de mercado
    nicho = "estudio contable en Lima"
    df = buscar_empresas(nicho)
    
    df.to_excel("leads_detectados.xlsx", index=False)
    print("✅ ¡Caza finalizada! Resultados en 'leads_detectados.xlsx'.")