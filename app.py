import streamlit as st
import pandas as pd
import os # Importamos la librería para trabajar con rutas de archivos

# --- Configuración de la página ---
st.set_page_config(
    page_title="Consulta de Calificaciones",
    page_icon="🎓",
    layout="wide"
)

# --- Cargar imágenes ---
portada_path = "assets/cabecera_estadistica.png"  # Reemplaza con tu imagen
logo_path = "assets/logo-utn.png"  # Reemplaza con tu logo

# --- Estilos CSS personalizados ---
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;  /* Color de fondo */
    }
    .dataframe {
        width: 100% !important; /* Ocupa todo el ancho disponible */
    }
    .dataframe td, .dataframe th {
        white-space: nowrap; /* Evita que el texto se envuelva */
    }
    """,
    unsafe_allow_html=True,
)

# --- Estilos CSS personalizados ---
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
        margin-bottom: 1rem; /* Más espacio debajo del título principal */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Encabezado con imagen de portada ---
st.image(portada_path)

# --- Título de la aplicación ---
st.markdown("<p class='big-font'>Consulta de Calificaciones - Estadística Aplicada a los Negocios</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 1. Define la ruta de tu archivo Excel ---
# ¡IMPORTANTE! Reemplaza "calificaciones.xlsx" con el nombre de tu archivo.
# Asegúrate de que el archivo esté en la misma carpeta que tu script.
excel_file_path = "Estadística aplicada a los negocios - Calificaciones finales - 1er cuatrimestre 2025.xlsx"

# --- Carga de datos desde el archivo Excel ---
@st.cache_data(ttl="5m") # Cachea los datos por 5 minutos
def load_data(file_path):
    """Carga los datos de la hoja de cálculo en un DataFrame."""
    # Verificamos si el archivo existe
    if not os.path.exists(file_path):
        st.error(f"Error: No se encontró el archivo '{file_path}'. Asegúrate de que esté en la misma carpeta que el script.")
        st.stop()
        
    try:
        # Lee el archivo Excel. Asegúrate de que el nombre de la hoja sea correcto.
        df = pd.read_excel(file_path, sheet_name="Calificaciones - En Limpio")
        
        # Limpia los datos y convierte las columnas clave a string
        df["Número de ID"] = df["Número de ID"].astype(str).str.strip()
        df["Apellido(s)"] = df["Apellido(s)"].astype(str).str.strip()
        
        return df
    except Exception as e:
        st.error(f"Hubo un error al cargar los datos desde el archivo. Revisa si la hoja se llama 'Calificaciones - En Limpio' y si los encabezados de las columnas son correctos. Error: {e}")
        return pd.DataFrame() # Devuelve un DataFrame vacío en caso de error

# Carga los datos en un DataFrame
df = load_data(excel_file_path)

if df.empty:
    # Este mensaje solo se muestra si load_data devuelve un DataFrame vacío por un error de lectura
    st.info("No se pudieron cargar los datos desde el archivo. Por favor, verifica el contenido y vuelve a intentarlo.")
    st.stop()

# --- 2. Interfaz de búsqueda ---
search_term = st.text_input(
    "Ingresa tu número de **ID** o **apellido** para consultar tu calificación:",
    placeholder="Ej: 123456 o Perez",
)

# --- 3. Lógica de filtrado y visualización ---
if search_term:
    # Filtra el DataFrame por el término de búsqueda, sin distinguir mayúsculas/minúsculas
    search_results = df[
        df["Número de ID"].str.contains(search_term, case=False, na=False) |
        df["Apellido(s)"].str.contains(search_term, case=False, na=False)
    ]

    if not search_results.empty:
        st.subheader("Tu calificación:")
        
        # Muestra solo las columnas que especificaste
        result_to_show = search_results[[
            "Nombre", "Apellido(s)", "Número de ID", 
            "% Actividades realizadas", "Nota", "Condición del estudiante"
        ]].copy() # Usamos .copy() para evitar un aviso de Pandas
        # Aplica el formato de porcentaje al DataFrame antes de mostrarlo en la tabla
        # Multiplicamos por 100 si los valores están entre 0 y 1
        result_to_show['% Actividades realizadas'] = result_to_show['% Actividades realizadas'].apply(lambda x: f'{x:.1%}')
        
        st.dataframe(result_to_show, use_container_width=True)

    else:
        st.warning("No se encontraron resultados con el ID o apellido ingresado. Por favor, inténtalo de nuevo.")
else:
    st.info("Ingresa tu número de ID o apellido en el campo de arriba para ver tu calificación.")

st.markdown("---")
st.image(logo_path, width=250)
st.markdown("Aplicación desarrollada para la cátedra de Estadística Aplicada a los Negocios")