import requests
import streamlit as st
from typing import Dict, List, Optional, Any


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers con autenticación JWT"""
        headers = {"Content-Type": "application/json"}
        
        if st.session_state.get("token"):
            headers["Authorization"] = f"Bearer {st.session_state['token']}"
        
        return headers
    
    
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.base_url}{endpoint}"
        
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update(self._get_headers())
        
       
        response = requests.request(method, url, **kwargs)
        
        if response.status_code == 401:
            st.session_state.clear()

            return {"error": "unauthorized"}

        
        response.raise_for_status() 
        return response.json()
    
    # Autenticación
    def login(self, email: str, password: str) -> Dict:
        return self._make_request("POST", "/auth/login", json={"email": email, "password": password})
    
    def get_me(self) -> Dict:
        """Obtener usuario actual con manejo robusto"""
        try:
            response = self._make_request("GET", "/auth/me")
            
            if response and 'id' in response:
                # DEBUG: Log para depuración
                print(f"API_CLIENT get_me() SUCCESS: {response}")
                return response
            else:
                print(f"API_CLIENT get_me() INVALID RESPONSE: {response}")
                return {}
                
        except Exception as e:
            print(f"API_CLIENT get_me() ERROR: {e}")
            return {}
    
    # Users
    def get_users(self, page: int = 1, size: int = 50) -> Dict:
        return self._make_request("GET", f"/users/?page={page}&size={size}")
    
    def get_user(self, user_id: int) -> Dict:
        return self._make_request("GET", f"/users/{user_id}")
    
    def create_user(self, user_data: Dict) -> Dict:
        return self._make_request("POST", "/users/", json=user_data)
    
    def get_user_by_email(self, email: str) -> Dict:
        return self._make_request("GET", f"/users/email/{email}")
    
    # Volunteers
    def get_volunteers(self, page: int = 1, size: int = 50) -> Dict:
        return self._make_request("GET", f"/volunteers/?page={page}&size={size}")
    
    def get_volunteer(self, user_id: int) -> Dict:
        return self._make_request("GET", f"/volunteers/{user_id}")
    
    def create_volunteer(self, volunteer_data: Dict) -> Dict:
        return self._make_request("POST", "/volunteers/", json=volunteer_data)
    
    def update_volunteer(self, volunteer_id: int, data: Dict) -> Dict:
        return self._make_request("PUT", f"/volunteers/{volunteer_id}", json=data)
    
    def add_skill_to_volunteer(self, volunteer_id: int, skill_id: int) -> Dict:
        return self._make_request("POST", f"/volunteers/{volunteer_id}/skills/{skill_id}")
    
    def get_volunteer_skills(self, user_id: int) -> Dict:
        return self._make_request("GET", f"/volunteers/{user_id}/skills/")
    
    # Projects
    def get_project(self, project_id: int) -> Dict:
        return self._make_request("GET", f"/projects/{project_id}")

    def update_project(self, project_id: int, data: Dict) -> Dict:
        return self._make_request("PUT", f"/projects/{project_id}", json=data)
    
    def get_projects(self, page: int = 1, size: int = 50) -> Dict:
        return self._make_request("GET", f"/projects/?page={page}&size={size}")
    
    def create_project(self, project_data: Dict) -> Dict:
        return self._make_request("POST", "/projects/", json=project_data)
    
    def get_project_matching_volunteers(self, project_id: int) -> Dict:
        return self._make_request("GET", f"/projects/{project_id}/matching-volunteers")
    
    def add_skill_to_project(self, project_id: int, skill_id: int) -> Dict:
        return self._make_request("POST", f"/projects/{project_id}/skills/{skill_id}")
    
    # Skills
    def get_skills(self, page: int = 1, size: int = 50) -> Dict:
        return self._make_request("GET", f"/skills/?page={page}&size={size}")
    
    def create_skill(self, skill_data: Dict) -> Dict:
        return self._make_request("POST", "/skills/", json=skill_data)
    
    def update_skill(self, skill_id: int, data: Dict) -> Dict:
        return self._make_request("PUT", f"/skills/{skill_id}", json=data)
    
    # Categories
    def get_categories(self, page: int = 1, size: int = 50) -> Dict:
        return self._make_request("GET", f"/categories/?page={page}&size={size}")
    
    def create_category(self, category_data: Dict) -> Dict:
        return self._make_request("POST", "/categories/", json=category_data)
    
    # Assignments
    def get_volunteer_assignments(self, volunteer_id: int) -> Dict:
        return self._make_request("GET", f"/assignments/volunteer/{volunteer_id}")
    
    def get_project_assignments(self, project_id: int) -> Dict:
        return self._make_request("GET", f"/assignments/project/{project_id}")
    
    def create_assignment(self, assignment_data: Dict) -> Dict:
        return self._make_request("POST", "/assignments/", json=assignment_data)
    
    def update_assignment_status(self, assignment_id: int, status: str) -> Dict:
        return self._make_request("PATCH", f"/assignments/{assignment_id}/status", 
                                json={"status": status})
        
    #Roles
    def get_roles(self, page: int = 1, size: int = 50) -> Dict:
        """Obtener todos los roles disponibles"""
        return self._make_request("GET", f"/roles/?page={page}&size={size}")
    
    # Añadir método para obtener todas las asignaciones (solo admin)
    def get_all_assignments(self, page: int = 1, size: int = 50) -> Dict:
        """Obtener todas las asignaciones (solo admin)"""
        return self._make_request("GET", f"/assignments/all/?page={page}&size={size}")

    # Obtener información de project_skill específico
    def get_project_skill_details(self, project_id: int, skill_id: int) -> Dict:
        """Obtener detalles de project_skill (requerido para crear asignaciones)"""
        return self._make_request("GET", f"/projects/{project_id}/skills/{skill_id}")

    # Obtener información de volunteer_skill específico
    def get_volunteer_skill_details(self, volunteer_id: int, skill_id: int) -> Dict:
        """Obtener detalles de volunteer_skill (requerido para crear asignaciones)"""
        return self._make_request("GET", f"/volunteers/{volunteer_id}/skills/{skill_id}")

# Instancia global del cliente
api_client = APIClient()