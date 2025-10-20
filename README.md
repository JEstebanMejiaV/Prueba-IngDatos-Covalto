# Data Engineering Challenge — Repo

Este repositorio reúne código, pruebas y documentos del reto (BI, Riesgo, Fraude).
El objetivo de este README es **explicar qué hay en las carpetas/archivos** y cómo **ejecutar los tests** y el **CI**.

## 📁 Contenido del repositorio (alto nivel)

- **Documentos del reto**  
- **High Level Problem (pptx)**  
  Visión ejecutiva: objetivos, Arquitectura a alto nivel, restricciones y métricas de éxito.  
  → [Abrir](./The%20High%20Level%20Problem.pptx)

- **Low Level Problem**  
  Implementaciòn y test del problema del DAG   
  → [Abrir](./The%20Low%20Level%20Problem)

- **Scenario Problem (pptx)**  
  Narrativa del caso: contexto, motivación y riesgos.  
  → [Abrir](./The%20Scenario%20Problem.pptx)
## ▶️ Cómo ejecutar las pruebas (local)

- **.github/workflows/ci.yml**  
  Workflow de GitHub Actions que corre pruebas automáticamente en cada *push* y *pull request* a `main/master`.

- **tests/**  
  Pruebas de `pytest` (ej.: `tests/test_dag.py`). Importan el módulo principal del repo.

- **prog.py** *(o `prog` si tu editor oculta la extensión)*  
  Código fuente principal usado por los tests (`from prog import ...`).

- **pytest.ini**  
  Configuración de `pytest` (ruta de tests, flags de salida y cobertura).

- **requirements-dev.txt**  
  Dependencias mínimas para desarrollo y tests (ej.: `pytest`, `pytest-cov`).

- **Services/** *(opcional)*  
  Carpeta para código adicional/experimentos. Si ejecutas CI dentro de esta carpeta en modo monorepo, ajusta el `working-directory` del workflow.



```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q
```

> Si aparece `ModuleNotFoundError: No module named 'prog'`, verifica que `prog.py` esté **en la misma raíz** donde vive `tests/` o exporta `PYTHONPATH` hacia esa carpeta.

## 🤖 CI (muy breve)

- El workflow está en **`.github/workflows/ci.yml`**.  
- Pasos: *checkout* → configurar Python → instalar deps → `python -m pytest`.  
- En monorepo: usa `defaults.run.working-directory: <tu_carpeta>` y `cache-dependency-path` apuntando a tu `requirements-dev.txt`.

## 📝 Notas rápidas

- Mantén los tests dentro de `tests/`.  
- Nombra el archivo de configuración exactamente **`pytest.ini`**.  
- Si cambias el nombre/ubicación de `prog.py`, ajusta los imports en los tests o el `PYTHONPATH` del workflow.

