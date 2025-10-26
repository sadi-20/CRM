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
def init_data():
    """Inicializa el DataFrame de clientes, cargando desde CSV o creando uno nuevo."""
    try:
        df = pd.read_csv("crm_data.csv")
        # Asegura que las fechas se manejen correctamente
        df['Fecha de Servicio'] = pd.to_datetime(df['Fecha de Servicio']).dt.date
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

# Guarda los datos en un archivo CSV (simulación de persistencia)
def save_data():
    st.session_state['clientes_df'].to_csv("crm_data.csv", index=False)

init_data()

# --- Funcionalidad de Descarga Excel ---
@st.cache_data
def to_excel(df):
    """Convierte el DataFrame a formato Excel para descarga."""
    output = BytesIO()
    # Usamos xlsxwriter para aplicar formato, como el color amarillo en el encabezado
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Clientes')
    
    workbook = writer.book
    # Formato amarillo para el encabezado (coincide con el amarillo solicitado)
    yellow_format = workbook.add_format({'bg_color': '#FFC300', 'bold': True, 'align': 'center'}) 
    worksheet = writer.sheets['Clientes']
    
    # Aplica el formato al encabezado
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, yellow_format)
    
    # Ajusta el ancho de las columnas (opcional)
    worksheet.set_column('A:L', 20) 
    
    writer.close()
    processed_data = output.getvalue()
    return processed_data

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
    
    tipo_cliente = st.selectbox("Clasificación de Cliente", ("Nuevo", "Antiguo"))

    submit_button = st.form_submit_button(label='💾 Registrar Cliente', type="primary") # Aplica el azul primario

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
st.markdown("---")

df = st.session_state['clientes_df'].copy()

if df.empty:
    st.info("Aún no hay datos de clientes. Use el formulario de la barra lateral para comenzar.")
else:
    # --- Filtros ---
    st.subheader("Filtros de Clientes")
    col_filt1, col_filt2, col_filt3 = st.columns(3)
    
    # Filtro 1: Tipo de Cliente (Antiguo/Nuevo)
    tipos_cliente = df['Tipo de Cliente'].unique().tolist()
    tipo_seleccionado = col_filt1.multiselect("Filtrar por Tipo de Cliente", tipos_cliente, default=tipos_cliente)
    
    # Filtro 2: Score Mínimo
    min_score = col_filt2.slider("Score Mínimo (0-1000)", 0, 1000, 0)
    
    # === INICIO DE CORRECCIÓN PARA EL SLIDER DE PRECIO ===
    precio_min_actual = float(df['Precio'].min())
    precio_max_actual = float(df['Precio'].max())

    if precio_min_actual == precio_max_actual:
        # Solución: Si min y max son iguales (ej: solo un registro), forzar un rango
        slider_min = precio_min_actual 
        # Si el precio es 0, hacemos el max 10, si no, le damos un margen de 10
        slider_max = precio_max_actual + 10.0 if precio_max_actual == 0 else precio_max_actual * 1.05 + 10.0 
        slider_default = (precio_min_actual, slider_max)
    else:
        # Caso normal: usar el rango real
        slider_min = precio_min_actual
        slider_max = precio_max_actual
        slider_default = (precio_min_actual, precio_max_actual)

    # Filtro 3: Rango de Precio (Usando los rangos ajustados)
    min_price, max_price = col_filt3.slider(
        "Rango de Precio ($)",
        slider_min, 
        slider_max,
        slider_default
    )
    # === FIN DE CORRECCIÓN ===

    # Aplicar filtros
    df_filtrado = df[
        (df['Tipo de Cliente'].isin(tipo_seleccionado)) &
        (df['Score (0-1000)'] >= min_score) &
        (df['Precio'] >= min_price) &
        (df['Precio'] <= max_price)
    ]

    st.markdown(f"**Mostrando {len(df_filtrado)} de {len(df)} clientes registrados.**")
    st.markdown("---")

    # --- Métricas Clave (KPIs) ---
    col1, col2, col3 = st.columns(3)
    
    # Usamos markdown para dar color a los títulos, aunque el tema ya aplica colores.
    col1.metric("Clientes Filtrados", len(df_filtrado))
    col2.metric("Precio Promedio Filtrado", f"${df_filtrado['Precio'].mean():,.2f}" if not df_filtrado.empty else "$0.00")
    col3.metric("Score Promedio Filtrado", f"{df_filtrado['Score (0-1000)'].mean():.0f}" if not df_filtrado.empty else "N/A")

    st.markdown("---")

    # --- Gráficos de Visualización ---
    tab1, tab2, tab3 = st.tabs(["Gráficos y Tendencias", "Tabla de Datos y Descarga", "Datos Crudos (DataFrame Completo)"])

    with tab1:
        st.subheader("Análisis Visual de Clientes Filtrados")
        colA, colB = st.columns(2)
        
        with colA:
            # Gráfico de Distribución de Precios (Amarillo y Azul)
            fig_price = px.histogram(df_filtrado, x='Precio', 
                                     title='Distribución de Precios por Tipo de Cliente', 
                                     color='Tipo de Cliente', 
                                     barmode='overlay', 
                                     color_discrete_map={'Nuevo': '#FFC300', 'Antiguo': '#007ACC'}) 
            st.plotly_chart(fig_price, use_container_width=True)

        with colB:
            # Gráfico de Clientes Antiguos vs. Nuevos (Amarillo y Azul)
            count_type = df_filtrado['Tipo de Cliente'].value_counts().reset_index()
            count_type.columns = ['Tipo', 'Conteo']
            fig_type = px.bar(count_type, x='Tipo', y='Conteo', title='Conteo de Clientes Antiguos/Nuevos', 
                             color='Tipo', 
                             color_discrete_map={'Nuevo': '#FFC300', 'Antiguo': '#007ACC'}) 
            st.plotly_chart(fig_type, use_container_width=True)


    with tab2:
        st.subheader("Tabla de Clientes Filtrados y Ordenados")
        # Ordenado por Fecha de Servicio
        df_ordenado = df_filtrado.sort_values(by='Fecha de Servicio', ascending=False)
        st.dataframe(df_ordenado, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Exportar a Excel")
        
        # Botón de descarga de Excel (el color 'primary' es el azul, '#007ACC')
        excel_data = to_excel(df_ordenado)
        
        st.download_button(
            label="Descargar Datos Filtrados (.xlsx) ⬇️",
            data=excel_data,
            file_name=f'clientes_camionetas_{date.today()}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            type="primary" 
        )
        st.caption("La descarga contiene los datos filtrados y ordenados que se muestran en la tabla superior.")

    with tab3:
        st.subheader("Datos Crudos Almacenados (Sin Filtrar)")
        st.dataframe(df.sort_values(by='Fecha de Servicio', ascending=False), use_container_width=True)
