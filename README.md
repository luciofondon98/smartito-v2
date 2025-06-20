¡Perfecto! Aquí tienes el README con la sección de documentación de la función `get_data_looks_per_route` integrada justo después de "Ejemplos de preguntas":

---

Perfecto. Aquí tienes la **documentación actualizada** de tu proyecto, alineada con todo lo que conversamos: conexión a base de datos local, Streamlit como frontend, y ahora con estructura modular para la API externa y la base de datos. Incluye la idea del agente RAG con OpenAI y GPT para responder preguntas de negocio.

---

# 🧠 Agente de Conversión y Tráfico — MVP RAG

Este proyecto contiene un **MVP funcional** de un asistente RAG construido con **OpenAI** y **Streamlit**, capaz de responder preguntas en lenguaje natural sobre métricas de tráfico y conversión de un sitio web. La fuente de datos es una **base de datos PostgreSQL local** (y próximamente una API externa), y el modelo genera automáticamente las consultas SQL necesarias para responder.

---

## ✅ Tecnologías usadas

* Python 3.10+
* PostgreSQL (base de datos local)
* OpenAI (`openai`)
* SQLAlchemy (`sqlalchemy`)
* Streamlit (frontend)
* psycopg2-binary
* python-dotenv

---

## 📁 Estructura del proyecto

```
.
├── app.py                  ← Código principal del agente RAG con Streamlit
├── requirements.txt        ← Dependencias necesarias
├── .env                    ← Variables de entorno (no se sube al repo)
├── README.md               ← Esta documentación
│
├── api/                    ← Funciones y módulos para la API externa
│   ├── api.py
│   ├── amplitude_events.py
│   └── amplitude_filters.py
│
├── database/               ← Funciones y módulos para la base de datos
│   ├── database_functions.py
│   └── conversion_only_culture.py
│
├── venv/                   ← Entorno virtual (no subir al repo)
└── __pycache__/            ← Archivos temporales de Python
```

---

## ⚙️ Configuración

### 1. Clona el repositorio y entra a la carpeta

```bash
git clone <tu-repo>
cd <tu-repo>
```

### 2. Crea y activa el entorno virtual

* **Windows**:

  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

* **Mac/Linux**:

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instala las dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Crea un archivo `.env` con estas variables:

```
OPENAI_API_KEY=tu_clave_de_openai
DB_URI=postgresql+psycopg2://usuario:contraseña@localhost:5432/tu_base
```

---

## ▶️ Cómo correr el proyecto

```bash
streamlit run app.py
```

* La interfaz se abrirá en `http://localhost:8501`.
* Escribe una pregunta como:

  > ¿Cuánto tráfico tuvimos el 5 de enero en Chile?
* El agente generará un SQL, consultará la base y mostrará la respuesta textual.

---

## 🧠 Base de datos usada: `client_conversion_only_culture`

### Estructura de la tabla:

| Columna                       | Tipo       | Descripción                           |
| ----------------------------- | ---------- | ------------------------------------- |
| `date`                        | `datetime` | Fecha de la métrica                   |
| `culture`                     | `string`   | Código de país o región (ej: `CL`)    |
| `traffic`                     | `float`    | Sesiones o visitas                    |
| `flight_dom_loaded_flight`    | `float`    | Cargas de página de vuelos nacionales |
| `payment_confirmation_loaded` | `float`    | Confirmaciones de pago                |
| `median_time_seconds`         | `float`    | Tiempo mediano (segundos)             |
| `median_time_minutes`         | `float`    | Tiempo mediano (minutos)              |

---

## 🧪 Ejemplos de preguntas

* ¿Cuántas confirmaciones de pago hubo el 3 de enero en CL?
* ¿Cuál fue el tiempo mediano de conversión en minutos el 10 de enero?
* ¿Cuánto tráfico tuvimos en Chile durante la primera semana de enero?

---

## 📊 Consulta de Looks por Ruta Aérea (API Externa)

### Función: `get_data_looks_per_route`
**Ubicación:** `api/amplitude_events.py`

#### **Descripción:**
Esta función obtiene y procesa datos de “looks” (consultas o búsquedas de vuelos) por ruta aérea, usando la API de Amplitude. Permite analizar cuántas veces se ha consultado una ruta específica entre dos ciudades en un rango de fechas determinado, agrupando por mercado de ida y vuelta (RTMarket).

#### **Parámetros:**
- `dates_list` (`list[str]`): Lista de fechas en formato `YYYY-MM-DD` para las que se desea obtener el reporte.
- `hour_filter` (`int`, opcional, default=23): Hora máxima a considerar (0 a 23). Por ejemplo, si es 2, filtra hasta las 03:00.
- `return_per_hour` (`bool`, opcional, default=False): Si es `True`, retorna también el detalle por hora.

#### **Retorna:**
- Un DataFrame con columnas:
  - `Date`: Fecha de la consulta.
  - `Origin`: Ciudad de origen.
  - `Destination`: Ciudad de destino.
  - `Looks`: Número de búsquedas para esa ruta.
  - `RTMarket`: Identificador único de la ruta ida/vuelta (ej: LIMCUZ o CUZLIM).

#### **Ejemplo de uso:**
```python
dates_list = ['2025-04-08']
df_looks = get_data_looks_per_route(dates_list)
```
**Ejemplo de resultado:**
| Date                | Origin | Destination | Looks | RTMarket |
|---------------------|--------|-------------|-------|----------|
| 2025-04-08T00:00:00 | LIM    | CUZ         | 486   | CUZLIM   |
| 2025-04-08T00:00:00 | CUZ    | LIM         | 181   | CUZLIM   |

---

### 🧠 **Cómo debe usarlo el LLM**
Cuando el usuario pregunte por el número de búsquedas, consultas o “looks” de una ruta específica entre dos ciudades (por ejemplo: “¿Cuántas veces se buscó la ruta LIM-CUZ el 8 de abril de 2025?”), utiliza la función `get_data_looks_per_route` para obtener la información.

- Si el usuario pide el detalle por hora, usa el parámetro `return_per_hour=True`.
- Filtra el resultado por las ciudades de origen y destino indicadas por el usuario.
- El campo `RTMarket` agrupa rutas de ida y vuelta bajo un mismo identificador.

**Ejemplo de prompt para el LLM:**
> El 8 de abril de 2025, hubo 486 búsquedas de la ruta LIM-CUZ y 181 de CUZ-LIM (RTMarket: CUZLIM).

---

¿Te gustaría que agregue alguna otra función/documentación o necesitas algún ajuste en la redacción?