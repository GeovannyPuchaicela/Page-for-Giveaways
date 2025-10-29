GiveHub - Bosquejo Frontend

Descripción
---------
Pequeño frontend estático para probar el backend de GiveHub. Incluye formularios básicos para registrar y loguear usuarios, crear giveaways y listar giveaways.

Requisitos
---------
- Backend corriendo en: http://127.0.0.1:8080 (uvicorn app.main:app --reload --port 8080)
- Permitir CORS en el backend si accedes desde un origen distinto: FastAPI + CORSMiddleware (ver nota abajo).

Cómo probar
---------
1. Desde la carpeta `backend` activa tu virtualenv y corre el backend:

```cmd
venv\Scripts\activate
uvicorn app.main:app --reload --port 8080
```

2. Sirve la carpeta `frontend` con un servidor estático. Desde `frontend` puedes usar el servidor de Python:

```cmd
# desde c:\Users\chris\Desktop\givehub\frontend
python -m http.server 5500
# luego abre http://127.0.0.1:5500
```

3. Usa los formularios de la página para registrar, loguear, crear y listar giveaways.

Nota sobre CORS
---------------
Si obtienes errores de CORS en la consola del navegador, añade lo siguiente al `app/main.py` del backend (ejemplo mínimo):

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Ajustes
------
- El bosquejo asume que los endpoints son:
  - POST /users/register
  - POST /users/login -> devuelve { access_token }
  - GET /giveaways/
  - POST /giveaways/ (requiere Authorization: Bearer <token>)

Si tu API usa rutas o formatos distintos, ajusta `app.js` en consecuencia.

Limitaciones
-----------
- Seguridad mínima; token almacenado en memoria de la página (no persistente).
- No validaciones exhaustivas en el frontend.

Próximos pasos sugeridos
-----------------------
- Hacer un pequeño cambio en el backend para habilitar CORS en desarrollo.
- Convertir el frontend en una SPA con React/Vue si quieres iterar más rápido.
