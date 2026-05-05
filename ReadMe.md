# ParoTrash Backend - Sistema de Verificación Inteligente

Este es el servidor central desarrollado en **FastAPI (Python)** para el procesamiento de alertas de movilidad. Se encarga de validar reportes mediante un sistema de **consenso social** (proximidad geográfica) y **reputación de usuario**, además de gestionar la **Inteligencia de Descarte** para penalizar reportes falsos.

## 🚀 Requisitos Previos

- **Python 3.9** o superior.
- Acceso a la consola de **Firebase** y el archivo `serviceAccountKey.json`.
- Tanto el servidor como el dispositivo Android deben estar en la **misma red** (Hotspot o Wi-Fi local).

---

## 🛠️ Instalación y Configuración

### 1. Clonar el Proyecto

Abre tu terminal (Kubuntu/Linux) o CMD/PowerShell (Windows) y ejecuta:

```bash
git clone https://github.com/Nicolasrc404/ParoTrashBackend.git
cd ParoTrashBackend
```

### 2. Crear y Activar el Entorno Virtual

Es recomendable usar un entorno virtual para no ensuciar las librerías globales de tu sistema.

**En Linux (Kubuntu):**

```bash
python3 -m venv venv
source venv/bin/activate
```

En Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar Dependencias

Una vez activado el entorno, instala las librerías necesarias:

```bash
pip install fastapi uvicorn firebase-admin pydantic
```

---

## 🔑 Configuración de Firebase

1. Ve a tu proyecto en **Firebase Console**.
2. Configuración del proyecto > Cuentas de servicio.
3. Haz clic en **Generar nueva clave privada**.
4. Descarga el archivo `.json`, cámbiale el nombre a `serviceAccountKey.json` y colócalo en la raíz de la carpeta del backend.

---

## 🌐 Configuración de Red e IPs (Paso Crítico)

Para que la App de Android pueda comunicarse con este servidor, necesitas configurar la IP correcta.

### 📍 Paso A: Obtener la IP de tu Laptop

- **En Linux:** Ejecuta `hostname -I` en la terminal.
- **En Windows:** Ejecuta `ipconfig` y busca "Dirección IPv4".
- *Ejemplo de IP:* `192.168.1.15`

### 📍 Paso B: Configurar en Android

En tu proyecto de Android Studio, busca el archivo `RetrofitClient.kt` y actualiza la `BASE_URL`:

```kotlin
// Usa la IP obtenida en el Paso A
private const val BASE_URL = "http://192.168.1.15:8000/"
```

### 📍 Paso C: El Host en Python

El servidor debe estar configurado para escuchar en todas las interfaces de red para que el celular pueda entrar:

```python
# Al final de tu main.py
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)[cite: 3]
```

---

## ⚡ Ejecución del Servidor

Para iniciar el backend con recarga automática (útil para desarrollo):

```bash
uvicorn main:app --reload --host 0.0.0.0
```

Si todo está bien, verás un mensaje indicando que el servidor corre en `[http://0.0.0.0:8000](http://0.0.0.0:8000)`.

---

**🧠 Lógica de Inteligencia Integrada
✅ Validación (Endpoint: `/procesar-alerta`)**
• **Consenso:** Si hay 3 o más reportes en un radio de 100 metros.  

• **Reputación:** Si el autor tiene más de 50 puntos de reputación.  

**❌ Descarte (Endpoint: `/descartar-alerta`)**
• Si un reporte recibe **5 "No"** (descartes), el backend resta automáticamente **10 puntos** de reputación al autor original para prevenir "trolls".  

• Al llegar a **10 "No"**, la alerta se elimina automáticamente del mapa. 

---

## 📝 Notas para la Universidad (Tadeo)

Si el Wi-Fi institucional bloquea la conexión, recuerda usar el **Hotspot de tu celular**. Conecta la laptop al celular y repite el proceso de obtener la IP (Paso A). ¡Esto garantiza que la conexión sea directa y sin firewalls!