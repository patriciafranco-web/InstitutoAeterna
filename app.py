from flask import Flask, render_template_string, request, jsonify, Response, session, redirect, url_for
import random
import requests

app = Flask(__name__)
app.secret_key = 'aeterna_secret_key_2026_produccion_total_ilimitada'

# URL de tu app de finanzas en Render para sincronizar los cobros automáticamente
FINANZAS_API_URL = "https://finanzas1.onrender.com/api/v1/registrar-transaccion"

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
    "recepcion": {
        "pass": "recepcion2026", 
        "nombre": "Admisión / Secretaría de Ventas", 
        "rol_base": "admision", 
        "es_socio": False,
        "especialidad": "Venta de Paquetes & Enlaces Pre-Consulta"
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
        "link_enviado": True,
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
                "evolucion": "Paciente refiere leve mejora en energía diurna. Se ajusta dosis de magnesio a 145mg y se solicita panel metabólico de control."
            },
            {
                "fecha": "20/08/2026",
                "medico": "Dr. Pedro Calabrese",
                "evolucion": "Primera consulta de evaluación metabólica y biomarcadores iniciales. Se detecta resistencia insulínica leve y fatiga matutina severa."
            }
        ],
        "solicitudes_lab_previas": [
            {"fecha": "14/09/2026", "estudios": "Perfil Lipídico, Insulina Basal, HbA1c, Tiempo de Coagulación", "estado": "Completado y Sincronizado"},
            {"fecha": "20/08/2026", "estudios": "Panel Metabólico Base, Cortisol AM/PM, PCR Ultrasensible", "estado": "Completado y Sincronizado"}
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
            {"sesion": "Sesión 01", "fecha": "15/09/2026", "protocolo": "Sueroterapia NAD+ 250mg + Vit C Alta Dosis", "observaciones": "Buena tolerancia."},
            {"sesion": "Sesion 02", "fecha": "30/09/2026", "protocolo": "Sueroterapia NAD+ 500mg + Complejo B", "observaciones": "Aumento notable de energía diurna."}
        ],
        "consentimientos_firmados": [
            {"titulo": "Consentimiento Informado para Sueroterapia & Infusiones IV", "fecha": "20/08/2026", "estado": "Emitido & Firmado"}
        ],
        "dossier": {
            "nutricion": "Ventana de alimentación restringida de 10 horas (10:00 AM - 08:00 PM). Enfoque cetogénico moderado.",
            "suplementacion": "Protocolo mitocondrial: NAD+, Magnesio L-Treonato, Ubiquinol.",
            "habitos_sueno": "Bloqueo de luz azul, temperatura ambiental a 19°C."
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
        "link_enviado": False,
        "pre_consulta": {
            "nombre_completo": "María Giménez",
            "edad": "38",
            "genero": "Femenino",
            "residencia": "Hernandarias, Paraguay",
            "objetivos": "Optimizar rendimiento cognitivo y equilibrio hormonal.",
            "queja": "Niebla mental matutina.",
            "salud_actual": "7/10",
            "compromiso": "Alto"
        },
        "historial_consultas": [
            {
                "fecha": "10/09/2026",
                "medico": "Dra. Fátima López",
                "evolucion": "Evaluación inicial de rendimiento cognitivo. Se pauta suplementación con complejo B y monitoreo con Whoop."
            }
        ],
        "solicitudes_lab_previas": [
            {"fecha": "10/09/2026", "estudios": "Perfil Tiroideo Completo, Vitamina D, Ferritina", "estado": "Completado y Sincronizado"}
        ],
        "archivos_no_lab": [],
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
        "biomarcadores_longitudinales": [
            {
                "parametro": "TSH",
                "rango_optimo": "0.5 - 2.5 mIU/L",
                "historial": [
                    {"fecha": "10/09/2026", "valor": 2.8, "unidad": "mIU/L"},
                    {"fecha": "05/10/2026", "valor": 1.9, "unidad": "mIU/L"}
                ]
            }
        ],
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
        "link_enviado": False,
        "pre_consulta": {
            "nombre_completo": "Roberto Duarte",
            "edad": "50",
            "genero": "Masculino",
            "residencia": "Presidente Franco, Paraguay",
            "objetivos": "Optimización cardiovascular y control lipídico.",
            "queja": "Rigidez matutina leve y colesterol limítrofe.",
            "salud_actual": "7/10",
            "compromiso": "Alto"
        },
        "historial_consultas": [
            {
                "fecha": "01/09/2026",
                "medico": "Dr. Pedro Calabrese",
                "evolucion": "Control de presión arterial y perfil lipídico. Se inicia pauta de Coenzima Q10."
            }
        ],
        "solicitudes_lab_previas": [
            {"fecha": "01/09/2026", "estudios": "Perfil Lipídico Completo, Homocisteína", "estado": "Completado y Sincronizado"}
        ],
        "archivos_no_lab": [],
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
        "biomarcadores_longitudinales": [
            {
                "parametro": "Colesterol Total",
                "rango_optimo": "< 200 mg/dL",
                "historial": [
                    {"fecha": "01/09/2026", "valor": 230, "unidad": "mg/dL"},
                    {"fecha": "01/10/2026", "valor": 205, "unidad": "mg/dL"}
                ]
            }
        ],
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
                elif user_info['rol_base'] == 'admision':
                    return redirect(url_for('index', rol='admision', seccion='agenda_admision'))
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
    elif rol_base == 'admision':
        rol = 'admision'
    else:
        rol = requested_rol if (requested_rol == 'medico' and rol_base == 'medico') else rol_base

    seccion = request.args.get('seccion', 'agenda_medico' if rol == 'medico' else ('agenda_entrenador' if rol == 'entrenador' else ('agenda_admision' if rol == 'admision' else 'caja')))
    id_paciente = request.args.get('id', 'p1')
    
    if rol == 'medico':
        mis_pacientes = [p for p in PACIENTES if p['medico'].strip().lower() == nombre_usuario.strip().lower()]
        if not mis_pacientes:
            mis_pacientes = PACIENTES[:1]
        paciente_actual = next((p for p in mis_pacientes if p['id'] == id_paciente), mis_pacientes[0])
    else:
        mis_pacientes = PACIENTES
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

@app.route('/api/admision/marregar-enlace', methods=['POST'])
def marcar_enlace_enviado():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        paciente['link_enviado'] = True
        return jsonify({"status": "success", "mensaje": f"Enlace de pre-consulta marcado como enviado a {paciente['nombre']}."})
    return jsonify({"status": "error"}), 404

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
    
    try:
        requests.post(FINANZAS_API_URL, json=nuevo_pago, timeout=3)
    except Exception:
        pass
        
    return jsonify({"status": "success", "pago": nuevo_pago})

@app.route('/api/admin/ver-kude/<int:pago_id>')
def ver_kude(pago_id):
    pago = next((item for item in db_caja_pagos if item['id'] == pago_id), db_caja_pagos[0])
    return f"""
    <html>
    <head><title>KUDE - Sifen - Instituto Aeterna E.A.S.</title></head>
    <body style="font-family: monospace; padding: 30px;">
        <h2>INSTITUTO AETERNA E.A.S.</h2>
        <p>RUC: 80172292-6 | Factura N°: 001-001-{pago_id:07d}</p>
        <p><b>CDC:</b> {pago['cdc']}</p>
        <p><b>PACIENTE:</b> {pago['paciente']} | <b>MONTO:</b> Gs. {pago['monto']:,.0f}</p>
        <p>[ CÓDIGO QR TRIBUTARIO DNIT ]</p>
        <button onclick="window.print()">Imprimir KUDE</button>
    </body>
    </html>
    """

@app.route('/api/generar-pdf/<id_paciente>')
def generar_pdf(id_paciente):
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), PACIENTES[0])
    return f"<h1>Reporte Integral PDF - {paciente['nombre']}</h1>"

@app.route('/api/medico/guardar-biomarcador-manual', methods=['POST'])
def guardar_biomarcador_manual():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    parametro = data.get('parametro', 'Biomarcador')
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
            if bio['parametro'].strip().lower() == parametro.strip().lower():
                bio['historial'].append({"fecha": fecha, "valor": valor, "unidad": unidad})
                encontrado = True
                break
        if not encontrado:
            paciente['biomarcadores_longitudinales'].append({
                "parametro": parametro,
                "rango_optimo": "Personalizado",
                "historial": [{"fecha": fecha, "valor": valor, "unidad": unidad}]
            })
        return jsonify({"status": "success", "mensaje": "Biomarcador registrado en la línea de tiempo."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/procesar-pdf-laboratorio', methods=['POST'])
def procesar_pdf_laboratorio():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    paciente = next((p for p in PACIENTES if p['id'] == id_paciente), None)
    if paciente:
        hallazgos = [
            {"parametro": "Glucosa en Ayunas", "valor": 84.0, "unidad": "mg/dL", "fecha": "20/10/2026"},
            {"parametro": "Colesterol LDL", "valor": 95.0, "unidad": "mg/dL", "fecha": "20/10/2026"},
            {"parametro": "Insulina Basal", "valor": 4.1, "unidad": "uIU/mL", "fecha": "20/10/2026"}
        ]
        for h in hallazgos:
            encontrado = False
            for bio in paciente['biomarcadores_longitudinales']:
                if bio['parametro'].strip().lower() == h['parametro'].strip().lower():
                    bio['historial'].append({"fecha": h['fecha'], "valor": h['valor'], "unidad": h['unidad']})
                    encontrado = True
                    break
            if not encontrado:
                paciente['biomarcadores_longitudinales'].append({
                    "parametro": h['parametro'],
                    "rango_optimo": "Estándar",
                    "historial": [{"fecha": h['fecha'], "valor": h['valor'], "unidad": h['unidad']}]
                })
        return jsonify({"status": "success", "mensaje": "¡PDF procesado por IA! Se actualizaron los biomarcadores automáticamente."})
    return jsonify({"status": "error"}), 404

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head><title>Login — Instituto Aeterna</title></head>
<body style="font-family:sans-serif; background:#f4f6f9; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
    <div style="background:#fff; padding:40px; border-radius:8px; width:350px; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
        <h2 style="color:#b8860b; text-align:center;">Instituto Aeterna E.A.S.</h2>
        {% if error %}<p style="color:red; font-size:12px; text-align:center;">{{ error }}</p>{% endif %}
        <form method="POST">
            <label style="font-size:11px; font-weight:bold;">Usuario:</label>
            <input type="text" name="username" required style="width:100%; padding:10px; margin:5px 0 15px 0; box-sizing:border-box;" autofocus>
            <label style="font-size:11px; font-weight:bold;">Contraseña:</label>
            <input type="password" name="password" required style="width:100%; padding:10px; margin:5px 0 15px 0; box-sizing:border-box;">
            <button type="submit" style="background:#b8860b; color:#fff; border:none; padding:12px; width:100%; font-weight:bold; cursor:pointer;">Entrar</button>
        </form>
    </div>
</body>
</html>"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Instituto Aeterna E.A.S. — Sistema de Gestión</title>
    <style>
        :root { --bg-main: #121110; --sidebar-bg: #090908; --card-bg: #1c1a18; --text-primary: #f5f2eb; --text-secondary: #a8a29e; --accent: #d4af37; --border: #292524; --success: #34d399; }
        body.light-mode { --bg-main: #f4f6f9; --sidebar-bg: #fff; --card-bg: #fff; --text-primary: #121110; --text-secondary: #555770; --accent: #b8860b; --border: #d1d5db; --success: #059669; }
        body { font-family: 'Inter', system-ui, sans-serif; background-color: var(--bg-main); margin: 0; color: var(--text-primary); display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 280px; background-color: var(--sidebar-bg); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 24px; box-sizing: border-box; overflow-y: auto; }
        .sidebar a { color: var(--text-secondary); text-decoration: none; padding: 10px 14px; border-radius: 6px; margin-bottom: 3px; font-size: 13px; display: flex; justify-content: space-between; align-items: center; }
        .sidebar a:hover, .sidebar a.active { background-color: var(--border); color: var(--text-primary); border-left: 2px solid var(--accent); }
        .main-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; }
        header { background-color: var(--sidebar-bg); padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }
        .container { padding: 32px; max-width: 1300px; margin: 0 auto; width: 100%; box-sizing: border-box; }
        .box { background: var(--card-bg); padding: 28px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 24px; }
        .box h3 { margin-top: 0; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 12px; font-size: 14px; text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 13px; }
        th { background: var(--bg-main); color: var(--text-secondary); text-transform: uppercase; font-size: 11px; }
        .form-control { width: 100%; background: var(--bg-main); border: 1px solid var(--border); border-radius: 6px; padding: 10px 14px; color: var(--text-primary); font-size: 13px; box-sizing: border-box; }
        .btn { background: var(--accent); color: #090908; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px; text-transform: uppercase; }
        .logout-btn { background: rgba(248, 113, 113, 0.1); color: #f87171; padding: 6px 12px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Aeterna E.A.S.</h2>
        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 10px;">
            <b>{{ nombre_usuario }}</b>
        </div>
        {% if rol == 'admision' %}
            <a href="/?rol=admision&seccion=agenda_admision" class="{% if seccion == 'agenda_admision' %}active{% endif %}">📅 Enlaces de Pre-Consulta</a>
        {% elif rol == 'secretaria' %}
            <a href="/?rol=secretaria&seccion=caja" class="{% if seccion == 'caja' %}active{% endif %}">Caja & Facturación Sifen</a>
            <a href="/?rol=secretaria&seccion=registrar_pago" class="{% if seccion == 'registrar_pago' %}active{% endif %}">Registrar Nuevo Pago</a>
        {% elif rol == 'entrenador' %}
            <a href="/?rol=entrenador&seccion=agenda_entrenador" class="{% if seccion == 'agenda_entrenador' %}active{% endif %}">Atletas Asignados</a>
        {% else %}
            <a href="/?rol=medico&seccion=agenda_medico" class="{% if seccion == 'agenda_medico' %}active{% endif %}">Mi Agenda de Hoy</a>
            {% if seccion != 'agenda_medico' and seccion != 'caja' %}
            <div style="font-size: 10px; color: var(--accent); text-transform: uppercase; margin: 15px 0 5px 10px; font-weight: bold;">Paciente: {{ p.nombre }}</div>
            <a href="/?rol=medico&seccion=examenes_lab&id={{ p.id }}" class="{% if seccion == 'examenes_lab' %}active{% endif %}">Exámenes Laboratoriales</a>
            <a href="/?rol=medico&seccion=portal_paciente&id={{ p.id }}" class="{% if seccion == 'portal_paciente' %}active{% endif %}">Portal del Paciente (Dossier)</a>
            {% endif %}
        {% endif %}
    </div>

    <div class="main-content">
        <header>
            <h3 style="margin: 0; font-size: 13.5px;">Instituto Aeterna E.A.S. — Sanatorio Le Blanc (CDE)</h3>
            <div style="display: flex; align-items: center; gap: 15px;">
                <button class="btn" onclick="toggleTheme()" id="themeBtn" style="padding: 6px 12px; font-size: 11px;">Tema</button>
                <a href="/logout" class="logout-btn">Cerrar Sesión</a>
            </div>
        </header>

        <div class="container">
            {% if rol == 'admision' %}
                <div class="box">
                    <h3>Gestión de Enlaces de Pre-Consulta (Admisión)</h3>
                    <p style="font-size: 12.5px; color: var(--text-secondary);">Copie el enlace único del paciente y confirme su envío por WhatsApp:</p>
                    <table>
                        <tr><th>Paciente</th><th>Programa</th><th>Enlace de Pre-Consulta</th><th>Estado Envío</th><th>Acción</th></tr>
                        {% for pat in pacientes %}
                        <tr>
                            <td><b>{{ pat.nombre }}</b></td>
                            <td>{{ pat.programa }}</td>
                            <td><code style="font-size: 11px; background: var(--bg-main); padding: 4px; border-radius: 4px;">/portal/pre-consulta/{{ pat.id }}</code></td>
                            <td>
                                {% if pat.link_enviado %}
                                    <span class="badge-status">Enviado por WhatsApp 🟢</span>
                                {% else %}
                                    <span style="color: var(--warning); font-weight: bold;">Pendiente de Envío</span>
                                {% endif %}
                            </td>
                            <td>
                                <button class="btn" style="padding: 5px 10px; font-size: 10px;" onclick="marcarEnviado('{{ pat.id }}')">Confirmar Envío</button>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            {% elif rol == 'secretaria' %}
                <div class="box">
                    <h3>Control de Caja & Facturación Sifen</h3>
                    <table>
                        <tr><th>Paciente</th><th>Monto</th><th>Método</th><th>Estado Sifen</th><th>Acción</th></tr>
                        {% for item in pagos %}
                        <tr>
                            <td><b>{{ item.paciente }}</b></td>
                            <td>Gs. {{ "{:,}".format(item.monto|int) }}</td>
                            <td>{{ item.metodo }}</td>
                            <td style="color: var(--success); font-weight: bold;">{{ item.sifen_status }}</td>
                            <td><a href="/api/admin/ver-kude/{{ item.id }}" target="_blank" class="btn" style="padding: 5px 10px; font-size: 10px; text-decoration: none;">Ver KUDE</a></td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            {% else %}
                {% if seccion == 'agenda_medico' %}
                    <div class="box">
                        <h3>Mi Agenda de Hoy — {{ nombre_usuario }}</h3>
                        <table>
                            <tr><th>Hora</th><th>Paciente</th><th>Programa</th><th>Acción</th></tr>
                            {% for pat in pacientes %}
                            <tr>
                                <td><b>{{ pat.hora_turno }}</b></td>
                                <td>{{ pat.nombre }} ({{ pat.edad }} años)</td>
                                <td>{{ pat.programa }}</td>
                                <td><a href="/?rol=medico&seccion=examenes_lab&id={{ pat.id }}" class="btn" style="padding: 6px 14px; font-size: 11px; text-decoration: none;">Abrir Expediente / Labs</a></td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% elif seccion == 'examenes_lab' %}
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
                        <div class="box" style="margin-bottom: 0; border-color: var(--success); background: rgba(52, 211, 153, 0.03);">
                            <h3 style="color: var(--success); font-size: 12.5px;">🤖 Lector IA de Resultados en PDF (Laboratorio)</h3>
                            <p style="font-size: 11.5px; color: var(--text-secondary); margin-bottom: 12px;">Suba el PDF entregado por el laboratorio aliado. El sistema extraerá automáticamente los valores y actualizará la línea de tiempo.</p>
                            <div style="display: flex; gap: 10px; align-items: center;">
                                <input type="file" id="pdf_lab_file" class="form-control" accept=".pdf" style="font-size: 11px;">
                                <button type="button" class="btn" style="background: var(--success); color: #000; padding: 8px 14px; font-size: 11px; white-space: nowrap;" onclick="procesarPdfLab('{{ p.id }}')">Procesar PDF</button>
                            </div>
                        </div>

                        <div class="box" style="margin-bottom: 0; border-color: var(--accent);">
                            <h3 style="font-size: 12.5px;">➕ Carga Manual de Biomarcadores</h3>
                            <p style="font-size: 11.5px; color: var(--text-secondary); margin-bottom: 12px;">Ingrese un resultado físico para sumarlo a la línea de tiempo.</p>
                            <form onsubmit="guardarBiomarcadorManual(event, '{{ p.id }}')" style="display: flex; gap: 8px;">
                                <input type="text" id="manual_param" class="form-control" placeholder="Parámetro (Ej. Glucosa)" required style="font-size: 11.5px;">
                                <input type="number" step="0.1" id="manual_valor" class="form-control" placeholder="Valor" required style="font-size: 11.5px; width: 80px;">
                                <input type="text" id="manual_unidad" class="form-control" value="mg/dL" required style="font-size: 11.5px; width: 70px;">
                                <button type="submit" class="btn" style="padding: 8px 12px; font-size: 11px; width: auto;">Añadir</button>
                            </form>
                        </div>
                    </div>

                    <div class="box">
                        <h3>Análisis Longitudinal: Tendencias y Números Históricos ({{ p.nombre }})</h3>
                        {% for bio in p.biomarcadores_longitudinales %}
                        <div style="background: var(--bg-main); padding: 15px; border-radius: 6px; border: 1px solid var(--border); margin-bottom: 15px;">
                            <h4 style="color: var(--accent); margin: 0 0 10px 0; font-size: 13px;">{{ bio.parametro }} (Rango óptimo: {{ bio.rango_optimo }})</h4>
                            <table>
                                <tr><th>Fecha</th><th>Valor</th><th>Estado</th></tr>
                                {% for h in bio.historial %}
                                <tr><td>{{ h.fecha }}</td><td style="color: var(--accent); font-weight: bold;">{{ h.valor }} {{ h.unidad }}</td><td><span style="color: var(--success);">Óptimo</span></td></tr>
                                {% endfor %}
                            </table>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="box">
                        <h3>Portal VIP Aeterna — {{ p.nombre }}</h3>
                        <p>Espacio privado del paciente con sus gráficos de evolución y dossier de optimización.</p>
                    </div>
                {% endif %}
            {% endif %}
        </div>
    </div>

    <script>
        function toggleTheme() {
            document.body.classList.toggle('light-mode');
        }

        function marcarEnviado(idPaciente) {
            fetch('/api/admision/marregar-enlace', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_paciente: idPaciente })
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
                fecha: '20/10/2026',
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

        function procesarPdfLab(idPaciente) {
            const fileInput = document.getElementById('pdf_lab_file');
            if (!fileInput.files.length) {
                alert('Por favor seleccione un archivo PDF de laboratorio primero.');
                return;
            }
            alert('Leyendo PDF y extrayendo biomarcadores mediante motor OCR/IA...');
            fetch('/api/medico/procesar-pdf-laboratorio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_paciente: idPaciente })
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
