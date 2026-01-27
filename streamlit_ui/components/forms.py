import streamlit as st
from typing import Dict, List, Any, Optional
from components.api_client import api_client
from datetime import datetime, date

def user_form(user_data: Optional[Dict] = None) -> Dict:
    """Formulario para crear/editar usuarios"""
    
    with st.form("user_form"):
        st.subheader("📝 Información de Usuario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nombre Completo *", 
                value=user_data.get('name', '') if user_data else '',
                key="user_name"
            )
            email = st.text_input(
                "Email *", 
                value=user_data.get('email', '') if user_data else '',
                key="user_email"
            )
        
        with col2:
            phone = st.text_input(
                "Teléfono", 
                value=user_data.get('phone', '') if user_data else '',
                key="user_phone"
            )
            birth_date = st.date_input(
                "Fecha de Nacimiento",
                value=datetime.strptime(user_data.get('birth_date', '2000-01-01'), 
                                      '%Y-%m-%d').date() if user_data and user_data.get('birth_date') else date(2000, 1, 1),
                key="user_birth_date"
            )
        
        # Password (solo para nuevos usuarios)
        if not user_data:
            password = st.text_input("Contraseña *", type="password", key="user_password")
            confirm_password = st.text_input("Confirmar Contraseña *", type="password", key="user_confirm_password")
            
            if password and password != confirm_password:
                st.error("Las contraseñas no coinciden")
        
        # Role selection
        roles_response = api_client.get_roles()
        roles = roles_response.get('items', []) if isinstance(roles_response, dict) else []
        
        if roles:
            role_options = {role['name']: role['id'] for role in roles}
            selected_role_name = st.selectbox(
                "Rol *",
                options=list(role_options.keys()),
                index=0,  # Default primer rol
                key="user_role"
            )
            selected_role_id = role_options[selected_role_name]
        else:
            st.error("No hay roles disponibles. Contacte al administrador.")
            return None
        
        submitted = st.form_submit_button("💾 Guardar Usuario", type="primary")
        
        if submitted:
            form_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'birth_date': birth_date.isoformat(),
                'role_id': selected_role_id
            }
            
            if not user_data and password:
                form_data['password'] = password
            
            return form_data
        
        return None

def volunteer_form(volunteer_data: Optional[Dict] = None) -> Dict:
    """Formulario para crear/editar voluntarios"""
    
    with st.form("volunteer_form"):
        st.subheader("🤝 Información de Voluntario")
        
        # User selection (si es creación)
        if not volunteer_data:
            users_response = api_client.get_users()
            users = users_response.get('items', []) if isinstance(users_response, dict) else []
            
            # Filtrar usuarios que no son voluntarios aún
            user_options = {f"{u['name']} ({u['email']})": u['id'] for u in users}
            
            selected_user = st.selectbox(
                "Seleccionar Usuario *",
                options=list(user_options.keys()),
                key="volunteer_user"
            )
        
        # Campos adicionales del voluntario
        col1, col2 = st.columns(2)
        
        with col1:
            availability = st.text_input(
                "Disponibilidad",
                value=volunteer_data.get('availability', '') if volunteer_data else '',
                key="volunteer_availability",
                help="Ej: Fin de semana, Tardes, etc."
            )
        
        with col2:
            experience = st.text_input(
                "Experiencia",
                value=volunteer_data.get('experience', '') if volunteer_data else '',
                key="volunteer_experience",
                help="Describe tu experiencia relevante"
            )
        
        motivation = st.text_area(
            "Motivación",
            value=volunteer_data.get('motivation', '') if volunteer_data else '',
            key="volunteer_motivation",
            help="¿Por qué quieres ser voluntario?"
        )
        
        # Status
        status_options = ["active", "inactive", "suspended"]
        status = st.selectbox(
            "Estado",
            options=status_options,
            index=status_options.index(volunteer_data.get('status', 'active')) if volunteer_data else 0,
            key="volunteer_status"
        )
        
        submitted = st.form_submit_button("💾 Guardar Voluntario", type="primary")
        
        if submitted:
            form_data = {
                'availability': availability,
                'experience': experience,
                'motivation': motivation,
                'status': status
            }
            
            if not volunteer_data:
                form_data['user_id'] = user_options[selected_user]
            
            return form_data
        
        return None

def project_form(project_data: Optional[Dict] = None) -> Dict:
    """Formulario para crear/editar proyectos"""
    
    with st.form("project_form"):
        st.subheader("📋 Información del Proyecto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nombre del Proyecto *",
                value=project_data.get('name', '') if project_data else '',
                key="project_name"
            )
            
            # Start date y end date en lugar de deadline
            start_date = st.date_input(
                "Fecha de Inicio *",
                value=datetime.strptime(project_data.get('start_date', '2024-01-01'), 
                                      '%Y-%m-%d').date() if project_data else date.today(),
                key="project_start_date"
            )
            
            end_date = st.date_input(
                "Fecha de Fin *",
                value=datetime.strptime(project_data.get('end_date', '2024-12-31'), 
                                      '%Y-%m-%d').date() if project_data else date.today(),
                key="project_end_date"
            )
            
            # Status
            status_options = ["planning", "in_progress", "completed", "cancelled"]
            status = st.selectbox(
                "Estado",
                options=status_options,
                index=status_options.index(project_data.get('status', 'planning')) if project_data else 0,
                key="project_status"
            )
        
        with col2:
            # Category
            categories_response = api_client.get_categories()
            categories = categories_response.get('items', []) if isinstance(categories_response, dict) else []
            
            if categories:
                category_options = {cat['name']: cat['id'] for cat in categories}
                selected_category_name = st.selectbox(
                    "Categoría *",
                    options=list(category_options.keys()),
                    index=0,
                    key="project_category"
                )
                category_id = category_options[selected_category_name]
            else:
                st.error("No hay categorías disponibles")
                return None
        
        description = st.text_area(
            "Descripción *",
            value=project_data.get('description', '') if project_data else '',
            key="project_description"
        )
        
        submitted = st.form_submit_button("💾 Guardar Proyecto", type="primary")
        
        if submitted:
            form_data = {
                'name': name,
                'description': description,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'status': status,
                'category_id': category_id
            }
            
            return form_data
        
        return None

def skill_form(skill_data: Optional[Dict] = None) -> Dict:
    """Formulario para crear/editar skills"""
    
    with st.form("skill_form"):
        st.subheader("🛠️ Información de Skill")
        
        name = st.text_input(
            "Nombre de la Skill *",
            value=skill_data.get('name', '') if skill_data else '',
            key="skill_name"
        )
        
        submitted = st.form_submit_button("💾 Guardar Skill", type="primary")
        
        if submitted:
            return {'name': name}
        
        return None

def category_form(category_data: Optional[Dict] = None) -> Dict:
    """Formulario para crear/editar categorías"""
    
    with st.form("category_form"):
        st.subheader("📂 Información de Categoría")
        
        name = st.text_input(
            "Nombre de Categoría *",
            value=category_data.get('name', '') if category_data else '',
            key="category_name"
        )
        
        description = st.text_area(
            "Descripción",
            value=category_data.get('description', '') if category_data else '',
            key="category_description"
        )
        
        submitted = st.form_submit_button("💾 Guardar Categoría", type="primary")
        
        if submitted:
            return {
                'name': name,
                'description': description
            }
        
        return None