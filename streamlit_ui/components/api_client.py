import requests
import streamlit as st
from typing import Dict, List, Optional, Any


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Realiza petición a la API con manejo de errores"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error de conexión: {e}")
            return {}
    
    # Users
    def get_users(self, page: int = 1, size: int = 50) -> Dict:
        return self._make_request("GET", f"/users/?page={page}&size={size}")
    
    def create_user(self, user_data: Dict) -> Dict:
        return self._make_request("POST", "/users/", json=user_data)
    
    # Volunteers
    def get_volunteers(self, page: int = 1, size: int = 50) -> Dict:
        return self._make_request("GET", f"/volunteers/?page={page}&size={size}")
    
    def get_volunteer(self, volunteer_id: int) -> Dict:
        return self._make_request("GET", f"/volunteers/{volunteer_id}")
    
    def update_volunteer(self, volunteer_id: int, data: Dict) -> Dict:
        return self._make_request("PUT", f"/volunteers/{volunteer_id}", json=data)
    
    def add_skill_to_volunteer(self, volunteer_id: int, skill_id: int) -> Dict:
        return self._make_request("POST", f"/volunteers/{volunteer_id}/skills/{skill_id}")
    
    def get_volunteer_skills(self, volunteer_id: int) -> Dict:
        return self._make_request("GET", f"/volunteers/{volunteer_id}/skills")
    
    # Projects
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

# Instancia global del cliente
api_client = APIClient()