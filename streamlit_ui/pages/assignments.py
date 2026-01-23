import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth
from components.tables import create_paginated_table, assignment_table, status_badge, format_date
from typing import Dict, List, Any
import plotly.express as px

def show():
    """Página de gestión de asignaciones"""
    require_auth()
    
    user = auth.get_current_user()
    is_admin = auth.is_admin()
    
    if is_admin:
        st.markdown("# 📊 Gestión de Asignaciones")
        show_admin_assignments()
    else:
        st.markdown("# 📋 Mis Asignaciones")
        show_volunteer_assignments(user)

def show_admin_assignments():
    """Vista de administrador para todas las asignaciones"""
    # Filtros
    st.markdown("## 🔍 Filtros de Búsqueda")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Estado",
            options=["Todas", "pending", "accepted", "rejected", "completed"],
            key="assignment_status_filter"
        )
    
    with col2:
        project_filter = st.selectbox(
            "Proyecto",
            options=["Todos"],
            key="assignment_project_filter"
        )
        
        # Obtener proyectos
        try:
            projects_response = api_client.get_projects(size=1000)
            projects = projects_response.get('items', [])
            project_names = ["Todos"] + [p.get('name', '') for p in projects]
            project_filter = st.selectbox(
                "Proyecto",
                options=project_names,
                index=0,
                key="assignment_project_filter"
            )
        except:
            pass
    
    with col3:
        volunteer_filter = st.selectbox(
            "Voluntario",
            options=["Todos"],
            key="assignment_volunteer_filter"
        )
        
        # Obtener voluntarios
        try:
            volunteers_response = api_client.get_volunteers(size=1000)
            volunteers = volunteers_response.get('items', [])
            volunteer_names = ["Todos"] + [v.get('name', '') for v in volunteers]
            volunteer_filter = st.selectbox(
                "Voluntario",
                options=volunteer_names,
                index=0,
                key="assignment_volunteer_filter"
            )
        except:
            pass
    
    with col4:
        search_term = st.text_input("🔍 Buscar asignación", key="assignment_search")
    
    # Acciones rápidas
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Nueva Asignación", type="primary"):
            st.session_state.action = "create_assignment"
            st.rerun()
    
    with col2:
        if st.button("📊 Estadísticas"):
            st.session_state.show_assignment_stats = True
            st.rerun()
    
    with col3:
        if st.button("🔄 Procesar Pendientes"):
            st.session_state.process_pending = True
            st.rerun()
    
    with col4:
        if st.button("📥 Exportar"):
            st.info("Exportación en desarrollo...")
    
    # Mostrar vistas especiales
    if st.session_state.get('show_assignment_stats'):
        show_assignment_statistics()
        return
    
    if st.session_state.get('action') == 'create_assignment':
        show_create_assignment()
        return
    
    if st.session_state.get('process_pending'):
        show_pending_assignments()
        return
    
    # Listado principal de asignaciones
    show_assignment_list(status_filter, project_filter, volunteer_filter, search_term)

def show_volunteer_assignments(user: Dict):
    """Vista de voluntario para sus asignaciones"""
    # Obtener voluntario actual
    volunteers_response = api_client.get_volunteers(size=1000)
    volunteers = volunteers_response.get('items', [])
    
    my_volunteer = None
    for volunteer in volunteers:
        if volunteer.get('user_id') == user['id']:
            my_volunteer = volunteer
            break
    
    if not my_volunteer:
        st.warning("No se encontró tu perfil de voluntario")
        return
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Mis Asignaciones", "📊 Mi Progreso", "🎯 Disponibles"])
    
    with tab1:
        show_my_assignments(my_volunteer)
    
    with tab2:
        show_assignment_progress(my_volunteer)
    
    with tab3:
        show_available_assignments(my_volunteer)

def show_my_assignments(volunteer: Dict):
    """Muestra asignaciones del voluntario actual"""
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response.get('items', [])
        
        if assignments:
            for assignment in assignments:
                project = assignment.get('project', {})
                skill = assignment.get('skill', {})
                
                with st.expander(f"📋 {project.get('name', 'N/A')}"):
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:150]}...")
                    st.write(f"**🛠️ Mi Rol:** {skill.get('name', 'N/A')}")
                    st.write(f"**📅 Límite:** {format_date(project.get('deadline'))}")
                    st.write(f"**🎯 Estado:** {status_badge(assignment.get('status'))}")
                    st.write(f"**📅 Asignado:** {format_date(assignment.get('created_at'))}")
                    
                    # Acciones según estado
                    status = assignment.get('status')
                    if status == 'pending':
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Aceptar", key=f"accept_{assignment['id']}"):
                                api_client.update_assignment_status(assignment['id'], 'accepted')
                                st.success("¡Asignación aceptada!")
                                st.rerun()
                        with col2:
                            if st.button("❌ Rechazar", key=f"reject_{assignment['id']}"):
                                api_client.update_assignment_status(assignment['id'], 'rejected')
                                st.success("Asignación rechazada")
                                st.rerun()
                    elif status == 'accepted':
                        if st.button("✅ Marcar Completado", key=f"complete_{assignment['id']}"):
                            api_client.update_assignment_status(assignment['id'], 'completed')
                            st.success("¡Asignación completada! 🎉")
                            st.rerun()
        else:
            st.info("No tienes asignaciones actualmente")
    
    except Exception as e:
        st.error(f"Error al cargar tus asignaciones: {e}")

def show_assignment_progress(volunteer: Dict):
    """Muestra progreso y estadísticas del voluntario"""
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response.get('items', [])
        
        if not assignments:
            st.info("No hay asignaciones para mostrar estadísticas")
            return
        
        # Estadísticas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_assignments = len(assignments)
            st.metric("📋 Total Asignaciones", total_assignments)
        
        with col2:
            completed = len([a for a in assignments if a.get('status') == 'completed'])
            st.metric("✅ Completadas", completed)
        
        with col3:
            pending = len([a for a in assignments if a.get('status') == 'pending'])
            st.metric("⏳ Pendientes", pending)
        
        with col4:
            active = len([a for a in assignments if a.get('status') == 'accepted'])
            st.metric("🔄 Activas", active)
        
        # Gráfico de progreso
        st.subheader("📈 Distribución de Asignaciones")
        
        status_counts = {}
        for assignment in assignments:
            status = assignment.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Estado de tus Asignaciones"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Skills más usadas
        st.subheader("🛠️ Skills Más Usadas")
        
        skill_counts = {}
        for assignment in assignments:
            skill_name = assignment.get('skill', {}).get('name', 'Unknown')
            skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
        
        if skill_counts:
            fig = px.bar(
                x=list(skill_counts.values()),
                y=list(skill_counts.keys()),
                orientation='h',
                title="Frecuencia de Skills"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")

def show_available_assignments(volunteer: Dict):
    """Muestra asignaciones disponibles para el voluntario"""
    st.info("🔍 Buscando proyectos que matchean tus skills...")
    
    try:
        # Obtener skills del voluntario
        my_skills = volunteer.get('skills', [])
        if not my_skills:
            st.warning("No tienes skills registradas. Añade skills para ver asignaciones disponibles.")
            return
        
        # Obtener todos los proyectos activos
        projects_response = api_client.get_projects(size=1000)
        projects = projects_response.get('items', [])
        
        # Buscar asignaciones potenciales
        available_assignments = []
        my_skill_ids = [s['id'] for s in my_skills]
        
        for project in projects:
            if project.get('status') in ['not_assigned', 'assigned']:
                project_skills = project.get('skills', [])
                
                for project_skill in project_skills:
                    # Si el proyecto requiere una de mis skills
                    if project_skill['id'] in my_skill_ids:
                        # Verificar si ya tengo una asignación para este skill en este proyecto
                        # (Esto requeriría lógica adicional)
                        
                        available_assignments.append({
                            'project': project,
                            'skill': project_skill,
                            'project_skill_match': True
                        })
        
        if available_assignments:
            st.write(f"**Se encontraron {len(available_assignments)} oportunidades:**")
            
            for assignment in available_assignments:
                project = assignment['project']
                skill = assignment['skill']
                
                with st.expander(f"📋 {project.get('name', 'N/A')} - {skill.get('name', 'N/A')}"):
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:150]}...")
                    st.write(f"**🛠️ Skill Requerida:** {skill.get('name', 'N/A')}")
                    st.write(f"**📅 Límite:** {format_date(project.get('deadline'))}")
                    st.write(f"**🎯 Estado:** {status_badge(project.get('status'))}")
                    
                    if st.button("🤝 Solicitar Asignación", key=f"request_{project['id']}_{skill['id']}"):
                        # Crear solicitud de asignación
                        assignment_data = {
                            'project_skill_id': f"{project['id']}_{skill['id']}",  # Formato假设
                            'volunteer_skill_id': f"{volunteer['id']}_{skill['id']}",    # Formato假设
                            'status': 'pending'
                        }
                        
                        try:
                            api_client.create_assignment(assignment_data)
                            st.success("¡Solicitud enviada! El administrador la revisará pronto.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al crear solicitud: {e}")
        else:
            st.info("No hay nuevas asignaciones disponibles para tus skills en este momento")
    
    except Exception as e:
        st.error(f"Error al buscar asignaciones disponibles: {e}")

def show_create_assignment():
    """Formulario para crear nueva asignación manualmente"""
    st.markdown("## ➕ Crear Nueva Asignación")
    
    try:
        # Obtener datos necesarios
        volunteers_response = api_client.get_volunteers(size=1000)
        projects_response = api_client.get_projects(size=1000)
        
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        
        with st.form("create_assignment_form"):
            st.subheader("📋 Información de Asignación")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleccionar voluntario
                volunteer_options = {f"{v.get('name', '')} ({v.get('email', '')})": v['id'] for v in volunteers}
                selected_volunteer_name = st.selectbox(
                    "Voluntario *",
                    options=list(volunteer_options.keys())
                )
                
                # Seleccionar proyecto
                project_options = {p.get('name', ''): p['id'] for p in projects}
                selected_project_name = st.selectbox(
                    "Proyecto *",
                    options=list(project_options.keys())
                )
            
            with col2:
                # Obtener skills del proyecto seleccionado
                selected_project = next(
                    (p for p in projects if p['id'] == project_options[selected_project_name]), 
                    None
                )
                
                if selected_project:
                    project_skills = selected_project.get('skills', [])
                    if project_skills:
                        skill_options = {s.get('name', ''): s['id'] for s in project_skills}
                        selected_skill_name = st.selectbox(
                            "Skill Requerida *",
                            options=list(skill_options.keys())
                        )
                    else:
                        st.warning("El proyecto seleccionado no tiene skills requeridas")
                        selected_skill_name = None
                else:
                    selected_skill_name = None
                
                # Estado inicial
                status_options = ["pending", "accepted"]
                initial_status = st.selectbox(
                    "Estado Inicial",
                    options=status_options,
                    index=0
                )
            
            submitted = st.form_submit_button("💾 Crear Asignación", type="primary")
            
            if submitted and selected_skill_name:
                try:
                    assignment_data = {
                        'project_skill_id': f"{project_options[selected_project_name]}_{skill_options[selected_skill_name]}",
                        'volunteer_skill_id': f"{volunteer_options[selected_volunteer_name]}_{skill_options[selected_skill_name]}",
                        'status': initial_status
                    }
                    
                    api_client.create_assignment(assignment_data)
                    st.success("✅ Asignación creada exitosamente")
                    st.session_state.action = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al crear asignación: {e}")
    
    except Exception as e:
        st.error(f"Error al cargar datos para crear asignación: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.action = None
        st.rerun()

def show_pending_assignments():
    """Muestra y permite procesar asignaciones pendientes"""
    st.markdown("## ⏳ Procesar Asignaciones Pendientes")
    
    try:
        # Obtener todas las asignaciones pendientes
        # (Esto requeriría un endpoint específico o filtrar todas las asignaciones)
        
        # Por ahora, simulo el proceso
        st.info("📝 Buscando asignaciones pendientes...")
        
        # Simulación - en realidad necesitarías un endpoint para obtener todas las asignaciones
        st.warning("Esta funcionalidad requiere un endpoint para obtener todas las asignaciones pendientes")
        
        # Ejemplo de cómo se vería el procesamiento:
        with st.expander("📋 Ejemplo: Asignación Pendiente"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write("**Proyecto:** Ejemplo Proyecto")
                st.write("**Voluntario:** Juan Pérez")
                st.write("**Skill:** Python")
                st.write("**Fecha:** 2024-01-20")
            
            with col2:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅", key="example_accept"):
                        st.success("Aceptado")
                with col_btn2:
                    if st.button("❌", key="example_reject"):
                        st.error("Rechazado")
    
    except Exception as e:
        st.error(f"Error al procesar asignaciones pendientes: {e}")
    
    if st.button("🔙 Volver al Listado"):
        st.session_state.process_pending = None
        st.rerun()

def show_assignment_statistics():
    """Muestra estadísticas generales de asignaciones"""
    st.markdown("## 📊 Estadísticas de Asignaciones")
    
    try:
        # Simulación - necesitarías endpoints reales para obtener estadísticas
        st.info("📊 Cargando estadísticas de asignaciones...")
        
        # KPIs simulados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Asignaciones", "156")
        
        with col2:
            st.metric("✅ Completadas", "89")
        
        with col3:
            st.metric("⏳ Pendientes", "34")
        
        with col4:
            st.metric("🔄 Activas", "33")
        
        # Gráficos simulados
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Tendencia Mensual")
            
            # Simulación de datos mensuales
            months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
            completed = [12, 15, 18, 22, 25, 23]
            pending = [5, 7, 6, 8, 9, 7]
            
            fig = px.line(
                x=months,
                y=[completed, pending],
                title="Evolución de Asignaciones"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🛠️ Asignaciones por Skill")
            
            skills_data = {
                'Python': 45,
                'JavaScript': 38,
                'Diseño': 28,
                'Marketing': 22,
                'Datos': 23
            }
            
            fig = px.bar(
                x=list(skills_data.values()),
                y=list(skills_data.keys()),
                orientation='h',
                title="Distribución por Skills"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    if st.button("🔙 Volver"):
        st.session_state.show_assignment_stats = None
        st.rerun()

def show_assignment_list(status_filter: str, project_filter: str, volunteer_filter: str, search_term: str):
    """Muestra listado filtrado de asignaciones"""
    try:
        # NOTA: Esta función requeriría un endpoint para obtener TODAS las asignaciones
        st.warning("📝 Esta funcionalidad requiere un endpoint para obtener todas las asignaciones con filtros")
        
        # Simulación de cómo se vería el listado
        st.info("Mostrando listado simulado de asignaciones...")
        
        # Ejemplo de tabla de asignaciones
        assignment_data = [
            {
                'ID': 1,
                'Proyecto': 'Website ONG',
                'Voluntario': 'María García',
                'Skill': 'Diseño UX',
                'Estado': 'accepted',
                'Fecha': '2024-01-15'
            },
            {
                'ID': 2,
                'Proyecto': 'App Móvil',
                'Voluntario': 'Juan López',
                'Skill': 'React Native',
                'Estado': 'pending',
                'Fecha': '2024-01-20'
            }
        ]
        
        for assignment in assignment_data:
            with st.expander(f"📋 {assignment['Proyecto']} - {assignment['Voluntario']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**👤 Voluntario:** {assignment['Voluntario']}")
                    st.write(f"**📋 Proyecto:** {assignment['Proyecto']}")
                
                with col2:
                    st.write(f"**🛠️ Skill:** {assignment['Skill']}")
                    st.write(f"**🎯 Estado:** {status_badge(assignment['Estado'])}")
                
                with col3:
                    st.write(f"**📅 Fecha:** {assignment['Fecha']}")
                    
                    if assignment['Estado'] == 'pending':
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("✅", key=f"accept_{assignment['ID']}"):
                                st.success("Aceptado")
                        with col_btn2:
                            if st.button("❌", key=f"reject_{assignment['ID']}"):
                                st.error("Rechazado")
    
    except Exception as e:
        st.error(f"Error al cargar asignaciones: {e}")