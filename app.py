import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# --- Configuración de la Página ---
st.set_page_config(
    page_title="CRM Alquiler Camionetas",
    layout="wide"
)

# --- Variables de Estado para Almacenamiento (Simulación de DB) ---
# Intenta cargar datos existentes, si no existen, crea un DataFrame vacío.
def init_data():
    try:
        # Intenta cargar desde un archivo (simulando persistencia en GitHub)
        # En un entorno real, usarías una base de datos o Google Sheets.
        df = pd.read_csv("crm_data.csv")
    except FileNotFoundError:
        # Columnas según lo solicitado
        data = {
            'Fecha de Servicio': [],
            'Empresa': [],
            'RUC': [],
            'Tiempo de Servicio (días)': [],
            '¿Conductor?': [],
            'Precio': [],
            'Contacto': [],
            'Email': [],
            'Teléfono': [],
            'Score (0-1000)': [],
            'Trabajadores': [],
            'Tipo de Cliente': [],
        }
        df = pd.DataFrame(data)
    
    if 'clientes_df' not in st.session_state:
        st.session_state['clientes_df'] = df

# Guarda los datos en un archivo CSV
def save_data():
    st.session_state['clientes_df'].to_csv("crm_data.csv", index=False)

init_data()

# --- Funcionalidad: Ingreso de Datos (CRM) ---
st.sidebar.header("📝 Ingreso de Nuevo Cliente")

with st.sidebar.form(key='crm_form'):
    st.subheader("Datos del Servicio")
    
    # Campos de entrada
    fecha_servicio = st.date_input("Fecha de Servicio", date.today())
    empresa = st.text_input("Empresa")
    ruc = st.text_input("RUC")
    tiempo_dias = st.number_input("Tiempo de Servicio (días)", min_value=1, step=1)
    precio = st.number_input("Precio ($)", min_value=0.0, step=10.0)
    con_conductor = st.selectbox("¿Conductor o Sin Conductor?", ("Con Conductor", "Sin Conductor"))

    st.subheader("Datos del Contacto")
    contacto = st.text_input("Nombre de Contacto")
    email = st.text_input("Email")
    telefono = st.text_input("Teléfono")
    
    st.subheader("Datos de Evaluación")
    score = st.slider("Score de Crédito (0-1000)", 0, 1000, 500)
    trabajadores = st.number_input("Cantidad de Trabajadores", min_value=1, step=1)
    
    # Determinación simple de tipo de cliente (aquí se podría añadir lógica avanzada)
    tipo_cliente = st.selectbox("Clasificación de Cliente", ("Nuevo", "Antiguo"))

    submit_button = st.form_submit_button(label='💾 Registrar Cliente')

    if submit_button:
        # Validaciones básicas
        if not empresa or not ruc or not contacto:
            st.error("Por favor, complete los campos de Empresa, RUC y Contacto.")
        else:
            # Crea el nuevo registro
            new_entry = {
                'Fecha de Servicio': fecha_servicio,
                'Empresa': empresa,
                'RUC': ruc,
                'Tiempo de Servicio (días)': tiempo_dias,
                '¿Conductor?': con_conductor,
                'Precio': precio,
                'Contacto': contacto,
                'Email': email,
                'Teléfono': telefono,
                'Score (0-1000)': score,
                'Trabajadores': trabajadores,
                'Tipo de Cliente': tipo_cliente,
            }

            # Añade el registro al DataFrame de la sesión
            new_df = pd.DataFrame([new_entry])
            st.session_state['clientes_df'] = pd.concat([st.session_state['clientes_df'], new_df], ignore_index=True)
            
            # Guarda los datos
            save_data()
            st.success("✅ Cliente registrado y datos guardados.")


# --- Funcionalidad: Visualización de Datos ---
st.title("📊 Dashboard de Gestión de Clientes (Camionetas)")
st.write("---")

df = st.session_state['clientes_df']

if df.empty:
    st.info("Aún no hay datos de clientes. Use el formulario de la barra lateral para comenzar.")
else:
    # --- Métricas Clave (KPIs) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Clientes", len(df))
    col2.metric("Precio Promedio", f"${df['Precio'].mean():,.2f}")
    col3.metric("Clientes Antiguos", len(df[df['Tipo de Cliente'] == 'Antiguo']))

    st.write("---")

    # --- Gráficos de Visualización ---
    tab1, tab2, tab3 = st.tabs(["Distribución de Precios", "Clientes por Tipo", "Detalle de Clientes"])

    with tab1:
        st.subheader("Distribución de Precios de Servicios")
        fig_price = px.histogram(df, x='Precio', 
                                 title='Frecuencia de Precios de Alquiler', 
                                 color='Tipo de Cliente', 
                                 barmode='overlay')
        st.plotly_chart(fig_price, use_container_width=True)

    with tab2:
        colA, colB = st.columns(2)
        
        with colA:
            st.subheader("Conductor vs. Sin Conductor")
            count_driver = df['¿Conductor?'].value_counts().reset_index()
            count_driver.columns = ['Tipo', 'Conteo']
            fig_driver = px.pie(count_driver, values='Conteo', names='Tipo', title='Servicios con/sin Conductor')
            st.plotly_chart(fig_driver, use_container_width=True)

        with colB:
            st.subheader("Clientes Antiguos vs. Nuevos")
            count_type = df['Tipo de Cliente'].value_counts().reset_index()
            count_type.columns = ['Tipo', 'Conteo']
            fig_type = px.bar(count_type, x='Tipo', y='Conteo', title='Conteo de Clientes Antiguos/Nuevos', color='Tipo')
            st.plotly_chart(fig_type, use_container_width=True)

    with tab3:
        st.subheader("Detalle de Todos los Clientes")
        st.dataframe(df, use_container_width=True) # Muestra el DataFrame completo

# --- Instrucciones de Despliegue (Importante) ---
st.sidebar.info("""
    **Para Desplegar:**
    1. Sube este código (`app.py`, `requirements.txt` y, si existe, `crm_data.csv`) a un repositorio público en **GitHub**.
    2. Ve a **Streamlit Community Cloud** (share.streamlit.io).
    3. Conecta tu cuenta de GitHub y selecciona el repositorio.
    4. Elige el archivo principal (`app.py`) y despliega la aplicación.
""")
