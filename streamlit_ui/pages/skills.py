import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth, require_admin
from components.tables import create_paginated_table, status_badge, format_date
from components.forms import skill_form
from typing import Dict, List, Any
import plotly.express as px

def show():
    """Página de gestión de skills (solo administradores)"""
    require_admin()
    
    st.markdown("# 🛠️ Gestión de Skills")
    
    # Manejar acciones
    handle_actions()
    
    # Filtros y búsqueda
    st.markdown("## 🔍 Filtros de Búsqueda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        usage_filter = st.selectbox(
            "Filtrar por Uso",
            options=["Todas", "En uso", "Sin uso"],
            key="skill_usage_filter"
        )
    
    with col2:
        search_term = st.text_input("🔍 Buscar skill", key="skill_search")
    
    # Acciones rápidas
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Nueva Skill", type="primary"):
            st.session_state.action = "create_skill"
            st.rerun()
    
    with col2:
        if st.button("📊 Estadísticas"):
            st.session_state.show_skill_stats = True
            st.rerun()
    
    with col3:
        if st.button("📥 Exportar"):
            st.info("Exportación en desarrollo...")
    
    # Mostrar estadísticas si se solicita
    if st.session_state.get('show_skill_stats'):
        show_skill_statistics()
        return
    
    # Crear nueva skill
    if st.session_state.get('action') == 'create_skill':
        show_create_skill()
        return
    
    # Editar skill
    if st.session_state.get('edit_skill'):
        show_edit_skill()
        return
    
    # Ver detalles de skill
    if st.session_state.get('selected_skill'):
        show_skill_details()
        return
    
    # Listado principal de skills
    show_skill_list(usage_filter, search_term)

def handle_actions():
    """Maneja acciones rápidas desde session state"""
    
    # Activar/Desactivar skill (si tuviera estado)
    if st.session_state.get('toggle_skill_status'):
        skill = st.session_state.get('toggle_skill_status')
        # Implementar lógica de toggle si es necesario
        st.session_state.toggle_skill_status = None
        st.rerun()

def show_create_skill():
    """Formulario para crear nueva skill"""
    st.markdown("## ➕ Crear Nueva Skill")
    
    skill_data = skill_form()
    
    if skill_data:
        try:
            created_skill = api_client.create_skill(skill_data)
            st.success("✅ Skill creada exitosamente")
            st.session_state.action = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al crear skill: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.action = None
        st.rerun()

def show_edit_skill():
    """Formulario para editar skill existente"""
    skill = st.session_state.get('edit_skill')
    
    st.markdown(f"## ✏️ Editar Skill: {skill.get('name', 'N/A')}")
    
    skill_data = skill_form(skill)
    
    if skill_data:
        try:
            api_client.update_skill(skill['id'], skill_data)
            st.success("✅ Skill actualizada exitosamente")
            st.session_state.edit_skill = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al actualizar skill: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.edit_skill = None
        st.rerun()

def show_skill_details():
    """Muestra detalles completos de una skill"""
    skill = st.session_state.get('selected_skill')
    
    st.markdown(f"## 🛠️ Detalles de Skill: {skill.get('name', 'N/A')}")
    
    # Información básica
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**🆔 ID:** {skill.get('id', 'N/A')}")
        st.write(f"**📅 Creada:** {format_date(skill.get('created_at'))}")
    
    with col2:
        st.write(f"**📝 Nombre:** {skill.get('name', 'N/A')}")
        st.write(f"**📅 Actualizada:** {format_date(skill.get('updated_at'))}")
    
    with col3:
        st.write(f"**🗑️ Eliminada:** {format_date(skill.get('deleted_at')) if skill.get('deleted_at') else 'Activa'}")
    
    # Estadísticas de uso
    st.markdown("### 📊 Estadísticas de Uso")
    
    try:
        # Obtener datos de uso
        volunteers_response = api_client.get_volunteers(size=1000)
        projects_response = api_client.get_projects(size=1000)
        
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        
        # Contar voluntarios con esta skill
        volunteers_with_skill = []
        for volunteer in volunteers:
            volunteer_skills = volunteer.get('skills', [])
            if any(s.get('id') == skill['id'] for s in volunteer_skills):
                volunteers_with_skill.append(volunteer)
        
        # Contar proyectos que requieren esta skill
        projects_with_skill = []
        for project in projects:
            project_skills = project.get('skills', [])
            if any(s.get('id') == skill['id'] for s in project_skills):
                projects_with_skill.append(project)
        
        # Mostrar estadísticas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👤 Voluntarios", len(volunteers_with_skill))
        
        with col2:
            st.metric("📋 Proyectos", len(projects_with_skill))
        
        with col3:
            # Proyectos activos que requieren esta skill
            active_projects = [
                p for p in projects_with_skill 
                if p.get('status') in ['not_assigned', 'assigned']
            ]
            st.metric("🔄 Proyectos Activos", len(active_projects))
        
        with col4:
            # Proyectos completados con esta skill
            completed_projects = [
                p for p in projects_with_skill 
                if p.get('status') == 'completed'
            ]
            st.metric("✅ Proyectos Completados", len(completed_projects))
        
        # Listados detallados
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"👤 Voluntarios con '{skill.get('name')}' ({len(volunteers_with_skill)})")
            
            if volunteers_with_skill:
                for volunteer in volunteers_with_skill[:10]:  # Mostrar solo primeros 10
                    st.write(f"• {volunteer.get('name', 'N/A')} ({volunteer.get('email', 'N/A')})")
                
                if len(volunteers_with_skill) > 10:
                    st.write(f"... y {len(volunteers_with_skill) - 10} más")
            else:
                st.info("Ningún voluntario tiene esta skill")
        
        with col2:
            st.subheader(f"📋 Proyectos que requieren '{skill.get('name')}' ({len(projects_with_skill)})")
            
            if projects_with_skill:
                for project in projects_with_skill[:10]:  # Mostrar solo primeros 10
                    st.write(f"• {project.get('name', 'N/A')} - {status_badge(project.get('status'))}")
                
                if len(projects_with_skill) > 10:
                    st.write(f"... y {len(projects_with_skill) - 10} más")
            else:
                st.info("Ningún proyecto requiere esta skill")
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    # Acciones
    st.markdown("### ⚡ Acciones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✏️ Editar Skill"):
            st.session_state.edit_skill = skill
            st.session_state.selected_skill = None
            st.rerun()
    
    with col2:
        if st.button("👥 Ver Voluntarios"):
            st.session_state.show_skill_volunteers = skill
            st.session_state.selected_skill = None
            st.rerun()
    
    with col3:
        if st.button("🔙 Volver al Listado"):
            st.session_state.selected_skill = None
            st.rerun()

def show_skill_statistics():
    """Muestra estadísticas generales de skills"""
    st.markdown("## 📊 Estadísticas de Skills")
    
    try:
        # Obtener todos los datos
        skills_response = api_client.get_skills(size=1000)
        volunteers_response = api_client.get_volunteers(size=1000)
        projects_response = api_client.get_projects(size=1000)
        
        skills = skills_response.get('items', [])
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        
        if not skills:
            st.info("No hay datos de skills para mostrar")
            return
        
        # KPIs generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_skills = len(skills)
            st.metric("🛠️ Total Skills", total_skills)
        
        with col2:
            # Skills usadas por al menos un voluntario
            used_skills = set()
            for volunteer in volunteers:
                for skill in volunteer.get('skills', []):
                    used_skills.add(skill.get('id'))
            st.metric("✅ Skills en Uso", len(used_skills))
        
        with col3:
            # Skills sin uso
            unused_skills = len(skills) - len(used_skills)
            st.metric("❌ Skills sin Uso", unused_skills)
        
        with col4:
            # Skill más popular
            skill_counts = {}
            for volunteer in volunteers:
                for skill in volunteer.get('skills', []):
                    skill_name = skill.get('name', 'Unknown')
                    skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
            
            if skill_counts:
                most_popular = max(skill_counts, key=skill_counts.get)
                st.metric("🔥 Skill Más Popular", most_popular[:15])  # Limitar longitud
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Top 10 Skills Más Populares")
            
            if skill_counts:
                # Ordenar y tomar top 10
                top_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10])
                
                fig = px.bar(
                    x=list(top_skills.values()),
                    y=list(top_skills.keys()),
                    orientation='h',
                    title="Skills Más Usadas por Voluntarios"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📋 Skills en Proyectos")
            
            project_skill_counts = {}
            for project in projects:
                for skill in project.get('skills', []):
                    skill_name = skill.get('name', 'Unknown')
                    project_skill_counts[skill_name] = project_skill_counts.get(skill_name, 0) + 1
            
            if project_skill_counts:
                # Ordenar y tomar top 10
                top_project_skills = dict(sorted(project_skill_counts.items(), key=lambda x: x[1], reverse=True)[:10])
                
                fig = px.pie(
                    values=list(top_project_skills.values()),
                    names=list(top_project_skills.keys()),
                    title="Skills Más Requeridas en Proyectos"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de eficiencia
        st.subheader("📊 Eficiencia de Skills")
        
        skill_efficiency = []
        for skill in skills:
            skill_id = skill['id']
            skill_name = skill['name']
            
            # Contar voluntarios con esta skill
            volunteer_count = len([
                v for v in volunteers 
                if any(s.get('id') == skill_id for s in v.get('skills', []))
            ])
            
            # Contar proyectos que requieren esta skill
            project_count = len([
                p for p in projects 
                if any(s.get('id') == skill_id for s in p.get('skills', []))
            ])
            
            # Contar proyectos completados con esta skill
            completed_count = len([
                p for p in projects 
                if p.get('status') == 'completed' and
                   any(s.get('id') == skill_id for s in p.get('skills', []))
            ])
            
            # Calcular eficiencia (proyectos completados / proyectos totales que requieren la skill)
            efficiency = (completed_count / project_count * 100) if project_count > 0 else 0
            
            skill_efficiency.append({
                'Skill': skill_name,
                'Voluntarios': volunteer_count,
                'Proyectos': project_count,
                'Completados': completed_count,
                'Eficiencia (%)': f"{efficiency:.1f}%"
            })
        
        # Ordenar por eficiencia
        skill_efficiency.sort(key=lambda x: float(x['Eficiencia (%)'].rstrip('%')), reverse=True)
        
        st.dataframe(skill_efficiency, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    if st.button("🔙 Volver"):
        st.session_state.show_skill_stats = None
        st.rerun()

def show_skill_list(usage_filter: str, search_term: str):
    """Muestra listado filtrado de skills"""
    try:
        skills_response = api_client.get_skills(size=1000)
        skills = skills_response.get('items', [])
        
        # Obtener datos de uso
        volunteers_response = api_client.get_volunteers(size=1000)
        projects_response = api_client.get_projects(size=1000)
        
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        
        # Preparar lista enriquecida con datos de uso
        enriched_skills = []
        for skill in skills:
            skill_id = skill['id']
            
            # Contar voluntarios con esta skill
            volunteer_count = len([
                v for v in volunteers 
                if any(s.get('id') == skill_id for s in v.get('skills', []))
            ])
            
            # Contar proyectos que requieren esta skill
            project_count = len([
                p for p in projects 
                if any(s.get('id') == skill_id for s in p.get('skills', []))
            ])
            
            enriched_skills.append({
                **skill,
                'volunteer_count': volunteer_count,
                'project_count': project_count,
                'in_use': volunteer_count > 0 or project_count > 0
            })
        
        # Aplicar filtros
        filtered_skills = enriched_skills
        
        # Filtro por uso
        if usage_filter == "En uso":
            filtered_skills = [s for s in filtered_skills if s['in_use']]
        elif usage_filter == "Sin uso":
            filtered_skills = [s for s in filtered_skills if not s['in_use']]
        
        # Filtro por búsqueda
        if search_term:
            filtered_skills = [
                s for s in filtered_skills 
                if search_term.lower() in s.get('name', '').lower()
            ]
        
        # Mostrar resultados
        if filtered_skills:
            st.write(f"**Resultados encontrados:** {len(filtered_skills)}")
            
            for skill in filtered_skills:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**🛠️ {skill.get('name', 'N/A')}**")
                        st.write(f"📅 Creada: {format_date(skill.get('created_at'))}")
                    
                    with col2:
                        st.write(f"👤 {skill['volunteer_count']} voluntarios")
                        st.write(f"📋 {skill['project_count']} proyectos")
                        
                        if not skill['in_use']:
                            st.write("❌ No está en uso")
                    
                    with col3:
                        if st.button("Ver", key=f"view_{skill['id']}"):
                            st.session_state.selected_skill = skill
                            st.rerun()
                        if st.button("Editar", key=f"edit_{skill['id']}"):
                            st.session_state.edit_skill = skill
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No se encontraron skills con los filtros seleccionados")
    
    except Exception as e:
        st.error(f"Error al cargar skills: {e}")