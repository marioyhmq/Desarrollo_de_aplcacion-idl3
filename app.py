import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Configuración de Supabase
SUPABASE_URL = "https://mitsyxhkdjkjmgflpmvf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pdHN5eGhrZGpram1nZmxwbXZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIxNTA1NTMsImV4cCI6MjA1NzcyNjU1M30.sapb_dB9eOClGRhJ20J4Ftka2GF2XLCf2JK19kecre8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de la interfaz
st.set_page_config(page_title="Gestión de Usuarios", layout="wide")

# Cargar el logo de la empresa (Asegurar que el archivo existe)
logo_path = "logo.png"
try:
    st.image(logo_path, width=200)
except FileNotFoundError:
    st.warning("No se encontró el logo de la empresa.")

st.title("Sistema de Gestión de Usuarios")

# Función para obtener datos con paginación
def get_users(limit=10, offset=0):
    response = supabase.table("usuarios").select("*").range(offset, offset + limit - 1).execute()
    return response.data if response.data else []

# Función para agregar usuario
def add_user(nombre, apellido, email, telefono):
    if not (nombre and apellido and email and telefono):
        return None
    response = supabase.table("usuarios").insert({
        "nombres": nombre,
        "apellidos": apellido,
        "emails": email,
        "telefono": telefono,
        "fecha_registro": pd.Timestamp.now().isoformat()
    }).execute()
    return response.data

# Función para actualizar usuario
def update_user(id, nombre, apellido, email, telefono):
    if not id:
        return None
    response = supabase.table("usuarios").update({
        "nombres": nombre,
        "apellidos": apellido,
        "emails": email,
        "telefono": telefono
    }).eq("id", id).execute()
    return response.data

# Función para eliminar usuario
def delete_user(id):
    if not id:
        return None
    response = supabase.table("usuarios").delete().eq("id", id).execute()
    return response.data

# Interfaz de usuario
st.sidebar.header("Agregar Nuevo Usuario")
with st.sidebar.form(key="add_user_form"):
    nombre = st.text_input("Nombres")
    apellido = st.text_input("Apellidos")
    email = st.text_input("Email")
    telefono = st.text_input("Teléfono")
    submit = st.form_submit_button("Agregar Usuario")
    if submit:
        result = add_user(nombre, apellido, email, telefono)
        if result:
            st.success("Usuario agregado exitosamente!")
            st.experimental_rerun()
        else:
            st.error("Todos los campos son obligatorios!")

# Paginación
limit = 5
if "offset" not in st.session_state:
    st.session_state.offset = 0

users = get_users(limit, st.session_state.offset)

data = pd.DataFrame(users, columns=["id", "nombres", "apellidos", "emails", "telefono", "fecha_registro"])
if not data.empty:
    st.dataframe(data, width=800)
else:
    st.info("No hay usuarios registrados.")

col1, col2 = st.columns(2)
if col1.button("Anterior"):
    if st.session_state.offset > 0:
        st.session_state.offset -= limit
        st.experimental_rerun()
if col2.button("Siguiente"):
    st.session_state.offset += limit
    st.experimental_rerun()

# Edición de usuario
st.header("Editar Usuario")
id_edit = st.number_input("ID del usuario a editar", min_value=0, step=1)
if st.button("Cargar Usuario"):
    user_data = supabase.table("usuarios").select("*").eq("id", id_edit).execute().data
    if user_data:
        user = user_data[0]
        nombre_edit = st.text_input("Nombres", value=user.get("nombres", ""))
        apellido_edit = st.text_input("Apellidos", value=user.get("apellidos", ""))
        email_edit = st.text_input("Email", value=user.get("emails", ""))
        telefono_edit = st.text_input("Teléfono", value=user.get("telefono", ""))
        if st.button("Actualizar Usuario"):
            update_result = update_user(id_edit, nombre_edit, apellido_edit, email_edit, telefono_edit)
            if update_result:
                st.success("Usuario actualizado exitosamente!")
                st.experimental_rerun()
            else:
                st.error("Error al actualizar el usuario.")
    else:
        st.error("Usuario no encontrado!")

# Eliminación de usuario
st.header("Eliminar Usuario")
id_delete = st.number_input("ID del usuario a eliminar", min_value=0, step=1)
if st.button("Eliminar Usuario"):
    delete_result = delete_user(id_delete)
    if delete_result:
        st.success("Usuario eliminado exitosamente!")
        st.experimental_rerun()
    else:
        st.error("Error al eliminar el usuario.")