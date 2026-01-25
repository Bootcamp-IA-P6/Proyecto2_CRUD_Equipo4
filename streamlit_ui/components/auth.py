import streamlit as st
import requests
from components.api_client import api_client
from typing import Optional, Dict, Any

class Authentication:
    def __init__(self):
        self.api_client = api_client
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Login usando api_client con manejo mejorado"""
        try:
            response = self.api_client.login(email, password)
            
            if response and 'access_token' in response:
                # Guardar token
                st.session_state.token = response['access_token']
                
                # Obtener datos del usuario INMEDIATAMENTE
                user_data = self.get_me()
                if user_data:
                    st.session_state.user = user_data
                    st.session_state.is_authenticated = True
                    st.success(f"¡Bienvenido {user_data['name']}!")
                    return user_data
            else:
                st.error("Credenciales incorrectas")
                return None
            
        except Exception as e:
            st.error(f"Error de login: {e}")
            return None
    
    def get_me(self) -> Optional[Dict]:
        """Obtener usuario actual usando api_client con mejor manejo"""
        if not st.session_state.get("token"):
            return None
            
        try:
            response = self.api_client.get_me()
            
            # DEBUG: Mostrar respuesta para depurar
            print(f"DEBUG - get_me() response: {response}")
            
            if response and 'id' in response:
                # Asegurarse que el role_id esté presente
                if 'role_id' not in response:
                    print("WARNING: role_id no encontrado en respuesta")
                    # Intentar obtener de otra forma o asignar valor por defecto
                    response['role_id'] = 2  # Default a voluntario por seguridad
                
                return response
            else:
                print("ERROR: Respuesta inválida de get_me()")
                return None
                
        except Exception as e:
            print(f"ERROR en get_me(): {e}")
            self.logout()
            return None
    
    def logout(self):
        """Cerrar sesión con LIMPIEZA TOTAL"""
    
        keys_to_clear = list(st.session_state.keys())
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()
    
    def is_authenticated(self) -> bool:
        """Verificar si hay sesión activa"""
        return st.session_state.get("is_authenticated", False) and st.session_state.get("user") is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """Obtener usuario actual de sesión"""
        return st.session_state.get("user")
    
    def is_admin(self) -> bool:
        """Verificar si el usuario es admin - CORREGIDO"""
        user = self.get_current_user()
        
        if not user:
            print("DEBUG: is_admin() - No hay usuario en sesión")
            return False
        
        role_id = user.get("role_id")
        is_admin = role_id == 1
        
        print(f"DEBUG: is_admin() - User: {user.get('name')}, role_id: {role_id}, is_admin: {is_admin}")
        
        return is_admin

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
