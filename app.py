import streamlit as st
import pandas as pd
import os # Importamos la librería para trabajar con rutas de archivos
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
st.markdown("<p class='big-font'>Consulta de Calificaciones - Principios en administración y finanzas</p>", unsafe_allow_html=True)
st.markdown("---")

# --- Cargar variables de entorno ---
load_dotenv()

# --- Obtener credenciales de Supabase ---
# Asegúrate de que estas variables estén definidas en tu archivo .env
# SUPABASE_URL="https://your_project_ref.supabase.co"
# SUPABASE_KEY="your_anon_public_key"
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# --- Inicializar cliente Supabase fuera de la función cacheada ---
# El cliente Supabase no es "cacheable" por Streamlit de forma directa.
# Es mejor crearlo una vez y pasarlo o usarlo globalmente.
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error al inicializar el cliente Supabase. Verifica tus variables de entorno. Error: {e}")
    st.stop() # Detenemos la ejecución si no podemos conectar a Supabase

# --- Carga de datos desde Supabase ---
@st.cache_data(ttl="5m") # Cachea los datos por 5 minutos
def load_data_from_supabase():
    """
    Carga los datos de la tabla 'calificaciones_administracion_y_finanzas_utn' de Supabase
    en un DataFrame de pandas.
    """
    try:
        # Usamos el cliente Supabase globalmente
        response = supabase.table('calificaciones_administracion_y_finanzas_utn').select('*').execute()
        
        # Supabase client retorna los datos en .data
        df = pd.DataFrame(response.data)
        
        # Limpia los datos y convierte las columnas clave a string
        if not df.empty:
            df["Número de ID"] = df["Número de ID"].astype(str).str.strip()
            df["Dirección de correo"] = df["Dirección de correo"].astype(str).str.strip()
        
        return df
    except Exception as e:
        st.error(f"Hubo un error al cargar los datos desde Supabase. Revisa la tabla y las columnas. Error: {e}")
        return pd.DataFrame() # Devuelve un DataFrame vacío en caso de error

# --- Carga los datos en un DataFrame desde Supabase ---
df = load_data_from_supabase()

if df.empty:
    # Este mensaje solo se muestra si load_data devuelve un DataFrame vacío por un error de lectura
    st.info("No se pudieron cargar los datos desde Supabase. Por favor, verifica tu conexión y la tabla.")
    st.stop()

# --- 2. Interfaz de búsqueda ---
search_term = st.text_input(
    "Ingresa tu **número de ID** o **correo electrónico** para consultar tu calificación:",
    placeholder="Ej: 123456 o perez@gmail",
)

# Elimina espacios en blanco al inicio y al final del término de búsqueda.
search_term = search_term.strip()

# --- 3. Lógica de filtrado y visualización ---
if search_term:
    # La búsqueda por id y email es exacta y no distingue mayúsculas/minúsculas.
    search_results = df[
        (df["Número de ID"] == search_term) |
        (df["Dirección de correo"].str.lower() == search_term.lower())
    ]

    if not search_results.empty:

        st.subheader("Tu calificación:")
        
        # Muestra solo las columnas que especificaste
        result_to_show = search_results[[
            "Nombre", "Número de ID", "Dirección de correo",
            "% Actividades realizadas", "Nota", "Condición del estudiante"
        ]].copy() # Usamos .copy() para evitar un aviso de Pandas
        # Aplica el formato de porcentaje al DataFrame antes de mostrarlo en la tabla
        # Multiplicamos por 100 si los valores están entre 0 y 1
        result_to_show['% Actividades realizadas'] = result_to_show['% Actividades realizadas'].apply(lambda x: f'{x:.1%}')
        
        st.dataframe(result_to_show, use_container_width=True)

        ###  --- Mensajes personalizados ---
        # Accedemos a la primera fila de los resultados
        estudiante_resultado = search_results.iloc[0]

        # Mensajes condicionales
        condicion = estudiante_resultado["Condición del estudiante"]
        nombre = estudiante_resultado["Nombre"]
        
        # Verificamos si la condición es "Promociona" o "Final"
        if condicion == "Promociona":
            st.balloons() # ¡Globos de celebración!
            st.success(f"¡Felicitaciones, {nombre}! ¡Has promocionado la materia! 🎉")
        elif condicion == "Final":
            st.info(f"¡Hola, {nombre}! Te esperamos en la instancia de examen final para darlo todo 💪. Te animamos a dar un último esfuerzo para aprobar la materia. ¡No dudes en hacernos todas las consultas que necesites 🤗!")
        

    else:
        st.warning("No se encontraron resultados con el ID o email ingresado. Por favor, inténtalo de nuevo.")
else:
    st.info("Ingresa tu número de ID o email en el campo de arriba para ver tu calificación.")

st.markdown("---")

# --- Composición calificación ---

st.image(composicion_calificacion, use_container_width=True) # Ajusta el ancho según sea necesario

st.markdown("---")

st.image(logo_path, width=250)
st.markdown("Aplicación desarrollada para la cátedra de Principios en administración y finanzas")











# import streamlit as st
# import pandas as pd
# import os # Importamos la librería para trabajar con rutas de archivos

# # --- Configuración de la página ---
# st.set_page_config(
#     page_title="Consulta de Calificaciones",
#     page_icon="🎓",
#     layout="wide"
# )

# # --- Cargar imágenes ---
# portada_path = "assets/cabecera_estadistica.png"  # Reemplaza con tu imagen
# logo_path = "assets/logo-utn.png"  # Reemplaza con tu logo
# composicion_calificacion = "assets/composicion_calificacion.png"  # Reemplaza con tu imagen

# # --- Estilos CSS personalizados ---
# st.markdown(
#     """
#     <style>
#     body {
#         background-color: #ffffff;  /* Color de fondo */
#     }
#     .dataframe {
#         width: 100% !important; /* Ocupa todo el ancho disponible */
#     }
#     .dataframe td, .dataframe th {
#         white-space: nowrap; /* Evita que el texto se envuelva */
#     }
#     """,
#     unsafe_allow_html=True,
# )

# # --- Estilos CSS personalizados ---
# st.markdown(
#     """
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

#     body, h1, h2, h3, h4, h5, h6, p, span, div, a, button {
#         font-family: 'Poppins', sans-serif !important;
#     }
#     .big-font {
#         font-size: 2.5rem !important;
#         font-weight: bold;
#         color: #005873;
#         margin-bottom: 1rem; /* Más espacio debajo del título principal */
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # --- Encabezado con imagen de portada ---
# st.image(portada_path)

# # --- Título de la aplicación ---
# st.markdown("<p class='big-font'>Consulta de Calificaciones - Principios en administración y finanzas</p>", unsafe_allow_html=True)
# st.markdown("---")

# # --- 1. Define la ruta de tu archivo Excel ---
# # ¡IMPORTANTE! Reemplaza "calificaciones.xlsx" con el nombre de tu archivo.
# # Asegúrate de que el archivo esté en la misma carpeta que tu script.
# excel_file_path = "Estadística aplicada a los negocios - Calificaciones finales - 1er cuatrimestre 2025.xlsx"

# # --- Carga de datos desde el archivo Excel ---
# @st.cache_data(ttl="5m") # Cachea los datos por 5 minutos
# def load_data(file_path):
#     """Carga los datos de la hoja de cálculo en un DataFrame."""
#     # Verificamos si el archivo existe
#     if not os.path.exists(file_path):
#         st.error(f"Error: No se encontró el archivo '{file_path}'. Asegúrate de que esté en la misma carpeta que el script.")
#         st.stop()
        
#     try:
#         # Lee el archivo Excel. Asegúrate de que el nombre de la hoja sea correcto.
#         df = pd.read_excel(file_path, sheet_name="Calificaciones - En Limpio")
        
#         # Limpia los datos y convierte las columnas clave a string
#         df["Número de ID"] = df["Número de ID"].astype(str).str.strip()
#         df["Apellido(s)"] = df["Apellido(s)"].astype(str).str.strip()
        
#         return df
#     except Exception as e:
#         st.error(f"Hubo un error al cargar los datos desde el archivo. Revisa si la hoja se llama 'Calificaciones - En Limpio' y si los encabezados de las columnas son correctos. Error: {e}")
#         return pd.DataFrame() # Devuelve un DataFrame vacío en caso de error

# # Carga los datos en un DataFrame
# df = load_data(excel_file_path)

# if df.empty:
#     # Este mensaje solo se muestra si load_data devuelve un DataFrame vacío por un error de lectura
#     st.info("No se pudieron cargar los datos desde el archivo. Por favor, verifica el contenido y vuelve a intentarlo.")
#     st.stop()

# # --- 2. Interfaz de búsqueda ---
# search_term = st.text_input(
#     "Ingresa tu número de **ID** o **apellido** para consultar tu calificación:",
#     placeholder="Ej: 123456 o Perez",
# )

# # --- 3. Lógica de filtrado y visualización ---
# if search_term:
#     # Filtra el DataFrame por el término de búsqueda, sin distinguir mayúsculas/minúsculas
#     search_results = df[
#         df["Número de ID"].str.contains(search_term, case=False, na=False) |
#         df["Apellido(s)"].str.contains(search_term, case=False, na=False)
#     ]

#     if not search_results.empty:
#         st.subheader("Tu calificación:")
        
#         # Muestra solo las columnas que especificaste
#         result_to_show = search_results[[
#             "Nombre", "Apellido(s)", "Número de ID", 
#             "% Actividades realizadas", "Nota", "Condición del estudiante"
#         ]].copy() # Usamos .copy() para evitar un aviso de Pandas
#         # Aplica el formato de porcentaje al DataFrame antes de mostrarlo en la tabla
#         # Multiplicamos por 100 si los valores están entre 0 y 1
#         result_to_show['% Actividades realizadas'] = result_to_show['% Actividades realizadas'].apply(lambda x: f'{x:.1%}')
        
#         st.dataframe(result_to_show, use_container_width=True)

#     else:
#         st.warning("No se encontraron resultados con el ID o apellido ingresado. Por favor, inténtalo de nuevo.")
# else:
#     st.info("Ingresa tu número de ID o apellido en el campo de arriba para ver tu calificación.")

# st.markdown("---")

# # --- Título y Logo (CAMBIO 1) ---

# st.image(composicion_calificacion, use_container_width=True) # Ajusta el ancho según sea necesario

# st.markdown("---")

# st.image(logo_path, width=250)
# st.markdown("Aplicación desarrollada para la cátedra de Principios en administración y finanzas")



