from googlesearch import search
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def extraer_emails(url):
    """Extrae correos electrónicos de una página web"""
    emails = set()
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            patron = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            encontrados = re.findall(patron, response.text)
            for email in encontrados:
                if not any(x in email for x in ['example.com', 'test.com', 'png', 'jpg']):
                    emails.add(email)
    except:
        pass
    return list(emails)

def detectar_pdf(url):
    """Detecta si el sitio web tiene enlaces a PDFs"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            if 'pdf' in response.text.lower():
                return True
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if '.pdf' in link['href']:
                    return True
    except:
        pass
    return False

def buscar_empresas(query, cantidad=15):
    print(f"🦈 Cazando: {query}")
    resultados = []
    
    try:
        # ✅ SOLO USAMOS num_results y pause (sin stop)
        for url in search(query, num_results=cantidad):
            print(f"🔍 Analizando: {url}")
            emails = extraer_emails(url)
            tiene_pdf = detectar_pdf(url)
            
            # Extraer nombre del dominio
            dominio = url.split('/')[2] if '//' in url else url
            nombre = dominio.replace('www.', '')
            
            resultados.append({
                'nombre': nombre,
                'url': url,
                'dominio': dominio,
                'emails': ', '.join(emails),
                'primer_email': emails[0] if emails else '',
                'tiene_pdf': tiene_pdf
            })
            time.sleep(1)
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    return pd.DataFrame(resultados)

if __name__ == "__main__":
    # 🔥 CAMBIA ESTO POR TU NICHO
    consulta = "estudio contable en Lima"
    # Otras ideas: "consultora de recursos humanos Perú", "empresa de logística Lima"
    
    df = buscar_empresas(consulta, cantidad=15)
    
    # Guardar en Excel
    archivo = "leads_definitivos.xlsx"
    df.to_excel(archivo, index=False)
    
    print("\n" + "="*50)
    print(f"✅ ¡Caza completada! {len(df)} leads encontrados.")
    print(f"📁 Archivo guardado: {archivo}")
    print("="*50)
    
    # Mostrar resumen
    print("\n📋 RESUMEN DE LEADS:")
    for i, row in df.iterrows():
        pdf = "SÍ 📄" if row['tiene_pdf'] else "NO"
        print(f"{i+1}. {row['nombre']} - Email: {row['primer_email']} - PDF: {pdf}")
    
    print("\n🎯 Filtra los que tienen 'PDF: SÍ' para contactar primero.")