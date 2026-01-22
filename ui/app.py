import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Plataforma ONG")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------ Registro ------------------
if choice == "Register":
    st.subheader("Registro de nuevo voluntario")

    name = st.text_input("Nombre")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")

    if st.button("Registrarse"):
        data = {
            "name": name,
            "email": email,
            "password": password
        }

        response = requests.post(f"{API_URL}/auth/register", json=data)

        if response.status_code == 200:
            st.success("Usuario registrado correctamente. Ahora puedes iniciar sesión.")
        else:
            st.error(response.json().get("detail", "Error en el registro"))


# ------------------ Login ------------------
if choice == "Login":
    st.subheader("Iniciar sesión")

    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")

    if st.button("Login"):
        data = {
            "email": email,
            "password": password
        }

        response = requests.post(f"{API_URL}/auth/login", json=data)

        if response.status_code == 200:
            result = response.json()

            # Guardar token en sesión
            st.session_state.token = result["access_token"]

            st.success("Login exitoso")
        else:
            st.error(response.json().get("detail", "Credenciales inválidas"))
