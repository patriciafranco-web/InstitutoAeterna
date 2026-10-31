from flask import Flask, render_template_string, request, jsonify, Response, session, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = 'aeterna_secret_key_2026_produccion_total'

# ==========================================
# BASE DE DATOS INSTITUCIONAL — AETERNA E.A.S.
# ==========================================

USUARIOS_DB = {
    "pedro.calabrese": {
        "pass": "aeterna2026", 
        "pass_admin": "caja2026",
        "nombre": "Dr. Pedro Calabrese", 
        "rol_base": "medico", 
        "es_socio": True,
        "especialidad": "Traumatología y Ortopedia (Socio)"
    },
    "fatima.lopez": {
        "pass": "aeterna2026", 
        "pass_admin": "caja2026",
        "nombre": "Dra. Fátima López", 
        "rol_base": "medico", 
        "es_socio": True,
        "especialidad": "Traumatología y Ortopedia (Socio)"
    },
    "romina.espinola": {
        "pass": "aeterna2026", 
        "pass_admin": "caja2026",
        "nombre": "Dra. Romina Espinola", 
        "rol_base": "medico", 
        "es_socio": True,
        "especialidad": "Medicina Familiar - Pos Endocrinología (Socio)"
    },
    "ximena.ruiz": {
        "pass": "aeterna2026", 
        "nombre": "Lic. Ximena Ruiz", 
        "rol_base": "medico", 
        "es_socio": False,
        "especialidad": "Nutricionista Clínica & Longevidad"
    },
    "alfredo.estigarribia": {
        "pass": "aeterna2026", 
        "nombre": "Dr. Alfredo Estigarribia", 
        "rol_base": "medico", 
        "es_socio": False,
        "especialidad": "Odontología del Sueño"
    },
    "manuel.duarte": {
        "pass": "aeterna2026", 
        "nombre": "Manuel Duarte", 
        "rol_base": "entrenador", 
        "es_socio": False,
        "especialidad": "Preparador Físico / Performance Coach"
    },
    "nadia.bortolace": {
        "pass": "caja2026", 
        "nombre": "Nadia Bortolace", 
        "rol_base": "secretaria", 
        "es_socio": False,
        "especialidad": "Gestión Financiera & Facturación Sifen"
    },
    "daiana.gomez": {
        "pass": "caja2026", 
        "nombre": "Daiana Gomez", 
        "rol_base": "secretaria", 
        "es_socio": False,
        "especialidad": "Gestión Financiera & Facturación Sifen"
    },
    "buro": {
        "pass": "admin2026", 
        "nombre": "Buró (Administración / Contabilidad)", 
        "rol_base": "secretaria", 
        "es_socio": False,
        "especialidad": "Administración General & Facturación Sifen"
    }
}

PACIENTES = [
    {
        "id": "p1",
        "nombre": "Carlos Benítez",
        "edad": 42,
        "programa": "Longevidad & Optimización Metabólica",
        "medico": "Dra. Romina Espinola",
        "entrenador": "Manuel Duarte",
        "reg_profesional": "MP 4291",
        "hora_turno": "09:00 hs",
        "estado_turno": "En Espera / Sala VIP",
        "pre_consulta": {
            "nombre_completo": "Carlos Benítez",
            "fecha_nac": "12/05/1984",
            "edad": "42",
            "genero": "Masculino",
            "nacionalidad": "Paraguaya",
            "residencia": "Ciudad del Este, Paraguay",
            "profesion": "Empresario",
            "estado_civil": "Casado",
            "telefono": "+595 981 123456",
            "correo": "carlos.benitez@aeterna.py",
            "contacto_emergencia": "María Benítez (+595 981 654321)",
            "objetivos": "Aumentar niveles de energía y vitalidad diaria, Optimizar rendimiento físico y/o cognitivo",
            "queja": "Fatiga crónica vespertina y ligera dificultad de concentración.",
            "salud_actual": "6/10",
            "impacto_vida": "Mejorar la productividad gerencial y disfrutar más tiempo con la familia.",
            "antecedentes": "Sin enfermedades crónicas diagnosticadas. Niega cirugías previas.",
            "cirugias": "Ninguna",
            "ant_familiares": "Padre con hipertensión leve a los 60 años.",
            "alergias": "Ninguna conocida",
            "medicamentos": "Ninguno",
            "suplementos_actuales": "Magnesio L-Treonato, Vitamina D3 5000UI, Omega-3.",
            "trh": "No",
            "estudios_geneticos": "No",
            "nutricion": "Dieta baja en carbohidratos / Flexitariana.",
            "procesados": "1-2 veces por semana",
            "sintomas_digestivos": "Leve hinchazón ocasional post-almuerzo.",
            "agua": "2.5 Litros",
            "sueno_horas": "6.5 horas",
            "sueno_calidad": "Regular (Me despierto cansado a veces)",
            "wearable": "Oura Ring (Gen 3 / 4 / 5)",
            "compartir_sueno": "Sí",
            "dias_ejercicio": "4 días",
            "tipo_entrenamiento": "Fuerza y Cardio Zona 2",
            "dolor_articular": "No",
            "estres": "7/10",
            "manejo_estres": "Lectura y caminatas al aire libre.",
            "toxinas": "No",
            "energia_dia": "6/10",
            "bajones_energia": "Sí. A las 16:00 hs.",
            "libido": "Normal",
            "ciclo_menstrual": "N/A",
            "compromiso": "Sí, estoy 100% comprometido.",
            "lab_recientes": "Sí, los llevaré/enviaré",
            "estado": "Completado 🟢"
        },
        "historial_consultas": [
            {
                "fecha": "14/09/2026",
                "medico": "Dra. Romina Espinola",
                "evolucion": "Paciente refiere leve mejora en energía diurna. Se ajusta dosis de magnesio y se solicita panel metabólico de control.",
            },
            {
                "fecha": "20/08/2026",
                "medico": "Dr. Pedro Calabrese",
                "evolucion": "Primera consulta de evaluación metabólica y biomarcadores iniciales. Se detecta fatiga matutina severa.",
            }
        ],
        "solicitudes_lab_previas": [
            {"fecha": "14/09/2026", "estudios": "Perfil Lipídico, Insulina Basal, HbA1c, Tiempo de Coagulación", "estado": "Completado y Sincronizado"},
            {"fecha": "20/10/2026", "estudios": "PCR Ultrasensible, Panel Hormonal Completo, Apob", "estado": "Pendiente de LIS"}
        ],
        "archivos_no_lab": [
            {
                "fecha": "10/08/2026", 
                "tipo": "Resonancia Magnética Cerebral", 
                "archivo": "rmn_cerebral_carlos.pdf", 
                "medico": "Dra. Romina Espinola", 
                "estado": "Cargado e Informado",
                "informe": "Paciente sin contraindicaciones en estudio imagenológico previo. Se observa indemnidad estructural."
            },
            {
                "fecha": "18/10/2026", 
                "tipo": "Evaluación Funcional / Ergoespirometría", 
                "archivo": "Informe Directo (Texto)", 
                "medico": "Dra. Romina Espinola", 
                "estado": "Redactado Directo",
                "informe": "Excelente respuesta cardiorrespiratoria al esfuerzo máximo. VO2 máx estimado en 48 ml/kg/min (Óptimo para la edad)."
            }
        ],
        "wearables": {
            "dispositivo": "Oura Ring Gen 3 & Apple Health",
            "sync_status": "Sincronizado hace 12 minutos",
            "sueno_horas": "7h 42m",
            "eficiencia_sueno": "88% (REM Óptimo: 1h 45m)",
            "hrv": "68 ms",
            "frecuencia_cardiaca_reposo": "54 lpm",
            "temperatura_corporal": "-0.1 °C (Línea Base Estable)",
            "strain_esfuerzo": "14.2 / 21.0 (Actividad Moderada)",
            "alerta_ia": "Alerta IA Aeterna: Tendencia positiva sostenida en HRV (+14% en 30 días). Recuperación nocturna óptima tras instauración de Magnesio L-Treonato y NAD+.",
            "observaciones": "Excelente recuperación nocturna tras ajuste de Magnesio L-Treonato y protocolo NAD+."
        },
        "entrenamiento": {
            "enfoque": "Fuerza hipertrófica & Cardiorespiratorio Zona 2",
            "sesiones_semanales": "4 días (Lunes, Martes, Jueves, Viernes)",
            "prescripcion_ejercicio": "1. Cardio Zona 2: 45 min en bicicleta estática (Frecuencia cardiaca objetivo: 115-125 lpm).\n2. Fuerza (Día A - Tren Superior): Press banca multipower 4x8, Dominadas asistidas 3x10, Remo con mancuernas 4x10.\n3. Movilidad y Core: 15 minutos diarios post-entrenamiento.",
            "historial_rendimiento": [
                {"fecha": "20/08/2026", "vo2": "42 ml/kg/min", "fuerza_agarre": "38 kg", "grasa": "18.5%"},
                {"fecha": "14/09/2026", "vo2": "45 ml/kg/min", "fuerza_agarre": "41 kg", "grasa": "17.8%"},
                {"fecha": "20/10/2026", "vo2": "48 ml/kg/min", "fuerza_agarre": "44 kg", "grasa": "16.9%"}
            ]
        },
        "wearables_longitudinal": [
            {
                "metrica": "Variabilidad de la Frecuencia Cardíaca (HRV)",
                "unidad": "ms",
                "rango_optimo": "> 60 ms",
                "historial": [
                    {"fecha": "20/08/2026", "valor": 52},
                    {"fecha": "14/09/2026", "valor": 61},
                    {"fecha": "20/10/2026", "valor": 68}
                ]
            },
            {
                "metrica": "Promedio de Sueño Profundo / REM",
                "unidad": "Horas",
                "rango_optimo": "> 7.5 hs",
                "historial": [
                    {"fecha": "20/08/2026", "valor": 6.2},
                    {"fecha": "14/09/2026", "valor": 7.0},
                    {"fecha": "20/10/2026", "valor": 7.7}
                ]
            }
        ],
        "biomarcadores_longitudinales": [
            {
                "parametro": "Glucosa en Ayunas",
                "rango_optimo": "70 - 99 mg/dL",
                "historial": [
                    {"fecha": "20/08/2026", "valor": 96, "unidad": "mg/dL"},
                    {"fecha": "14/09/2026", "valor": 92, "unidad": "mg/dL"},
                    {"fecha": "20/10/2026", "valor": 88, "unidad": "mg/dL"}
                ]
            },
            {
                "parametro": "Insulina Basal",
                "rango_optimo": "< 6.0 uIU/mL",
                "historial": [
                    {"fecha": "20/08/2026", "valor": 6.8, "unidad": "uIU/mL"},
                    {"fecha": "14/09/2026", "valor": 5.4, "unidad": "uIU/mL"},
                    {"fecha": "20/10/2026", "valor": 4.2, "unidad": "uIU/mL"}
                ]
            },
            {
                "parametro": "Colesterol LDL",
                "rango_optimo": "< 100 mg/dL",
                "historial": [
                    {"fecha": "20/08/2026", "valor": 115, "unidad": "mg/dL"},
                    {"fecha": "14/09/2026", "valor": 105, "unidad": "mg/dL"},
                    {"fecha": "20/10/2026", "valor": 98, "unidad": "mg/dL"}
                ]
            }
        ],
        "receta_texto": "1. NAD+ Sublingual Protocol: 500 mg semanal en ayunas con agua filtrada.\n2. Magnesio L-Treonato: 145 mg (20:00 hs), 2 cápsulas por la noche para optimizar descanso REM.\n3. Coenzima Q10 Ubiquinol: 200 mg diarios con el almuerzo principal.",
        "regenerativa_dx": "Síndrome de Fatiga Crónica Mitocondrial & Desgaste Energético por Estrés Oxidativo.",
        "regenerativa_sesiones": [
            {"sesion": "Sesión 01", "fecha": "15/09/2026", "protocolo": "Sueroterapia NAD+ 250mg + Vit C Alta Dosis", "observaciones": "Buena tolerancia. Ligero bochorno inicial autolimitado."},
            {"sesion": "Sesion 02", "fecha": "30/09/2026", "protocolo": "Sueroterapia NAD+ 500mg + Complejo B", "observaciones": "Paciente refiere aumento notable de energía diurna."},
            {"sesion": "Sesion 03", "fecha": "14/10/2026", "protocolo": "Sueroterapia NAD+ 500mg + Magnesio IV", "observaciones": "Sueño profundo mejorado según Oura Ring."},
            {"sesion": "Sesion 04", "fecha": "Pendiente", "protocolo": "Protocolo de Mantenimiento Quincenal", "observaciones": "Agendado en Sala VIP Aeterna."}
        ],
        "consentimientos_firmados": [
            {"titulo": "Consentimiento Informado para Sueroterapia & Infusiones IV", "fecha": "20/08/2026", "estado": "Emitido & Firmado"},
            {"titulo": "Consentimiento para Protocolos de Medicina Regenerativa & NAD+", "fecha": "20/08/2026", "estado": "Emitido & Firmado"}
        ],
        "dossier": {
            "nutricion": "Ventana de alimentación restringida de 10 horas (10:00 AM - 08:00 PM). Enfoque cetogénico moderado con alta densidad de polifenoles y ácidos grasos Omega-3.",
            "suplementacion": "Protocolo de mitocondriogénesis: NAD+ Sublingual en ayunas, Magnesio L-Treonato (2g) 60 minutos antes de dormir, Coenzima Q10 Ubiquinol (200mg) con el almuerzo principal.",
            "habitos_sueno": "Bloqueo de luz azul 2 horas antes de pernoctar, temperatura ambiental en habitación a 19°C, cena ligera 3 horas antes de acostarse."
        }
    },
    {
        "id": "p2",
        "nombre": "María Giménez",
        "edad": 38,
        "programa": "Bienestar & Rendimiento Cognitivo",
        "medico": "Dra. Fátima López",
        "entrenador": "Manuel Duarte",
        "reg_profesional": "MP 3415",
        "hora_turno": "10:30 hs",
        "estado_turno": "Confirmado",
        "pre_consulta": None,
        "historial_consultas": [],
        "solicitudes_lab_previas": [],
        "archivos_no_lab": [],
        "biomarcadores_longitudinales": [],
        "wearables": {
            "dispositivo": "Whoop 4.0",
            "sync_status": "Sincronizado",
            "sueno_horas": "8h 10m",
            "eficiencia_sueno": "91%",
            "hrv": "74 ms",
            "frecuencia_cardiaca_reposo": "50 lpm",
            "temperatura_corporal": "Normal",
            "strain_esfuerzo": "12.0",
            "alerta_ia": "Alerta IA Aeterna: Parámetros bioenergéticos estables y óptimos.",
            "observaciones": "Excelente recuperación cardiovascular."
        },
        "wearables_longitudinal": [],
        "entrenamiento": {
            "enfoque": "Pilates & Resistencia Aeróbica",
            "sesiones_semanales": "3 días",
            "prescripcion_ejercicio": "1. Pilates reformer 2x semana.\n2. Caminata en pendiente Zona 2 (30 min)."
        },
        "receta_texto": "1. Complex B Bioactivo: 1 cápsula diaria con el almuerzo.\n2. Vitamina D3 5000 UI: 1 cápsula semanal.",
        "regenerativa_dx": "Fatiga Adrenal Leve por Exigencia Cognitiva.",
        "regenerativa_sesiones": [],
        "consentimientos_firmados": [],
        "dossier": {
            "nutricion": "Dieta mediterránea rica en antioxidantes y grasas saludables.",
            "suplementacion": "Complex B bioactivo diario, Vitamina D3 con K2 semanal.",
            "habitos_sueno": "Higiene de sueño estricta con 8 horas continuas."
        }
    },
    {
        "id": "p3",
        "nombre": "Roberto Duarte",
        "edad": 50,
        "programa": "Optimización Cardiovascular",
        "medico": "Dr. Pedro Calabrese",
        "entrenador": "Manuel Duarte",
        "reg_profesional": "MP 3102",
        "hora_turno": "11:45 hs",
        "estado_turno": "Confirmado",
        "pre_consulta": None,
        "historial_consultas": [],
        "solicitudes_lab_previas": [],
        "archivos_no_lab": [],
        "biomarcadores_longitudinales": [],
        "wearables": {
            "dispositivo": "Apple Watch Series 9",
            "sync_status": "Sincronizado",
            "sueno_horas": "6h 50m",
            "eficiencia_sueno": "82%",
            "hrv": "52 ms",
            "frecuencia_cardiaca_reposo": "62 lpm",
            "temperatura_corporal": "Normal",
            "strain_esfuerzo": "15.5",
            "alerta_ia": "Alerta IA Aeterna: Descenso leve en HRV detectado anoche.",
            "observaciones": "Mejorar higiene del sueño."
        },
        "wearables_longitudinal": [],
        "entrenamiento": {
            "enfoque": "Rehabilitación & Acondicionamiento Endotelial",
            "sesiones_semanales": "3 días",
            "prescripcion_ejercicio": "1. Elíptica suave Zona 2 (30 min).\n2. Cargas livianas para densidad ósea."
        },
        "receta_texto": "1. Coenzima Q10 Ubiquinol: 200 mg diarios.",
        "regenerativa_dx": "Prevención Cardiovascular.",
        "regenerativa_sesiones": [],
        "consentimientos_firmados": [],
        "dossier": {
            "nutricion": "Control estricto de sodio y aumento de ácidos grasos EPA/DHA.",
            "suplementacion": "Coenzima Q10 Ubiquinol diaria.",
            "habitos_sueno": "Monitoreo constante de frecuencia cardíaca nocturna."
        }
    }
]

db_caja_pagos = [
    {
        "id": 1, "paciente": "Carlos Benítez", "monto": 1500000, "metodo": "Tarjeta", 
        "referencia": "POS-9821", "estado": "Completado", "fecha": "2026-10-20",
        "sifen_status": "Aprobado Sifen", "cdc": "800" + "".join([str(random.randint(0, 9)) for _ in range(41)])
    },
    {
        "id": 2, "paciente": "María Giménez", "monto": 1200000, "metodo": "Transferencia", 
        "referencia": "TX-44910", "estado": "Completado", "fecha": "2026-10-20",
        "sifen_status": "Aprobado Sifen", "cdc": "800" + "".join([str(random.randint(0, 9)) for _ in range(41)])
    }
]

db_cuentas_cobrar = [
    {"id": 101, "paciente": "Roberto Duarte", "concepto": "Seña Programa Cardiovascular", "monto": 800000, "tipo": "Seña / Anticipo", "vencimiento": "2026-10-25"}
]

db_gastos_operativos = [
    {"id": 501, "concepto": "Insumos Sueroterapia & Kits NAD+", "monto": 2500000, "categoria": "Insumos Médicos", "fecha": "2026-10-18"},
    {"id": 502, "concepto": "Mantenimiento Equipos Ergoespirometría", "monto": 1200000, "categoria": "Infraestructura", "fecha": "2026-10-15"}
]

db_honorarios_medicos = [
    {"profesional": "Dr. Pedro Calabrese", "consultas": 14, "honorarios_gs": 4200000, "estado": "Liquidado"},
    {"profesional": "Dra. Romina Espinola", "consultas": 18, "honorarios_gs": 5400000, "estado": "Pendiente de Pago"},
    {"profesional": "Dra. Fátima López", "consultas": 10, "honorarios_gs": 3000000, "estado": "Pendiente de Pago"}
]

# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        
        if username in USUARIOS_DB:
            user_info = USUARIOS_DB[username]
            if user_info["es_socio"] and password == user_info["pass_admin"]:
                session['user'] = username
                session['nombre'] = f"{user_info['nombre']} (Admin)"
                session['rol_base'] = 'secretaria'
                session['es_socio'] = True
                return redirect(url_for('index', rol='secretaria', seccion='caja'))
            elif password == user_info["pass"] or (user_info["es_socio"] and password == user_info["pass_admin"]):
                session['user'] = username
                session['nombre'] = user_info['nombre']
                session['rol_base'] = user_info['rol_base']
                session['es_socio'] = user_info['es_socio']
                
                if user_info['rol_base'] == 'entrenador':
                    return redirect(url_for('index', rol='entrenador', seccion='agenda_entrenador'))
                elif user_info['rol_base'] == 'secretaria':
                    return redirect(url_for('index', rol='secretaria', seccion='caja'))
                else:
                    return redirect(url_for('index', rol='medico', seccion='agenda_medico'))
            else:
                error = "Contraseña incorrecta."
        else:
            error = "El usuario ingresado no existe en el sistema."
            
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
# PORTAL PÚBLICO DEL PACIENTE (PRE-CONSULTA 360°)
# ==========================================

@app.route('/portal/pre-consulta/<id_paciente>', methods=['GET'])
def portal_preconsulta_form(id_paciente):
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if not paciente:
        return "Paciente no encontrado o enlace expirado.", 404
        
    portal_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pre-Consulta 360° | Instituto Aeterna E.A.S.</title>
        <style>
            body { font-family: 'Inter', system-ui, sans-serif; background-color: #121110; color: #f5f2eb; padding: 30px 20px; display: flex; justify-content: center; margin: 0; }
            .card { background: #1c1a18; border: 1px solid #292524; padding: 40px; border-radius: 12px; width: 100%; max-width: 900px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
            h2 { color: #d4af37; text-align: center; text-transform: uppercase; font-size: 16px; letter-spacing: 2px; margin-top: 0; }
            p.sub { text-align: center; font-size: 12px; color: #a8a29e; margin-bottom: 30px; line-height: 1.6; }
            .section-title { color: #d4af37; font-size: 14px; text-transform: uppercase; border-bottom: 1px solid #292524; padding-bottom: 6px; margin: 35px 0 15px 0; font-weight: bold; letter-spacing: 1px; }
            .sub-section { color: #f5f2eb; font-size: 12.5px; font-weight: bold; margin: 20px 0 10px 0; text-transform: uppercase; }
            .form-group { margin-bottom: 16px; }
            label { display: block; font-size: 11.5px; color: #a8a29e; text-transform: uppercase; margin-bottom: 6px; font-weight: bold; line-height: 1.4; }
            input[type="text"], textarea, select { width: 100%; background: #121110; border: 1px solid #292524; border-radius: 6px; padding: 10px 14px; color: #f5f2eb; font-size: 13px; box-sizing: border-box; outline: none; }
            input[type="text"]:focus, textarea:focus, select:focus { border-color: #d4af37; }
            .checkbox-grid { display: grid; grid-template-columns: 1fr; gap: 8px; background: #121110; padding: 15px; border-radius: 6px; border: 1px solid #292524; }
            .checkbox-label { display: flex; align-items: center; font-size: 12px; color: #f5f2eb; font-weight: normal; cursor: pointer; text-transform: none; margin-bottom: 0; }
            .checkbox-label input { width: auto; margin-right: 10px; accent-color: #d4af37; }
            .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
            .btn { background: #d4af37; color: #090908; border: none; padding: 14px; border-radius: 6px; width: 100%; font-weight: bold; font-size: 13px; text-transform: uppercase; cursor: pointer; margin-top: 35px; letter-spacing: 1px; }
            .btn:hover { background: #e5c158; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Formulario de Pre-Consulta: Clínica Aeterna - Instituto de Optimización Humana</h2>
            <p class="sub">Bienvenido a Clínica Aeterna. Este cuestionario de pre-consulta es el primer paso en su viaje hacia la optimización humana. Nuestro enfoque de medicina funcional y longevidad requiere una comprensión profunda de su biología, entorno, hábitos y objetivos.<br><br>La información proporcionada aquí es estrictamente confidencial y permitirá a nuestro equipo médico diseñar una estrategia de evaluación 360° personalizada desde su primera visita a nuestro Instituto en Ciudad del Este.<br><b>Bienvenido/a, {{ paciente.nombre }}.</b></p>
            
            <form method="POST" action="/portal/pre-consulta/{{ paciente.id }}">
                
                <!-- 1. DATOS PERSONALES -->
                <div class="section-title">1. Datos Personales y de Contacto</div>
                <div class="form-group"><label>Nombre completo:</label><input type="text" name="nombre_completo" value="{{ paciente.nombre }}" required></div>
                <div class="grid-2">
                    <div class="form-group"><label>Fecha de nacimiento:</label><input type="text" name="fecha_nac" placeholder="DD/MM/AAAA"></div>
                    <div class="form-group"><label>Edad:</label><input type="text" name="edad" value="{{ paciente.edad }}"></div>
                </div>
                <div class="grid-2">
                    <div class="form-group"><label>Género:</label>
                        <select name="genero">
                            <option value="Femenino">[ ] Femenino</option>
                            <option value="Masculino">[ ] Masculino</option>
                            <option value="Otro">[ ] Otro</option>
                        </select>
                    </div>
                    <div class="form-group"><label>Nacionalidad:</label><input type="text" name="nacionalidad" placeholder="Paraguaya / Otra..."></div>
                </div>
                <div class="form-group"><label>Lugar de residencia (Ciudad/País):</label><input type="text" name="residencia" placeholder="Ciudad del Este, Paraguay"></div>
                <div class="form-group"><label>Profesión / Ocupación actual:</label><input type="text" name="profesion" placeholder="Ocupación..."></div>
                <div class="form-group"><label>Estado civil:</label><input type="text" name="estado_civil" placeholder="Soltero/a, Casado/a..."></div>
                <div class="form-group"><label>Teléfono (WhatsApp):</label><input type="text" name="telefono" placeholder="+595 981 ..."></div>
                <div class="form-group"><label>Correo electrónico:</label><input type="text" name="correo" placeholder="correo@dominio.com"></div>
                <div class="form-group"><label>Contacto de emergencia (Nombre y Teléfono):</label><input type="text" name="contacto_emergencia" placeholder="Nombre y Teléfono..."></div>

                <!-- 2. OBJETIVOS Y EXPECTATIVAS -->
                <div class="section-title">2. Objetivos y Expectativas (Visión High Ticket)</div>
                <p style="font-size: 11.5px; color: var(--text-secondary); margin-bottom: 10px;">En Clínica Aeterna no solo tratamos síntomas; optimizamos su rendimiento y extendemos su vitalidad.</p>
                <div class="form-group">
                    <label>¿Cuál es su objetivo principal al acudir a Clínica Aeterna? (Seleccione hasta 3)</label>
                    <div class="checkbox-grid">
                        <label class="checkbox-label"><input type="checkbox" name="obj" value="Aumentar niveles de energía y vitalidad diaria"> Aumentar mis niveles de energía y vitalidad diaria</label>
                        <label class="checkbox-label"><input type="checkbox" name="obj" value="Optimizar rendimiento físico y/o cognitivo"> Optimizar mi rendimiento físico y/o cognitivo</label>
                        <label class="checkbox-label"><input type="checkbox" name="obj" value="Prevenir enfermedades crónicas y envejecimiento acelerado"> Prevenir enfermedades crónicas y envejecimiento acelerado</label>
                        <label class="checkbox-label"><input type="checkbox" name="obj" value="Mejorar composición corporal (pérdida de grasa, ganancia muscular)"> Mejorar mi composición corporal (pérdida de grasa, ganancia muscular)</label>
                        <label class="checkbox-label"><input type="checkbox" name="obj" value="Resolver problemas digestivos crónicos"> Resolver problemas digestivos crónicos</label>
                        <label class="checkbox-label"><input type="checkbox" name="obj" value="Equilibrar hormonas (libido, menopausia, andropausia)"> Equilibrar mis hormonas (libido, menopausia, andropausia)</label>
                        <label class="checkbox-label"><input type="checkbox" name="obj" value="Mejorar calidad de sueño y recuperación"> Mejorar la calidad de mi sueño y recuperación</label>
                    </div>
                </div>
                <div class="form-group"><label>Describa brevemente su principal queja de salud actual (si la hay):</label><textarea name="queja" rows="2" placeholder="Descripción..."></textarea></div>
                <div class="form-group"><label>¿Cómo calificaría su estado de salud actual en una escala del 1 al 10?</label><input type="text" name="salud_actual" placeholder="Ej: 7/10"></div>
                <div class="form-group"><label>¿Qué impacto tendría en su vida alcanzar sus objetivos de salud?</label><textarea name="impacto_vida" rows="2" placeholder="Describa el impacto..."></textarea></div>

                <!-- 3. HISTORIAL MÉDICO -->
                <div class="section-title">3. Historial Médico y Antecedentes</div>
                <div class="form-group"><label>¿Ha sido diagnosticado con alguna enfermedad crónica? (Diabetes, Hipertensión, Autoinmunidad, Cáncer, Hipotiroidismo):</label><input type="text" name="antecedentes" placeholder="[ ] No [ ] Sí. ¿Cuáles?: ..."></div>
                <div class="form-group"><label>¿Ha tenido cirugías u hospitalizaciones previas?</label><input type="text" name="cirugias" placeholder="[ ] No [ ] Sí. Especifique y año: ..."></div>
                <div class="form-group"><label>Antecedentes familiares relevantes (Padres, abuelos, hermanos con enfermedades crónicas o autoinmunes):</label><textarea name="ant_familiares" rows="2" placeholder="Antecedentes..."></textarea></div>
                <div class="form-group"><label>¿Tiene alergias o intolerancias conocidas? (Medicamentos, alimentos, ambientales):</label><input type="text" name="alergias" placeholder="Alergias..."></div>

                <!-- 4. MEDICAMENTOS Y SUPLEMENTOS -->
                <div class="section-title">4. Medicamentos, Suplementos y Terapias</div>
                <div class="form-group"><label>Enumere todos los medicamentos recetados que toma actualmente (incluya dosis):</label><textarea name="medicamentos" rows="2" placeholder="Medicamentos y dosis..."></textarea></div>
                <div class="form-group"><label>Enumere todos los suplementos, vitaminas o péptidos que consume actualmente:</label><textarea name="suplementos_actuales" rows="2" placeholder="Suplementos..."></textarea></div>
                <div class="form-group"><label>¿Ha utilizado terapias de reemplazo hormonal (TRH), implantes o pellets?</label><input type="text" name="trh" placeholder="[ ] No [ ] Sí. Especifique: ..."></div>
                <div class="form-group"><label>¿Se ha realizado estudios genéticos, microbioma o epigenéticos previamente?</label><input type="text" name="estudios_geneticos" placeholder="[ ] No [ ] Sí. Especifique: ..."></div>

                <!-- 5. HÁBITOS DE VIDA Y ENTORNO -->
                <div class="section-title">5. Hábitos de Vida y Entorno (Evaluación 360°)</div>
                <div class="sub-section">A. Nutrición y Digestión</div>
                <div class="form-group"><label>¿Cómo describiría su patrón alimentario actual? (Ej. Omnívoro, Keto, Vegano, Ayuno intermitente, Mediterráneo):</label><input type="text" name="nutricion" placeholder="Patrón alimentario..."></div>
                <div class="form-group"><label>¿Con qué frecuencia consume alimentos ultraprocesados o azúcares refinados?</label><input type="text" name="procesados" placeholder="[ ] Nunca [ ] 1-2 veces/sem [ ] 3-5 veces/sem [ ] Diario"></div>
                <div class="form-group"><label>¿Sufre de síntomas digestivos frecuentes? (Hinchazón, gases, reflujo, estreñimiento, diarrea):</label><input type="text" name="sintomas_digestivos" placeholder="[ ] No [ ] Sí. Especifique: ..."></div>
                <div class="form-group"><label>Consumo de agua diario aproximado:</label><input type="text" name="agua" placeholder="Ej: 2.5 Litros"></div>

                <div class="sub-section">B. Sueño y Recuperación</div>
                <div class="grid-2">
                    <div class="form-group"><label>¿Cuántas horas duerme en promedio por noche?</label><input type="text" name="sueno_horas" placeholder="7.5 horas"></div>
                    <div class="form-group"><label>Calidad del sueño:</label><input type="text" name="sueno_calidad" placeholder="[ ] Excelente [ ] Regular [ ] Mala"></div>
                </div>
                
                <div class="form-group"><label>¿Utiliza algún dispositivo wearable o sistema de monitoreo de sueño y/o rendimiento?</label>
                    <div class="checkbox-grid">
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="No utilizo ningún dispositivo"> [ ] No utilizo ningún dispositivo de este tipo.</label>
                        
                        <div style="font-size: 11.5px; color: #d4af37; font-weight: bold; margin-top: 8px;">Anillos inteligentes (Smart Rings):</div>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Oura Ring (Gen 3 / 4 / 5)"> • Oura Ring (Gen 3 / 4 / 5)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Ultrahuman Ring AIR"> • Ultrahuman Ring AIR</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Samsung Galaxy Ring"> • Samsung Galaxy Ring</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="RingConn Smart Ring"> • RingConn Smart Ring</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Sleepon Go2Sleep"> • Sleepon Go2Sleep</label>

                        <div style="font-size: 11.5px; color: #d4af37; font-weight: bold; margin-top: 8px;">Relojes inteligentes y pulseras (Smartwatches / Fitness Bands):</div>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Apple Watch (Series 9 / 10 / 11 / Ultra / SE)"> • Apple Watch (Series 9 / 10 / 11 / Ultra / SE)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Samsung Galaxy Watch (7 / Ultra / FE)"> • Samsung Galaxy Watch (7 / Ultra / FE)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Garmin (Fenix / Forerunner / Venu / Vívoactive / Epix)"> • Garmin (Fenix / Forerunner / Venu / Vívoactive / Epix)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="WHOOP 4.0 / 5.0 / MG"> • WHOOP 4.0 / 5.0 / MG</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Google Pixel Watch (3 / 4)"> • Google Pixel Watch (3 / 4)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Fitbit (Charge / Sense / Versa)"> • Fitbit (Charge / Sense / Versa)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Polar (Ignite / Vantage / Pacer)"> • Polar (Ignite / Vantage / Pacer)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Amazfit (Active / Balance / GTR / GTS)"> • Amazfit (Active / Balance / GTR / GTS)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Huawei Watch (GT / Fit)"> • Huawei Watch (GT / Fit)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Withings ScanWatch (2 / Nova)"> • Withings ScanWatch (2 / Nova)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Xiaomi Smart Band"> • Xiaomi Smart Band</label>

                        <div style="font-size: 11.5px; color: #d4af37; font-weight: bold; margin-top: 8px;">Dispositivos no portables (Non-Wearables):</div>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Eight Sleep Pod (3/4/Ultra)"> • Eight Sleep Pod (3 / 4 / Ultra) — colchón inteligente</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Withings Sleep Analyzer"> • Withings Sleep Analyzer — sensor bajo el colchón</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Google Nest Hub (2ª gen)"> • Google Nest Hub (2ª gen) — monitoreo sin contacto</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Garmin Index Sleep Monitor"> • Garmin Index Sleep Monitor — brazalete nocturno</label>

                        <div style="font-size: 11.5px; color: #d4af37; font-weight: bold; margin-top: 8px;">Dispositivos de biofeedback y neurología del sueño:</div>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Muse S Athena"> • Muse S Athena — diadema EEG de ondas cerebrales</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Bía Smart Sleep Mask"> • Bía Smart Sleep Mask — antifaz con sensores fNIRS</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Dreem 2"> • Dreem 2 — diadema EEG clínica</label>

                        <div style="font-size: 11.5px; color: #d4af37; font-weight: bold; margin-top: 8px;">Aplicaciones de análisis (sin hardware adicional):</div>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Rise Science"> • Rise Science (deuda de sueño y ritmo circadiano)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Sleep Cycle"> • Sleep Cycle (app con micrófono)</label>
                        <label class="checkbox-label"><input type="checkbox" name="wearable" value="Pillow"> • Pillow (app para iPhone/Apple Watch)</label>
                    </div>
                </div>

                <div class="form-group"><label>Otro dispositivo no listado / Otra app:</label><input type="text" name="otro_dispositivo" placeholder="Especifique..."></div>
                <div class="form-group"><label>¿Estaría dispuesto a compartir sus datos de sueño con nuestro equipo médico?</label><input type="text" name="compartir_sueno" placeholder="[ ] Sí [ ] No [ ] Necesito más información"></div>

                <div class="sub-section">C. Actividad Física y Movimiento</div>
                <div class="grid-2">
                    <div class="form-group"><label>¿Cuántos días a la semana realiza ejercicio estructurado?</label><input type="text" name="dias_ejercicio" placeholder="Ej: 4 días"></div>
                    <div class="form-group"><label>Tipo de entrenamiento principal:</label><input type="text" name="tipo_entrenamiento" placeholder="Fuerza, Cardio, HIIT, Yoga..."></div>
                </div>
                <div class="form-group"><label>¿Siente dolor articular o limitaciones físicas al moverse?</label><input type="text" name="dolor_articular" placeholder="[ ] No [ ] Sí. Especifique: ..."></div>

                <div class="sub-section">D. Estrés, Entorno y Salud Mental</div>
                <div class="form-group"><label>En una escala del 1 al 10, ¿cuál es su nivel de estrés promedio diario?</label><input type="text" name="estres" placeholder="Ej: 6/10"></div>
                <div class="form-group"><label>¿Cómo maneja el estrés actualmente? (Meditación, respiración, hobbies, terapia):</label><input type="text" name="manejo_estres" placeholder="Estrategias..."></div>
                <div class="form-group"><label>¿Está expuesto regularmente a toxinas ambientales? (Moho, metales pesados, químicos):</label><input type="text" name="toxinas" placeholder="[ ] No [ ] Sí / No estoy seguro"></div>

                <!-- 6. SALUD HORMONAL Y ENERGÍA -->
                <div class="section-title">6. Salud Hormonal y Energía</div>
                <div class="form-group"><label>Nivel de energía promedio durante el día (1-10):</label><input type="text" name="energia_dia" placeholder="Ej: 7/10"></div>
                <div class="form-group"><label>¿Experimenta "bajones" de energía en momentos específicos del día? (¿A qué hora?):</label><input type="text" name="bajones_energia" placeholder="[ ] No [ ] Sí. Hora: ..."></div>
                <div class="form-group"><label>¿Ha notado cambios recientes en su libido (deseo sexual) o rendimiento sexual?</label><input type="text" name="libido" placeholder="[ ] No [ ] Sí. Especifique: ..."></div>
                <div class="form-group"><label>(Solo mujeres) Describa su ciclo menstrual o estado de menopausia:</label><input type="text" name="ciclo_menstrual" placeholder="N/A o descripción..."></div>

                <!-- 7. PRÓXIMOS PASOS Y COMPROMISO -->
                <div class="section-title">7. Próximos Pasos y Compromiso</div>
                <p style="font-size: 11.5px; color: var(--text-secondary); margin-bottom: 10px;">En Clínica Aeterna, la optimización humana es un trabajo en equipo. Requerimos su compromiso activo con los protocolos diseñados para usted.</p>
                <div class="form-group">
                    <label>¿Está dispuesto a realizar cambios significativos en su estilo de vida, nutrición y rutinas para alcanzar sus objetivos de salud?</label>
                    <select name="compromiso">
                        <option value="Sí, estoy 100% comprometido.">Sí, estoy 100% comprometido.</option>
                        <option value="Estoy dispuesto, pero necesito mucha guía y apoyo.">Estoy dispuesto, pero necesito mucha guía y apoyo.</option>
                        <option value="Me cuesta hacer cambios, prefiero intervenciones médicas directas.">Me cuesta hacer cambios, prefiero intervenciones médicas directas.</option>
                    </select>
                </div>
                <div class="form-group"><label>¿Tiene exámenes de laboratorio recientes (últimos 6 meses) que pueda aportar a su primera consulta?</label><input type="text" name="lab_recientes" placeholder="[ ] Sí, los llevaré/enviaré [ ] No"></div>

                <button type="submit" class="btn">Enviar Cuestionario 360° al Instituto</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(portal_template, paciente=paciente)

@app.route('/portal/pre-consulta/<id_paciente>', methods=['POST'])
def portal_preconsulta_guardar(id_paciente):
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        objetivos = request.form.getlist('obj')
        wearables_sel = request.form.getlist('wearable')
        
        paciente['pre_consulta'] = {
            "nombre_completo": request.form.get('nombre_completo', paciente['nombre']),
            "fecha_nac": request.form.get('fecha_nac', 'N/A'),
            "edad": request.form.get('edad', str(paciente['edad'])),
            "genero": request.form.get('genero', 'N/A'),
            "nacionalidad": request.form.get('nacionalidad', 'N/A'),
            "residencia": request.form.get('residencia', 'N/A'),
            "profesion": request.form.get('profesion', 'N/A'),
            "estado_civil": request.form.get('estado_civil', 'N/A'),
            "telefono": request.form.get('telefono', 'N/A'),
            "correo": request.form.get('correo', 'N/A'),
            "contacto_emergencia": request.form.get('contacto_emergencia', 'N/A'),
            "objetivos": ", ".join(objetivos) if objetivos else "Optimización general",
            "queja": request.form.get('queja', 'N/A'),
            "salud_actual": request.form.get('salud_actual', 'N/A'),
            "impacto_vida": request.form.get('impacto_vida', 'N/A'),
            "antecedentes": request.form.get('antecedentes', 'Ninguno'),
            "cirugias": request.form.get('cirugias', 'Ninguna'),
            "ant_familiares": request.form.get('ant_familiares', 'Ninguno'),
            "alergias": request.form.get('alergias', 'Ninguna'),
            "medicamentos": request.form.get('medicamentos', 'Ninguno'),
            "suplementos_actuales": request.form.get('suplementos_actuales', 'Ninguno'),
            "trh": request.form.get('trh', 'No'),
            "estudios_geneticos": request.form.get('estudios_geneticos', 'No'),
            "nutricion": request.form.get('nutricion', 'N/A'),
            "procesados": request.form.get('procesados', 'N/A'),
            "sintomas_digestivos": request.form.get('sintomas_digestivos', 'N/A'),
            "agua": request.form.get('agua', 'N/A'),
            "sueno_horas": request.form.get('sueno_horas', '7 horas'),
            "sueno_calidad": request.form.get('sueno_calidad', 'N/A'),
            "wearable": ", ".join(wearables_sel) if wearables_sel else "Ninguno",
            "otro_dispositivo": request.form.get('otro_dispositivo', 'N/A'),
            "compartir_sueno": request.form.get('compartir_sueno', 'N/A'),
            "dias_ejercicio": request.form.get('dias_ejercicio', 'N/A'),
            "tipo_entrenamiento": request.form.get('tipo_entrenamiento', 'N/A'),
            "dolor_articular": request.form.get('dolor_articular', 'No'),
            "estres": request.form.get('estres', 'N/A'),
            "manejo_estres": request.form.get('manejo_estres', 'N/A'),
            "toxinas": request.form.get('toxinas', 'No'),
            "energia_dia": request.form.get('energia_dia', 'N/A'),
            "bajones_energia": request.form.get('bajones_energia', 'No'),
            "libido": request.form.get('libido', 'No'),
            "ciclo_menstrual": request.form.get('ciclo_menstrual', 'N/A'),
            "compromiso": request.form.get('compromiso', 'Alto'),
            "lab_recientes": request.form.get('lab_recientes', 'No'),
            "estado": "Completado 🟢"
        }
    
    gracias_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>¡Completado! | Instituto Aeterna</title>
        <style>
            body { font-family: 'Inter', system-ui, sans-serif; background-color: #121110; color: #f5f2eb; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
            .box { background: #1c1a18; border: 1px solid #292524; padding: 40px; border-radius: 12px; max-width: 400px; box-shadow: 0 15px 30px rgba(0,0,0,0.5); }
            h2 { color: #d4af37; text-transform: uppercase; font-size: 15px; margin-top: 0; }
            p { font-size: 13px; color: #a8a29e; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>¡Formulario Recibido!</h2>
            <p>Gracias. Sus respuestas han sido sincronizadas de manera automática y segura en su expediente clínico para su consulta en el Instituto Aeterna.</p>
            <p style="font-size: 11px; margin-top: 25px; color: #555770;">Ya puede cerrar esta ventana.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(gracias_template)

# ==========================================
# RUTA PRINCIPAL Y CONTROLADORES
# ==========================================

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    rol_base = session.get('rol_base', 'medico')
    es_socio = session.get('es_socio', False)
    nombre_usuario = session.get('nombre', 'Profesional')
    
    requested_rol = request.args.get('rol')
    if es_socio and requested_rol in ['medico', 'secretaria']:
        rol = requested_rol
        if rol == 'secretaria':
            nombre_usuario = nombre_usuario.replace(" (Admin)", "") + " (Admin)"
        else:
            nombre_usuario = nombre_usuario.replace(" (Admin)", "")
    elif rol_base == 'secretaria':
        rol = 'secretaria'
    elif rol_base == 'entrenador':
        rol = 'entrenador'
    else:
        rol = requested_rol if (requested_rol == 'medico' and rol_base == 'medico') else rol_base

    seccion = request.args.get('seccion', 'agenda_medico' if rol == 'medico' else ('agenda_entrenador' if rol == 'entrenador' else 'caja'))
    id_paciente = request.args.get('id', 'p1')
    
    paciente_actual = next((p for p in PACIENTES if p['id'] == id_paciente), PACIENTES[0])
    
    total_recaudado = sum(item["monto"] for item in db_caja_pagos)
    total_gastos = sum(item["monto"] for item in db_gastos_operativos)
    balance_neto = total_recaudado - total_gastos

    desglose_metodos = {
        "Efectivo": sum(i["monto"] for i in db_caja_pagos if i["metodo"] == "Efectivo"),
        "Tarjeta": sum(i["monto"] for i in db_caja_pagos if i["metodo"] == "Tarjeta"),
        "Transferencia": sum(i["monto"] for i in db_caja_pagos if i["metodo"] == "Transferencia")
    }

    porc_efectivo = int((desglose_metodos["Efectivo"] / total_recaudado * 100) if total_recaudado > 0 else 0)
    porc_tarjeta = int((desglose_metodos["Tarjeta"] / total_recaudado * 100) if total_recaudado > 0 else 0)
    porc_transf = int((desglose_metodos["Transferencia"] / total_recaudado * 100) if total_recaudado > 0 else 0)

    return render_template_string(
        HTML_TEMPLATE, 
        rol=rol, 
        es_socio=es_socio,
        nombre_usuario=nombre_usuario,
        seccion=seccion, 
        p=paciente_actual, 
        pacientes=PACIENTES,
        pagos=db_caja_pagos,
        cuentas=db_cuentas_cobrar,
        gastos=db_gastos_operativos,
        honorarios=db_honorarios_medicos,
        total_recaudado=total_recaudado,
        total_gastos=total_gastos,
        balance_neto=balance_neto,
        desglose=desglose_metodos,
        porcs={"tarjeta": porc_tarjeta, "transf": porc_transf, "efectivo_val": porc_efectivo}
    )

@app.route('/api/admin/registrar-pago', methods=['POST'])
def registrar_pago_admin():
    data = request.get_json() if request.is_json else request.form
    cdc_generado = "800" + "".join([str(random.randint(0, 9)) for _ in range(41)])
    nuevo_pago = {
        "id": len(db_caja_pagos) + 1,
        "paciente": data.get("paciente", "Paciente General"),
        "monto": float(data.get("monto", 0.0)),
        "metodo": data.get("metodo", "Efectivo"),
        "referencia": data.get("referencia", "N/A"),
        "estado": "Completado", "fecha": "2026-10-20",
        "sifen_status": "Aprobado Sifen", "cdc": cdc_generado
    }
    db_caja_pagos.append(nuevo_pago)
    return jsonify({"status": "success", "pago": nuevo_pago})

@app.route('/api/admin/ver-kude/<int:pago_id>')
def ver_kude(pago_id):
    pago = next((item for item in db_caja_pagos if item['id'] == pago_id), db_caja_pagos[0])
    return f"""
    <html>
    <head><title>KUDE - Factura Electrónica Sifen - Instituto Aeterna E.A.S.</title>
    <style>
        body {{ font-family: monospace; padding: 30px; background: #fff; color: #000; max-width: 600px; margin: auto; border: 1px solid #ccc; }}
        h2, h4 {{ text-align: center; margin: 5px 0; }}
        .line {{ border-bottom: 1px dashed #000; margin: 15px 0; }}
        .qr {{ text-align: center; margin: 20px 0; }}
    </style>
    </head>
    <body>
        <h2>INSTITUTO AETERNA E.A.S.</h2>
        <h4>RUC: 80172292-6</h4>
        <p style="text-align: center; font-size: 11px;">Avenida Guido Spano, c/ San José — CDE, Paraguay.<br>Sanatorio Le Blanc, 3er piso, torre D.</p>
        <div class="line"></div>
        <p><b>TIMBRADO N°:</b> 12893812</p>
        <p><b>FACTURA ELECTRÓNICA N°:</b> 001-001-{pago_id:07d}</p>
        <p><b>CDC:</b> {pago['cdc']}</p>
        <div class="line"></div>
        <p><b>FECHA:</b> {pago['fecha']}</p>
        <p><b>CLIENTE:</b> {pago['paciente']}</p>
        <p><b>MÉTODO DE PAGO:</b> {pago['metodo']} ({pago['referencia']})</p>
        <div class="line"></div>
        <table width="100%">
            <tr><td><b>CONCEPTO</b></td><td style="text-align: right;"><b>MONTO (Gs.)</b></td></tr>
            <tr><td>Programa Longevidad & Optimización Aeterna</td><td style="text-align: right;">{pago['monto']:,.0f}</td></tr>
        </table>
        <div class="line"></div>
        <h4 style="text-align: right;">TOTAL A PAGAR: Gs. {pago['monto']:,.0f}</h4>
        <div class="qr">
            <p style="font-size: 10px;">[ CÓDIGO QR TRIBUTARIO DNIT ]</p>
            <svg width="100" height="100" viewBox="0 0 20 20">
                <path fill="#000" d="M0 0h7v7H0zM2 2h3v3H2zM13 0h7v7h-7zM15 2h3v3h-3zM0 13h7v7H0zM2 15h3v3H2zM9 2h2v2H9zM15 13h2v2H-2zM13 15h2v2H-2zM17 17h3v3h-3zM9 9h2v2H9zM13 9h2v2H9zM9 13h2v2H9zM17 9h2v2H-2z"/>
            </svg>
        </div>
        <p style="text-align: center; font-size: 10px;">Consulte su factura electrónica en la web de la DNIT con el CDC.<br>Correo receptor: institutoaeterna.py@gmail.com</p>
        <div style="text-align: center; margin-top: 20px;" class="no-print">
            <button onclick="window.print()" style="padding: 10px 20px; font-weight: bold; cursor: pointer;">Imprimir KUDE</button>
        </div>
    </body>
    </html>
    """

@app.route('/api/admin/exportar-caja', methods=['GET'])
def exportar_cierre_caja():
    csv_data = "ID,Paciente,Monto,Metodo,Referencia,Estado,SifenStatus,CDC,Fecha\n"
    for item in db_caja_pagos:
        csv_data += f"{item['id']},{item['paciente']},{item['monto']},{item['metodo']},{item['referencia']},{item['estado']},{item['sifen_status']},{item['cdc']},{item['fecha']}\n"
    return Response(csv_data, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=cierre_caja_sifen_aeterna.csv"})

@app.route('/api/generar-pdf/<id_paciente>')
def generar_pdf(id_paciente):
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), PACIENTES[0])
    report_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte Integral de Longevidad - {{ paciente.nombre }}</title>
        <style>
            body { font-family: 'Inter', Arial, sans-serif; padding: 40px; color: #121110; background: #fff; max-width: 800px; margin: auto; }
            .header { border-bottom: 2px solid #b8860b; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-start; }
            .title { color: #b8860b; font-size: 18px; text-transform: uppercase; margin: 0; font-weight: bold; }
            .subtitle { font-size: 11px; color: #555; margin: 3px 0 0 0; }
            .badge { font-size: 10px; background: #f4f6f9; padding: 4px 10px; border: 1px solid #d1d5db; font-weight: bold; color: #b8860b; border-radius: 4px; }
            .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #f9fafb; padding: 15px; border-radius: 6px; margin-bottom: 25px; font-size: 12.5px; border: 1px solid #e5e7eb; }
            .section-title { color: #b8860b; font-size: 13.5px; text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 25px; margin-bottom: 10px; font-weight: bold; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px; }
            th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid #ddd; font-size: 12px; }
            th { background: #f3f4f6; color: #374151; text-transform: uppercase; font-size: 10.5px; }
            p { font-size: 12.5px; line-height: 1.5; color: #333; }
            .footer { margin-top: 40px; border-top: 1px solid #b8860b; padding-top: 15px; display: flex; justify-content: space-between; font-size: 10.5px; color: #666; }
            @media print {
                .no-print { display: none !important; }
                body { padding: 10px; }
            }
        </style>
    </head>
    <body>
        <div class="no-print" style="margin-bottom: 20px; text-align: right;">
            <button onclick="window.print()" style="background: #b8860b; color: #fff; border: none; padding: 10px 20px; font-weight: bold; border-radius: 4px; cursor: pointer; text-transform: uppercase;">Imprimir / Guardar PDF</button>
        </div>

        <div class="header">
            <div>
                <h2 class="title">Instituto Aeterna E.A.S.</h2>
                <p class="subtitle">Avenida Guido Spano, c/ San José — CDE, Paraguay (Sanatorio Le Blanc, 3er piso, torre D)</p>
            </div>
            <div>
                <span class="badge">REPORTE INTEGRAL VIP</span>
            </div>
        </div>

        <h3 style="margin: 0 0 5px 0; color: #111; font-size: 16px;">Informe Biológico & Clínico de Paciente</h3>
        <p style="color: #666; font-size: 11.5px; margin-bottom: 20px;">RUC: 80172292-6</p>

        <div class="info-grid">
            <div>
                <p style="margin: 3px 0;"><b>Paciente:</b> {{ paciente.nombre }} ({{ paciente.edad }} años)</p>
                <p style="margin: 3px 0;"><b>Programa:</b> {{ paciente.programa }}</p>
            </div>
            <div>
                <p style="margin: 3px 0;"><b>Médica Tratante:</b> {{ paciente.medico }}</p>
                <p style="margin: 3px 0;"><b>Entrenador:</b> {{ paciente.entrenador }}</p>
            </div>
        </div>

        <div class="section-title">1. Plan de Rendimiento Físico & Entrenamiento</div>
        <p><b>Enfoque:</b> {{ paciente.entrenamiento.enfoque }}</p>
        <p><b>Frecuencia:</b> {{ paciente.entrenamiento.sesiones_semanales }}</p>
        <p><b>Prescripción:</b><br>{{ paciente.entrenamiento.prescripcion_ejercicio | replace('\n', '<br>') | safe }}</p>

        <div class="footer">
            <div>
                <p style="margin: 0;"><b>Médica:</b> {{ paciente.medico }} | <b>Entrenador:</b> {{ paciente.entrenador }}</p>
                <p style="margin: 2px 0 0 0;">Instituto Aeterna E.A.S. — Medicina de Precisión</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-family: monospace;">Hash: AE-REP-2026-9982X</p>
                <p style="margin: 2px 0 0 0; color: #059669; font-weight: bold;">Certificado Digital Aeterna</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(report_template, paciente=paciente)

@app.route('/api/entrenador/guardar-entrenamiento', methods=['POST'])
def guardar_entrenamiento():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        paciente['entrenamiento']['enfoque'] = data.get('enfoque', paciente['entrenamiento']['enfoque'])
        paciente['entrenamiento']['sesiones_semanales'] = data.get('sesiones', paciente['entrenamiento']['sesiones_semanales'])
        paciente['entrenamiento']['prescripcion_ejercicio'] = data.get('prescripcion', paciente['entrenamiento']['prescripcion_ejercicio'])
        return jsonify({"status": "success", "mensaje": "Plan de entrenamiento actualizado correctamente."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-evolucion', methods=['POST'])
def guardar_evolucion():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    evolucion_texto = data.get('evolucion', '(Sin nota)')
    
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        nueva_consulta = {
            "fecha": "20/10/2026",
            "medico": paciente['medico'],
            "evolucion": evolucion_texto,
        }
        paciente['historial_consultas'].insert(0, nueva_consulta)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-solicitud-lab', methods=['POST'])
def guardar_solicitud_lab():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    estudios = data.get('estudios', 'Perfil Genérico de Longevidad')
    
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        nueva_solicitud = {
            "fecha": "20/10/2026",
            "estudios": estudios,
            "estado": "Pendiente de LIS"
        }
        paciente['solicitudes_lab_previas'].insert(0, nueva_solicitud)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/sincronizar-lis', methods=['POST'])
def sincronizar_lis():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        for sol in paciente['solicitudes_lab_previas']:
            if "Pendiente" in sol['estado']:
                sol['estado'] = "Completado y Sincronizado"
        return jsonify({"status": "success", "mensaje": "Resultados de laboratorio sincronizados desde LIS externo."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-biomarcador-manual', methods=['POST'])
def guardar_biomarcador_manual():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    parametro_ingresado = data.get('parametro', '').strip().lower()
    fecha = data.get('fecha', '20/10/2026')
    try:
        valor = float(data.get('valor', 0))
    except ValueError:
        valor = 0.0
    unidad = data.get('unidad', 'mg/dL')
    
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        encontrado = False
        for bio in paciente['biomarcadores_longitudinales']:
            if bio['parametro'].strip().lower() == parametro_ingresado:
                bio['historial'].append({"fecha": fecha, "valor": valor, "unidad": unidad})
                encontrado = True
                break
        
        if not encontrado:
            paciente['biomarcadores_longitudinales'].append({
                "parametro": data.get('parametro', 'Nuevo Biomarcador'),
                "rango_optimo": "Personalizado",
                "historial": [{"fecha": fecha, "valor": valor, "unidad": unidad}]
            })
            
        return jsonify({"status": "success", "mensaje": "Resultado biométrico manual registrado e integrado a la línea de tiempo."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-informe-directo-nolab', methods=['POST'])
def guardar_informe_directo_nolab():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    tipo_estudio = data.get('tipo', 'Estudio Clínico No Lab')
    informe_texto = data.get('informe', '')
    
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        nuevo_registro = {
            "fecha": "20/10/2026",
            "tipo": tipo_estudio,
            "archivo": "Informe Directo (Texto)",
            "medico": paciente['medico'],
            "estado": "Redactado Directo",
            "informe": informe_texto
        }
        paciente['archivos_no_lab'].insert(0, nuevo_registro)
        return jsonify({"status": "success", "mensaje": "Informe no laboratorial redactado y guardado en expediente."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-receta-texto', methods=['POST'])
def guardar_receta_texto():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    receta_texto = data.get('receta_texto', '')
    
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        paciente['receta_texto'] = receta_texto
        return jsonify({"status": "success", "mensaje": "Receta A5 guardada y actualizada correctamente."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-regenerativa', methods=['POST'])
def guardar_regenerativa():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        paciente['regenerativa_dx'] = data.get('dx', '')
        sesiones = []
        for i in range(1, 5):
            sesiones.append({
                "sesion": f"Sesión 0{i}",
                "fecha": data.get(f"fecha_{i}", "-"),
                "protocolo": data.get(f"protocolo_{i}", "-"),
                "observaciones": data.get(f"obs_{i}", "-")
            })
        paciente['regenerativa_sesiones'] = sesiones
        return jsonify({"status": "success", "mensaje": "Protocolo de Medicina Regenerativa actualizado correctamente."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-wearables', methods=['POST'])
def guardar_wearables():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        paciente['wearables']['dispositivo'] = data.get('dispositivo', paciente['wearables']['dispositivo'])
        paciente['wearables']['sueno_horas'] = data.get('sueno', paciente['wearables']['sueno_horas'])
        paciente['wearables']['hrv'] = data.get('hrv', paciente['wearables']['hrv'])
        paciente['wearables']['frecuencia_cardiaca_reposo'] = data.get('fcr', paciente['wearables']['frecuencia_cardiaca_reposo'])
        paciente['wearables']['strain_esfuerzo'] = data.get('strain', paciente['wearables']['strain_esfuerzo'])
        paciente['wearables']['observaciones'] = data.get('obs', paciente['wearables']['observaciones'])
        return jsonify({"status": "success", "mensaje": "Métricas de Wearables actualizadas correctamente."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/registrar-consentimiento', methods=['POST'])
def registrar_consentimiento():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    titulo = data.get('titulo', 'Consentimiento Informado')
    
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        nuevo_cons = {
            "titulo": titulo,
            "fecha": "20/10/2026",
            "estado": "Emitido & Firmado"
        }
        paciente['consentimientos_firmados'].insert(0, nuevo_cons)
        return jsonify({"status": "success", "mensaje": "Consentimiento registrado y asociado al expediente."})
    return jsonify({"status": "error"}), 404

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso — Instituto Aeterna E.A.S.</title>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; background-color: #f4f6f9; color: #121110; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: #ffffff; border: 1px solid #d1d5db; padding: 40px; border-radius: 8px; width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); }
        h2 { color: #b8860b; text-align: center; text-transform: uppercase; font-size: 15px; letter-spacing: 1.5px; margin-top: 0; }
        p.sub { text-align: center; font-size: 11px; color: #555770; margin-bottom: 25px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 11px; color: #555770; text-transform: uppercase; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; background: #f9fafb; border: 1px solid #d1d5db; border-radius: 6px; padding: 10px 12px; color: #121110; font-size: 13px; box-sizing: border-box; outline: none; }
        input:focus { border-color: #b8860b; }
        .btn { background: #b8860b; color: #ffffff; border: none; padding: 12px; border-radius: 6px; width: 100%; font-weight: bold; font-size: 12px; text-transform: uppercase; cursor: pointer; margin-top: 10px; }
        .btn:hover { background: #996f05; }
        .error { color: #dc2626; font-size: 12px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Instituto Aeterna E.A.S.</h2>
        <p class="sub">RUC: 80172292-6 — Sanatorio Le Blanc (CDE)</p>
        
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label>Usuario:</label>
                <input type="text" name="username" required placeholder="Ingrese su usuario..." autofocus>
            </div>
            <div class="form-group">
                <label>Contraseña:</label>
                <input type="password" name="password" required placeholder="••••••••">
            </div>
            <button type="submit" class="btn">Iniciar Sesión</button>
        </form>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instituto Aeterna E.A.S. — Sistema de Gestión</title>
    <style>
        :root {
            --bg-main: #121110; --sidebar-bg: #090908; --card-bg: #1c1a18;
            --text-primary: #f5f2eb; --text-secondary: #a8a29e; --accent: #d4af37;
            --accent-hover: #e5c158; --border: #292524; --success: #34d399; --warning: #f59e0b;
        }
        body.light-mode {
            --bg-main: #f4f6f9; --sidebar-bg: #ffffff; --card-bg: #ffffff;
            --text-primary: #121110; --text-secondary: #555770; --accent: #b8860b;
            --accent-hover: #996f05; --border: #d1d5db; --success: #059669; --warning: #d97706;
        }
        body { font-family: 'Inter', system-ui, sans-serif; background-color: var(--bg-main); margin: 0; color: var(--text-primary); display: flex; height: 100vh; overflow: hidden; transition: background 0.3s, color 0.3s; }
        .sidebar { width: 280px; background-color: var(--sidebar-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 24px; box-sizing: border-box; flex-shrink: 0; overflow-y: auto; }
        .sidebar h2 { font-size: 13px; letter-spacing: 1.5px; color: var(--accent); margin-top: 0; margin-bottom: 6px; font-weight: 700; text-transform: uppercase; }
        .sidebar-subtitle { font-size: 11px; color: var(--text-secondary); margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }
        .menu-section-title { font-size: 10px; color: var(--accent); text-transform: uppercase; letter-spacing: 1.5px; margin: 18px 0 6px 10px; font-weight: bold; }
        .sidebar a { color: var(--text-secondary); text-decoration: none; padding: 10px 14px; border-radius: 6px; margin-bottom: 3px; font-size: 13px; font-weight: 500; display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
        .sidebar a:hover, .sidebar a.active { background-color: var(--border); color: var(--text-primary); border-left: 2px solid var(--accent); }
        .main-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; background: radial-gradient(circle at top right, #1a1715 0%, #121110 60%); }
        body.light-mode .main-content { background: radial-gradient(circle at top right, #ffffff 0%, #f4f6f9 60%); }
        header { background-color: rgba(9, 9, 8, 0.85); backdrop-filter: blur(10px); padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 10; }
        body.light-mode header { background-color: rgba(255, 255, 255, 0.85); }
        .container { padding: 32px; max-width: 1300px; margin: 0 auto; width: 100%; box-sizing: border-box; }
        .role-btn { background: var(--card-bg); color: var(--text-secondary); border: 1px solid var(--border); padding: 6px 14px; border-radius: 4px; font-size: 11.5px; font-weight: 600; cursor: pointer; text-decoration: none; }
        .role-btn.active { background: var(--accent); color: #090908; border-color: var(--accent); font-weight: 700; }
        .box { background: var(--card-bg); padding: 28px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 24px; }
        .box h3 { margin-top: 0; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 12px; font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
        .badge-pill { background: rgba(212, 175, 55, 0.1); color: var(--accent); padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; border: 1px solid rgba(212, 175, 55, 0.2); display: inline-block; }
        .badge-status { background: rgba(52, 211, 153, 0.1); color: var(--success); padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; border: 1px solid rgba(52, 211, 153, 0.2); display: inline-block; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: middle; }
        th { background: var(--bg-main); color: var(--text-secondary); font-weight: 600; font-size: 11.5px; text-transform: uppercase; }
        td { color: var(--text-primary); }
        p { line-height: 1.6; color: var(--text-secondary); font-size: 13.5px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; font-size: 11.5px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; text-transform: uppercase; }
        .form-control { width: 100%; background: var(--bg-main); border: 1px solid var(--border); border-radius: 6px; padding: 10px 14px; color: var(--text-primary); font-size: 13px; box-sizing: border-box; outline: none; }
        .form-control:focus { border-color: var(--accent); }
        .btn { background: var(--accent); color: #090908; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 12px; text-transform: uppercase; transition: 0.2s; width: 100%; text-decoration: none; display: inline-block; text-align: center; }
        .btn:hover { background: var(--accent-hover); }
        .logout-btn { background: rgba(248, 113, 113, 0.1); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.3); padding: 6px 12px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: bold; }
        .logout-btn:hover { background: rgba(248, 113, 113, 0.2); }
        .grid-evolucion { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }

        @media print {
            body * { visibility: hidden; }
            .consent-print-sheet, .consent-print-sheet * { visibility: visible; }
            .consent-print-sheet {
                position: absolute; left: 0; top: 0;
                width: 100%; background: #ffffff !important; color: #121110 !important;
                border: none !important; box-shadow: none !important;
                margin: 0; padding: 20px;
            }
            .no-print { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="sidebar no-print">
        <h2>Aeterna E.A.S.</h2>
        <div class="sidebar-subtitle">
            <b>{{ nombre_usuario }}</b><br>
            <span style="color: var(--success);">Sesión Activa</span>
        </div>

        {% if rol == 'secretaria' %}
            <a href="/?rol=secretaria&seccion=caja" class="{% if seccion == 'caja' %}active{% endif %}">Caja & Facturación Sifen</a>
            <a href="/?rol=secretaria&seccion=registrar_pago" class="{% if seccion == 'registrar_pago' %}active{% endif %}">Registrar Nuevo Pago</a>
            <a href="/?rol=secretaria&seccion=cuentas_cobrar" class="{% if seccion == 'cuentas_cobrar' %}active{% endif %}">Cuentas por Cobrar & Señas</a>
            <a href="/?rol=secretaria&seccion=honorarios_gastos" class="{% if seccion == 'honorarios_gastos' %}active{% endif %}">Honorarios & Gastos VIP</a>
            <a href="/?rol=secretaria&seccion=agenda" class="{% if seccion == 'agenda' %}active{% endif %}">Agenda General</a>
        {% elif rol == 'entrenador' %}
            <div class="menu-section-title">Panel de Rendimiento</div>
            <a href="/?rol=entrenador&seccion=agenda_entrenador" class="{% if seccion == 'agenda_entrenador' %}active{% endif %}">Atletas Asignados</a>
            
            {% if seccion != 'agenda_entrenador' %}
            <div class="menu-section-title" style="color: var(--accent);">Atleta: {{ p.nombre }}</div>
            <a href="/?rol=entrenador&seccion=prescripcion_ejercicio&id={{ p.id }}" class="{% if seccion == 'prescripcion_ejercicio' %}active{% endif %}">Prescripción & Zona 2</a>
            <a href="/?rol=entrenador&seccion=wearables_atleta&id={{ p.id }}" class="{% if seccion == 'wearables_atleta' %}active{% endif %}">Recuperación & Wearable</a>
            {% endif %}
        {% else %}
            <div class="menu-section-title">Mi Consulta & Pacientes</div>
            <a href="/?rol=medico&seccion=agenda_medico" class="{% if seccion == 'agenda_medico' %}active{% endif %}">Mi Agenda de Hoy</a>
            
            {% if seccion != 'agenda_medico' and seccion != 'caja' %}
            <div class="menu-section-title" style="color: var(--accent);">Paciente Activo: {{ p.nombre }}</div>
            <a href="/?rol=medico&seccion=paciente&id={{ p.id }}" class="{% if seccion == 'paciente' %}active{% endif %}">Ficha & Pre-Consulta</a>
            <a href="/?rol=medico&seccion=evolucion_consulta&id={{ p.id }}" class="{% if seccion == 'evolucion_consulta' %}active{% endif %}">Evolución & SOAP</a>
            <a href="/?rol=medico&seccion=examenes_lab&id={{ p.id }}" class="{% if seccion == 'examenes_lab' %}active{% endif %}">Exámenes Laboratoriales</a>
            <a href="/?rol=medico&seccion=examenes_no_lab&id={{ p.id }}" class="{% if seccion == 'examenes_no_lab' %}active{% endif %}">Exámenes No Laboratoriales</a>
            <a href="/?rol=medico&seccion=recetas&id={{ p.id }}" class="{% if seccion == 'recetas' %}active{% endif %}">Recetas A5 (QR PY)</a>
            <a href="/?rol=medico&seccion=regenerativa&id={{ p.id }}" class="{% if seccion == 'regenerativa' %}active{% endif %}">Med. Regenerativa</a>
            <a href="/?rol=medico&seccion=wearables&id={{ p.id }}" class="{% if seccion == 'wearables' %}active{% endif %}">Wearables & Biometría</a>
            <a href="/?rol=medico&seccion=consentimientos&id={{ p.id }}" class="{% if seccion == 'consentimientos' %}active{% endif %}">Consentimientos</a>
            <a href="/?rol=medico&seccion=reporte_longevidad&id={{ p.id }}" class="{% if seccion == 'reporte_longevidad' %}active{% endif %}">Reporte Integral PDF</a>
            {% endif %}

            <div class="menu-section-title">Paciente & Conectividad</div>
            <a href="/?rol=medico&seccion=portal_paciente&id={{ p.id }}" class="{% if seccion == 'portal_paciente' %}active{% endif %}">Portal del Paciente (VIP Dossier)</a>
        {% endif %}
    </div>

    <div class="main-content">
        <header class="no-print">
            <h3 style="margin: 0; color: var(--text-primary); font-size: 13.5px; font-weight: 600;">Instituto Aeterna E.A.S. — Sanatorio Le Blanc (CDE)</h3>
            <div style="display: flex; align-items: center; gap: 15px;">
                <button class="role-btn" onclick="toggleTheme()" id="themeBtn" style="background: var(--card-bg); color: var(--accent); border: 1px solid var(--accent);">Tema</button>
                <span style="font-size: 12px; color: var(--text-secondary);">Usuario: <b>{{ nombre_usuario }}</b> ({{ rol | upper }})</span>
                <a href="/logout" class="logout-btn">Cerrar Sesión</a>
            </div>
        </header>

        <div class="container">
            {% if rol == 'secretaria' %}
                {% if seccion == 'agenda' %}
                    <div class="box">
                        <h3>Agenda General de la Clínica</h3>
                        <p>Control global de turnos y disponibilidad de salas en Aeterna E.A.S.</p>
                        <table>
                            <tr><th>Hora</th><th>Paciente</th><th>Médico Asignado</th><th>Sala</th><th>Estado</th></tr>
                            <tr><td>09:00 hs</td><td>Carlos Benítez</td><td>Dra. Romina Espinola</td><td>Sala Metabólica VIP</td><td><span style="color: var(--success); font-weight: bold;">En Espera</span></td></tr>
                            <tr><td>10:30 hs</td><td>María Giménez</td><td>Dra. Fátima López</td><td>Sueroterapia</td><td><span style="color: var(--accent); font-weight: bold;">Confirmado</span></td></tr>
                        </table>
                    </div>
                {% elif seccion == 'registrar_pago' %}
                    <div class="box" style="max-width: 600px; margin: 0 auto;">
                        <h3>Registrar Nuevo Cobro & Factura Sifen</h3>
                        <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 20px;">Emisión de factura electrónica legal para el Instituto Aeterna E.A.S. (RUC: 80172292-6).</p>
                        <form onsubmit="registrarPagoAdmin(event)">
                            <div class="form-group">
                                <label>Nombre del Paciente / Cliente:</label>
                                <input type="text" id="reg_paciente" class="form-control" required placeholder="Ej. Juan Pérez">
                            </div>
                            <div class="form-group">
                                <label>Monto Total (Guaraníes):</label>
                                <input type="number" id="reg_monto" class="form-control" required placeholder="1500000">
                            </div>
                            <div class="form-group">
                                <label>Método de Pago:</label>
                                <select id="reg_metodo" class="form-control">
                                    <option value="Tarjeta">Tarjeta / POS</option>
                                    <option value="Transferencia">Transferencia Bancaria</option>
                                    <option value="Efectivo">Efectivo en Caja</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Referencia / Nro. de Voucher / Transacción:</label>
                                <input type="text" id="reg_ref" class="form-control" placeholder="POS-9923">
                            </div>
                            <button type="submit" class="btn" style="margin-top: 10px;">Emitir Factura y Sifen</button>
                        </form>
                    </div>
                {% elif seccion == 'cuentas_cobrar' %}
                    <div class="box">
                        <h3>Cuentas por Cobrar, Señas & Anticipos</h3>
                        <p>Seguimiento de saldos pendientes y compromisos financieros de pacientes.</p>
                        <table>
                            <tr><th>Paciente</th><th>Concepto</th><th>Monto (Gs.)</th><th>Tipo</th><th>Vencimiento</th><th>Acción</th></tr>
                            {% for c in cuentas %}
                            <tr>
                                <td><b>{{ c.paciente }}</b></td>
                                <td>{{ c.concepto }}</td>
                                <td>Gs. {{ "{:,}".format(c.monto|int) }}</td>
                                <td><span class="badge-pill">{{ c.tipo }}</span></td>
                                <td>{{ c.vencimiento }}</td>
                                <td><button class="btn" style="padding: 5px 10px; font-size: 10px; width: auto;" onclick="alert('Cuenta saldada y registrada en Sifen.')">Cobrar</button></td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% elif seccion == 'honorarios_gastos' %}
                    <div class="box">
                        <h3>Gestión de Honorarios Médicos & Gastos Operativos</h3>
                        <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 20px;">Control financiero gerencial de egresos y distribución de comisiones profesionales.</p>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                            <div style="background: var(--bg-main); padding: 20px; border-radius: 8px; border: 1px solid var(--border);">
                                <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Total Recaudado Bruto</span>
                                <h4 style="color: var(--success); font-size: 20px; margin: 5px 0 0 0;">Gs. {{ "{:,}".format(total_recaudado) }}</h4>
                            </div>
                            <div style="background: var(--bg-main); padding: 20px; border-radius: 8px; border: 1px solid var(--border);">
                                <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Balance Neto Operativo</span>
                                <h4 style="color: var(--accent); font-size: 20px; margin: 5px 0 0 0;">Gs. {{ "{:,}".format(balance_neto) }}</h4>
                            </div>
                        </div>

                        <h4 style="color: var(--accent); font-size: 13px; text-transform: uppercase; margin-bottom: 10px;">Liquidación de Honorarios Médicos</h4>
                        <table>
                            <tr><th>Profesional</th><th>Consultas Atendidas</th><th>Honorarios Generados (Gs.)</th><th>Estado</th></tr>
                            {% for h in honorarios %}
                            <tr>
                                <td><b>{{ h.profesional }}</b></td>
                                <td>{{ h.consultas }}</td>
                                <td style="color: var(--accent); font-weight: bold;">Gs. {{ "{:,}".format(h.honorarios_gs|int) }}</td>
                                <td><span class="badge-pill">{{ h.estado }}</span></td>
                            </tr>
                            {% endfor %}
                        </table>

                        <h4 style="color: var(--accent); font-size: 13px; text-transform: uppercase; margin: 30px 0 10px 0;">Gastos Operativos & Proveedores</h4>
                        <table>
                            <tr><th>Concepto</th><th>Categoría</th><th>Monto (Gs.)</th><th>Fecha</th></tr>
                            {% for g in gastos %}
                            <tr>
                                <td><b>{{ g.concepto }}</b></td>
                                <td>{{ g.categoria }}</td>
                                <td style="color: #f87171; font-weight: bold;">- Gs. {{ "{:,}".format(g.monto|int) }}</td>
                                <td>{{ g.fecha }}</td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% else %}
                    <div class="box">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 20px;">
                            <h3 style="margin: 0; border: none;">Control de Caja & Facturación Sifen (RUC: 80172292-6)</h3>
                            <a href="/api/admin/exportar-caja" class="btn" style="width: auto; text-decoration: none; display: inline-block;">Exportar Cierre (CSV)</a>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;">
                            <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Total Recaudado</span>
                                <h4 style="color: var(--success); font-size: 19px; margin: 5px 0 0 0;">Gs. {{ "{:,}".format(total_recaudado) }}</h4>
                            </div>
                            <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Gastos Operativos</span>
                                <h4 style="color: #f87171; font-size: 17px; margin: 5px 0 0 0;">- Gs. {{ "{:,}".format(total_gastos) }}</h4>
                            </div>
                            <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Balance Neto</span>
                                <h4 style="color: var(--accent); font-size: 17px; margin: 5px 0 0 0;">Gs. {{ "{:,}".format(balance_neto) }}</h4>
                            </div>
                            <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Tarjetas / POS</span>
                                <h4 style="color: var(--accent); font-size: 17px; margin: 5px 0 0 0;">Gs. {{ "{:,}".format(desglose.Tarjeta) }}</h4>
                            </div>
                        </div>

                        <!-- GRÁFICOS DE DISTRIBUCIÓN -->
                        <div class="box" style="margin-bottom: 25px; background: var(--bg-main);">
                            <h4 style="color: var(--accent); font-size: 12px; text-transform: uppercase; margin-top: 0;">Distribución de Ingresos por Método de Pago</h4>
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 3px;">
                                    <span>Tarjetas / POS ({{ porcs.tarjeta }}%)</span><span>Gs. {{ "{:,}".format(desglose.Tarjeta) }}</span>
                                </div>
                                <div style="background: var(--card-bg); height: 7px; border-radius: 4px; overflow: hidden; border: 1px solid var(--border);">
                                    <div style="background: var(--accent); width: {{ porcs.tarjeta }}%; height: 100%;"></div>
                                </div>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 3px;">
                                    <span>Transferencias Bancarias ({{ porcs.transf }}%)</span><span>Gs. {{ "{:,}".format(desglose.Transferencia) }}</span>
                                </div>
                                <div style="background: var(--card-bg); height: 7px; border-radius: 4px; overflow: hidden; border: 1px solid var(--border);">
                                    <div style="background: var(--success); width: {{ porcs.transf }}%; height: 100%;"></div>
                                </div>
                            </div>
                            <div>
                                <div style="display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 3px;">
                                    <span>Efectivo en Caja ({{ porcs.efectivo_val }}%)</span><span>Gs. {{ "{:,}".format(desglose.Efectivo) }}</span>
                                </div>
                                <div style="background: var(--card-bg); height: 7px; border-radius: 4px; overflow: hidden; border: 1px solid var(--border);">
                                    <div style="background: #3b82f6; width: {{ porcs.efectivo_val }}%; height: 100%;"></div>
                                </div>
                            </div>
                        </div>

                        <table>
                            <tr><th>Paciente</th><th>Monto</th><th>Método</th><th>Estado Sifen / CDC</th><th>Acción Sifen</th></tr>
                            {% for item in pagos %}
                            <tr>
                                <td><b>{{ item.paciente }}</b></td>
                                <td>Gs. {{ "{:,}".format(item.monto|int) }}</td>
                                <td><span class="badge-pill">{{ item.metodo }}</span></td>
                                <td><span style="color: var(--success); font-weight: bold;">{{ item.sifen_status }}</span></td>
                                <td style="display: flex; gap: 8px;">
                                    <a href="/api/admin/ver-kude/{{ item.id }}" target="_blank" class="btn" style="padding: 5px 10px; font-size: 10px; width: auto; text-decoration: none; background: var(--bg-main); color: var(--accent); border: 1px solid var(--accent);">Ver KUDE</a>
                                    <button class="btn" onclick="enviarWhatsApp('Factura Electrónica y KUDE Sifen')" style="padding: 5px 10px; font-size: 10px; width: auto; background: var(--success); color: #000;">WhatsApp</button>
                                </td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% endif %}
            {% elif rol == 'entrenador' %}
                {% if seccion == 'agenda_entrenador' %}
                    <div class="box">
                        <h3>Atletas Asignados — Manuel Duarte (Preparador Físico)</h3>
                        <p>Seleccione un atleta para revisar su recuperación por wearables y prescribir su entrenamiento:</p>
                        <table>
                            <tr><th>Atleta</th><th>Programa Aeterna</th><th>Enfoque Físico</th><th>Dispositivo</th><th>Acción</th></tr>
                            {% for pat in pacientes %}
                            <tr>
                                <td><b>{{ pat.nombre }}</b> ({{ pat.edad }} años)</td>
                                <td>{{ pat.programa }}</td>
                                <td><span class="badge-pill">{{ pat.entrenamiento.enfoque }}</span></td>
                                <td>{{ pat.wearables.dispositivo }}</td>
                                <td>
                                    <a href="/?rol=entrenador&seccion=prescripcion_ejercicio&id={{ pat.id }}" class="btn" style="padding: 6px 14px; font-size: 11px; width: auto; text-decoration: none;">Ver Plan Físico</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% else %}
                    <div style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;" class="no-print">
                        <a href="/?rol=entrenador&seccion=agenda_entrenador" class="btn" style="width: auto; background: var(--card-bg); color: var(--accent); border: 1px solid var(--accent); text-decoration: none;">Volver a Mis Atletas</a>
                        <span style="font-size: 13px; color: var(--accent);"><b>Atleta Seleccionado:</b> {{ p.nombre }}</span>
                    </div>

                    {% if seccion == 'prescripcion_ejercicio' %}
                        <div class="box" style="border-color: var(--accent);">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 20px;">
                                <h3 style="margin: 0; border: none; padding: 0;">Prescripción de Rendimiento & Zona 2</h3>
                                <span class="badge-status">Coach: Manuel Duarte</span>
                            </div>

                            <form onsubmit="guardarEntrenamiento(event, '{{ p.id }}')">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                                    <div class="form-group" style="margin-bottom: 0;">
                                        <label>Enfoque Físico Principal:</label>
                                        <input type="text" id="ent_enfoque" class="form-control" value="{{ p.entrenamiento.enfoque }}">
                                    </div>
                                    <div class="form-group" style="margin-bottom: 0;">
                                        <label>Frecuencia Semanal:</label>
                                        <input type="text" id="ent_sesiones" class="form-control" value="{{ p.entrenamiento.sesiones_semanales }}">
                                    </div>
                                </div>

                                <div class="form-group">
                                    <label>Detalle de Rutina (Cardio Zona 2, Fuerza, Movilidad):</label>
                                    <textarea id="ent_prescripcion" class="form-control" rows="8" style="font-family: monospace; font-size: 12.5px;">{{ p.entrenamiento.prescripcion_ejercicio }}</textarea>
                                </div>

                                <button type="submit" class="btn" style="width: auto;">Guardar Plan de Entrenamiento</button>
                            </form>
                        </div>
                    {% elif seccion == 'wearables_atleta' %}
                        <div style="background: rgba(212, 175, 55, 0.12); border: 1px solid var(--accent); padding: 14px 20px; border-radius: 8px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span style="font-size: 18px;">i</span>
                                <div>
                                    <h4 style="margin: 0; color: var(--accent); font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.5px;">Estado de Recuperación (IA para Coach)</h4>
                                    <p style="margin: 3px 0 0 0; font-size: 12.5px; color: var(--text-primary);">{{ p.wearables.alerta_ia }}</p>
                                </div>
                            </div>
                            <span class="badge-status" style="font-size: 10.5px;">Listo para Carga</span>
                        </div>

                        <div class="box">
                            <h3>Biometría de Recuperación ({{ p.wearables.dispositivo }})</h3>
                            <table>
                                <tr><th>Métrica</th><th>Valor Actual</th><th>Evaluación para Entrenamiento</th></tr>
                                <tr><td><b>Variabilidad Cardíaca (HRV)</b></td><td style="color: var(--accent); font-weight: bold;">{{ p.wearables.hrv }}</td><td>Excelente recuperación autonómica</td></tr>
                                <tr><td><b>Sueño Profundo / Eficiencia</b></td><td style="color: var(--accent); font-weight: bold;">{{ p.wearables.sueno_horas }} ({{ p.wearables.eficiencia_sueno }})</td><td>Suficiente para alta intensidad</td></tr>
                                <tr><td><b>Índice de Esfuerzo (Strain)</b></td><td style="color: var(--accent); font-weight: bold;">{{ p.wearables.strain_esfuerzo }}</td><td>Margen disponible para sesión de fuerza</td></tr>
                            </table>
                        </div>
                    {% endif %}
                {% endif %}
            {% else %}
                {% if seccion == 'agenda_medico' %}
                    <div class="box">
                        <h3>Agenda de Turnos de Hoy — {{ nombre_usuario }}</h3>
                        <p>Seleccione un paciente para acceder directamente a su Ficha y Evolución:</p>
                        <table>
                            <tr><th>Hora</th><th>Paciente</th><th>Programa</th><th>Estado</th><th>Acción Rápida</th></tr>
                            {% for pat in pacientes %}
                            <tr>
                                <td><b>{{ pat.hora_turno }}</b></td>
                                <td>{{ pat.nombre }} ({{ pat.edad }} años)</td>
                                <td>{{ pat.programa }}</td>
                                <td><span class="badge-status">{{ pat.estado_turno }}</span></td>
                                <td>
                                    <a href="/?rol=medico&seccion=paciente&id={{ pat.id }}" class="btn" style="padding: 6px 14px; font-size: 11px; width: auto; text-decoration: none;">Atender Paciente</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% else %}
                    <div style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;" class="no-print">
                        <a href="/?rol=medico&seccion=agenda_medico" class="btn" style="width: auto; background: var(--card-bg); color: var(--accent); border: 1px solid var(--accent); text-decoration: none;">Volver a Mi Agenda</a>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <button class="btn" onclick="enviarWhatsApp('Resumen de Consulta y Receta Aeterna')" style="width: auto; padding: 6px 12px; font-size: 11px; background: var(--success); color: #000;">Enviar WhatsApp al Paciente</button>
                            <span style="font-size: 13px; color: var(--accent);"><b>Paciente en Atención:</b> {{ p.nombre }} ({{ p.edad }} años)</span>
                        </div>
                    </div>

                    {% if seccion == 'paciente' %}
                        <div class="box" style="border-color: var(--accent);">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px;">
                                <h3 style="margin: 0; border: none; padding: 0;">Formulario de Pre-Consulta 360° (Enviado por Paciente)</h3>
                                <span class="badge-status">Cloud Sincronizado</span>
                            </div>

                            {% if p.pre_consulta %}
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                                    <div>
                                        <p style="margin: 4px 0;"><b>Paciente:</b> {{ p.pre_consulta.nombre_completo }} ({{ p.pre_consulta.edad }} años)</p>
                                        <p style="margin: 4px 0;"><b>Nacionalidad / Residencia:</b> {{ p.pre_consulta.nacionalidad }} / {{ p.pre_consulta.residencia }}</p>
                                        <p style="margin: 4px 0;"><b>Profesión / Ocupación:</b> {{ p.pre_consulta.profesion }} ({{ p.pre_consulta.estado_civil }})</p>
                                        <p style="margin: 4px 0;"><b>Contacto Emergencia:</b> {{ p.pre_consulta.contacto_emergencia }}</p>
                                        <p style="margin: 4px 0;"><b>Autoevaluación de Salud:</b> {{ p.pre_consulta.salud_actual }}</p>
                                    </div>
                                    <div>
                                        <p style="margin: 4px 0;"><b>Médico Tratante:</b> {{ p.medico }}</p>
                                        <p style="margin: 4px 0;"><b>Wearable:</b> {{ p.pre_consulta.wearable }} (Otro: {{ p.pre_consulta.otro_dispositivo }})</p>
                                        <p style="margin: 4px 0;"><b>Teléfono / Correo:</b> {{ p.pre_consulta.telefono }} / {{ p.pre_consulta.correo }}</p>
                                        <p style="margin: 4px 0;"><b>Compromiso:</b> <span style="color: var(--success);">{{ p.pre_consulta.compromiso }}</span></p>
                                    </div>
                                </div>
                                <hr style="border-color: var(--border); margin: 15px 0;">
                                <p style="color: var(--success); font-weight: bold; margin-bottom: 10px;">{{ p.pre_consulta.estado }}</p>
                                <p><b>Objetivos Principales seleccionados:</b> {{ p.pre_consulta.objetivos }}</p>
                                <p><b>Queja Principal:</b> {{ p.pre_consulta.queja }}</p>
                                <p><b>Impacto esperable en su vida:</b> {{ p.pre_consulta.impacto_vida }}</p>
                                <p><b>Antecedentes Médicos:</b> {{ p.pre_consulta.antecedentes }} | Cirugías: {{ p.pre_consulta.cirugias }}</p>
                                <p><b>Antecedentes Familiares:</b> {{ p.pre_consulta.ant_familiares }}</p>
                                <p><b>Alergias o Intolerancias:</b> {{ p.pre_consulta.alergias }}</p>
                                <p><b>Medicamentos Recetados:</b> {{ p.pre_consulta.medicamentos }}</p>
                                <p><b>Suplementos Actuales:</b> {{ p.pre_consulta.suplementos_actuales }}</p>
                                <p><b>Terapias Previas (TRH / Estudios genéticos):</b> TRH: {{ p.pre_consulta.trh }} | Genéticos: {{ p.pre_consulta.estudios_geneticos }}</p>
                                <p><b>Nutrición & Hidratación:</b> {{ p.pre_consulta.nutricion }} | Ultraprocesados: {{ p.pre_consulta.procesados }} | Síntomas: {{ p.pre_consulta.sintomas_digestivos }} | Agua: {{ p.pre_consulta.agua }}</p>
                                <p><b>Sueño Promedio:</b> {{ p.pre_consulta.sueno_horas }} (Calidad: {{ p.pre_consulta.sueno_calidad }}) | Compartir datos: {{ p.pre_consulta.compartir_sueno }}</p>
                                <p><b>Actividad Física:</b> {{ p.pre_consulta.dias_ejercicio }} — {{ p.pre_consulta.tipo_entrenamiento }} | Dolor articular: {{ p.pre_consulta.dolor_articular }}</p>
                                <p><b>Estrés y Entorno:</b> Nivel {{ p.pre_consulta.estres }} | Manejo: {{ p.pre_consulta.manejo_estres }} | Toxinas: {{ p.pre_consulta.toxinas }}</p>
                                <p><b>Salud Hormonal y Energía:</b> Energía: {{ p.pre_consulta.energia_dia }} | Bajones: {{ p.pre_consulta.bajones_energia }} | Libido: {{ p.pre_consulta.libido }} | Ciclo: {{ p.pre_consulta.ciclo_menstrual }}</p>
                                <p><b>Laboratorios Recientes (6 meses):</b> {{ p.pre_consulta.lab_recientes }}</p>
                            {% else %}
                                <p style="color: var(--warning);">Pendiente: El paciente aún no ha completado el formulario en su portal.</p>
                            {% endif %}
                        </div>
                    {% elif seccion == 'evolucion_consulta' %}
                        <div class="grid-evolucion">
                            <div class="box">
                                <h3>Evolución de Hoy & Consulta</h3>
                                <form onsubmit="guardarEvolucion(event, '{{ p.id }}')">
                                    <div class="form-group">
                                        <label>Nota de Evolución / Hallazgos Clínicos:</label>
                                        <textarea id="evo_texto" class="form-control" rows="8" placeholder="Escriba la evolución clínica basada en la pre-consulta de hoy..."></textarea>
                                    </div>
                                    <button type="submit" class="btn">Guardar Evolución de Hoy</button>
                                </form>
                            </div>

                            <div class="box" style="max-height: 520px; overflow-y: auto;">
                                <h3>Historial de Consultas Anteriores</h3>
                                {% if p.historial_consultas %}
                                    {% for hc in p.historial_consultas %}
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border); margin-bottom: 15px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                            <span style="font-size: 11.5px; color: var(--accent); font-weight: bold;">{{ hc.fecha }}</span>
                                            <span class="badge-pill">Dr(a). {{ hc.medico }}</span>
                                        </div>
                                        <p style="margin: 4px 0; font-size: 12.5px;"><b>Evolución:</b> {{ hc.evolucion }}</p>
                                    </div>
                                    {% endfor %}
                                {% else %}
                                    <p style="color: var(--text-secondary);">No registra consultas anteriores en el sistema.</p>
                                {% endif %}
                            </div>
                        </div>
                    {% elif seccion == 'examenes_lab' %}
                        <div style="display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 20px; margin-bottom: 24px;">
                            <div class="box" style="margin-bottom: 0; border-color: var(--accent);">
                                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px;">
                                    <h3 style="margin: 0; border: none; padding: 0;">Solicitar Exámenes Laboratoriales (Listas Oficiales Aeterna)</h3>
                                    <button class="btn" style="width: auto; background: var(--bg-main); color: var(--success); border: 1px solid var(--success); font-size: 11px; padding: 6px 12px;" onclick="sincronizarLIS('{{ p.id }}')">Sincronizar LIS</button>
                                </div>
                                <form onsubmit="solicitarLab(event, '{{ p.id }}')">
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border); max-height: 350px; overflow-y: auto; margin-bottom: 15px;">
                                        
                                        <div style="color: var(--accent); font-weight: bold; font-size: 12px; margin-bottom: 8px; text-transform: uppercase;">Lista 1 de 2: Complejidad Media (Evaluación Metabólica Base)</div>
                                        
                                        <div style="font-size: 11px; color: var(--text-secondary); font-weight: bold; margin-top: 6px;">• Glucosa e insulina:</div>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Glucemia en ayunas"> Glucemia en ayunas</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Hemoglobina glicosilada (HbA1c)"> Hemoglobina glicosilada (HbA1c)</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Insulina en ayunas (HOMA-IR)"> Insulina en ayunas (para calcular HOMA-IR)</label>

                                        <div style="font-size: 11px; color: var(--text-secondary); font-weight: bold; margin-top: 10px;">• Perfil lipídico:</div>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Colesterol total, HDL, LDL y no-HDL"> Colesterol total, HDL, LDL y no-HDL</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Triglicéridos"> Triglicéridos</label>

                                        <div style="font-size: 11px; color: var(--text-secondary); font-weight: bold; margin-top: 10px;">• Hígado:</div>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="TGO/AST, TGP/ALT, GGT y fosfatasa alcalina"> TGO/AST, TGP/ALT, GGT y fosfatasa alcalina</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Bilirrubinas y albúmina"> Bilirrubinas y albúmina</label>

                                        <div style="font-size: 11px; color: var(--text-secondary); font-weight: bold; margin-top: 10px;">• Riñón, Electrolitos & Coagulación:</div>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Urea, creatinina y ácido úrico"> Urea, creatinina con tasa de filtración estimada y ácido úrico</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Sodio, potasio, calcio, magnesio y fósforo"> Sodio, potasio, calcio, magnesio y fósforo</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Uroanálisis y relación albúmina/creatinina"> Uroanálisis y relación albúmina/creatinina en orina</label>
                                        <label style="font-size: 11.5px; color: var(--accent); font-weight: bold; cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Tiempo de coagulación"> ⏱️ Tiempo de coagulación</label>

                                        <div style="font-size: 11px; color: var(--text-secondary); font-weight: bold; margin-top: 10px;">• Tiroides, Inflamación & Micronutrientes:</div>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="TSH y T4 libre"> TSH y T4 libre</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Hemograma completo & PCR ultrasensible"> Hemograma completo & PCR ultrasensible</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Vitamina D (25-OH), B12, Ferritina"> Vitamina D (25-OH), Vitamina B12, Ferritina y transferrina</label>

                                        <div style="color: var(--accent); font-weight: bold; font-size: 12px; margin: 18px 0 8px 0; text-transform: uppercase;">Lista 2 de 2: Complejidad Alta (Evaluación Ampliada)</div>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Curva de tolerancia a la glucosa con insulina"> Curva de tolerancia a la glucosa con insulina (0, 60, 120 min)</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Riesgo Cardiometabólico (Lipoproteína(a), ApoB, Homocisteína)"> Riesgo Cardiometabólico (Lp(a), ApoB, Fibrinógeno, Homocisteína, Cistatina C)</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Perfil Hormonal Completo (Cortisol, Testosterona, SHBG, Estradiol)"> Perfil Hormonal Completo (Cortisol am/pm, Testosterona total/libre, SHBG, IGF-1)</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Nutrientes y Estado Antioxidante (Zinc, Magnesio eritrocitario, Omega-3)"> Nutrientes y Antioxidantes (Zinc, Magnesio eritrocitario, Omega-3)</label>
                                        <label style="font-size: 11.5px; color: var(--text-primary); cursor: pointer; display: block; margin: 4px 0;"><input type="checkbox" name="lab" value="Intestino y Microbiota (Calprotectina, Heces, Secuenciación)"> Intestino y Microbiota (Calprotectina fecal, Secuenciación de microbiota)</label>

                                    </div>
                                    <div style="display: flex; gap: 10px;">
                                        <button type="submit" class="btn" style="padding: 8px 14px; font-size: 11px;">Generar Orden Oficial</button>
                                        <a href="/api/generar-pdf/{{ p.id }}" target="_blank" class="btn" style="padding: 8px 14px; font-size: 11px; background: var(--card-bg); color: var(--accent); border: 1px solid var(--accent); text-decoration: none;">Imprimir / WhatsApp</a>
                                    </div>
                                </form>
                            </div>

                            <div class="box" style="margin-bottom: 0; max-height: 480px; overflow-y: auto;">
                                <h3 style="font-size: 12.5px;">Estudios Solicitados</h3>
                                {% if p.solicitudes_lab_previas %}
                                    {% for sol in p.solicitudes_lab_previas %}
                                    <div style="background: var(--bg-main); padding: 10px; border-radius: 6px; border: 1px solid var(--border); margin-bottom: 10px; font-size: 12px;">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                            <span style="color: var(--accent); font-weight: bold;">{{ sol.fecha }}</span>
                                            <span class="badge-pill" style="font-size: 9px; padding: 2px 6px;">{{ sol.estado }}</span>
                                        </div>
                                        <p style="margin: 0; color: var(--text-primary); font-size: 11.5px;">{{ sol.estudios }}</p>
                                    </div>
                                    {% endfor %}
                                {% else %}
                                    <p style="font-size: 12px; color: var(--text-secondary);">Sin solicitudes previas.</p>
                                {% endif %}
                            </div>
                        </div>

                        <!-- CAJA DE CARGA MANUAL DE RESULTADOS -->
                        <div class="box" style="border-color: var(--accent); margin-bottom: 24px;">
                            <h3>➕ Carga Manual de Resultados de Laboratorio</h3>
                            <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 15px;">Ingrese los valores físicos o en PDF entregados por el paciente para actualizar su línea de tiempo gráfica.</p>
                            
                            <form onsubmit="guardarBiomarcadorManual(event, '{{ p.id }}')" style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap: 10px; align-items: flex-end;">
                                <div class="form-group" style="margin-bottom: 0;">
                                    <label>Parámetro / Estudio:</label>
                                    <input type="text" id="manual_param" class="form-control" placeholder="Ej. Glucosa en Ayunas" required style="font-size: 12px;">
                                </div>
                                <div class="form-group" style="margin-bottom: 0;">
                                    <label>Fecha:</label>
                                    <input type="text" id="manual_fecha" class="form-control" value="20/10/2026" required style="font-size: 12px;">
                                </div>
                                <div class="form-group" style="margin-bottom: 0;">
                                    <label>Valor Numérico:</label>
                                    <input type="number" step="0.1" id="manual_valor" class="form-control" placeholder="90" required style="font-size: 12px;">
                                </div>
                                <div class="form-group" style="margin-bottom: 0;">
                                    <label>Unidad:</label>
                                    <input type="text" id="manual_unidad" class="form-control" value="mg/dL" required style="font-size: 12px;">
                                </div>
                                <button type="submit" class="btn" style="padding: 10px 15px; font-size: 11px; height: 38px;">Añadir</button>
                            </form>
                        </div>

                        <div class="box">
                            <h3>Análisis Longitudinal: Tendencias y Números Históricos</h3>
                            <p style="font-size: 12.5px; color: var(--text-secondary); margin-bottom: 20px;">Visualización gráfica de la evolución del paciente consulta tras consulta junto con sus valores numéricos exactos.</p>
                            
                            {% for bio in p.biomarcadores_longitudinales %}
                            <div style="background: var(--bg-main); padding: 20px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h4 style="margin: 0; color: var(--accent); font-size: 13.5px; text-transform: uppercase;">{{ bio.parametro }}</h4>
                                    <span class="badge-pill" style="font-size: 11px;">Rango Óptimo: {{ bio.rango_optimo }}</span>
                                </div>

                                <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; align-items: center;">
                                    <div style="background: var(--card-bg); padding: 15px; border-radius: 6px; border: 1px solid var(--border); text-align: center;">
                                        <svg width="100%" height="110" viewBox="0 0 300 110" style="overflow: visible;">
                                            <line x1="0" y1="20" x2="300" y2="20" stroke="var(--border)" stroke-dasharray="3,3" />
                                            <line x1="0" y1="60" x2="300" y2="60" stroke="var(--border)" stroke-dasharray="3,3" />
                                            <line x1="0" y1="100" x2="300" y2="100" stroke="var(--border)" stroke-dasharray="3,3" />
                                            
                                            {% set count = bio.historial | length %}
                                            {% if count > 1 %}
                                                {% set points = namespace(val="") %}
                                                {% for h in bio.historial %}
                                                    {% set x = 30 + (loop.index0 * (240 / (count - 1))) %}
                                                    {% set y = 100 - ((h.valor / 150.0) * 80) %}
                                                    {% if loop.first %}
                                                        {% set points.val = x ~ "," ~ y %}
                                                    {% else %}
                                                        {% set points.val = points.val ~ " " ~ x ~ "," ~ y %}
                                                    {% endif %}
                                                {% endfor %}
                                                
                                                <polyline fill="none" stroke="var(--accent)" stroke-width="2.5" points="{{ points.val }}" />
                                                
                                                {% for h in bio.historial %}
                                                    {% set x = 30 + (loop.index0 * (240 / (count - 1))) %}
                                                    {% set y = 100 - ((h.valor / 150.0) * 80) %}
                                                    <circle cx="{{ x }}" cy="{{ y }}" r="5" fill="var(--accent)" />
                                                    <text x="{{ x }}" y="{{ y - 10 }}" fill="var(--text-primary)" font-size="10" text-anchor="middle" font-weight="bold">{{ h.valor }}</text>
                                                    <text x="{{ x }}" y="115" fill="var(--text-secondary)" font-size="9" text-anchor="middle">{{ h.fecha }}</text>
                                                {% endfor %}
                                            {% else %}
                                                <text x="150" y="55" fill="var(--text-secondary)" font-size="11" text-anchor="middle">Se requieren al menos 2 mediciones históricas.</text>
                                                <text x="150" y="75" fill="var(--accent)" font-size="12" text-anchor="middle" font-weight="bold">Valor actual: {{ bio.historial[0].valor }} {{ bio.historial[0].unidad }}</text>
                                            {% endif %}
                                        </svg>
                                    </div>

                                    <div>
                                        <table style="margin-top: 0;">
                                            <tr><th>Fecha</th><th>Valor</th><th>Estado</th></tr>
                                            {% for h in bio.historial %}
                                            <tr>
                                                <td><b>{{ h.fecha }}</b></td>
                                                <td style="color: var(--accent); font-weight: bold;">{{ h.valor }} {{ h.unidad }}</td>
                                                <td><span style="color: var(--success); font-weight: bold;">Registrado</span></td>
                                            </tr>
                                            {% endfor %}
                                        </table>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% elif seccion == 'examenes_no_lab' %}
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
                            <div class="box" style="margin-bottom: 0; border-color: var(--accent);">
                                <h3>Adjuntar Archivo Externo</h3>
                                <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">Suba PDFs o imágenes de resonancias, ecografías, holter, etc.</p>
                                <div style="background: var(--bg-main); padding: 20px; border-radius: 6px; border: 1px dashed var(--accent); text-align: center;">
                                    <input type="file" class="form-control" style="font-size: 11px; margin-bottom: 12px;">
                                    <button class="btn" style="width: auto; padding: 6px 14px; font-size: 11px;" onclick="alert('Estudio adjuntado correctamente al expediente.')">Subir Archivo</button>
                                </div>
                            </div>

                            <div class="box" style="margin-bottom: 0; border-color: var(--accent);">
                                <h3>Redactar Informe Directo</h3>
                                <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">Escriba un dictamen clínico sin necesidad de adjuntar archivos.</p>
                                <form onsubmit="guardarInformeDirectoNoLab(event, '{{ p.id }}')">
                                    <div class="form-group" style="margin-bottom: 10px;">
                                        <input type="text" id="nolab_tipo" class="form-control" placeholder="Título del estudio (ej. Ergoespirometría)" required style="font-size: 12px;">
                                    </div>
                                    <div class="form-group" style="margin-bottom: 10px;">
                                        <textarea id="nolab_informe" class="form-control" rows="3" placeholder="Redacte el dictamen o interpretación clínica..." required style="font-size: 12px;"></textarea>
                                    </div>
                                    <button type="submit" class="btn" style="padding: 7px 14px; font-size: 11px;">Guardar y Añadir al Expediente</button>
                                </form>
                            </div>
                        </div>

                        <div class="box">
                            <h3>Listado de Estudios No Laboratoriales en Expediente</h3>
                            <table>
                                <tr><th>Fecha</th><th>Tipo de Estudio / Título</th><th>Origen / Archivo</th><th>Médico</th><th>Estado / Dictamen</th></tr>
                                {% for arc in p.archivos_no_lab %}
                                <tr>
                                    <td><b>{{ arc.fecha }}</b></td>
                                    <td><b>{{ arc.tipo }}</b><br><small style="color: var(--text-secondary);">{{ arc.informe }}</small></td>
                                    <td><span class="badge-pill">{{ arc.archivo }}</span></td>
                                    <td>{{ arc.medico }}</td>
                                    <td><span style="color: var(--success); font-weight: bold;">{{ arc.estado }}</span></td>
                                </tr>
                                {% endfor %}
                            </table>
                        </div>
                    {% elif seccion == 'recetas' %}
                        <div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; margin-bottom: 24px;" class="no-print">
                            <div class="box" style="margin-bottom: 0; border-color: var(--accent);">
                                <h3>Editor Libre de Receta Médica</h3>
                                <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 15px;">Escriba o pegue libremente todas las prescripciones, dosis e indicaciones que desee para el paciente.</p>
                                
                                <form onsubmit="guardarRecetaTexto(event, '{{ p.id }}')">
                                    <div class="form-group">
                                        <label>Contenido de la Prescripción:</label>
                                        <textarea id="receta_input_texto" class="form-control" rows="12" placeholder="Escriba aquí libremente..." style="font-family: monospace; font-size: 12.5px; line-height: 1.5;">{{ p.receta_texto }}</textarea>
                                    </div>
                                    <button type="submit" class="btn" style="margin-bottom: 10px;">Guardar y Actualizar Receta</button>
                                </form>
                            </div>

                            <div>
                                <div style="display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 10px;">
                                    <button class="btn" style="width: auto; background: var(--success); color: #000;" onclick="enviarWhatsApp('Receta Digital A5 con Código QR')">Enviar WhatsApp</button>
                                    <button class="btn" style="width: auto; background: var(--accent); color: #090908;" onclick="window.print()">Imprimir Hoja A5</button>
                                </div>

                                <div class="a5-prescription-sheet" style="background: #ffffff; color: #121110; border: 2px solid var(--accent); padding: 25px; box-sizing: border-box; border-radius: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #d4af37; padding-bottom: 12px; margin-bottom: 15px;">
                                        <div>
                                            <h4 style="margin: 0; color: #b8860b; font-size: 15px; letter-spacing: 1px; text-transform: uppercase;">Instituto Aeterna E.A.S.</h4>
                                            <p style="margin: 2px 0 0 0; font-size: 10.5px; color: #555;">Avenida Guido Spano, c/ San José — CDE, Paraguay</p>
                                        </div>
                                        <div style="text-align: right;">
                                            <span style="font-size: 10px; background: #f4f6f9; padding: 3px 8px; border-radius: 4px; border: 1px solid #d1d5db; font-weight: bold; color: #b8860b;">RECETA DIGITAL VÁLIDA PARAGUAY</span>
                                        </div>
                                    </div>

                                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 15px; font-size: 11.5px; background: #f9fafb; padding: 10px; border-radius: 6px;">
                                        <div>
                                            <p style="margin: 2px 0; color: #333;"><b>Paciente:</b> {{ p.nombre }} ({{ p.edad }} años)</p>
                                            <p style="margin: 2px 0; color: #333;"><b>Programa:</b> {{ p.programa }}</p>
                                        </div>
                                        <div>
                                            <p style="margin: 2px 0; color: #333;"><b>Fecha:</b> 20/10/2026</p>
                                            <p style="margin: 2px 0; color: #333;"><b>Emisor:</b> {{ p.medico }}</p>
                                            <p style="margin: 2px 0; color: #333;"><b>Reg. Prof:</b> {{ p.reg_profesional }}</p>
                                        </div>
                                    </div>

                                    <h5 style="margin: 10px 0 5px 0; color: #b8860b; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 4px;">Prescripciones Médicas</h5>
                                    <div style="min-height: 200px; margin-bottom: 15px; font-size: 12.5px; color: #111; white-space: pre-wrap; line-height: 1.6; font-family: inherit;">{{ p.receta_texto }}</div>

                                    <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #d4af37; margin-top: 20px; padding-top: 10px;">
                                        <div>
                                            <p style="margin: 0; font-size: 9.5px; color: #666; font-family: monospace;"><b>CÓDIGO QR DE VALIDACIÓN DNIT/MSPBS:</b></p>
                                            <p style="margin: 2px 0 0 0; font-size: 9px; color: #888;">Hash: AE-9823-PY-2026-X89Q</p>
                                            <p style="margin: 2px 0 0 0; font-size: 9px; color: #059669; font-weight: bold;">Firma Digital Autorizada de Aeterna</p>
                                        </div>
                                        <div style="background: #111; padding: 6px; border-radius: 4px; display: inline-block;">
                                            <svg width="50" height="50" viewBox="0 0 20 20">
                                                <path fill="#fff" d="M0 0h7v7H0zM2 2h3v3H2zM13 0h7v7h-7zM15 2h3v3h-3zM0 13h7v7H0zM2 15h3v3H2zM9 2h2v2H9zM15 13h2v2H-2zM13 15h2v2H-2zM17 17h3v3h-3zM9 9h2v2H9zM13 9h2v2H9zM9 13h2v2H9zM17 9h2v2H-2z"/>
                                            </svg>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    {% elif seccion == 'regenerativa' %}
                        <div class="box" style="border-color: var(--accent);">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 20px;">
                                <h3 style="margin: 0; border: none; padding: 0;">Protocolos de Medicina Regenerativa & Infusiones</h3>
                                <span class="badge-status">Control Clínico Aeterna</span>
                            </div>

                            <form onsubmit="guardarRegenerativa(event, '{{ p.id }}')">
                                <div class="form-group" style="margin-bottom: 25px;">
                                    <label style="font-size: 13px; color: var(--accent);">Diagnóstico Clínico / Indicación Regenerativa (DX):</label>
                                    <textarea id="reg_dx" class="form-control" rows="3" placeholder="Escriba el diagnóstico o enfoque regenerativo del paciente...">{{ p.regenerativa_dx }}</textarea>
                                </div>

                                <h4 style="color: var(--accent); font-size: 12.5px; text-transform: uppercase; margin-bottom: 15px;">Seguimiento de Sesiones</h4>
                                
                                <div style="overflow-x: auto; margin-bottom: 20px;">
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <thead>
                                            <tr style="background: var(--bg-main);">
                                                <th style="width: 15%; padding: 10px; font-size: 11px; color: var(--accent);">Sesión</th>
                                                <th style="width: 20%; padding: 10px; font-size: 11px; color: var(--accent);">Fecha</th>
                                                <th style="width: 32.5%; padding: 10px; font-size: 11px; color: var(--accent);">Protocolo / Infusión</th>
                                                <th style="width: 32.5%; padding: 10px; font-size: 11px; color: var(--accent);">Observaciones / Evolución</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for s in p.regenerativa_sesiones %}
                                            <tr>
                                                <td style="padding: 10px; font-weight: bold; color: var(--accent);">{{ s.sesion }}</td>
                                                <td style="padding: 10px;">
                                                    <input type="text" id="fecha_{{ loop.index }}" class="form-control" value="{{ s.fecha }}" style="font-size: 12px; padding: 6px 10px;">
                                                </td>
                                                <td style="padding: 10px;">
                                                    <input type="text" id="protocolo_{{ loop.index }}" class="form-control" value="{{ s.protocolo }}" style="font-size: 12px; padding: 6px 10px;">
                                                </td>
                                                <td style="padding: 10px;">
                                                    <input type="text" id="obs_{{ loop.index }}" class="form-control" value="{{ s.observaciones }}" style="font-size: 12px; padding: 6px 10px;">
                                                </td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>

                                <button type="submit" class="btn" style="width: auto;">Guardar Protocolo Regenerativo</button>
                            </form>
                        </div>
                    {% elif seccion == 'wearables' %}
                        <div style="background: rgba(212, 175, 55, 0.12); border: 1px solid var(--accent); padding: 14px 20px; border-radius: 8px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <span style="font-size: 18px;">i</span>
                                <div>
                                    <h4 style="margin: 0; color: var(--accent); font-size: 12.5px; text-transform: uppercase; letter-spacing: 0.5px;">Panel de Monitoreo & Alerta IA Aeterna</h4>
                                    <p style="margin: 3px 0 0 0; font-size: 12.5px; color: var(--text-primary);">{{ p.wearables.alerta_ia }}</p>
                                </div>
                            </div>
                            <span class="badge-status" style="font-size: 10.5px;">IA Activa 24/7</span>
                        </div>

                        <div class="box" style="border-color: var(--accent);">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 20px;">
                                <h3 style="margin: 0; border: none; padding: 0;">Métricas Biométricas en Tiempo Real</h3>
                                <span class="badge-status">{{ p.wearables.sync_status }}</span>
                            </div>

                            <form onsubmit="guardarWearables(event, '{{ p.id }}')">
                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                        <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Dispositivo Vinculado</span>
                                        <input type="text" id="wear_disp" class="form-control" value="{{ p.wearables.dispositivo }}" style="margin-top: 5px; font-size: 12.5px;">
                                    </div>
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                        <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Promedio de Sueño / Eficiencia</span>
                                        <input type="text" id="wear_sueno" class="form-control" value="{{ p.wearables.sueno_horas }} ({{ p.wearables.eficiencia_sueno }})" style="margin-top: 5px; font-size: 12.5px;">
                                    </div>
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                        <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">HRV Actual</span>
                                        <input type="text" id="wear_hrv" class="form-control" value="{{ p.wearables.hrv }}" style="margin-top: 5px; font-size: 12.5px;">
                                    </div>
                                </div>

                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                        <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Frecuencia Cardiaca en Reposo (FCR)</span>
                                        <input type="text" id="wear_fcr" class="form-control" value="{{ p.wearables.frecuencia_cardiaca_reposo }}" style="margin-top: 5px; font-size: 12.5px;">
                                    </div>
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                        <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Índice de Esfuerzo / Strain</span>
                                        <input type="text" id="wear_strain" class="form-control" value="{{ p.wearables.strain_esfuerzo }}" style="margin-top: 5px; font-size: 12.5px;">
                                    </div>
                                    <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border);">
                                        <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Temperatura & Circadiano</span>
                                        <input type="text" class="form-control" value="{{ p.wearables.temperatura_corporal }}" readonly style="margin-top: 5px; font-size: 12.5px; opacity: 0.8;">
                                    </div>
                                </div>

                                <div class="form-group" style="margin-bottom: 20px;">
                                    <label>Observaciones Clínicas & Notas del Médico:</label>
                                    <textarea id="wear_obs" class="form-control" rows="3">{{ p.wearables.observaciones }}</textarea>
                                </div>

                                <button type="submit" class="btn" style="width: auto;">Guardar Datos de Wearables</button>
                            </form>
                        </div>
                    {% elif seccion == 'consentimientos' %}
                        <div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; margin-bottom: 24px;">
                            <div class="box no-print" style="margin-bottom: 0; border-color: var(--accent);">
                                <h3>Generador de Consentimiento Informado</h3>
                                <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 15px;">Seleccione la plantilla predefinida. El sistema completará automáticamente los datos del paciente para su impresión inmediata.</p>
                                
                                <form onsubmit="registrarConsentimiento(event, '{{ p.id }}')">
                                    <div class="form-group">
                                        <label>Plantilla Institucional:</label>
                                        <select id="cons_select" class="form-control">
                                            <option value="Consentimiento Informado para Sueroterapia & Infusiones IV">Consentimiento para Sueroterapia & Infusiones IV</option>
                                            <option value="Contrato de Tratamiento de Medicina Regenerativa & NAD+">Contrato de Medicina Regenerativa & NAD+</option>
                                            <option value="Consentimiento para Evaluación Metabólica & Biomarcadores">Consentimiento para Evaluación Metabólica</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label>Cláusulas / Observaciones Adicionales (Opcional):</label>
                                        <textarea id="cons_notas" class="form-control" rows="4" placeholder="Agregue indicaciones particulares si es necesario..."></textarea>
                                    </div>
                                    <button type="submit" class="btn" style="margin-bottom: 10px;">Registrar en Expediente</button>
                                </form>
                            </div>

                            <div>
                                <div style="display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 10px;" class="no-print">
                                    <button class="btn" style="width: auto; background: var(--success); color: #000;" onclick="enviarWhatsApp('Consentimiento Informado y Documentación Legal')">Enviar WhatsApp</button>
                                    <button class="btn" style="width: auto; background: var(--accent); color: #090908;" onclick="window.print()">Imprimir Consentimiento Autocompletado</button>
                                </div>

                                <div class="consent-print-sheet" style="background: #ffffff; color: #121110; border: 2px solid var(--accent); padding: 30px; box-sizing: border-box; border-radius: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #d4af37; padding-bottom: 12px; margin-bottom: 20px;">
                                        <div>
                                            <h4 style="margin: 0; color: #b8860b; font-size: 15px; letter-spacing: 1px; text-transform: uppercase;">Instituto Aeterna E.A.S.</h4>
                                            <p style="margin: 2px 0 0 0; font-size: 10.5px; color: #555;">Avenida Guido Spano, c/ San José — CDE, Paraguay (RUC: 80172292-6)</p>
                                        </div>
                                        <div style="text-align: right;">
                                            <span style="font-size: 10px; background: #f4f6f9; padding: 3px 8px; border-radius: 4px; border: 1px solid #d1d5db; font-weight: bold; color: #b8860b;">DOCUMENTO LEGAL VÁLIDO</span>
                                        </div>
                                    </div>

                                    <div style="background: #f9fafb; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-size: 12px; border: 1px solid #e5e7eb;">
                                        <p style="margin: 3px 0; color: #111;"><b>Paciente:</b> {{ p.nombre }} ({{ p.edad }} años)</p>
                                        <p style="margin: 3px 0; color: #111;"><b>Programa Clínico:</b> {{ p.programa }}</p>
                                        <p style="margin: 3px 0; color: #111;"><b>Médico Tratante:</b> {{ p.medico }} ({{ p.reg_profesional }})</p>
                                        <p style="margin: 3px 0; color: #111;"><b>Fecha de Emisión:</b> 20/10/2026</p>
                                    </div>

                                    <h4 style="color: #b8860b; font-size: 13px; text-transform: uppercase; text-align: center; margin-bottom: 15px;">CONSENTIMIENTO INFORMADO & TÉRMINOS CLÍNICOS</h4>

                                    <p style="font-size: 12px; color: #333; line-height: 1.6; text-align: justify;">
                                        Por medio del presente documento, el/la paciente <b>{{ p.nombre }}</b> manifiesta haber recibido información detallada, clara y suficiente por parte del <b>{{ p.medico }}</b> respecto al protocolo médico, los objetivos de optimización biológica y los procedimientos de medicina regenerativa a ser aplicados en el Instituto Aeterna E.A.S.
                                    </p>

                                    <p style="font-size: 12px; color: #333; line-height: 1.6; text-align: justify;">
                                        El paciente autoriza expresamente la realización de las terapias bajo estricto monitoreo clínico, asumiendo el compromiso de seguir las pautas de suplementación, descanso y control biométrico establecidas en su dossier personalizado.
                                    </p>

                                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 50px; text-align: center;">
                                        <div style="border-top: 1px solid #333; padding-top: 8px;">
                                            <p style="margin: 0; font-size: 11px; color: #333;"><b>{{ p.nombre }}</b></p>
                                            <p style="margin: 2px 0 0 0; font-size: 10px; color: #666;">Firma del Paciente / C.I.</p>
                                        </div>
                                        <div style="border-top: 1px solid #333; padding-top: 8px;">
                                            <p style="margin: 0; font-size: 11px; color: #333;"><b>{{ p.medico }}</b></p>
                                            <p style="margin: 2px 0 0 0; font-size: 10px; color: #666;">Firma y Sello Médico</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    {% elif seccion == 'reporte_longevidad' %}
                        <div class="box" style="border-color: var(--accent);">
                            <h3>Generador de Reporte Integral de Longevidad (PDF)</h3>
                            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 20px;">Consolida la historia clínica, evolución, gráficos longitudinales de laboratorio, biometría de wearables y recetas en un único reporte ejecutivo listo para entregar al paciente.</p>
                            <div style="display: flex; gap: 10px;">
                                <a href="/api/generar-pdf/{{ p.id }}" target="_blank" class="btn" style="width: auto; text-decoration: none; display: inline-block;">Generar Reporte Integral PDF</a>
                                <button class="btn" onclick="enviarWhatsApp('Reporte Integral de Longevidad PDF')" style="width: auto; background: var(--success); color: #000;">Enviar por WhatsApp</button>
                            </div>
                        </div>
                    {% elif seccion == 'portal_paciente' %}
                        <div class="box" style="border-color: var(--accent);">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 20px;">
                                <h3 style="margin: 0; border: none; padding: 0;">Portal VIP Aeterna — Mi Dossier de Bio-Hacking & Tendencias</h3>
                                <div style="display: flex; gap: 10px; align-items: center;">
                                    <span class="badge-status">Acceso Exclusivo Paciente</span>
                                    <a href="/api/generar-pdf/{{ p.id }}" target="_blank" class="btn" style="width: auto; padding: 6px 14px; font-size: 11px; text-decoration: none;">Descargar Mi Dossier PDF</a>
                                </div>
                            </div>
                            
                            <p style="font-size: 13.5px; color: var(--text-secondary); margin-bottom: 25px;">Estimado/a <b>{{ p.nombre }}</b>, este es su espacio privado de optimización humana en Instituto Aeterna E.A.S. Aquí visualiza sus guías de longevidad a medida, pautas de nutrición circadiana y el seguimiento gráfico de sus biomarcadores y dispositivos.</p>

                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px;">
                                <div style="background: var(--bg-main); padding: 18px; border-radius: 8px; border: 1px solid var(--border); text-align: center;">
                                    <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Programa Activo</span>
                                    <h4 style="color: var(--accent); font-size: 13.5px; margin: 8px 0 0 0;">{{ p.programa }}</h4>
                                </div>
                                <div style="background: var(--bg-main); padding: 18px; border-radius: 8px; border: 1px solid var(--border); text-align: center;">
                                    <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Dispositivo Sincronizado</span>
                                    <h4 style="color: var(--success); font-size: 13.5px; margin: 8px 0 0 0;">{{ p.wearables.dispositivo }}</h4>
                                </div>
                                <div style="background: var(--bg-main); padding: 18px; border-radius: 8px; border: 1px solid var(--border); text-align: center;">
                                    <span style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Estado Biológico (IA)</span>
                                    <h4 style="color: var(--success); font-size: 13.5px; margin: 8px 0 0 0;">Optimizado</h4>
                                </div>
                            </div>

                            <div style="background: var(--bg-main); padding: 22px; border-radius: 8px; border: 1px solid var(--accent); margin-bottom: 25px;">
                                <h4 style="color: var(--accent); font-size: 13px; text-transform: uppercase; margin-top: 0; border-bottom: 1px solid var(--border); padding-bottom: 8px;">Mi Dossier de Nutrición Circadiana & Suplementación</h4>
                                
                                <div style="margin-bottom: 15px; margin-top: 12px;">
                                    <span style="font-size: 11.5px; color: var(--accent); font-weight: bold; text-transform: uppercase;">Pautas de Alimentación & Ventana Metabólica:</span>
                                    <p style="font-size: 13px; color: var(--text-primary); margin: 4px 0 0 0;">{{ p.dossier.nutricion }}</p>
                                </div>

                                <div style="margin-bottom: 15px;">
                                    <span style="font-size: 11.5px; color: var(--accent); font-weight: bold; text-transform: uppercase;">Protocolo de Suplementación Avanzada:</span>
                                    <p style="font-size: 13px; color: var(--text-primary); margin: 4px 0 0 0;">{{ p.dossier.suplementacion }}</p>
                                </div>

                                <div>
                                    <span style="font-size: 11.5px; color: var(--accent); font-weight: bold; text-transform: uppercase;">Higiene del Sueño & Cronobiología:</span>
                                    <p style="font-size: 13px; color: var(--text-primary); margin: 4px 0 0 0;">{{ p.dossier.habitos_sueno }}</p>
                                </div>
                            </div>

                            <h4 style="color: var(--accent); font-size: 13px; text-transform: uppercase; margin-bottom: 15px;">Mis Gráficos de Evolución & Tendencias Biológicas</h4>
                            
                            {% for bio in p.biomarcadores_longitudinales %}
                            <div style="background: var(--bg-main); padding: 20px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 20px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <h5 style="margin: 0; color: var(--accent); font-size: 13px; text-transform: uppercase;">{{ bio.parametro }}</h5>
                                    <span class="badge-pill" style="font-size: 11px;">Rango Óptimo: {{ bio.rango_optimo }}</span>
                                </div>

                                <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; align-items: center;">
                                    <div style="background: var(--card-bg); padding: 15px; border-radius: 6px; border: 1px solid var(--border); text-align: center;">
                                        <svg width="100%" height="110" viewBox="0 0 300 110" style="overflow: visible;">
                                            <line x1="0" y1="20" x2="300" y2="20" stroke="var(--border)" stroke-dasharray="3,3" />
                                            <line x1="0" y1="60" x2="300" y2="60" stroke="var(--border)" stroke-dasharray="3,3" />
                                            <line x1="0" y1="100" x2="300" y2="100" stroke="var(--border)" stroke-dasharray="3,3" />
                                            
                                            {% set count = bio.historial | length %}
                                            {% if count > 1 %}
                                                {% set points = namespace(val="") %}
                                                {% for h in bio.historial %}
                                                    {% set x = 30 + (loop.index0 * (240 / (count - 1))) %}
                                                    {% set y = 100 - ((h.valor / 150.0) * 80) %}
                                                    {% if loop.first %}
                                                        {% set points.val = x ~ "," ~ y %}
                                                    {% else %}
                                                        {% set points.val = points.val ~ " " ~ x ~ "," ~ y %}
                                                    {% endif %}
                                                {% endfor %}
                                                
                                                <polyline fill="none" stroke="var(--accent)" stroke-width="2.5" points="{{ points.val }}" />
                                                
                                                {% for h in bio.historial %}
                                                    {% set x = 30 + (loop.index0 * (240 / (count - 1))) %}
                                                    {% set y = 100 - ((h.valor / 150.0) * 80) %}
                                                    <circle cx="{{ x }}" cy="{{ y }}" r="5" fill="var(--accent)" />
                                                    <text x="{{ x }}" y="{{ y - 10 }}" fill="var(--text-primary)" font-size="10" text-anchor="middle" font-weight="bold">{{ h.valor }}</text>
                                                    <text x="{{ x }}" y="115" fill="var(--text-secondary)" font-size="9" text-anchor="middle">{{ h.fecha }}</text>
                                                {% endfor %}
                                            {% else %}
                                                <text x="150" y="55" fill="var(--text-secondary)" font-size="11" text-anchor="middle">Se requieren al menos 2 mediciones históricas.</text>
                                                <text x="150" y="75" fill="var(--accent)" font-size="12" text-anchor="middle" font-weight="bold">Valor actual: {{ bio.historial[0].valor }} {{ bio.historial[0].unidad }}</text>
                                            {% endif %}
                                        </svg>
                                    </div>

                                    <div>
                                        <table style="margin-top: 0;">
                                            <tr><th>Fecha</th><th>Valor</th><th>Estado</th></tr>
                                            {% for h in bio.historial %}
                                            <tr>
                                                <td><b>{{ h.fecha }}</b></td>
                                                <td style="color: var(--accent); font-weight: bold;">{{ h.valor }} {{ h.unidad }}</td>
                                                <td><span style="color: var(--success); font-weight: bold;">Óptimo</span></td>
                                            </tr>
                                            {% endfor %}
                                        </table>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                {% endif %}
            {% endif %}
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            if (localStorage.getItem('medysis_theme') === 'light') {
                document.body.classList.add('light-mode');
                const btn = document.getElementById('themeBtn');
                if (btn) btn.textContent = "Tema";
            }
        });

        function toggleTheme() {
            const body = document.body;
            body.classList.toggle('light-mode');
            const btn = document.getElementById('themeBtn');
            if (body.classList.contains('light-mode')) {
                localStorage.setItem('medysis_theme', 'light');
                btn.textContent = "Tema";
            } else {
                localStorage.setItem('medysis_theme', 'dark');
                btn.textContent = "Tema";
            }
        }

        function enviarWhatsApp(tipoDoc) {
            alert('Documento (' + tipoDoc + ') enviado exitosamente al WhatsApp del paciente registrado.');
        }

        function registrarPagoAdmin(event) {
            event.preventDefault();
            const data = {
                paciente: document.getElementById('reg_paciente').value,
                monto: document.getElementById('reg_monto').value,
                metodo: document.getElementById('reg_metodo').value,
                referencia: document.getElementById('reg_ref').value
            };
            fetch('/api/admin/registrar-pago', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert('Pago registrado y aprobado por Sifen correctamente.');
                window.location.href = '/?rol=secretaria&seccion=caja';
            });
        }

        function guardarEntrenamiento(event, idPaciente) {
            event.preventDefault();
            const data = {
                id_paciente: idPaciente,
                enfoque: document.getElementById('ent_enfoque').value,
                sesiones: document.getElementById('ent_sesiones').value,
                prescripcion: document.getElementById('ent_prescripcion').value
            };
            fetch('/api/entrenador/guardar-entrenamiento', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }

        function guardarEvolucion(event, idPaciente) {
            event.preventDefault();
            const data = { id_paciente: idPaciente, evolucion: document.getElementById('evo_texto').value };
            fetch('/api/medico/guardar-evolucion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(() => { alert('Evolución guardada.'); window.location.reload(); });
        }

        function solicitarLab(event, idPaciente) {
            event.preventDefault();
            const checkboxes = document.querySelectorAll('input[name="lab"]:checked');
            let seleccionados = Array.from(checkboxes).map(cb => cb.value).join(', ');
            if (!seleccionados) seleccionados = "Perfil Metabólico Base Aeterna";
            
            const data = { id_paciente: idPaciente, estudios: seleccionados };
            fetch('/api/medico/guardar-solicitud-lab', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(() => { alert('Orden oficial de exámenes laboratoriales generada con éxito.'); window.location.reload(); });
        }

        function sincronizarLIS(idPaciente) {
            const data = { id_paciente: idPaciente };
            fetch('/api/medico/sincronizar-lis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }

        function guardarBiomarcadorManual(event, idPaciente) {
            event.preventDefault();
            const data = {
                id_paciente: idPaciente,
                parametro: document.getElementById('manual_param').value,
                fecha: document.getElementById('manual_fecha').value,
                valor: document.getElementById('manual_valor').value,
                unidad: document.getElementById('manual_unidad').value
            };
            fetch('/api/medico/guardar-biomarcador-manual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }

        function guardarInformeDirectoNoLab(event, idPaciente) {
            event.preventDefault();
            const data = {
                id_paciente: idPaciente,
                tipo: document.getElementById('nolab_tipo').value,
                informe: document.getElementById('nolab_informe').value
            };
            fetch('/api/medico/guardar-informe-directo-nolab', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }

        function guardarRecetaTexto(event, idPaciente) {
            event.preventDefault();
            const data = {
                id_paciente: idPaciente,
                receta_texto: document.getElementById('receta_input_texto').value
            };
            fetch('/api/medico/guardar-receta-texto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }

        function guardarRegenerativa(event, idPaciente) {
            event.preventDefault();
            const data = {
                id_paciente: idPaciente,
                dx: document.getElementById('reg_dx').value,
                fecha_1: document.getElementById('fecha_1').value,
                protocolo_1: document.getElementById('protocolo_1').value,
                obs_1: document.getElementById('obs_1').value,
                fecha_2: document.getElementById('fecha_2').value,
                protocolo_2: document.getElementById('protocolo_2').value,
                obs_2: document.getElementById('obs_2').value,
                fecha_3: document.getElementById('fecha_3').value,
                protocolo_3: document.getElementById('protocolo_3').value,
                obs_3: document.getElementById('obs_3').value,
                fecha_4: document.getElementById('fecha_4').value,
                protocolo_4: document.getElementById('protocolo_4').value,
                obs_4: document.getElementById('obs_4').value,
            };
            fetch('/api/medico/guardar-regenerativa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }

        function guardarWearables(event, idPaciente) {
            event.preventDefault();
            const data = {
                id_paciente: idPaciente,
                dispositivo: document.getElementById('wear_disp').value,
                sueno: document.getElementById('wear_sueno').value,
                hrv: document.getElementById('wear_hrv').value,
                fcr: document.getElementById('wear_fcr').value,
                strain: document.getElementById('wear_strain').value,
                obs: document.getElementById('wear_obs').value
            };
            fetch('/api/medico/guardar-wearables', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }

        function registrarConsentimiento(event, idPaciente) {
            event.preventDefault();
            const data = {
                id_paciente: idPaciente,
                titulo: document.getElementById('cons_select').value
            };
            fetch('/api/medico/registrar-consentimiento', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(resp => {
                alert(resp.mensaje);
                window.location.reload();
            });
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, port=5000)
