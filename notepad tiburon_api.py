import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from transformers import pipeline
import torch

# ================= CONFIGURACIÓN =================
app = FastAPI(title="Tiburón Supremo Maximal AI", version="1.0.0")

# Logs para producción
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= MODELO DE IA LOCAL (Transformers) =================
# Cargamos el modelo al arrancar (para que responda rápido)
# Si tienes GPU, se usa sola; si no, CPU.
device = 0 if torch.cuda.is_available() else -1
logger.info(f"Cargando modelo de resumen en {'GPU' if device == 0 else 'CPU'}...")

try:
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",  # Puedes cambiarlo por "google/pegasus-xsum" si quieres
        device=device,
        truncation=True
    )
    logger.info("¡Modelo de IA cargado con éxito!")
except Exception as e:
    logger.error(f"Error cargando el modelo: {e}")
    summarizer = None

# ================= SCRAPER =================
async def scrape_text_from_url(url: str) -> str:
    """Extrae el texto principal de una URL."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Eliminamos scripts y estilos
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Buscamos párrafos o el body
            paragraphs = soup.find_all('p')
            text = " ".join([p.get_text(strip=True) for p in paragraphs])
            
            # Si no hay párrafos, agarramos todo el texto del body
            if not text:
                text = soup.get_text(separator=" ", strip=True)
                
            # Limpiamos espacios extras
            text = " ".join(text.split())
            return text if len(text) > 100 else "No se encontró suficiente texto en la URL."
            
    except Exception as e:
        logger.error(f"Error al scrapear {url}: {e}")
        return f"Error al obtener la URL: {str(e)}"

# ================= MODELOS DE DATOS (Schemas) =================
class ScrapeRequest(BaseModel):
    url: str
    max_length: Optional[int] = 150
    min_length: Optional[int] = 30

class ErrorRequest(BaseModel):
    error_code: str
    sistema: Optional[str] = "general"  # ej: windows, linux, python, etc.

class ResponseData(BaseModel):
    status: str
    original_text: Optional[str] = None
    summary: Optional[str] = None
    message: str

# ================= ENDPOINTS =================

# 1. Endpoint que ya tenías (lo mantenemos)
@app.get("/analyze/Python")
async def analyze_python():
    return {
        "status": "success",
        "data": {
            "status": "success",
            "message": "Conectado correctamente para Python - Modo Tiburón Supremo Activado"
        }
    }

# 2. ENDPOINT ESTRELLA: Scraper + Resumen con IA
@app.post("/scrape-and-summarize", response_model=ResponseData)
async def scrape_and_summarize(request: ScrapeRequest):
    """
    Recibe una URL, extrae el texto y lo resume con IA (Transformers).
    """
    if summarizer is None:
        raise HTTPException(status_code=503, detail="El modelo de IA no está disponible.")
    
    # 1. Scrapeamos
    raw_text = await scrape_text_from_url(request.url)
    
    if "Error al obtener" in raw_text or "No se encontró" in raw_text:
        return ResponseData(
            status="warning",
            original_text=raw_text,
            summary=None,
            message="Hubo un problema al obtener el texto, pero la IA puede intentar procesarlo."
        )
    
    # 2. Resumimos con IA
    try:
        # El modelo tiene límite de tokens, cortamos si es muy largo
        if len(raw_text) > 3500:  # Aprox 1024 tokens
            raw_text = raw_text[:3500]
            
        summary_result = summarizer(
            raw_text,
            max_length=request.max_length,
            min_length=request.min_length,
            do_sample=False
        )
        summary_text = summary_result[0]['summary_text']
        
        return ResponseData(
            status="success",
            original_text=raw_text[:500] + "... (truncado por legibilidad)",
            summary=summary_text,
            message="¡Análisis completado por el Tiburón Supremo!"
        )
    except Exception as e:
        logger.error(f"Error en IA: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la IA: {str(e)}")

# 3. ENDPOINT DE SOPORTE TÉCNICO AUTOMÁTICO
@app.post("/tech-support")
async def tech_support(request: ErrorRequest):
    """
    Busca en Google/DuckDuckGo una solución para el código de error,
    scrapea el primer resultado relevante y lo resume con IA.
    """
    if summarizer is None:
        raise HTTPException(status_code=503, detail="El modelo de IA no está disponible.")
    
    # Construimos la búsqueda (usamos DuckDuckGo HTML para no necesitar API key)
    query = f"{request.error_code} {request.sistema} solution fix"
    search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    
    # Scrapeamos la búsqueda para obtener el primer enlace real
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            search_response = await client.get(search_url)
            soup = BeautifulSoup(search_response.text, 'lxml')
            
            # Encontramos el primer resultado de la búsqueda
            result_link = soup.find('a', class_='result__a')
            if not result_link:
                return {
                    "status": "not_found",
                    "message": f"No se encontraron guías para el error {request.error_code}."
                }
            
            first_url = result_link.get('href')
            # DuckDuckGo usa enlaces relativos, limpiamos
            if first_url.startswith('/'):
                first_url = 'https://duckduckgo.com' + first_url
            elif not first_url.startswith('http'):
                first_url = 'https://' + first_url
                
            # Ahora scrapeamos esa URL
            raw_text = await scrape_text_from_url(first_url)
            
            # Resumimos
            if len(raw_text) > 3500:
                raw_text = raw_text[:3500]
            summary = summarizer(raw_text, max_length=200, min_length=40, do_sample=False)[0]['summary_text']
            
            return {
                "status": "success",
                "error_code": request.error_code,
                "url_encontrada": first_url,
                "resumen_solucion": summary,
                "mensaje": "¡Soporte técnico generado por IA, mi Tiburón!"
            }
            
    except Exception as e:
        logger.error(f"Error en soporte técnico: {e}")
        raise HTTPException(status_code=500, detail=f"Error en el soporte: {str(e)}")

# 4. Endpoint de salud (para producción)
@app.get("/health")
async def health_check():
    return {
        "status": "alive",
        "ia_loaded": summarizer is not None,
        "gpu_available": torch.cuda.is_available()
    }

# ================= EJECUCIÓN (para correr directo) =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9500, log_level="info")