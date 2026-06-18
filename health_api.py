import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import torch

# ================= CONFIGURACIÓN =================
app = FastAPI(title="Health Prediction AI Service - Tiburón Supremo", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= MODELOS DE DATOS =================
class Biomarkers(BaseModel):
    glucose: float
    haemoglobin: float
    cholesterol: float
    patient_name: Optional[str] = "Paciente"
    patient_age: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    data: dict
    clinical_report: Optional[str] = None
    message: str

# ================= ENDPOINTS =================
@app.get("/")
async def root():
    return {
        "service": "Health Prediction AI - Tiburón Supremo",
        "version": "1.0.0",
        "endpoints": {
            "/analyze-biomarkers": "POST - Analiza biomarcadores y genera reporte clínico",
            "/health": "GET - Estado del servicio",
            "/": "GET - Información del servicio"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "alive",
        "ia_loaded": False,
        "gpu_available": torch.cuda.is_available() if hasattr(torch, 'cuda') else False
    }

@app.post("/analyze-biomarkers", response_model=HealthResponse)
async def analyze_biomarkers(data: Biomarkers):
    try:
        if data.glucose <= 0:
            raise HTTPException(status_code=400, detail="La glucosa debe ser un valor positivo")
        if data.haemoglobin <= 0:
            raise HTTPException(status_code=400, detail="La hemoglobina debe ser un valor positivo")
        if data.cholesterol <= 0:
            raise HTTPException(status_code=400, detail="El colesterol debe ser un valor positivo")
        
        risks = {
            "diabetes_risk": "Alto" if data.glucose > 125 else "Moderado" if data.glucose > 100 else "Normal",
            "anemia_risk": "Alto" if data.haemoglobin < 12.0 else "Moderado" if data.haemoglobin < 13.5 else "Normal",
            "cardio_risk": "Alto" if data.cholesterol >= 240 else "Moderado" if data.cholesterol >= 200 else "Normal"
        }
        
        clinical_report = f"""
        Paciente: {data.patient_name}
        Edad: {data.patient_age if data.patient_age else 'No especificada'}
        Resultados:
        - Glucosa: {data.glucose} mg/dL - {risks['diabetes_risk']}
        - Hemoglobina: {data.haemoglobin} g/dL - {risks['anemia_risk']}
        - Colesterol: {data.cholesterol} mg/dL - {risks['cardio_risk']}
        Resumen: {sum(1 for v in risks.values() if v == 'Alto')} riesgo(s) alto(s) identificados.
        """
        
        return HealthResponse(
            status="success",
            data={
                "patient": data.patient_name,
                "age": data.patient_age,
                "biomarkers": {
                    "glucose": data.glucose,
                    "haemoglobin": data.haemoglobin,
                    "cholesterol": data.cholesterol
                },
                "risks": risks,
                "summary": {
                    "total_risks": sum(1 for v in risks.values() if v == "Alto"),
                    "moderate_risks": sum(1 for v in risks.values() if v == "Moderado")
                }
            },
            clinical_report=clinical_report.strip(),
            message="¡Análisis clínico completado por el Tiburón Supremo IA!"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9503, log_level="info")