import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import math
import uvicorn

# 1. Configuración de Firebase
# Asegúrate de que el archivo serviceAccountKey.json esté en la misma carpeta
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

class ReporteSchema(BaseModel):
    id: str
    id_usuario: str
    ubicacion: List[float]

def haversine(p1, p2):
    """Cálculo de distancia entre dos puntos [lat, lon] en metros"""
    R = 6371000 
    phi1, phi2 = math.radians(p1[0]), math.radians(p2[0])
    dphi = math.radians(p2[0] - p1[0])
    dlambda = math.radians(p2[1] - p1[1])
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@app.post("/procesar-alerta")
async def procesar_alerta(data: ReporteSchema):
    print(f"\n--- Analizando reporte: {data.id} ---")
    
    # Obtener datos del autor para verificar su reputación actual[cite: 7]
    user_ref = db.collection("usuarios").document(data.id_usuario).get()
    reputacion = 0
    if user_ref.exists:
        user_data = user_ref.to_dict()
        reputacion = user_data.get("reputacion", 0)
        print(f"User: {user_data.get('nombre', 'Invitado')} | Reputación: {reputacion}")

    # Buscar coincidencias cercanas en la base de datos[cite: 7]
    reportes_ref = db.collection("reportes").stream()
    coincidencias = 0
    for doc in reportes_ref:
        r = doc.to_dict()
        if doc.id == data.id: continue
        
        loc_existente = r.get("ubicacion")
        if loc_existente and isinstance(loc_existente, list) and len(loc_existente) >= 2:
            distancia = haversine(data.ubicacion, loc_existente)
            if distancia < 100:
                coincidencias += 1
    
    # Lógica de Verificación (Corregida sin etiquetas de texto)
    es_veridico = coincidencias >= 3 or reputacion > 50
    
    if es_veridico:
        # Marcar como verificado en Firestore[cite: 7]
        db.collection("reportes").document(data.id).update({"verificado": True})
        
        # Premiar al autor con +10 de reputación
        autor_ref = db.collection("usuarios").document(data.id_usuario)
        autor_ref.update({"reputacion": firestore.Increment(10)})
        
        print(f"✅ ESTADO: VERIFICADO | +10 puntos a {data.id_usuario}")
        return {"status": "validado", "puntos": 10}
    
    print("⏳ ESTADO: PENDIENTE")
    return {"status": "pendiente"}

@app.post("/descartar-alerta")
async def descartar_alerta(data: ReporteSchema):
    print(f"\n--- Analizando Descarte: {data.id} ---")
    
    reporte_ref = db.collection("reportes").document(data.id)
    reporte_doc = reporte_ref.get()
    
    if reporte_doc.exists:
        r = reporte_doc.to_dict()
        descartes = r.get("descartes", 0)
        id_autor = r.get("id_usuario") 
        
        # Si el reporte acumula 5 o más descartes, penalizamos al autor[cite: 7]
        if descartes >= 5 and id_autor:
            autor_ref = db.collection("usuarios").document(id_autor)
            if autor_ref.get().exists:
                # Penalizar al autor con -10 de reputación para mantener la simetría[cite: 3]
                autor_ref.update({"reputacion": firestore.Increment(-10)})
                print(f"⚠️ Penalización: -10 puntos a autor {id_autor}")
        
        return {"status": "descarte_procesado", "total_descartes": descartes}
    
    return {"status": "error", "message": "No existe"}

if __name__ == "__main__":
    # Host 0.0.0.0 para permitir conexiones desde la App en tu celular[cite: 7]
    uvicorn.run(app, host="0.0.0.0", port=8000)