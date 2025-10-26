import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from io import BytesIO

# --- Configuración de la Página ---
st.set_page_config(
    page_title="CRM Alquiler Camionetas",
    layout="wide"
)

# --- Variables de Estado para Almacenamiento (Simulación de DB) ---
# Intenta cargar datos existentes, si no existen, crea un DataFrame vacío.
def init_data():
    # Intenta cargar desde el archivo CSV.
    try:
        df = pd.read_csv("crm_data.csv")
        # Asegura que las fechas se manejen correctamente si el archivo existe
        df['Fecha de Servicio'] = pd.to_datetime(df['Fecha de Servicio']).dt.date
    except FileNotFoundError:
        # Crea el DataFrame vacío con los tipos de datos correctos
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

# Guarda los datos en un archivo CSV (persistencia simple)
def save_data():
    st.session_state['clientes_df'].to_csv("crm_data.csv", index=False)

init_data()

# --- Funcionalidad de Descarga Excel ---
@st.cache_data
def to_excel(df):
    """Convierte el DataFrame a formato Excel para descarga."""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Clientes')
    # Permite añadir formato, como un color amarillo para el encabezado (personalización)
    workbook = writer.book
    yellow_format = workbook.add_format({'bg_color': '#FFC300', 'bold': True}) # Amarillo para encabezados
    worksheet = writer.sheets['Clientes']
    worksheet.set_row(0, None, yellow_format)
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# --- Funcionalidad: Ingreso de Datos (CRM) ---
st.sidebar.header("📝 Ingreso de Nuevo Cliente")

# ... (El código del formulario de ingreso de datos es el mismo que antes, NO lo repetimos aquí) ...
# Asegúrate de mantener la lógica del 'submit_button'

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
    
    # Determinación simple de tipo de cliente
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


# --- Funcionalidad: Visualización de Datos y Descarga ---
st.title("📊 Dashboard de Gestión de Clientes (Camionetas)")
st.write("---")

df = st.session_state['clientes_df'].copy() # Trabaja con una copia para los filtros

if df.empty:
    st.info("Aún no hay datos de clientes. Use el formulario de la barra lateral para comenzar.")
else:
    # --- Filtros (Usando el color amarillo de forma indirecta con el fondo oscuro) ---
    st.subheader("Filtros de Clientes")
    col_filt1, col_filt2, col_filt3 = st.columns(3)
    
    # Filtro 1: Tipo de Cliente (Antiguo/Nuevo)
    tipos_cliente = df['Tipo de Cliente'].unique().tolist()
    tipo_seleccionado = col_filt1.multiselect("Filtrar por Tipo de Cliente", tipos_cliente, default=tipos_cliente)
    
    # Filtro 2: Score Mínimo
    min_score = col_filt2.slider("Score Mínimo (0-1000)", 0, 1000, 0)
    
    # Filtro 3: Rango de Precio
    min_price, max_price = col_filt3.slider(
        "Rango de Precio ($)",
        float(df['Precio'].min()), 
        float(df['Precio'].max()),
        (float(df['Precio'].min()), float(df['Precio'].max()))
    )

    # Aplicar filtros
    df_filtrado = df[
        (df['Tipo de Cliente'].isin(tipo_seleccionado)) &
        (df['Score (0-1000)'] >= min_score) &
        (df['Precio'] >= min_price) &
        (df['Precio'] <= max_price)
    ]

    st.write(f"Mostrando {len(df_filtrado)} de {len(df)} clientes.")
    st.write("---")

    # --- Métricas Clave (KPIs) ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Clientes Filtrados", len(df_filtrado))
    col2.metric("Precio Promedio Filtrado", f"${df_filtrado['Precio'].mean():,.2f}" if not df_filtrado.empty else "$0.00")
    col3.metric("Score Promedio Filtrado", f"{df_filtrado['Score (0-1000)'].mean():.0f}" if not df_filtrado.empty else "N/A")

    st.write("---")

    # --- Gráficos de Visualización (Usando Azul y complementos) ---
    # Los gráficos de Plotly usarán el color primario (#007ACC - Azul)

    tab1, tab2, tab3 = st.tabs(["Gráficos", "Tabla de Datos y Descarga", "Detalle CSV"])

    with tab1:
        st.subheader("Gráficos del CRM (Datos Filtrados)")
        colA, colB = st.columns(2)
        
        with colA:
            fig_price = px.histogram(df_filtrado, x='Precio', 
                                     title='Distribución de Precios', 
                                     color='Tipo de Cliente', 
                                     barmode='overlay', 
                                     color_discrete_map={'Nuevo': '#FFC300', 'Antiguo': '#007ACC'}) # Amarillo y Azul
            st.plotly_chart(fig_price, use_container_width=True)

        with colB:
            count_type = df_filtrado['Tipo de Cliente'].value_counts().reset_index()
            count_type.columns = ['Tipo', 'Conteo']
            fig_type = px.bar(count_type, x='Tipo', y='Conteo', title='Clientes Antiguos vs. Nuevos', 
                             color='Tipo', 
                             color_discrete_map={'Nuevo': '#FFC300', 'Antiguo': '#007ACC'}) # Amarillo y Azul
            st.plotly_chart(fig_type, use_container_width=True)


    with tab2:
        st.subheader("Tabla de Clientes Filtrados y Ordenados")
        # Mostrar la tabla ordenada por Fecha de Servicio (descendente)
        df_ordenado = df_filtrado.sort_values(by='Fecha de Servicio', ascending=False)
        st.dataframe(df_ordenado, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Descargar Datos en Excel")
        
        # Botón de descarga de Excel
        excel_data = to_excel(df_ordenado)
        
        st.download_button(
            label="Descargar Datos Filtrados (.xlsx) ⬇️",
            data=excel_data,
            file_name=f'clientes_camionetas_{date.today()}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            type="primary" # Color azul (primaryColor)
        )
        st.caption("La descarga contendrá los datos actualmente visibles en la tabla.")

    with tab3:
        st.subheader("Datos Brutos (CSV)")
        st.dataframe(df, use_container_width=True) # Muestra el DataFrame completo sin filtrar
