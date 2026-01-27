import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

def create_paginated_table(
    data: List[Dict], 
    page_size: int = 20,
    key_prefix: str = "table"
):
    """Crea tabla con paginación y búsqueda"""
    
    # Búsqueda
    search_term = st.text_input("🔍 Buscar...", key=f"{key_prefix}_search")
    
    # Filtrar datos
    if search_term:
        filtered_data = [
            item for item in data 
            if search_term.lower() in str(item).lower()
        ]
    else:
        filtered_data = data
    
    # Paginación
    total_items = len(filtered_data)
    total_pages = (total_items + page_size - 1) // page_size
    
    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior", key=f"{key_prefix}_prev"):
                if f"{key_prefix}_page" in st.session_state:
                    st.session_state[f"{key_prefix}_page"] = max(1, st.session_state[f"{key_prefix}_page"] - 1)
                else:
                    st.session_state[f"{key_prefix}_page"] = 1
        
        with col2:
            current_page = st.session_state.get(f"{key_prefix}_page", 1)
            st.write(f"Página {current_page} de {total_pages}")
        
        with col3:
            if st.button("Siguiente ➡️", key=f"{key_prefix}_next"):
                if f"{key_prefix}_page" in st.session_state:
                    st.session_state[f"{key_prefix}_page"] = min(total_pages, st.session_state[f"{key_prefix}_page"] + 1)
                else:
                    st.session_state[f"{key_prefix}_page"] = 2
    
    current_page = st.session_state.get(f"{key_prefix}_page", 1)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_data = filtered_data[start_idx:end_idx]
    
    # Mostrar tabla
    if paginated_data:
        df = pd.DataFrame(paginated_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay datos para mostrar")
    
    return paginated_data

def format_date(date_str: str) -> str:
    """Formatea fecha para visualización"""
    if not date_str:
        return "N/A"
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%d/%m/%Y %H:%M")
    except:
        return date_str

def status_badge(status: str, status_colors: Dict[str, str] = None) -> str:
    """Crea badge de estado con colores"""
    default_colors = {
        "active": "🟢",
        "inactive": "🔴", 
        "suspended": "🟡",
        "pending": "⏳",
        "accepted": "✅",
        "rejected": "❌",
        "completed": "🎉",
        "not_assigned": "📋",
        "assigned": "👥",
        "high": "🔴",
        "medium": "🟡", 
        "low": "🟢"
    }
    
    colors = status_colors or default_colors
    icon = colors.get(status.lower(), "📌")
    return f"{icon} {status.title()}"

def volunteer_table(volunteers: List[Dict], show_actions: bool = True):
    """Tabla específica para voluntarios"""
    
    for volunteer in volunteers:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**👤 {volunteer.get('name', 'N/A')}**")
                st.write(f"📧 {volunteer.get('email', 'N/A')}")
                st.write(f"📱 {volunteer.get('phone', 'N/A')}")
            
            with col2:
                status = volunteer.get('status', 'inactive')
                st.write(status_badge(status))
                
                # Skills resumidas
                skills = volunteer.get('skills', [])
                if skills:
                    skill_names = [s.get('name', '') for s in skills[:3]]
                    st.write(f"🛠️ Skills: {', '.join(skill_names)}")
                    if len(skills) > 3:
                        st.write(f"... y {len(skills) - 3} más")
            
            with col3:
                if show_actions:
                    if st.button("Ver", key=f"view_{volunteer['id']}"):
                        st.session_state.selected_volunteer = volunteer
                        st.rerun()
                    if st.button("Editar", key=f"edit_{volunteer['id']}"):
                        st.session_state.edit_volunteer = volunteer
                        st.rerun()
            
            st.divider()

def project_table(projects: List[Dict], show_actions: bool = True):
    """Tabla específica para proyectos"""
    
    for project in projects:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**📋 {project.get('name', 'N/A')}**")
                st.write(f"📝 {project.get('description', 'N/A')[:100]}...")
                
                deadline = format_date(project.get('deadline'))
                st.write(f"📅 Límite: {deadline}")
            
            with col2:
                status = project.get('status', 'not_assigned')
                priority = project.get('priority', 'medium')
                st.write(status_badge(status))
                st.write(status_badge(priority))
                
                category = project.get('category', {}).get('name', 'N/A')
                st.write(f"📂 Categoría: {category}")
                
                # Skills requeridas
                skills = project.get('skills', [])
                if skills:
                    skill_names = [s.get('name', '') for s in skills[:2]]
                    st.write(f"🛠️ Requiere: {', '.join(skill_names)}")
            
            with col3:
                if show_actions:
                    if st.button("Ver", key=f"view_{project['id']}"):
                        st.session_state.selected_project = project
                        st.rerun()
                    if st.button("Editar", key=f"edit_{project['id']}"):
                        st.session_state.edit_project = project
                        st.rerun()
                    if st.button("Asignar", key=f"assign_{project['id']}"):
                        st.session_state.assign_project = project
                        st.rerun()
            
            st.divider()

def assignment_table(assignments: List[Dict], show_actions: bool = True):
    """Tabla específica para asignaciones"""
    
    for assignment in assignments:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                project = assignment.get('project', {})
                volunteer = assignment.get('volunteer', {})
                
                st.write(f"**📋 {project.get('name', 'N/A')}**")
                st.write(f"**👤 {volunteer.get('name', 'N/A')}**")
                
                created = format_date(assignment.get('created_at'))
                st.write(f"📅 Creado: {created}")
            
            with col2:
                status = assignment.get('status', 'pending')
                st.write(status_badge(status))
                
                skill = assignment.get('skill', {})
                st.write(f"🛠️ Skill: {skill.get('name', 'N/A')}")
                
                # Progress si aplica
                if status == 'accepted':
                    st.progress(0.5, "En progreso")
            
            with col3:
                if show_actions:
                    if status == 'pending':
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("✅", key=f"accept_{assignment['id']}"):
                                st.session_state.accept_assignment = assignment
                                st.rerun()
                        with col_btn2:
                            if st.button("❌", key=f"reject_{assignment['id']}"):
                                st.session_state.reject_assignment = assignment
                                st.rerun()
                    elif status == 'accepted':
                        if st.button("✅ Completar", key=f"complete_{assignment['id']}"):
                            st.session_state.complete_assignment = assignment
                            st.rerun()
            
            st.divider()