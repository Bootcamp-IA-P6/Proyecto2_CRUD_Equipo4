import streamlit as st
import requests
from typing import Optional, Dict, Any

class Authentication:
    def __init__(self):
        self.api_base_url = "http://localhost:8000"
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Autentica usuario y devuelve datos"""
        try:
            # Nota: Esto requiere que tu API tenga endpoint de login
            # Por ahora, simulamos búsqueda por email
            response = requests.get(f"{self.api_base_url}/users/")
            users = response.json().get("items", [])
            
            user = next((u for u in users if u["email"] == email), None)
            
            if user:
                # En un caso real, verificar password aquí
                return {
                    "id": user["id"],
                    "email": user["email"], 
                    "name": user["name"],
                    "role_id": user["role_id"],
                    "is_admin": user["role_id"] == 1  # Asumiendo admin=1
                }
            return None
        except Exception as e:
            st.error(f"Error de login: {e}")
            return None
    
    def logout(self):
        """Cierra sesión"""
        st.session_state.clear()
    
    def is_authenticated(self) -> bool:
        """Verifica si hay usuario autenticado"""
        return "user" in st.session_state
    
    def get_current_user(self) -> Optional[Dict]:
        """Obtiene usuario actual"""
        return st.session_state.get("user")
    
    def is_admin(self) -> bool:
        """Verifica si es administrador"""
        user = self.get_current_user()
        return user.get("is_admin", False) if user else False

auth = Authentication()


def require_auth():
    """Middleware que requiere autenticación"""
    if not auth.is_authenticated():
        st.error("Debes iniciar sesión para acceder a esta página")
        st.stop()

def require_admin():
    """Middleware que requiere rol de administrador"""
    if not auth.is_admin():
        st.error("Esta función solo está disponible para administradores")
        st.stop()
        
