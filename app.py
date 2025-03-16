import streamlit as st
from supabase import create_client, Client 
import pandas as pd

SUPABASE_URL = "https://mitsyxhkdjkjmgflpmvf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pdHN5eGhrZGpram1nZmxwbXZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDIxNTA1NTMsImV4cCI6MjA1NzcyNjU1M30.sapb_dB9eOClGRhJ20J4Ftka2GF2XLCf2JK19kecre8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Gestion de Clientes", layout="wide")


logo_path = "logo.png"
try:
    st.image(logo_path, width=200)
except Exception:
    st.warning("No se encontro el logo de la empresa o hubo un error al cargarlo.")

st.title("Sistema de Gestion de Clientes")


def get_clients():
    try:
        response = supabase.table("clientes").select("*").order("id", asc=True).execute()
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.error(f"Error al obtener clientes: {e}")
        return []

def restructure_ids():
    clients = get_clients()
    for index, client in enumerate(clients, start=1):
        supabase.table("clientes").update({"id": index}).eq("id", client["id"]).execute()

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

def delete_client(id):
    if not id:
        return None
    try:
        supabase.table("clientes").delete().eq("id", id).execute()
        restructure_ids()
        return True
    except Exception as e:
        st.error(f"Error al eliminar cliente: {e}")
        return None

clients = get_clients()

st.sidebar.header("Informacion General")
st.sidebar.write(f"Total de clientes registrados: {len(clients)}")

data = pd.DataFrame(clients, columns=["id", "nombres", "apellidos", "email", "telefono", "fecha_registro"])
st.dataframe(data, width=800)


st.sidebar.header("Agregar Nuevo Cliente")
with st.sidebar.form(key="add_client_form"):
    nombre = st.text_input("Nombres")
    apellido = st.text_input("Apellidos")
    email = st.text_input("Email")
    telefono = st.text_input("Telefono")
    submit = st.form_submit_button("Agregar Cliente")
    if submit:
        result = add_client(nombre, apellido, email, telefono)
        if result:
            st.success("Cliente agregado exitosamente!")
            st.rerun()
        else:
            st.error("Todos los campos son obligatorios o hubo un error!")

st.header("Eliminar Cliente")
id_delete = st.number_input("ID del cliente a eliminar", min_value=1, step=1)
if st.button("Eliminar Cliente"):
    delete_result = delete_client(id_delete)
    if delete_result:
        st.success("Cliente eliminado exitosamente y IDs reestructurados!")
        st.rerun()
    else:
        st.error("Error al eliminar el cliente o cliente no encontrado.")