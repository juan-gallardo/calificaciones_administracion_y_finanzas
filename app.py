import streamlit as st
import pandas as pd
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# --- Configuración de la página ---
st.set_page_config(
    page_title="Consulta de Calificaciones",
    page_icon="🎓",
    layout="wide"
)

# --- Cargar imágenes ---
portada_path = "assets/cabecera_estadistica.png"
logo_path = "assets/logo-utn.png"
composicion_calificacion = "assets/composicion_calificacion.png"

# --- Estilos CSS personalizados ---
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;
    }
    .dataframe {
        width: 100% !important;
    }
    .dataframe td, .dataframe th {
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Tipografía ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    body, h1, h2, h3, h4, h5, h6, p, span, div, a, button {
        font-family: 'Poppins', sans-serif !important;
    }
    .big-font {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #005873;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Encabezado ---
st.image(portada_path)
st.markdown("<p class='big-font'>Consulta de Calificaciones - Principios en administración y finanzas</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Cargar variables de entorno ---
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# --- Inicializar Supabase ---
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error al inicializar Supabase. Verifica las variables de entorno. Error: {e}")
    st.stop()

# --- Función optimizada para buscar en Supabase ---
def buscar_estudiante(search_term: str):
    """
    Búsqueda exacta por ID o email.
    El email solo acepta diferencias en mayúsculas/minúsculas
    y espacios alrededor (que se eliminan).
    No permite coincidencias parciales.
    """
    try:
        # Limpiar espacios
        search_term_clean = search_term.strip()

        # Email se busca en minúsculas para que sea case-insensitive
        search_term_email = search_term_clean.lower()

        response = supabase.table('calificaciones_administracion_y_finanzas_utn') \
            .select("*") \
            .or_(
                f"\"Número de ID\".eq.{search_term_clean},"
                f"\"Dirección de correo\".ilike.{search_term_email}"
            ) \
            .execute()

        return pd.DataFrame(response.data)

    except Exception as e:
        st.error(f"Error al consultar Supabase: {e}")
        return pd.DataFrame()

# --- Interfaz de búsqueda ---
search_term = st.text_input(
    "Ingresa tu **número de ID** o **correo electrónico** para consultar tu calificación:",
    placeholder="Ej: 123456 o perez@gmail",
).strip()

# --- Lógica de búsqueda ---
if search_term:
    search_results = buscar_estudiante(search_term)

    if not search_results.empty:
        st.subheader("Tu calificación:")

        # Seleccionamos las columnas necesarias
        result_to_show = search_results[[
            "Nombre", "Número de ID", "Dirección de correo",
            "% Actividades realizadas", "Nota", "Condición del estudiante"
        ]].copy()

        # Formato de porcentaje
        result_to_show['% Actividades realizadas'] = \
            result_to_show['% Actividades realizadas'].apply(lambda x: f'{x:.1%}')

        # Mostrar resultado
        st.dataframe(result_to_show, use_container_width=True)

        # --- Mensajes personalizados ---
        estudiante = search_results.iloc[0]
        condicion = estudiante["Condición del estudiante"]
        nombre = estudiante["Nombre"]

        if condicion == "Promociona":
            st.balloons()
            st.success(f"¡Felicitaciones, {nombre}! ¡Has promocionado la materia! 🎉")

        elif condicion == "Final":
            st.info(
                f"¡Hola, {nombre}! Te esperamos en la instancia de examen final 💪. "
                "Hacenos todas las consultas que necesites 🤗"
            )

    else:
        st.warning("No se encontraron resultados para el ID o email ingresado.")

else:
    st.info("Ingresa tu número de ID o email para ver tu calificación.")

st.markdown("---")

# --- Composición calificación ---
st.image(composicion_calificacion, use_container_width=True)

st.markdown("---")
st.image(logo_path, width=250)
st.markdown("Aplicación desarrollada para la cátedra de Principios en administración y finanzas")
