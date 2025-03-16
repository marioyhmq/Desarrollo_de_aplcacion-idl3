import streamlit as st
from supabase import create_client, Client 
import pandas as pd

# Configuración de Supabase
SUPABASE_URL = "https://mitsyxhkdjkjmgflpmvf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pdHN5eGhrZGpram1nZmxwbXZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIxNTA1NTMsImV4cCI6MjA1NzcyNjU1M30.sapb_dB9eOClGRhJ20J4Ftka2GF2XLCf2JK19kecre8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de la interfaz
st.set_page_config(page_title="Gestión de Clientes", layout="wide")

# Cargar el logo de la empresa (Asegurar que el archivo existe)
logo_path = "logo.png"
try:
    st.image(logo_path, width=200)
except Exception:
    st.warning("No se encontró el logo de la empresa o hubo un error al cargarlo.")

st.title("Sistema de Gestión de Clientes")

# Función para obtener datos con paginación
def get_clients(limit=10, offset=0):
    try:
        response = supabase.table("clientes").select("*").range(offset, offset + limit - 1).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al obtener clientes: {e}")
        return []

# Función para agregar cliente
def add_client(nombre, apellido, email, telefono):
    if not (nombre and apellido and email and telefono):
        return None
    try:
        response = supabase.table("clientes").insert({
            "nombres": nombre,
            "apellidos": apellido,
            "email": email,
            "telefono": telefono,
            "fecha_registro": pd.Timestamp.now().isoformat()
        }).execute()
        return response.data
    except Exception as e:
        st.error(f"Error al agregar cliente: {e}")
        return None

# Función para actualizar cliente
def update_client(id, nombre, apellido, email, telefono):
    if not id:
        return None
    try:
        response = supabase.table("clientes").update({
            "nombres": nombre,
            "apellidos": apellido,
            "email": email,
            "telefono": telefono
        }).eq("id", id).execute()
        return response.data
    except Exception as e:
        st.error(f"Error al actualizar cliente: {e}")
        return None

# Función para eliminar cliente
def delete_client(id):
    if not id:
        return None
    try:
        response = supabase.table("clientes").delete().eq("id", id).execute()
        return response.data
    except Exception as e:
        st.error(f"Error al eliminar cliente: {e}")
        return None

# Interfaz de usuario
st.sidebar.header("Agregar Nuevo Cliente")
with st.sidebar.form(key="add_client_form"):
    nombre = st.text_input("Nombres")
    apellido = st.text_input("Apellidos")
    email = st.text_input("Email")
    telefono = st.text_input("Teléfono")
    submit = st.form_submit_button("Agregar Cliente")
    if submit:
        result = add_client(nombre, apellido, email, telefono)
        if result:
            st.success("Cliente agregado exitosamente!")
            st.experimental_rerun()
        else:
            st.error("Todos los campos son obligatorios o hubo un error!")

# Paginación
limit = 5
if "offset" not in st.session_state:
    st.session_state.offset = 0

clients = get_clients(limit, st.session_state.offset)

data = pd.DataFrame(clients, columns=["id", "nombres", "apellidos", "email", "telefono", "fecha_registro"])
if not data.empty:
    st.dataframe(data, width=800)
else:
    st.info("No hay clientes registrados o hubo un error en la consulta.")

col1, col2 = st.columns(2)
if col1.button("Anterior"):
    if st.session_state.offset > 0:
        st.session_state.offset -= limit
        st.experimental_rerun()
if col2.button("Siguiente"):
    st.session_state.offset += limit
    st.experimental_rerun()

# Edición de cliente
st.header("Editar Cliente")
id_edit = st.number_input("ID del cliente a editar", min_value=1, step=1)
if st.button("Cargar Cliente"):
    client_data = get_clients(1, id_edit - 1)
    if client_data:
        client = client_data[0]
        nombre_edit = st.text_input("Nombres", value=client.get("nombres", ""))
        apellido_edit = st.text_input("Apellidos", value=client.get("apellidos", ""))
        email_edit = st.text_input("Email", value=client.get("email", ""))
        telefono_edit = st.text_input("Teléfono", value=client.get("telefono", ""))
        if st.button("Actualizar Cliente"):
            update_result = update_client(id_edit, nombre_edit, apellido_edit, email_edit, telefono_edit)
            if update_result:
                st.success("Cliente actualizado exitosamente!")
                st.experimental_rerun()
            else:
                st.error("Error al actualizar el cliente.")
    else:
        st.error("Cliente no encontrado!")

# Eliminación de cliente
st.header("Eliminar Cliente")
id_delete = st.number_input("ID del cliente a eliminar", min_value=1, step=1)
if st.button("Eliminar Cliente"):
    delete_result = delete_client(id_delete)
    if delete_result:
        st.success("Cliente eliminado exitosamente!")
        st.experimental_rerun()
    else:
        st.error("Error al eliminar el cliente o cliente no encontrado.")