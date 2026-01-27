import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth, require_admin
from components.tables import create_paginated_table, status_badge, format_date
from components.forms import category_form
from typing import Dict, List, Any
import plotly.express as px

def show():
    """Página de gestión de categorías (solo administradores)"""
    require_admin()
    
    st.markdown("# 📂 Gestión de Categorías")
    
    # Manejar acciones
    handle_actions()
    
    # Filtros y búsqueda
    st.markdown("## 🔍 Filtros de Búsqueda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filtrar por Estado",
            options=["Todas", "Activas", "Eliminadas"],
            key="category_status_filter"
        )
    
    with col2:
        search_term = st.text_input("🔍 Buscar categoría", key="category_search")
    
    # Acciones rápidas
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Nueva Categoría", type="primary"):
            st.session_state.action = "create_category"
            st.rerun()
    
    with col2:
        if st.button("📊 Estadísticas"):
            st.session_state.show_category_stats = True
            st.rerun()
    
    with col3:
        if st.button("📥 Exportar"):
            st.info("Exportación en desarrollo...")
    
    # Mostrar estadísticas si se solicita
    if st.session_state.get('show_category_stats'):
        show_category_statistics()
        return
    
    # Crear nueva categoría
    if st.session_state.get('action') == 'create_category':
        show_create_category()
        return
    
    # Editar categoría
    if st.session_state.get('edit_category'):
        show_edit_category()
        return
    
    # Ver detalles de categoría
    if st.session_state.get('selected_category'):
        show_category_details()
        return
    
    # Listado principal de categorías
    show_category_list(status_filter, search_term)

def handle_actions():
    """Maneja acciones rápidas desde session state"""
    
    # Reactivar categoría eliminada
    if st.session_state.get('restore_category'):
        category = st.session_state.get('restore_category')
        try:
            # Lógica para restaurar (soft delete reverso)
            api_client.update_category(category['id'], {'deleted_at': None})
            st.success("✅ Categoría restaurada exitosamente")
            st.session_state.restore_category = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al restaurar categoría: {e}")

def show_create_category():
    """Formulario para crear nueva categoría"""
    st.markdown("## ➕ Crear Nueva Categoría")
    
    category_data = category_form()
    
    if category_data:
        try:
            created_category = api_client.create_category(category_data)
            st.success("✅ Categoría creada exitosamente")
            st.session_state.action = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al crear categoría: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.action = None
        st.rerun()

def show_edit_category():
    """Formulario para editar categoría existente"""
    category = st.session_state.get('edit_category')
    
    st.markdown(f"## ✏️ Editar Categoría: {category.get('name', 'N/A')}")
    
    category_data = category_form(category)
    
    if category_data:
        try:
            api_client.update_category(category['id'], category_data)
            st.success("✅ Categoría actualizada exitosamente")
            st.session_state.edit_category = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al actualizar categoría: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.edit_category = None
        st.rerun()

def show_category_details():
    """Muestra detalles completos de una categoría"""
    category = st.session_state.get('selected_category')
    
    st.markdown(f"## 📂 Detalles de Categoría: {category.get('name', 'N/A')}")
    
    # Información básica
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**🆔 ID:** {category.get('id', 'N/A')}")
        st.write(f"**📝 Nombre:** {category.get('name', 'N/A')}")
    
    with col2:
        st.write(f"**📅 Creada:** {format_date(category.get('created_at'))}")
        st.write(f"**📅 Actualizada:** {format_date(category.get('updated_at'))}")
    
    with col3:
        is_deleted = category.get('deleted_at') is not None
        st.write(f"**📊 Estado:** {'🗑️ Eliminada' if is_deleted else '✅ Activa'}")
        if is_deleted:
            st.write(f"**🗑️ Eliminada:** {format_date(category.get('deleted_at'))}")
    
    # Descripción
    description = category.get('description', '')
    if description:
        st.markdown("### 📝 Descripción")
        st.write(description)
    else:
        st.info("No hay descripción disponible")
    
    # Estadísticas de uso
    st.markdown("### 📊 Estadísticas de Uso")
    
    try:
        # Obtener proyectos de esta categoría
        projects_response = api_client.get_projects(size=100)
        projects = projects_response.get('items', [])
        
        category_projects = [
            p for p in projects 
            if p.get('category', {}).get('id') == category['id']
        ]
        
        if category_projects:
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📋 Total Proyectos", len(category_projects))
            
            with col2:
                active_projects = len([
                    p for p in category_projects 
                    if p.get('status') in ['not_assigned', 'assigned']
                ])
                st.metric("🔄 Activos", active_projects)
            
            with col3:
                completed_projects = len([
                    p for p in category_projects 
                    if p.get('status') == 'completed'
                ])
                st.metric("✅ Completados", completed_projects)
            
            with col4:
                # Proyectos por vencer
                from datetime import datetime, timedelta
                today = datetime.now()
                upcoming_deadlines = [
                    p for p in category_projects 
                    if datetime.fromisoformat(p.get('deadline').replace('Z', '+00:00')) > today and
                       datetime.fromisoformat(p.get('deadline').replace('Z', '+00:00')) <= today + timedelta(days=7)
                ]
                st.metric("⏰ Vencen esta semana", len(upcoming_deadlines))
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Proyectos por Estado")
                
                status_counts = {}
                for project in category_projects:
                    status = project.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                if status_counts:
                    fig = px.pie(
                        values=list(status_counts.values()),
                        names=list(status_counts.keys()),
                        title="Distribución de Estados"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🔥 Proyectos por Prioridad")
                
                priority_counts = {}
                for project in category_projects:
                    priority = project.get('priority', 'unknown')
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                if priority_counts:
                    fig = px.bar(
                        x=list(priority_counts.keys()),
                        y=list(priority_counts.values()),
                        title="Distribución de Prioridades"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Listado de proyectos
            st.subheader(f"📋 Proyectos en '{category.get('name')}'")
            
            for project in category_projects:
                with st.expander(f"📋 {project.get('name', 'N/A')}"):
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:100]}...")
                    st.write(f"**📅 Límite:** {format_date(project.get('deadline'))}")
                    st.write(f"**🎯 Estado:** {status_badge(project.get('status'))}")
                    st.write(f"**🔥 Prioridad:** {status_badge(project.get('priority'))}")
        else:
            st.info("No hay proyectos en esta categoría")
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    # Acciones
    st.markdown("### ⚡ Acciones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✏️ Editar Categoría"):
            st.session_state.edit_category = category
            st.session_state.selected_category = None
            st.rerun()
    
    with col2:
        if st.button("📋 Ver Proyectos"):
            st.session_state.view_category_projects = category
            st.session_state.selected_category = None
            st.rerun()
    
    with col3:
        if category.get('deleted_at'):
            if st.button("🔄 Restaurar"):
                st.session_state.restore_category = category
                st.rerun()
        else:
            if st.button("🗑️ Eliminar"):
                st.session_state.delete_category = category
                st.session_state.selected_category = None
                st.rerun()
    
    with col4:
        if st.button("🔙 Volver al Listado"):
            st.session_state.selected_category = None
            st.rerun()

def show_category_statistics():
    """Muestra estadísticas generales de categorías"""
    st.markdown("## 📊 Estadísticas de Categorías")
    
    try:
        # Obtener todos los datos
        categories_response = api_client.get_categories(size=100)
        projects_response = api_client.get_projects(size=100)
        
        categories = categories_response.get('items', [])
        projects = projects_response.get('items', [])
        
        if not categories:
            st.info("No hay datos de categorías para mostrar")
            return
        
        # Enriquecer categorías con estadísticas
        enriched_categories = []
        for category in categories:
            category_id = category['id']
            
            # Proyectos en esta categoría
            category_projects = [
                p for p in projects 
                if p.get('category', {}).get('id') == category_id
            ]
            
            active_projects = [
                p for p in category_projects 
                if p.get('status') in ['not_assigned', 'assigned']
            ]
            
            completed_projects = [
                p for p in category_projects 
                if p.get('status') == 'completed'
            ]
            
            enriched_categories.append({
                **category,
                'total_projects': len(category_projects),
                'active_projects': len(active_projects),
                'completed_projects': len(completed_projects),
                'completion_rate': (len(completed_projects) / len(category_projects) * 100) if len(category_projects) > 0 else 0
            })
        
        # KPIs generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_categories = len(enriched_categories)
            st.metric("📂 Total Categorías", total_categories)
        
        with col2:
            active_categories = len([
                c for c in enriched_categories 
                if c['active_projects'] > 0
            ])
            st.metric("🔄 Activas", active_categories)
        
        with col3:
            categories_with_projects = len([
                c for c in enriched_categories 
                if c['total_projects'] > 0
            ])
            st.metric("📋 Con Proyectos", categories_with_projects)
        
        with col4:
            # Categoría más productiva
            if categories_with_projects > 0:
                most_productive = max(enriched_categories, key=lambda x: x['completed_projects'])
                st.metric("🏆 Más Productiva", most_productive.get('name', 'N/A')[:12])
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Proyectos por Categoría")
            
            category_project_counts = {
                c.get('name', 'Unknown'): c['total_projects'] 
                for c in enriched_categories if c['total_projects'] > 0
            }
            
            if category_project_counts:
                fig = px.bar(
                    x=list(category_project_counts.values()),
                    y=list(category_project_counts.keys()),
                    orientation='h',
                    title="Proyectos Totales por Categoría"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("✅ Tasa de Completación")
            
            completion_rates = {
                c.get('name', 'Unknown'): c['completion_rate'] 
                for c in enriched_categories if c['total_projects'] > 0
            }
            
            if completion_rates:
                # Ordenar por tasa de completación
                sorted_rates = dict(sorted(completion_rates.items(), key=lambda x: x[1], reverse=True)[:10])
                
                fig = px.bar(
                    x=list(sorted_rates.values()),
                    y=list(sorted_rates.keys()),
                    orientation='h',
                    title="Tasa de Completación (%)"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📋 Detalles por Categoría")
        
        category_details = []
        for category in enriched_categories:
            category_details.append({
                'Categoría': category.get('name', 'N/A'),
                'Total Proyectos': category['total_projects'],
                'Activos': category['active_projects'],
                'Completados': category['completed_projects'],
                'Tasa Completación': f"{category['completion_rate']:.1f}%",
                'Estado': '🗑️ Eliminada' if category.get('deleted_at') else '✅ Activa'
            })
        
        # Ordenar por total de proyectos
        category_details.sort(key=lambda x: x['Total Proyectos'], reverse=True)
        
        st.dataframe(category_details, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    if st.button("🔙 Volver"):
        st.session_state.show_category_stats = None
        st.rerun()

def show_category_list(status_filter: str, search_term: str):
    """Muestra listado filtrado de categorías"""
    try:
        categories_response = api_client.get_categories(size=100)
        categories = categories_response.get('items', [])
        
        # Obtener proyectos para estadísticas
        projects_response = api_client.get_projects(size=100)
        projects = projects_response.get('items', [])
        
        # Enriquecer categorías con estadísticas básicas
        enriched_categories = []
        for category in categories:
            category_id = category['id']
            
            category_projects = [
                p for p in projects 
                if p.get('category', {}).get('id') == category_id
            ]
            
            enriched_categories.append({
                **category,
                'project_count': len(category_projects),
                'is_deleted': category.get('deleted_at') is not None
            })
        
        # Aplicar filtros
        filtered_categories = enriched_categories
        
        # Filtro por estado
        if status_filter == "Activas":
            filtered_categories = [c for c in filtered_categories if not c['is_deleted']]
        elif status_filter == "Eliminadas":
            filtered_categories = [c for c in filtered_categories if c['is_deleted']]
        
        # Filtro por búsqueda
        if search_term:
            filtered_categories = [
                c for c in filtered_categories 
                if search_term.lower() in c.get('name', '').lower() or
                   search_term.lower() in c.get('description', '').lower()
            ]
        
        # Mostrar resultados
        if filtered_categories:
            st.write(f"**Resultados encontrados:** {len(filtered_categories)}")
            
            for category in filtered_categories:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**📂 {category.get('name', 'N/A')}**")
                        st.write(f"📝 {category.get('description', 'N/A')[:80]}...")
                        st.write(f"📅 Creada: {format_date(category.get('created_at'))}")
                    
                    with col2:
                        st.write(f"📋 {category['project_count']} proyectos")
                        st.write(f"📊 Estado: {'🗑️ Eliminada' if category['is_deleted'] else '✅ Activa'}")
                    
                    with col3:
                        if st.button("Ver", key=f"view_{category['id']}"):
                            st.session_state.selected_category = category
                            st.rerun()
                        if st.button("Editar", key=f"edit_{category['id']}"):
                            st.session_state.edit_category = category
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No se encontraron categorías con los filtros seleccionados")
    
    except Exception as e:
        st.error(f"Error al cargar categorías: {e}")