# Datos de Ejemplo para Base de Datos - Sistema de Voluntariado Informática

**Fecha:** 26/01/2026  
**Propósito:** Datos de prueba para el sistema de gestión de voluntarios en el área de informática y programación.

---

## Estructura de la Base de Datos

### Modelos Principales:
- **Users**: Usuarios del sistema
- **Role**: Roles (admin, volunteer)
- **Volunteer**: Voluntarios (extensión de users)
- **Category**: Categorías de proyectos
- **Skill**: Habilidades técnicas
- **Project**: Proyectos disponibles
- **Assignment**: Asignaciones voluntario-proyecto

### Tablas Intermedias:
- **volunteer_skills**: Relación muchos-a-muchos voluntario-habilidades
- **project_skills**: Relación muchos-a-muchos proyecto-habilidades

---

## Scripts SQL de Inserción

### 1. Roles (Base)

```sql
INSERT INTO role (id, name) VALUES 
(1, 'admin'),
(2, 'volunteer');
```

### 2. Categorías (Informática y Programación)

```sql
INSERT INTO categories (id, name, description) VALUES 
(1, 'Desarrollo Web', 'Proyectos de desarrollo de aplicaciones web y sitios modernos'),
(2, 'Desarrollo Móvil', 'Aplicaciones para iOS y Android'),
(3, 'Inteligencia Artificial', 'Proyectos de machine learning, deep learning y IA'),
(4, 'Ciberseguridad', 'Auditorías de seguridad, análisis de vulnerabilidades y herramientas de defensa'),
(5, 'DevOps', 'Automatización, CI/CD, infraestructura en la nube y contenerización'),
(6, 'Bases de Datos', 'Diseño, optimización y administración de sistemas de bases de datos'),
(7, 'Ciencia de Datos', 'Análisis estadístico, visualización y procesamiento de datos masivos');
```

### 3. Habilidades Técnicas

```sql
INSERT INTO skills (id, name) VALUES 
(1, 'Python'),
(2, 'JavaScript'),
(3, 'TypeScript'),
(4, 'React'),
(5, 'Vue.js'),
(6, 'Angular'),
(7, 'Node.js'),
(8, 'Django'),
(9, 'Flask'),
(10, 'FastAPI'),
(11, 'Java'),
(12, 'Spring Boot'),
(13, 'C++'),
(14, 'C#'),
(15, '.NET'),
(16, 'Go'),
(17, 'Rust'),
(18, 'Docker'),
(19, 'Kubernetes'),
(20, 'AWS'),
(21, 'Azure'),
(22, 'GCP'),
(23, 'PostgreSQL'),
(24, 'MySQL'),
(25, 'MongoDB'),
(26, 'Redis'),
(27, 'Git'),
(28, 'CI/CD'),
(29, 'Terraform'),
(30, 'Machine Learning'),
(31, 'Deep Learning'),
(32, 'TensorFlow'),
(33, 'PyTorch'),
(34, 'Ciberseguridad'),
(35, 'Pentesting'),
(36, 'Análisis de Malware'),
(37, 'Blockchain'),
(38, 'Solidity'),
(39, 'Data Science'),
(40, 'Análisis Estadístico'),
(41, 'Big Data'),
(42, 'Apache Spark'),
(43, 'ETL'),
(44, 'Testing Automatizado'),
(45, 'UX/UI Design');
```

### 4. Usuarios (con contraseñas hasheadas)

```sql
-- Usuarios con contraseñas hasheadas usando bcrypt
-- Contraseñas: "admin123", "volunteer123"

INSERT INTO users (id, name, email, password, phone, birth_date, role_id) VALUES 
(1, 'Admin Sistema', 'admin@voluntariotech.org', '$2b$12$EhqOSj7ySdmazXbCrds5Q.yHFyZ8mR8zdBCGsuMeEh5u1ZELvXnwa', '600123456', '1990-05-15', 1),
(2, 'Ana García', 'ana.garcia@techmail.com', '$2b$12$6L5eQAv3KGXgf11saWcsP.aDB.0u4S9Zd7nfnv0z6R4nYt7kRD1JS', '600223456', '1992-08-22', 2),
(3, 'Carlos Rodríguez', 'carlos.rodriguez@devmail.com', '$2b$12$6L5eQAv3KGXgf11saWcsP.aDB.0u4S9Zd7nfnv0z6R4nYt7kRD1JS', '600323456', '1991-03-10', 2),
(4, 'María López', 'maria.lopez@datamail.com', '$2b$12$6L5eQAv3KGXgf11saWcsP.aDB.0u4S9Zd7nfnv0z6R4nYt7kRD1JS', '600423456', '1993-12-05', 2),
(5, 'David Chen', 'david.chen@techmail.com', '$2b$12$6L5eQAv3KGXgf11saWcsP.aDB.0u4S9Zd7nfnv0z6R4nYt7kRD1JS', '600523456', '1990-07-18', 2),
(6, 'Laura Martínez', 'laura.martinez@cybermail.com', '$2b$12$6L5eQAv3KGXgf11saWcsP.aDB.0u4S9Zd7nfnv0z6R4nYt7kRD1JS', '600623456', '1994-02-28', 2),
(7, 'Roberto Silva', 'roberto.silva@devmail.com', '$2b$12$6L5eQAv3KGXgf11saWcsP.aDB.0u4S9Zd7nfnv0z6R4nYt7kRD1JS', '600723456', '1989-11-12', 2);
```

### 5. Voluntarios

```sql
INSERT INTO volunteers (id, user_id, status) VALUES 
(1, 2, 'active'),
(2, 3, 'active'),
(3, 4, 'active'),
(4, 5, 'active'),
(5, 6, 'active'),
(6, 7, 'active');
```

### 6. Asignación de Habilidades a Voluntarios

```sql
INSERT INTO volunteer_skills (volunteer_id, skill_id) VALUES 
-- Ana García - Full Stack Developer
(1, 1),   -- Python
(1, 2),   -- JavaScript
(1, 4),   -- React
(1, 7),   -- Node.js
(1, 23),  -- PostgreSQL
(1, 27),  -- Git

-- Carlos Rodríguez - Backend Developer
(2, 1),   -- Python
(2, 8),   -- Django
(2, 10),  -- FastAPI
(2, 23),  -- PostgreSQL
(2, 24),  -- MySQL
(2, 27),  -- Git


-- LAS SIGUIENTES NO ESTAN RELACIONADAS AUN:
-- María López - Data Scientist
(3, 1),   -- Python
(3, 30),  -- Machine Learning
(3, 31),  -- Deep Learning
(3, 32),  -- TensorFlow
(3, 39),  -- Data Science
(3, 40),  -- Análisis Estadístico
(3, 42),  -- Apache Spark

-- David Chen - DevOps Engineer
(4, 16),  -- Go
(4, 18),  -- Docker
(4, 19),  -- Kubernetes
(4, 20),  -- AWS
(4, 28),  -- CI/CD
(4, 29),  -- Terraform

-- Laura Martínez - Cybersecurity Expert
(5, 1),   -- Python
(5, 34),  -- Ciberseguridad
(5, 35),  -- Pentesting
(5, 36),  -- Análisis de Malware
(5, 27),  -- Git

-- Roberto Silva - Mobile Developer
(6, 2),   -- JavaScript
(7, 11),  -- Java
(6, 14),  -- C#
(6, 27);  -- Git
```

### 7. Proyectos

```sql
INSERT INTO projects (id, name, description, deadline, status, priority, category_id) VALUES 
(1, 'Plataforma E-learning', 'Desarrollo de plataforma web completa para educación online con sistema de videoconferencias integrado', '2026-03-15 00:00:00', 'not_assigned', 'high', 1),
(2, 'App Fitness Móvil', 'Aplicación nativa para iOS y Android con seguimiento de entrenamiento y gamificación', '2026-04-20 00:00:00', 'not assigned', 'medium', 2),
(3, 'Sistema Detección Fraudes', 'Modelo de machine learning para detección de transacciones fraudulentas en tiempo real', '2026-02-28 00:00:00', 'not assigned', 'high', 3),
(4, 'Auditoría de Seguridad Web', 'Análisis completo de vulnerabilidades en aplicación web bancaria existente', '2026-03-10 00:00:00', 'not assigned', 'high', 4),
(5, 'Migración a Microservicios', 'Transformación de aplicación monolítica a arquitectura de microservicios en AWS', '2026-05-30 00:00:00', 'not assigned', 'medium', 5),
(6, 'Optimización Base de Datos', 'Rediseño y optimización de consultas para sistema de gestión de inventario con más de 1M registros', '2026-03-25 00:00:00', 'not assigned', 'medium', 6);

--LOS SIGUIENTES PROYECTOS NO ESTAN EN DDBB AUN:
(7, 'Dashboard Analytics', 'Sistema de análisis de datos masivos con visualizaciones interactivas para plataforma de e-commerce', '2026-04-15 00:00:00', 'not assigned', 'low', 7),
(8, 'API RESTful Gateway', 'Desarrollo de API Gateway centralizado para gestión de microservicios', '2026-03-20 00:00:00', 'not assigned', 'medium', 1),
(9, 'Chatbot Inteligente', 'Implementación de chatbot con NLP para servicio al cliente automático', '2026-04-10 00:00:00', 'not assigned', 'low', 3),
(10, 'Sistema CI/CD', 'Implementación de pipeline completo de integración continua y despliegue automatizado', '2026-03-18 00:00:00', 'not assigned', 'medium', 5);
```

### 8. Asignación de Habilidades a Proyectos

```sql
INSERT INTO project_skills (project_id, skill_id) VALUES 
-- Plataforma E-learning
(1, 2),   -- JavaScript
(1, 4),   -- React
(1, 7),   -- Node.js
(1, 23),  -- PostgreSQL
(1, 27),  -- Git
(1, 44),  -- Testing Automatizado

-- App Fitness Móvil
(2, 11),  -- Java
(2, 14),  -- C#
(2, 27),  -- Git
(2, 45),  -- UX/UI Design

-- Sistema Detección Fraudes
(3, 1),   -- Python
(3, 30),  -- Machine Learning
(3, 32),  -- TensorFlow
(3, 39),  -- Data Science
(3, 24),  -- MySQL

--LO SIGUIENTE NO ESTA EN BASE DE DATOS:
-- Auditoría de Seguridad Web
(4, 34),  -- Ciberseguridad
(4, 35),  -- Pentesting
(4, 36),  -- Análisis de Malware
(4, 2),   -- JavaScript

-- Migración a Microservicios
(5, 16),  -- Go
(5, 18),  -- Docker
(5, 19),  -- Kubernetes
(5, 20),  -- AWS
(5, 28),  -- CI/CD
(5, 29),  -- Terraform

-- Optimización Base de Datos
(6, 23),  -- PostgreSQL
(6, 24),  -- MySQL
(6, 25),  -- MongoDB
(6, 26),  -- Redis
(6, 1),   -- Python

-- Dashboard Analytics
(7, 39),  -- Data Science
(7, 40),  -- Análisis Estadístico
(7, 42),  -- Apache Spark
(7, 4),   -- React
(7, 25),  -- MongoDB

-- API RESTful Gateway
(8, 7),   -- Node.js
(8, 10),  -- FastAPI
(8, 27),  -- Git
(8, 28),  -- CI/CD

-- Chatbot Inteligente
(9, 1),   -- Python
(9, 30),  -- Machine Learning
(9, 31),  -- Deep Learning
(9, 33),  -- PyTorch

-- Sistema CI/CD
(10, 18), -- Docker
(10, 19), -- Kubernetes
(10, 20), -- AWS
(10, 27), -- Git
(10, 28); -- CI/CD
```

---

## Credenciales de Prueba

### Usuarios Principales:

1. **Admin Sistema**
   - Email: `admin@voluntariotech.org`
   - Contraseña: `admin123`
   - Rol: Administrador

2. **Ana García (Full Stack)**
   - Email: `ana.garcia@techmail.com`
   - Contraseña: `volunteer123`
   - Habilidades: Python, JavaScript, React, Node.js, PostgreSQL, Git

3. **Carlos Rodríguez (Backend)**
   - Email: `carlos.rodriguez@devmail.com`
   - Contraseña: `volunteer123`
   - Habilidades: Python, Django, FastAPI, PostgreSQL, MySQL, Git

4. **María López (Data Scientist)**
   - Email: `maria.lopez@datamail.com`
   - Contraseña: `volunteer123`
   - Habilidades: Python, Machine Learning, Deep Learning, TensorFlow, Data Science, Análisis Estadístico, Apache Spark

5. **David Chen (DevOps)**
   - Email: `david.chen@techmail.com`
   - Contraseña: `volunteer123`
   - Habilidades: Go, Docker, Kubernetes, AWS, CI/CD, Terraform

6. **Laura Martínez (Cybersecurity)**
   - Email: `laura.martinez@cybermail.com`
   - Contraseña: `volunteer123`
   - Habilidades: Python, Ciberseguridad, Pentesting, Análisis de Malware, Git

7. **Roberto Silva (Mobile Dev)**
   - Email: `roberto.silva@devmail.com`
   - Contraseña: `volunteer123`
   - Habilidades: JavaScript, Java, C#, Git

---

## Notas Técnicas

### Contraseñas Hasheadas:
- Todas las contraseñas están hasheadas usando bcrypt
- El hash `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/9bp.G.MiK` corresponde a: `volunteer123`
- El método `hash_password()` del sistema usa `pwd_context.hash(password[:72])`

### Fechas:
- Las fechas de deadline están configuradas para 2026
- Los años de nacimiento van de 1989 a 1994

### Estados:
- Todos los voluntarios están en estado 'active'
- Todos los proyectos están en estado 'not assigned' para permitir asignaciones desde la interfaz

### Relaciones:
- Las tablas intermedias (volunteer_skills, project_skills) gestionan las relaciones muchos-a-muchos
- Cada proyecto está asociado a una categoría
- Cada usuario está asociado a un rol

---

## Flujo de Prueba Recomendado

1. **Login como administrador** para verificar el dashboard admin
2. **Ver voluntarios disponibles** y sus habilidades
3. **Explorar proyectos** y sus requerimientos técnicos
4. **Realizar asignaciones** entre voluntarios y proyectos basados en habilidades coincidentes
5. **Login como voluntario** para verificar el dashboard de voluntario
6. **Ver asignaciones** y actualizar estados desde la perspectiva del voluntario

---

**ADVERTENCIA:** Este script debe ejecutarse en un entorno de desarrollo/prueba. Las contraseñas hasheadas son para pruebas únicamente.