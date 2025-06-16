import os
import streamlit as st
from sqlalchemy import text
from dotenv import load_dotenv
from database_functions import get_database_connection
from openai import OpenAI

# Cargar variables de entorno desde .env
load_dotenv()

# Leer la clave de OpenAI desde variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ Error: No se encontró OPENAI_API_KEY en las variables de entorno")
    st.stop()

# Configurar el cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def get_db_connection():
    return get_database_connection()

def generate_sql_query(question):
    """Genera una consulta SQL usando OpenAI"""
    prompt = f"""
    Eres un experto en SQL para PostgreSQL. Genera UNA SOLA consulta SQL válida basada en esta pregunta: {question}
    
    Objetivo de la LLM:
    El LLM está diseñado para responder preguntas del negocio relacionadas con:
        1. Desempeño y cambios en las métricas de conversión a lo largo del tiempo.
        2. Análisis de comportamiento de usuarios en el embudo de ventas.
        3. Efectividad de campañas de marketing (pagadas, orgánicas, promocionadas).
        4. Comparaciones entre mercados y culturas, y su impacto en los resultados de eCommerce.
        5. Identificación de tendencias, anomalías y oportunidades de mejora.
    Las respuestas deben ser específicas, claras y accionables, proporcionando recomendaciones cuando sea necesario.
    
    IMPORTANTE:
    - La tabla se llama 'client_conversion_only_culture'
    - Usa SOLO símbolos SQL estándar: >=, <=, =, !=, etc. (NO uses ≥, ≤, ≠)
    - NO incluyas markdown, comillas extra, o formato adicional
    - Responde SOLO con la consulta SQL pura
    
    La tabla 'client_conversion_only_culture' tiene estas columnas:
    - date (datetime): fecha de la métrica
    - culture (string): Representa el país del usuario basado en las siguientes asignaciones:
        'CL' -> 'Chile'
        'AR' -> 'Argentina'
        'PE' -> 'Perú'
        'CO' -> 'Colombia'
        'BR' -> 'Brasil'
        'UY' -> 'Uruguay'
        'PY' -> 'Paraguay'
        'EC' -> 'Ecuador'
        'US' -> 'Estados Unidos'
    - traffic (float): sesiones / usuarios únicos diarios
    - flight_dom_loaded_flight (int): veces que se cargó la página de vuelos nacionales
    - payment_confirmation_loaded (int): Total de usuarios únicos que completaron una transacción exitosa.
    - median_time_seconds (float): tiempo mediano hasta la conversión en segundos
    - median_time_minutes (float): tiempo mediano en minutos hasta la conversión
    
    Ejemplo de respuesta correcta:
    SELECT SUM(traffic) FROM client_conversion_only_culture WHERE culture = 'CL' AND date >= '2024-01-05'
    """
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    # Limpiar la respuesta de posibles formatos markdown
    sql_query = response.choices[0].message.content.strip()
    
    # Remover markdown si está presente
    if sql_query.startswith('```'):
        lines = sql_query.split('\n')
        sql_query = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql_query
    
    return sql_query

def execute_query(sql_query):
    """Ejecuta la consulta SQL y retorna los resultados"""
    engine = get_db_connection()
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        return result.fetchall()

def main():
    st.title("🧠 Agente RAG de Métricas Web")
    st.write("""
    Haz preguntas sobre tus métricas de tráfico y conversión. Ejemplos:
    - ¿Cuánto tráfico tuvimos el 5 de enero en CL?
    - ¿Cuántas confirmaciones de pago hubo el 3 de enero en CL?
    """)

    question = st.text_input("Escribe tu pregunta:")
    if question:
        try:
            # Generar SQL
            sql_query = generate_sql_query(question)
            
            # Mostrar SQL antes de ejecutar
            st.markdown("**SQL generado:**")
            st.code(sql_query, language="sql")
            
            # Ejecutar consulta
            results = execute_query(sql_query)
            
            # Mostrar resultados
            if results:
                st.markdown("**Respuesta:**")
                for row in results:
                    st.write(row)
            else:
                st.write("No se encontraron resultados.")
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.markdown("**SQL que causó el error:**")
            st.code(sql_query, language="sql")

    st.markdown("---")
    st.markdown("### Ejemplos de preguntas reales")
    st.markdown("**¿Cuánto tráfico tuvimos el 5 de enero en CL?**\nRespuesta: 12,345 sesiones.")
    st.markdown("**¿Cuántas confirmaciones de pago hubo el 3 de enero en CL?**\nRespuesta: 234 confirmaciones.")

if __name__ == "__main__":
    main()