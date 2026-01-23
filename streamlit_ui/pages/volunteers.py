import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth, require_admin
from components.tables import create_paginated_table, volunteer_table, status_badge
from components.forms import user_form, volunteer_form
from typing import Dict, List, Any

def show():
    """Página de gestión de voluntarios (solo administradores)"""
    require_admin()
    
    st.markdown("# 👤 Gestión de Voluntarios")
    
    # Manejar acciones
    handle_actions()
    
    # Filtros y búsqueda
    st.markdown("## 🔍 Filtros de Búsqueda")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Estado",
            options=["Todos", "active", "inactive", "suspended"],
            key="volunteer_status_filter"
        )
    
    with col2:
        skill_filter = st.selectbox(
            "Filtrar por Skill",
            options=["Todas"],
            key="volunteer_skill_filter"
        )
        # Obtener skills disponibles
        try:
            skills_response = api_client.get_skills(size=1000)
            skills = skills_response.get('items', [])
            skill_names = ["Todas"] + [s.get('name', '') for s in skills]
            skill_filter = st.selectbox(
                "Filtrar por Skill",
                options=skill_names,
                index=0,
                key="volunteer_skill_filter"
            )
        except:
            pass
    
    with col3:
        search_term = st.text_input("🔍 Buscar por nombre o email", key="volunteer_search")
    
    # Acciones rápidas
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Nuevo Voluntario", type="primary"):
            st.session_state.action = "create_volunteer"
            st.rerun()
    
    with col2:
        if st.button("📊 Ver Estadísticas"):
            st.session_state.show_stats = True
            st.rerun()
    
    with col3:
        if st.button("📥 Exportar Datos"):
            # Lógica para exportar
            st.info("Exportación en desarrollo...")
    
    # Mostrar estadísticas si se solicita
    if st.session_state.get('show_stats'):
        show_statistics()
        return
    
    # Crear nuevo voluntario
    if st.session_state.get('action') == 'create_volunteer':
        show_create_volunteer()
        return
    
    # Editar voluntario
    if st.session_state.get('edit_volunteer'):
        show_edit_volunteer()
        return
    
    # Ver detalles de voluntario
    if st.session_state.get('selected_volunteer'):
        show_volunteer_details()
        return
    
    # Listado principal de voluntarios
    show_volunteer_list(status_filter, skill_filter, search_term)

def handle_actions():
    """Maneja acciones rápidas desde session state"""
    
    # Activar/Desactivar voluntario
    if st.session_state.get('toggle_volunteer_status'):
        volunteer = st.session_state.get('toggle_volunteer_status')
        new_status = 'inactive' if volunteer.get('status') == 'active' else 'active'
        
        try:
            api_client.update_volunteer(volunteer['id'], {'status': new_status})
            st.success(f"✅ Voluntario {'activado' if new_status == 'active' else 'desactivado'} exitosamente")
            st.session_state.toggle_volunteer_status = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al actualizar estado: {e}")

def show_statistics():
    """Muestra estadísticas de voluntarios"""
    st.markdown("## 📊 Estadísticas de Voluntarios")
    
    try:
        volunteers_response = api_client.get_volunteers(size=1000)
        volunteers = volunteers_response.get('items', [])
        
        if not volunteers:
            st.info("No hay datos de voluntarios para mostrar")
            return
        
        # KPIs generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_volunteers = len(volunteers)
            st.metric("👤 Total Voluntarios", total_volunteers)
        
        with col2:
            active_volunteers = len([v for v in volunteers if v.get('status') == 'active'])
            st.metric("✅ Voluntarios Activos", active_volunteers)
        
        with col3:
            inactive_volunteers = len([v for v in volunteers if v.get('status') == 'inactive'])
            st.metric("⏸️ Inactivos", inactive_volunteers)
        
        with col4:
            suspended_volunteers = len([v for v in volunteers if v.get('status') == 'suspended'])
            st.metric("🚫 Suspendidos", suspended_volunteers)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Distribución por Estado")
            import plotly.express as px
            
            status_counts = {}
            for volunteer in volunteers:
                status = volunteer.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="Voluntarios por Estado"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🛠️ Top Skills")
            
            skill_counts = {}
            for volunteer in volunteers:
                skills = volunteer.get('skills', [])
                for skill in skills:
                    skill_name = skill.get('name', 'Unknown')
                    skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
            
            if skill_counts:
                # Ordenar y tomar top 10
                top_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10])
                
                fig = px.bar(
                    x=list(top_skills.values()),
                    y=list(top_skills.keys()),
                    orientation='h',
                    title="Skills Más Comunes"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📋 Detalles por Voluntario")
        
        volunteer_details = []
        for volunteer in volunteers:
            skills = volunteer.get('skills', [])
            volunteer_details.append({
                'Nombre': volunteer.get('name', 'N/A'),
                'Email': volunteer.get('email', 'N/A'),
                'Estado': status_badge(volunteer.get('status')),
                'Skills Count': len(skills),
                'Skills': ', '.join([s.get('name', '') for s in skills[:3]]) + ('...' if len(skills) > 3 else '')
            })
        
        st.dataframe(volunteer_details, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    if st.button("🔙 Volver al Listado"):
        st.session_state.show_stats = False
        st.rerun()

def show_create_volunteer():
    """Formulario para crear nuevo voluntario"""
    st.markdown("## ➕ Crear Nuevo Voluntario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Paso 1: Crear Usuario")
        user_data = user_form()
        
        if user_data:
            try:
                # Crear usuario primero
                created_user = api_client.create_user(user_data)
                st.success("✅ Usuario creado exitosamente")
                st.session_state.created_user_id = created_user['id']
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al crear usuario: {e}")
    
    with col2:
        # Si ya se creó el usuario, mostrar formulario de voluntario
        if st.session_state.get('created_user_id'):
            st.subheader("🤝 Paso 2: Crear Perfil de Voluntario")
            
            volunteer_data = volunteer_form()
            if volunteer_data:
                try:
                    volunteer_data['user_id'] = st.session_state.created_user_id
                    created_volunteer = api_client.create_volunteer(volunteer_data)
                    st.success("✅ Voluntario creado exitosamente")
                    
                    # Limpiar session state
                    del st.session_state.created_user_id
                    st.session_state.action = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al crear voluntario: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.action = None
        if 'created_user_id' in st.session_state:
            del st.session_state.created_user_id
        st.rerun()

def show_edit_volunteer():
    """Formulario para editar voluntario existente"""
    volunteer = st.session_state.get('edit_volunteer')
    
    st.markdown(f"## ✏️ Editar Voluntario: {volunteer.get('name', 'N/A')}")
    
    # Formulario de edición de voluntario (solo estado)
    with st.form("edit_volunteer_form"):
        st.subheader("🤝 Información de Voluntario")
        
        status_options = ["active", "inactive", "suspended"]
        new_status = st.selectbox(
            "Estado",
            options=status_options,
            index=status_options.index(volunteer.get('status', 'active')),
            key="edit_volunteer_status"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
        
        with col2:
            cancelled = st.form_submit_button("🔙 Cancelar")
        
        if submitted:
            try:
                api_client.update_volunteer(volunteer['id'], {'status': new_status})
                st.success("✅ Voluntario actualizado exitosamente")
                st.session_state.edit_volunteer = None
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al actualizar voluntario: {e}")
        
        if cancelled:
            st.session_state.edit_volunteer = None
            st.rerun()

def show_volunteer_details():
    """Muestra detalles completos de un voluntario"""
    volunteer = st.session_state.get('selected_volunteer')
    
    st.markdown(f"## 👤 Detalles de Voluntario: {volunteer.get('name', 'N/A')}")
    
    # Información básica
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**📧 Email:** {volunteer.get('email', 'N/A')}")
        st.write(f"**📱 Teléfono:** {volunteer.get('phone', 'N/A')}")
    
    with col2:
        st.write(f"**🎯 Estado:** {status_badge(volunteer.get('status'))}")
        st.write(f"**📅 Nacimiento:** {volunteer.get('birth_date', 'N/A')}")
    
    with col3:
        st.write(f"**🆔 ID Usuario:** {volunteer.get('user_id', 'N/A')}")
        st.write(f"**🆔 ID Voluntario:** {volunteer.get('id', 'N/A')}")
    
    # Skills
    st.markdown("### 🛠️ Skills del Voluntario")
    
    skills = volunteer.get('skills', [])
    if skills:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            for skill in skills:
                st.write(f"• {skill.get('name', 'N/A')}")
        
        with col2:
            if st.button("➕ Añadir Skill"):
                st.session_state.add_skill_to_volunteer = volunteer['id']
                st.rerun()
    else:
        st.info("Este voluntario no tiene skills registradas")
        if st.button("➕ Añadir Primera Skill"):
            st.session_state.add_skill_to_volunteer = volunteer['id']
            st.rerun()
    
    # Asignaciones
    st.markdown("### 📋 Asignaciones del Voluntario")
    
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response.get('items', [])
        
        if assignments:
            for assignment in assignments:
                project = assignment.get('project', {})
                skill = assignment.get('skill', {})
                
                with st.expander(f"📋 {project.get('name', 'N/A')}"):
                    st.write(f"**🛠️ Skill:** {skill.get('name', 'N/A')}")
                    st.write(f"**🎯 Estado:** {status_badge(assignment.get('status'))}")
                    st.write(f"**📅 Asignado:** {assignment.get('created_at', 'N/A')}")
        else:
            st.info("Este voluntario no tiene asignaciones")
    
    except Exception as e:
        st.error(f"Error al cargar asignaciones: {e}")
    
    # Acciones
    st.markdown("### ⚡ Acciones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✏️ Editar Voluntario"):
            st.session_state.edit_volunteer = volunteer
            st.session_state.selected_volunteer = None
            st.rerun()
    
    with col2:
        new_status = 'inactive' if volunteer.get('status') == 'active' else 'active'
        status_action = 'Desactivar' if new_status == 'inactive' else 'Activar'
        if st.button(f"🔄 {status_action}"):
            st.session_state.toggle_volunteer_status = volunteer
            st.rerun()
    
    with col3:
        if st.button("🔙 Volver al Listado"):
            st.session_state.selected_volunteer = None
            st.rerun()

def show_volunteer_list(status_filter: str, skill_filter: str, search_term: str):
    """Muestra listado filtrado de voluntarios"""
    try:
        volunteers_response = api_client.get_volunteers(size=1000)
        volunteers = volunteers_response.get('items', [])
        
        # Aplicar filtros
        filtered_volunteers = volunteers
        
        # Filtro por estado
        if status_filter != "Todos":
            filtered_volunteers = [
                v for v in filtered_volunteers 
                if v.get('status') == status_filter
            ]
        
        # Filtro por skill
        if skill_filter != "Todas":
            filtered_volunteers = [
                v for v in filtered_volunteers 
                if any(s.get('name', '') == skill_filter for s in v.get('skills', []))
            ]
        
        # Filtro por búsqueda
        if search_term:
            filtered_volunteers = [
                v for v in filtered_volunteers 
                if search_term.lower() in v.get('name', '').lower() or
                   search_term.lower() in v.get('email', '').lower()
            ]
        
        # Mostrar resultados
        if filtered_volunteers:
            st.write(f"**Resultados encontrados:** {len(filtered_volunteers)}")
            volunteer_table(filtered_volunteers, show_actions=True)
        else:
            st.info("No se encontraron voluntarios con los filtros seleccionados")
    
    except Exception as e:
        st.error(f"Error al cargar voluntarios: {e}")