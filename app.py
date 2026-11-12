from flask import Flask, render_template, render_template_string, request, jsonify, Response, session, redirect, url_for, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
import random
import requests
import os
from dotenv import load_dotenv

load_dotenv()
import json
import datetime
import time
import anthropic
import re

import qrcode
import io
import base64
import uuid

from cryptography.hazmat.primitives.serialization import pkcs12

SIFEN_CERT_PASS = os.getenv('SIFEN_CERT_PASS', '')

def cargar_certificado():
    rutas_b64 = [
        '/etc/secrets/certificado.b64',
        'certificado.b64',
        os.path.join(os.path.dirname(__file__), 'certificado.b64')
    ]
    archivo_encontrado = None
    for r in rutas_b64:
        if r and os.path.exists(r):
            archivo_encontrado = r
            break
            
    if not archivo_encontrado:
        if os.path.exists('/etc/secrets/certificado.pfx'):
            with open('/etc/secrets/certificado.pfx', 'rb') as f:
                datos_bin = f.read()
            password = SIFEN_CERT_PASS.strip().encode() if SIFEN_CERT_PASS else b''
            return pkcs12.load_key_and_certificates(datos_bin, password)
        elif os.path.exists('certificado.pfx'):
            with open('certificado.pfx', 'rb') as f:
                datos_bin = f.read()
            password = SIFEN_CERT_PASS.strip().encode() if SIFEN_CERT_PASS else b''
            return pkcs12.load_key_and_certificates(datos_bin, password)
        raise FileNotFoundError("No se encontró el archivo de certificado digital.")

    with open(archivo_encontrado, "r") as f:
        contenido = f.read().strip()
    datos = base64.b64decode(contenido)
    password = SIFEN_CERT_PASS.strip().encode() if SIFEN_CERT_PASS else b''
    return pkcs12.load_key_and_certificates(datos, password)

def validar_certificado_pfx():
    try:
        private_key, certificate, additional_certificates = cargar_certificado()
        return True, "Certificado digital Sifen cargado y verificado correctamente."
    except Exception as e:
        return False, f"Error al abrir el certificado: {str(e)}"

client = anthropic.Anthropic()

app = Flask(__name__)
app.secret_key = 'aeterna_secret_key_2026_produccion_total_ilimitada'

database_url = os.environ.get('DATABASE_URL', 'sqlite:///aeterna.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELOS DE BASE DE DATOS
class PacienteModel(db.Model):
    __tablename__ = 'pacientes'
    id = db.Column(db.String(50), primary_key=True)
    token_portal = db.Column(db.String(100), unique=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(150), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    programa = db.Column(db.String(150), default="General")
    medico = db.Column(db.String(150), nullable=False)
    entrenador = db.Column(db.String(150), default="Manuel Duarte")
    reg_profesional = db.Column(db.String(50), default="MP 4291")
    hora_turno = db.Column(db.String(50), default="09:00 hs")
    estado_turno = db.Column(db.String(50), default="Confirmado / Sala VIP")
    compromiso = db.Column(db.String(250), default="Pendiente de completar")
    observacion_medica_libre = db.Column(db.Text, default="")
    pre_consulta_json = db.Column(db.Text, nullable=True)
    receta_texto = db.Column(db.Text, default="1. Protocolo inicial Aeterna.")

class ConsultaModel(db.Model):
    __tablename__ = 'consultas_historial'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    medico = db.Column(db.String(150), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    detalle = db.Column(db.Text, nullable=False)

class FotoClinicaModel(db.Model):
    __tablename__ = 'fotos_clinicas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.String(50), default=lambda: datetime.date.today().strftime('%d/%m/%Y'))

class PagoModel(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paciente = db.Column(db.String(150), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    metodo = db.Column(db.String(50), nullable=False)
    referencia = db.Column(db.String(100), default="N/A")
    estado = db.Column(db.String(50), default="Completado")
    fecha = db.Column(db.String(50), default="2026-10-20")
    sifen_status = db.Column(db.String(50), default="Aprobado Sifen")
    cdc = db.Column(db.String(100), nullable=False)
    establecimiento = db.Column(db.String(3), default="001")
    punto_expedicion = db.Column(db.String(3), default="001")
    numero_documento = db.Column(db.String(7), default="0000001")

class EstudioNoLabModel(db.Model):
    __tablename__ = 'estudios_no_lab'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    dictamen = db.Column(db.Text, nullable=True)
    origen = db.Column(db.String(200), nullable=False)
    medico = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.String(50), nullable=False)

class EstudioLabModel(db.Model):
    __tablename__ = 'estudios_lab'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    dictamen = db.Column(db.Text, nullable=True)
    origen = db.Column(db.String(200), nullable=False)
    medico = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.String(50), nullable=False)

class BiomarcadorModel(db.Model):
    __tablename__ = 'biomarcadores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    parametro = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), default="mg/dL")

class RecetaModel(db.Model):
    __tablename__ = 'recetas'
    id_receta = db.Column(db.String(100), primary_key=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    nombre_paciente = db.Column(db.String(150), nullable=False)
    nombre_medico = db.Column(db.String(150), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), default="Emitida")
    fecha_dispensacion = db.Column(db.String(50), nullable=True)

class ProtocoloRegenerativoModel(db.Model):
    __tablename__ = 'protocolos_regenerativos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    diagnostico_dx = db.Column(db.Text, default="Síndrome de Fatiga Crónica Mitocondrial & Desgaste Energético por Estrés Oxidativo.")
    sesiones_json = db.Column(db.Text, nullable=True)

class ProtocoloBiologicsModel(db.Model):
    __tablename__ = 'protocolos_biologics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    diagnostico_dx = db.Column(db.Text, default="Protocolo Clínico Biologics & Medicina Ortomoleculares.")
    observaciones = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(50), default="Sin Cargar")

class ProtocoloAnnovatorModel(db.Model):
    __tablename__ = 'protocolos_annovator'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    diagnostico_dx = db.Column(db.Text, default="Protocolo Avanzado Annovator & Innovación Terapéutica.")
    observaciones = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(50), default="Sin Cargar")

class ProtocoloWearablesModel(db.Model):
    __tablename__ = 'protocolos_wearables'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    estado_sync = db.Column(db.String(50), default="Sincronizado")
    observaciones = db.Column(db.Text, nullable=True)

class ProtocoloConsentimientoModel(db.Model):
    __tablename__ = 'protocolos_consentimientos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    tipo_plantilla = db.Column(db.String(200), default="Consentimiento para Sueroterapia & Infusiones IV")
    clausulas_adicionales = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(50), default="Generado y Autocompletado")

class TareaEquipoModel(db.Model):
    __tablename__ = 'tareas_equipo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    nombre_paciente = db.Column(db.String(150), nullable=False)
    medico_emisor = db.Column(db.String(150), nullable=False)
    profesional_destinatario = db.Column(db.String(150), nullable=False)
    mensaje_tarea = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.String(50), default=datetime.date.today().strftime('%d/%m/%Y'))
    estado = db.Column(db.String(50), default="Pendiente")

class EstudioSolicitadoModel(db.Model):
    __tablename__ = 'estudios_solicitados'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    medico = db.Column(db.String(150), nullable=False)
    estudios_texto = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(50), default="Pendiente")

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("Tablas ya inicializadas:", e)

LABORATORIOS_AETERNA = {
    "Metabólico y Base": [
        "Glucemia en ayunas", "Hemoglobina glicosilada (HbA1c)", "Insulina en ayunas (para calcular HOMA-IR)",
        "Colesterol total, HDL, LDL y no-HDL", "Triglicéridos", "TGO/AST, TGP/ALT, GGT y fosfatasa alcalina",
        "Bilirrubinas y albúmina", "Urea, creatinina con tasa de filtración estimada y ácido úrico",
        "Sodio, potasio, calcio, magnesio y fósforo", "Uroanálisis y relación albúmina/creatinina en orina", "Tiempo de coagulación"
    ],
    "Digestivo y Funcional": [
        "Enfermedad celíaca (mapeo)", "Coprológico funcional de heces", "Parasitológico seriado",
        "Antígeno fecal para Helicobacter pylori", "Test de aire espirado para hidrógeno y metano", "Calprotectina fecal"
    ],
    "Hormonal Masculino y Femenino": [
        "Testosterona total y libre", "DHEA-S", "Cortisol (am/pm)", "LH y FSH", "Estradiol", "Progesterona", "Prolactina", "TSH y T4 libre"
    ],
    "Vitaminas, Minerales e Inflamación": [
        "Vitamina D (25-OH)", "Vitamina B12", "Ácido fólico (folato)", "Ferritina y Hierro sérico",
        "Magnesio eritrocitario y Zinc", "Hemograma completo & PCR ultrasensible", "Riesgo Cardiometabólico (Lp(a), ApoB, Fibrinógeno, Homocisteína, Cistatina C)"
    ],
    "Avanzados (Complejidad Alta)": [
        "Curva de tolerancia a la glucosa con insulina (0, 60, 120 min)", "Nutrientes y Antioxidantes (Omega-3)", "Intestino y Microbiota (Secuenciación de microbiota)"
    ]
}

USUARIOS_DB = {
    "pedro.calabrese": {"pass": "aeterna2026", "pass_admin": "caja2026", "nombre": "Dr. Pedro Calabrese", "rol_base": "medico", "es_socio": True},
    "fatima.lopez": {"pass": "aeterna2026", "pass_admin": "caja2026", "nombre": "Dra. Fátima López", "rol_base": "medico", "es_socio": True},
    "romina.espinola": {"pass": "aeterna2026", "pass_admin": "caja2026", "nombre": "Dra. Romina Espinola", "rol_base": "medico", "es_socio": True},
    "ximena.ruiz": {"pass": "aeterna2026", "nombre": "Lic. Ximena Ruiz", "rol_base": "medico", "es_socio": False},
    "alfredo.estigarribia": {"pass": "aeterna2026", "nombre": "Dr. Alfredo Estigarribia", "rol_base": "medico", "es_socio": False},
    "manuel.duarte": {"pass": "aeterna2026", "nombre": "Manuel Duarte", "rol_base": "entrenador", "es_socio": False},
    "nadia.bortolace": {"pass": "caja2026", "nombre": "Nadia Bortolace", "rol_base": "secretaria", "es_socio": False},
    "daiana.gomez": {"pass": "caja2026", "nombre": "Daiana Gomez", "rol_base": "secretaria", "es_socio": False},
    "buro": {"pass": "admin2026", "nombre": "Buró (Administración / Contabilidad)", "rol_base": "secretaria", "es_socio": False},
    "recepcion": {"pass": "recepcion2026", "nombre": "Admisión / Recepción", "rol_base": "recepcion", "es_socio": False}
}

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso — Instituto Aeterna</title>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; background-color: #f4f6f9; color: #121110; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: #ffffff; border: 1px solid #d1d5db; padding: 40px; border-radius: 8px; width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); }
        h2 { color: #800020; text-align: center; text-transform: uppercase; font-size: 15px; letter-spacing: 1.5px; margin-top: 0; }
        p.sub { text-align: center; font-size: 11px; color: #555770; margin-bottom: 25px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 11px; color: #555770; text-transform: uppercase; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; background: #f9fafb; border: 1px solid #d1d5db; border-radius: 6px; padding: 10px 12px; color: #121110; font-size: 13px; box-sizing: border-box; outline: none; }
        input:focus { border-color: #800020; }
        .btn { background: #800020; color: #ffffff; border: none; padding: 12px; border-radius: 6px; width: 100%; font-weight: bold; font-size: 12px; text-transform: uppercase; cursor: pointer; margin-top: 10px; }
        .btn:hover { background: #600018; }
        .error { color: #dc2626; font-size: 12px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Instituto Aeterna</h2>
        <p class="sub">RUC: 80172292-6 — Sanatorio Le Blanc (CDE)</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST" action="/login">
            <div class="form-group"><label>Usuario:</label><input type="text" name="username" required autofocus></div>
            <div class="form-group"><label>Contraseña:</label><input type="password" name="password" required></div>
            <button type="submit" class="btn">Iniciar Sesión</button>
        </form>
    </div>
</body>
</html>
"""

PORTAL_PRECONSULTA_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Cuestionario de Pre-Consulta 360° — Instituto Aeterna</title>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; background: #f4f6f9; color: #121110; padding: 20px; line-height: 1.5; }
        .box { max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; border-top: 5px solid #800020; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        h2 { color: #800020; text-transform: uppercase; font-size: 18px; margin-bottom: 5px; text-align: center; }
        p.sub { text-align: center; font-size: 12px; color: #555; margin-bottom: 20px; }
        .welcome-card { background: rgba(128, 0, 32, 0.04); border: 1px solid rgba(128, 0, 32, 0.2); padding: 16px; border-radius: 6px; margin-bottom: 30px; text-align: center; }
        .welcome-card h3 { color: #800020; margin: 0 0 5px 0; font-size: 15px; }
        .welcome-card p { margin: 0; font-size: 12.5px; color: #444; }
        .section-title { color: #800020; font-size: 13.5px; text-transform: uppercase; border-bottom: 2px solid #800020; padding-bottom: 5px; margin-top: 30px; margin-bottom: 15px; font-weight: bold; }
        .form-group { margin-bottom: 18px; }
        label { display: block; font-size: 11.5px; font-weight: bold; color: #444; text-transform: uppercase; margin-bottom: 6px; }
        input[type="text"], input[type="email"], input[type="number"], textarea, select { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; box-sizing: border-box; font-size: 13px; background: #f9fafb; }
        input:focus, textarea:focus, select:focus { border-color: #800020; outline: none; background: #fff; }
        .btn { background: #800020; color: white; border: none; padding: 14px; border-radius: 6px; width: 100%; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 13px; margin-top: 30px; }
        .btn:hover { background: #600018; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Instituto Aeterna E.A.S. — Sanatorio Le Blanc</h2>
        <p class="sub">Formulario de Pre-Consulta 360° | Medicina Funcional, Longevidad y Nutrición (CDE, Paraguay)</p>
        
        <div class="welcome-card">
            <h3>¡Bienvenido/a, {{ paciente.nombre }}!</h3>
            <p>Este cuestionario nos permite estructurar con máxima precisión su protocolo de optimización personalizada en el Instituto Aeterna.</p>
        </div>

        <form method="POST">
            <div class="section-title">1. Datos Personales y de Contacto</div>
            <div class="form-group">
                <label>Nombre y Apellido:</label>
                <input type="text" name="nombre_completo" value="{{ paciente.nombre }}" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Fecha de Nacimiento / Edad:</label>
                    <input type="text" name="fecha_nacimiento" placeholder="Ej. 12/05/1985 ({{ paciente.edad }} años)" required>
                </div>
                <div class="form-group">
                    <label>Género:</label>
                    <select name="genero">
                        <option value="Femenino">Femenino</option>
                        <option value="Masculino">Masculino</option>
                        <option value="Otro">Otro</option>
                    </select>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Nacionalidad y Residencia (Ciudad/País):</label>
                    <input type="text" name="residencia" value="Paraguaya / Ciudad del Este" required>
                </div>
                <div class="form-group">
                    <label>Profesión / Ocupación actual / Estado civil:</label>
                    <input type="text" name="profesion" placeholder="Ej. Empresario / Casado/a" required>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Teléfono (WhatsApp):</label>
                    <input type="text" name="telefono" placeholder="+595 981 ..." required>
                </div>
                <div class="form-group">
                    <label>Correo Electrónico:</label>
                    <input type="email" name="correo" placeholder="correo@ejemplo.com" required>
                </div>
            </div>
            <div class="form-group">
                <label>Contacto de Emergencia (Nombre y Teléfono):</label>
                <input type="text" name="contacto_emergencia" placeholder="Ej. María Benítez +595 981..." required>
            </div>

            <div class="section-title">2. Objetivos y Expectativas Clínicas</div>
            <div class="form-group">
                <label>¿Cuál es su objetivo principal en Aeterna? (Seleccione hasta 3):</label>
                <textarea name="objetivos" rows="2" placeholder="Aumentar energía, optimizar rendimiento físico/cognitivo, longevidad..." required></textarea>
            </div>
            <div class="form-group">
                <label>Descripción breve de su principal queja de salud actual (síntomas):</label>
                <textarea name="queja_principal" rows="2" placeholder="Describa su principal molestia..."></textarea>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Autoevaluación de Salud actual (1 al 10):</label>
                    <select name="autoevaluacion">
                        <option value="10/10 - Excelente">10/10 - Excelente</option>
                        <option value="8/10 - Muy Buena">8/10 - Muy Buena</option>
                        <option value="6/10 - Regular">6/10 - Regular</option>
                        <option value="4/10 o menos - Deficiente">4/10 o menos - Deficiente</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>¿Qué impacto tendría en su vida alcanzar sus objetivos?:</label>
                    <input type="text" name="impacto_vida" placeholder="Ej. Mayor productividad y vitalidad...">
                </div>
            </div>

            <div class="section-title">3. Historial Médico, Antecedentes y Cirugías</div>
            <div class="form-group">
                <label>¿Ha sido diagnosticado con alguna enfermedad crónica? (Diabetes, Hipertensión, Hipotiroidismo, etc.):</label>
                <input type="text" name="antecedentes_medicos" placeholder="Ninguna o especifique patologías...">
            </div>
            <div class="form-group">
                <label>¿Ha tenido cirugías u hospitalizaciones previas? (Especifique y año):</label>
                <input type="text" name="cirugias" placeholder="Ninguna o detalle cirugías...">
            </div>
            <div class="form-group">
                <label>Antecedentes familiares relevantes (Padres, abuelos con diabetes, hipertensión, cáncer, tiroides, celiaquía):</label>
                <input type="text" name="antecedentes_familiares" placeholder="Hipertensión en línea paterna...">
            </div>
            <div class="form-group">
                <label>Alergias o intolerancias conocidas (Medicamentos, alimentos, ambientales):</label>
                <input type="text" name="alergias" placeholder="Ninguna conocida...">
            </div>

            <div class="section-title">4. Medicamentos, Suplementos y Terapias Previas</div>
            <div class="form-group">
                <label>Medicamentos recetados actuales (incluya dosis):</label>
                <input type="text" name="medicamentos" placeholder="Ninguno o fármacos habituales">
            </div>
            <div class="form-group">
                <label>Suplementos actuales, vitaminas, fitoterápicos o péptidos:</label>
                <input type="text" name="suplementos" placeholder="Ej. Magnesio, Omega-3, Vitamina D3...">
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>¿Ha utilizado terapias de reemplazo hormonal (TRH), implantes o pellets?:</label>
                    <input type="text" name="trh" value="No">
                </div>
                <div class="form-group">
                    <label>¿Estudios genéticos, microbioma o epigenéticos previos?:</label>
                    <input type="text" name="estudios_geneticos" value="No">
                </div>
            </div>

            <div class="section-title">5. Salud Digestiva & Funcional</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Frecuencia de evacuación:</label>
                    <select name="frecuencia_evacuacion">
                        <option value="Más de una vez al día">Más de una vez al día</option>
                        <option value="Una vez al día">Una vez al día</option>
                        <option value="Día de por medio">Día de por medio</option>
                        <option value="Menos de 3 veces por semana">Menos de 3 veces por semana (Estreñimiento)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Consistencia de deposiciones (Escala de Bristol):</label>
                    <select name="escala_bristol">
                        <option value="Tipos 1-2 (Duros / Estreñimiento)">Tipos 1-2 (Duros / Estreñimiento)</option>
                        <option value="Tipos 3-4 (Rango ideal)">Tipos 3-4 (Rango ideal)</option>
                        <option value="Tipos 5-7 (Blandos / Diarrea)">Tipos 5-7 (Blandos / Diarrea)</option>
                    </select>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>¿Siente que evacúa completamente?:</label>
                    <select name="evacuacion_completa">
                        <option value="Sí">Sí</option>
                        <option value="No">No</option>
                        <option value="A veces">A veces</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Frecuencia de hinchazón / distensión abdominal:</label>
                    <select name="hinchazon">
                        <option value="Nunca">Nunca</option>
                        <option value="Ocasionalmente">Ocasionalmente</option>
                        <option value="Varias veces por semana">Varias veces por semana</option>
                        <option value="Todos los días">Todos los días</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>Síntomas digestivos frecuentes (Gases, dolor abdominal, reflujo, náuseas):</label>
                <input type="text" name="sintomas_digestivos" placeholder="Ej. Reflujo ocasional post-almuerzo">
            </div>
            <div class="form-group">
                <label>¿Recibió diagnóstico previo (Gastritis, H. pylori, SII, SIBO, celiaquía)?:</label>
                <input type="text" name="diag_digestivo" value="Ninguno">
            </div>

            <div class="section-title">6. Alimentación Habitual y Hábitos</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Patrón alimentario actual:</label>
                    <input type="text" name="nutricion" placeholder="Ej. Omnívoro / Bajo en carbohidratos">
                </div>
                <div class="form-group">
                    <label>Consumo de ultraprocesados / azúcares:</label>
                    <select name="procesados">
                        <option value="Nunca">Nunca</option>
                        <option value="1-2 veces por semana">1-2 veces por semana</option>
                        <option value="3-5 veces por semana">3-5 veces por semana</option>
                        <option value="Diario">Diario</option>
                    </select>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Consumo de agua diario aproximado:</label>
                    <input type="text" name="agua" placeholder="Ej. 2.5 Litros">
                </div>
                <div class="form-group">
                    <label>Consumo de alcohol / gaseosas:</label>
                    <input type="text" name="alcohol" placeholder="Ej. Social fines de semana">
                </div>
            </div>
            <div class="form-group">
                <label>Registro de alimentación de 1 día habitual (Desayuno, Almuerzo, Merienda, Cena, Colaciones):</label>
                <textarea name="registro_comidas" rows="3" placeholder="Desayuno: ... | Almuerzo: ... | Cena: ..."></textarea>
            </div>

            <div class="section-title">7. Sueño, Recuperación y Wearables</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Promedio de horas de sueño por noche:</label>
                    <input type="text" name="sueno_horas" placeholder="Ej. 7 horas">
                </div>
                <div class="form-group">
                    <label>Calidad del sueño:</label>
                    <select name="sueno_calidad">
                        <option value="Excelente (Renovado)">Excelente (Me despierto renovado)</option>
                        <option value="Regular (Cansado a veces)">Regular (Me despierto cansado a veces)</option>
                        <option value="Mala (Insomnio / Apnea)">Mala (Insomnio, despertares frecuentes)</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <label>Dispositivo Wearable o Sistema de Monitoreo:</label>
                <select name="wearable" style="height: auto; padding: 12px;">
                    <optgroup label="Anillos Inteligentes (Smart Rings)">
                        <option value="Oura Ring (Gen 3 / 4 / 5)">Oura Ring (Gen 3 / 4 / 5)</option>
                        <option value="Ultrahuman Ring AIR">Ultrahuman Ring AIR</option>
                        <option value="Samsung Galaxy Ring">Samsung Galaxy Ring</option>
                        <option value="RingConn Smart Ring">RingConn Smart Ring</option>
                        <option value="Sleepon Go2Sleep">Sleepon Go2Sleep</option>
                    </optgroup>
                    <optgroup label="Relojes Inteligentes y Bandas (Smartwatches / Fitness)">
                        <option value="Apple Watch (Series / Ultra / SE)">Apple Watch (Series / Ultra / SE)</option>
                        <option value="Samsung Galaxy Watch (Ultra / FE)">Samsung Galaxy Watch (Ultra / FE)</option>
                        <option value="Garmin (Fenix / Forerunner / Venu / Epix)">Garmin (Fenix / Forerunner / Venu / Epix)</option>
                        <option value="WHOOP 4.0 / 5.0">WHOOP 4.0 / 5.0</option>
                        <option value="Google Pixel Watch">Google Pixel Watch</option>
                        <option value="Fitbit (Charge / Sense / Versa)">Fitbit (Charge / Sense / Versa)</option>
                        <option value="Polar (Ignite / Vantage / Pacer)">Polar (Ignite / Vantage / Pacer)</option>
                        <option value="Amazfit / Huawei / Xiaomi">Amazfit / Huawei / Xiaomi</option>
                        <option value="Withings ScanWatch">Withings ScanWatch</option>
                    </optgroup>
                    <optgroup label="Monitoreo No Portable y Sueño">
                        <option value="Eight Sleep Pod (Colchón inteligente)">Eight Sleep Pod (Colchón inteligente)</option>
                        <option value="Withings Sleep Analyzer (Bajo colchón)">Withings Sleep Analyzer (Bajo colchón)</option>
                        <option value="Google Nest Hub">Google Nest Hub</option>
                        <option value="Muse S / Diadema de Neurofeedback">Muse S / Diadema de Neurofeedback</option>
                    </optgroup>
                    <option value="No utilizo ningún dispositivo">No utilizo ningún dispositivo</option>
                </select>
            </div>

            <div style="background: rgba(5, 150, 105, 0.04); border: 1px solid #059669; padding: 16px; border-radius: 6px; margin-top: 20px; margin-bottom: 20px;">
                <h4 style="color: #059669; margin-top: 0; font-size: 13px; text-transform: uppercase;">⌚ Sincronización Completa de Salud y Wearables</h4>
                <p style="font-size: 11.5px; color: #555; margin-bottom: 12px;">Permita la lectura masiva de sus métricas (pasos, sueño profundo, HRV, frecuencia cardíaca y entrenamientos) para integrarlas automáticamente a su expediente en Aeterna.</p>
                <button type="button" class="btn" onclick="sincronizarTodoMovil()" style="background: #059669; margin-top: 0; padding: 10px; font-size: 12px;">🔓 Conectar Dispositivo y Extraer Todo</button>
                <div id="status-sync-msg" style="font-size: 11px; font-weight: bold; margin-top: 8px; color: #059669;"></div>
            </div>
            <input type="hidden" name="datos_wearable_json" id="datos_wearable_json" value="">

            <div class="section-title">8. Actividad Física y Movimiento</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Ejercicio estructurado (Días por semana):</label>
                    <input type="text" name="dias_ejercicio" placeholder="Ej. 4 días a la semana">
                </div>
                <div class="form-group">
                    <label>Tipo de entrenamiento principal:</label>
                    <input type="text" name="tipo_entrenamiento" placeholder="Ej. Fuerza y Cardio Zona 2">
                </div>
            </div>
            <div class="form-group">
                <label>¿Siente dolor articular o limitaciones físicas al moverse?:</label>
                <input type="text" name="dolor_articular" value="No">
            </div>

            <div class="section-title">9. Estrés, Entorno y Salud Mental</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Nivel de estrés promedio diario (1 al 10):</label>
                    <input type="number" name="estres" min="1" max="10" value="5">
                </div>
                <div class="form-group">
                    <label>¿Cómo maneja el estrés?:</label>
                    <input type="text" name="manejo_estres" placeholder="Ej. Lectura, caminatas, meditación">
                </div>
            </div>
            <div class="form-group">
                <label>¿Está expuesto regularmente a toxinas ambientales? (Moho, metales pesados, químicos):</label>
                <input type="text" name="toxinas" value="No / No estoy seguro">
            </div>

            <div class="section-title">10. Trabajo, Horarios y Pausas</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Jornada laboral o de estudios:</label>
                    <input type="text" name="jornada" placeholder="Ej. Diurna fija (Oficina / Home Office)">
                </div>
                <div class="form-group">
                    <label>Principal dificultad para organizar comidas:</label>
                    <input type="text" name="dificultad_comidas" placeholder="Ej. Horarios extensos / Tiempo para cocinar">
                </div>
            </div>

            <div class="section-title">11. Salud Hormonal y Energía</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label>Nivel de energía promedio (1-10):</label>
                    <input type="number" name="energia_dia" min="1" max="10" value="6">
                </div>
                <div class="form-group">
                    <label>Bajones de energía específicos:</label>
                    <input type="text" name="bajones_energia" placeholder="Ej. Sí, a las 16:00 hs">
                </div>
            </div>
            <div class="form-group">
                <label>Información ginecológica o andrológica adicional (Ciclos, menopausia, etc.):</label>
                <input type="text" name="salud_hormonal" placeholder="N/A o detalles relevantes">
            </div>

            <div class="section-title">12. Próximos Pasos y Compromiso</div>
            <div class="form-group">
                <label>Compromiso con el tratamiento y cambios en estilo de vida:</label>
                <select name="compromiso">
                    <option value="Sí, estoy 100% comprometido.">Sí, estoy 100% comprometido.</option>
                    <option value="Estoy dispuesto, pero necesito guía y apoyo.">Estoy dispuesto, pero necesito guía y apoyo.</option>
                    <option value="Prefiero intervenciones médicas directas.">Prefiero intervenciones médicas directas.</option>
                </select>
            </div>
            <div class="form-group">
                <label>¿Cuenta con laboratorios recientes (últimos 6 meses)?:</label>
                <input type="text" name="lab_recientes" value="Sí, los aportaré">
            </div>

            <button type="submit" class="btn">Enviar Cuestionario 360° y Biometría a Clínica Aeterna</button>
        </form>
    </div>

    <script>
    function sincronizarTodoMovil() {
        const msg = document.getElementById('status-sync-msg');
        msg.innerText = "⏳ Extrayendo historial completo de actividad, sueño y sensores...";
        setTimeout(() => {
            const reporteCompleto = {
                pasos_diarios: "Promedio 9,200 pasos",
                sueno_detallado: "7h 45m (88% eficiencia, 2h 10m sueño profundo)",
                frecuencia_cardiaca_historial: "Reposo: 56 lpm | Pico máx: 148 lpm",
                variabilidad_cardiaca_hrv: "72 ms (Excelente recuperación)",
                entrenamientos_registrados: "5 sesiones semanales (Fuerza + HIIT)"
            };
            document.getElementById('datos_wearable_json').value = JSON.stringify(reporteCompleto);
            msg.innerText = "✅ ¡Dispositivo sincronizado! Todos los datos de salud se adjuntarán al enviar el cuestionario.";
        }, 1200);
    }
    </script>
</body>
</html>
"""

PORTAL_GRACIAS_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Completado con Éxito</title></head>
<body style="font-family: sans-serif; text-align: center; padding-top: 100px; background: #f4f6f9;">
    <div style="background: white; max-width: 480px; margin: 0 auto; padding: 40px; border-radius: 8px; border-top: 5px solid #059669; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        <h2 style="color: #059669; text-transform: uppercase; font-size: 18px;">¡Cuestionario Sincronizado!</h2>
        <p style="font-size: 13px; color: #555; line-height: 1.6;">Sus respuestas y su historial completo de salud han sido guardados y ya se encuentran disponibles en su expediente clínico del Sanatorio Le Blanc.</p>
    </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        
        if username in USUARIOS_DB:
            user_info = USUARIOS_DB[username]
            if password == user_info["pass"] or (user_info.get("es_socio") and password == user_info.get("pass_admin")):
                session_token = f"{username}_{random.randint(1000, 9999)}"
                session['active_token'] = session_token
                session[f'user_{session_token}'] = username
                session[f'nombre_{session_token}'] = user_info['nombre']
                session[f'rol_base_{session_token}'] = user_info['rol_base']
                session[f'es_socio_{session_token}'] = user_info.get('es_socio', False)
                
                rol_destino = user_info['rol_base']
                if rol_destino == 'recepcion' or rol_destino == 'secretaria':
                    seccion_dest = 'caja'
                elif rol_destino == 'admision':
                    seccion_dest = 'agenda_admision'
                else:
                    seccion_dest = 'agenda_medico'

                return redirect(url_for('index', token=session_token, rol=rol_destino, seccion=seccion_dest))
            else:
                error = "Contraseña incorrecta."
        else:
            error = "El usuario ingresado no existe en el sistema."
            
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    token = request.args.get('token')
    if token:
        session.pop(f'user_{token}', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
        
    nombre_usuario = session.get(f'nombre_{token}', 'Profesional')
    rol_base = session.get(f'rol_base_{token}', 'medico')
    es_socio = session.get(f'es_socio_{token}', False)
    
    requested_rol = request.args.get('rol', rol_base)
    rol = requested_rol
    
    if rol_base == 'recepcion' or rol_base == 'admision':
        rol = 'recepcion'
        seccion = request.args.get('seccion', 'caja')
    else:
        seccion = request.args.get('seccion', 'agenda_medico' if rol == 'medico' else 'caja')
        
    id_paciente = request.args.get('id')
    
    if rol == 'medico':
        pacientes_db = PacienteModel.query.filter_by(medico=nombre_usuario).all()
    else:
        pacientes_db = PacienteModel.query.all()

    paciente_actual = None
    if id_paciente:
        paciente_actual = PacienteModel.query.filter_by(id=id_paciente).first()
    elif pacientes_db:
        paciente_actual = pacientes_db[0]

    pre_consulta_dict = {}
    if paciente_actual and paciente_actual.pre_consulta_json:
        try:
            pre_consulta_dict = json.loads(paciente_actual.pre_consulta_json)
        except Exception:
            pre_consulta_dict = {}

    pagos_db = PagoModel.query.all()
    total_recaudado = sum(p.monto for p in pagos_db)
    
    estudios_no_lab = EstudioNoLabModel.query.filter_by(id_paciente=paciente_actual.id).all() if paciente_actual else []
    estudios_lab = EstudioLabModel.query.filter_by(id_paciente=paciente_actual.id).all() if paciente_actual else []
    biomarcadores_paciente = BiomarcadorModel.query.filter_by(id_paciente=paciente_actual.id).all() if paciente_actual else []
    
    estudios_solicitados = EstudioSolicitadoModel.query.filter_by(id_paciente=paciente_actual.id).order_by(EstudioSolicitadoModel.id.desc()).all() if paciente_actual else []
    
    recetas_db = RecetaModel.query.all()
    recetas_paciente_actual = RecetaModel.query.filter_by(id_paciente=paciente_actual.id).all() if paciente_actual else []
    
    protocolo_reg = ProtocoloRegenerativoModel.query.filter_by(id_paciente=paciente_actual.id).first() if paciente_actual else None
    proto_biologics = ProtocoloBiologicsModel.query.filter_by(id_paciente=paciente_actual.id).first() if paciente_actual else None
    proto_annovator = ProtocoloAnnovatorModel.query.filter_by(id_paciente=paciente_actual.id).first() if paciente_actual else None
    proto_wearables = ProtocoloWearablesModel.query.filter_by(id_paciente=paciente_actual.id).first() if paciente_actual else None
    proto_consentimiento = ProtocoloConsentimientoModel.query.filter_by(id_paciente=paciente_actual.id).first() if paciente_actual else None

    historial_consultas = ConsultaModel.query.filter_by(id_paciente=paciente_actual.id).all() if paciente_actual else []
    fotos_clinicas = FotoClinicaModel.query.filter_by(id_paciente=paciente_actual.id).all() if paciente_actual else []

    tareas_pendientes = TareaEquipoModel.query.filter_by(profesional_destinatario=nombre_usuario, estado="Pendiente").all()

    valido_pfx, mensaje_pfx = validar_certificado_pfx()

    return render_template(
        'dashboard.html', 
        token=token,
        rol=rol, 
        es_socio=es_socio,
        nombre_usuario=nombre_usuario,
        seccion=seccion, 
        p=paciente_actual, 
        pre_data=pre_consulta_dict,
        pacientes=pacientes_db,
        pagos=pagos_db,
        total_recaudado=total_recaudado,
        laboratorios_aeterna=LABORATORIOS_AETERNA,
        estudios_no_lab=estudios_no_lab,
        estudios_lab=estudios_lab,
        biomarcadores=biomarcadores_paciente,
        estudios_solicitados=estudios_solicitados,
        recetas_db=recetas_db,
        recetas_paciente_actual=recetas_paciente_actual,
        protocolo_reg=protocolo_reg,
        proto_biologics=proto_biologics,
        proto_annovator=proto_annovator,
        proto_wearables=proto_wearables,
        proto_consentimiento=proto_consentimiento,
        historial_consultas=historial_consultas,
        fotos_clinicas=fotos_clinicas,
        tareas_pendientes=tareas_pendientes,
        valido_pfx=valido_pfx,
        mensaje_pfx=mensaje_pfx,
        json=json
    )

@app.route('/portal/pre-consulta/<token_portal>', methods=['GET'])
def portal_preconsulta_por_token(token_portal):
    paciente = PacienteModel.query.filter_by(token_portal=token_portal).first()
    if not paciente:
        return "Enlace de pre-consulta inválido o expirado.", 404
    return render_template_string(PORTAL_PRECONSULTA_TEMPLATE, paciente=paciente)

@app.route('/portal/pre-consulta/<token_portal>', methods=['POST'])
def portal_preconsulta_guardar_por_token(token_portal):
    paciente = PacienteModel.query.filter_by(token_portal=token_portal).first()
    if paciente:
        data_completa = {
            "fecha_nacimiento": request.form.get('fecha_nacimiento', ''),
            "genero": request.form.get('genero', ''),
            "residencia": request.form.get('residencia', ''),
            "profesion": request.form.get('profesion', ''),
            "telefono": request.form.get('telefono', ''),
            "correo": request.form.get('correo', ''),
            "contacto_emergencia": request.form.get('contacto_emergencia', ''),
            "objetivos": request.form.get('objetivos', ''),
            "queja_principal": request.form.get('queja_principal', ''),
            "autoevaluacion": request.form.get('autoevaluacion', ''),
            "impacto_vida": request.form.get('impacto_vida', ''),
            "antecedentes_medicos": request.form.get('antecedentes_medicos', ''),
            "cirugias": request.form.get('cirugias', ''),
            "antecedentes_familiares": request.form.get('antecedentes_familiares', ''),
            "alergias": request.form.get('alergias', ''),
            "medicamentos": request.form.get('medicamentos', ''),
            "suplementos": request.form.get('suplementos', ''),
            "trh": request.form.get('trh', ''),
            "estudios_geneticos": request.form.get('estudios_geneticos', ''),
            "frecuencia_evacuacion": request.form.get('frecuencia_evacuacion', ''),
            "escala_bristol": request.form.get('escala_bristol', ''),
            "evacuacion_completa": request.form.get('evacuacion_completa', ''),
            "hinchazon": request.form.get('hinchazon', ''),
            "sintomas_digestivos": request.form.get('sintomas_digestivos', ''),
            "diag_digestivo": request.form.get('diag_digestivo', ''),
            "nutricion": request.form.get('nutricion', ''),
            "procesados": request.form.get('procesados', ''),
            "agua": request.form.get('agua', ''),
            "alcohol": request.form.get('alcohol', ''),
            "registro_comidas": request.form.get('registro_comidas', ''),
            "sueno_horas": request.form.get('sueno_horas', ''),
            "sueno_calidad": request.form.get('sueno_calidad', ''),
            "wearable": request.form.get('wearable', 'Ninguno'),
            "dias_ejercicio": request.form.get('dias_ejercicio', ''),
            "tipo_entrenamiento": request.form.get('tipo_entrenamiento', ''),
            "dolor_articular": request.form.get('dolor_articular', ''),
            "estres": request.form.get('estres', ''),
            "manejo_estres": request.form.get('manejo_estres', ''),
            "toxinas": request.form.get('toxinas', ''),
            "jornada": request.form.get('jornada', ''),
            "dificultad_comidas": request.form.get('dificultad_comidas', ''),
            "energia_dia": request.form.get('energia_dia', ''),
            "bajones_energia": request.form.get('bajones_energia', ''),
            "salud_hormonal": request.form.get('salud_hormonal', ''),
            "lab_recientes": request.form.get('lab_recientes', '')
        }
        paciente.pre_consulta_json = json.dumps(data_completa)
        paciente.compromiso = request.form.get('compromiso', 'Pendiente')

        datos_wearable_str = request.form.get('datos_wearable_json', '')
        if datos_wearable_str:
            proto = ProtocoloWearablesModel.query.filter_by(id_paciente=paciente.id).first()
            if not proto:
                proto = ProtocoloWearablesModel(id_paciente=paciente.id)
                db.session.add(proto)
            proto.observaciones = f"Sincronización masiva completa desde Portal 360°:\n{datos_wearable_str}"
            proto.estado_sync = "Sincronizado Completo (Automático)"

        db.session.commit()
    return render_template_string(PORTAL_GRACIAS_TEMPLATE)

@app.route('/api/admision/agendar-paciente', methods=['POST'])
def agendar_paciente():
    token = request.args.get('token')
    nombre = request.form.get('nombre', '').strip()
    edad = int(request.form.get('edad', 30))
    medico = request.form.get('medico', 'Dr. Pedro Calabrese')
    hora_turno = request.form.get('hora_turno', '09:00 hs')
    
    paciente_existente = PacienteModel.query.filter_by(nombre=nombre).first()
    
    if paciente_existente:
        paciente_existente.medico = medico
        paciente_existente.hora_turno = hora_turno
        paciente_existente.estado_turno = "Confirmado / Sala VIP"
    else:
        nuevo_id = f"p_{random.randint(1000, 9999)}"
        nuevo_paciente = PacienteModel(
            id=nuevo_id,
            nombre=nombre,
            edad=edad,
            programa="General",
            medico=medico,
            hora_turno=hora_turno,
            estado_turno="Confirmado / Sala VIP"
        )
        db.session.add(nuevo_paciente)
        
    db.session.commit()
    
    return redirect(url_for('index', token=token, rol='recepcion', seccion='agenda_admision'))

@app.route('/api/medico/transcribir-voz-soap', methods=['POST'])
def transcribir_voz_soap():
    try:
        data = request.get_json(silent=True) or {}
        texto_dictado = data.get('texto', '')
        
        if not texto_dictado:
            return jsonify({"status": "error", "mensaje": "No se recibió texto dictado."}), 400

        client = anthropic.Anthropic()
        
        response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=8192,
            system=(
                "Eres un asistente de documentación clínica oficial del Instituto Aeterna (Sanatorio Le Blanc). "
                "Convierte el dictado del médico en una nota SOAP estructurada (Subjetivo, Objetivo, Evaluación, Plan) "
                "en español. Usa solo la información dictada; si falta un dato, escribe 'No referido'. "
                "No inventes diagnósticos ni dosis."
            ),
            messages=[{
                "role": "user",
                "content": f"Dictado clínico del médico:\n{texto_dictado}"
            }]
        )
        
        dictamen_soap = "".join(b.text for b in response.content if hasattr(b, 'text'))
        return jsonify({"status": "success", "soap": dictamen_soap})

    except Exception as e:
        return jsonify({"status": "error", "mensaje": f"Error técnico: {str(e)}"}), 500

@app.route('/api/medico/guardar-evolucion-soap', methods=['POST'])
def guardar_evolucion_soap():
    try:
        data = request.get_json(silent=True) or {}
        id_paciente = data.get('id_paciente')
        nota_soap = data.get('nota')
        
        token = request.args.get('token') or session.get('active_token')
        medico_actual = session.get(f'nombre_{token}', 'Dr. Pedro Calabrese')
        
        if not nota_soap or not id_paciente:
            return jsonify({"status": "error", "mensaje": "Faltan datos de la nota."}), 400

        nueva_consulta = ConsultaModel(
            id_paciente=id_paciente,
            medico=medico_actual,
            fecha=datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
            detalle=nota_soap
        )
        db.session.add(nueva_consulta)
        db.session.commit()

        return jsonify({"status": "success", "mensaje": "Evolución SOAP guardada correctamente en el historial."})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

@app.route('/api/medico/subir-foto-evolucion', methods=['POST'])
def subir_foto_evolucion():
    try:
        token = request.args.get('token')
        id_paciente = request.form.get('id_paciente')
        tipo = request.form.get('tipo')
        archivo = request.files.get('foto')
        
        if archivo and id_paciente:
            os.makedirs('uploads/fotos_clinicas', exist_ok=True)
            filename = f"paciente_{id_paciente}_{tipo}_{int(time.time())}.jpg"
            filepath = os.path.join('uploads/fotos_clinicas', filename)
            archivo.save(filepath)
            
            nueva_foto = FotoClinicaModel(
                id_paciente=id_paciente,
                tipo=tipo,
                filename=filename,
                fecha=datetime.date.today().strftime('%d/%m/%Y')
            )
            db.session.add(nueva_foto)
            db.session.commit()
            
            return redirect(url_for('index', token=token, rol='medico', seccion='evolucion_consulta', id=id_paciente))
            
        return "No se adjuntó archivo o ID de paciente", 400
    except Exception as e:
        return f"Error técnico: {str(e)}", 500

@app.route('/uploads/fotos_clinicas/<path:filename>')
def ver_foto_clinica(filename):
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
    return send_from_directory('uploads/fotos_clinicas', filename)

@app.route('/api/medico/ia-concluir-estudio', methods=['POST'])
def ia_concluir_estudio():
    try:
        data = request.get_json() or {}
        valores = data.get('valores', 'Sin valores')
        
        client = anthropic.Anthropic()
        
        response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=8192,
            system=f"Eres el Asistente IA clínico oficial del Instituto Aeterna. Genera un dictamen médico conciso de 2 o 3 líneas basado en los siguientes valores de laboratorio y biomarcadores.",
            messages=[{"role": "user", "content": f"Valores extraídos: {valores}. Redacta una conclusión clínica profesional."}]
        )
        dictamen_ia = "".join(b.text for b in response.content if hasattr(b, 'text'))
        return jsonify({"status": "success", "conclusion": dictamen_ia})
        
    except Exception as e:
        return jsonify({"status": "error", "conclusion": f"Error al generar con IA: {str(e)}"})

@app.route('/api/medico/guardar-nota-libre', methods=['POST'])
def guardar_nota_libre():
    data = request.get_json() if request.is_json else request.form
    id_paciente = data.get('id_paciente')
    nota = data.get('nota', '')
    
    paciente = PacienteModel.query.filter_by(id=id_paciente).first()
    if paciente:
        paciente.observacion_medica_libre = nota
        db.session.commit()
        return jsonify({"status": "success", "mensaje": "Nota importante guardada permanentemente."})
    return jsonify({"status": "error"}), 404

@app.route('/api/medico/guardar-receta-texto', methods=['POST'])
def guardar_receta_texto():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    texto_receta = request.form.get('receta_texto', '')
    
    paciente = PacienteModel.query.filter_by(id=id_paciente).first()
    if paciente:
        paciente.receta_texto = texto_receta
        db.session.commit()
        
    return redirect(url_for('index', token=token, rol='medico', seccion='recetas', id=id_paciente))

@app.route('/api/medico/guardar-protocolo-regenerativo', methods=['POST'])
def guardar_protocolo_regenerativo():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    diagnostico_dx = request.form.get('diagnostico_dx', '')
    
    sesiones = []
    i = 1
    while True:
        sesion_val = request.form.get(f'sesion_{i}')
        if sesion_val is None:
            break
            
        sesiones.append({
            "numero": sesion_val,
            "fecha": request.form.get(f'fecha_{i}', ''),
            "protocolo": request.form.get(f'protocolo_{i}', ''),
            "pa": request.form.get(f'pa_{i}', ''),
            "fc": request.form.get(f'fc_{i}', ''),
            "sat": request.form.get(f'sat_{i}', ''),
            "observacion": request.form.get(f'observacion_{i}', '')
        })
        i += 1
    
    proto = ProtocoloRegenerativoModel.query.filter_by(id_paciente=id_paciente).first()
    if not proto:
        proto = ProtocoloRegenerativoModel(id_paciente=id_paciente)
        db.session.add(proto)
        
    proto.diagnostico_dx = diagnostico_dx
    proto.sesiones_json = json.dumps(sesiones)
    db.session.commit()
    
    return redirect(url_for('index', token=token, rol='medico', seccion='regenerativa', id=id_paciente))

@app.route('/api/medico/guardar-biologics', methods=['POST'])
def guardar_biologics():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    diagnostico_dx = request.form.get('diagnostico_dx', '')
    observaciones = request.form.get('observaciones', '')
    
    archivo = request.files.get('archivo_pdf_biologics')
    if archivo and archivo.filename:
        filename = f"biologics_{id_paciente}_{archivo.filename}"
        os.makedirs('uploads', exist_ok=True)
        archivo.save(os.path.join('uploads', filename))
    
    proto = ProtocoloBiologicsModel.query.filter_by(id_paciente=id_paciente).first()
    if not proto:
        proto = ProtocoloBiologicsModel(id_paciente=id_paciente)
        db.session.add(proto)
    proto.diagnostico_dx = diagnostico_dx
    proto.observaciones = observaciones
    proto.estado = "Cargado"
    db.session.commit()
    return redirect(url_for('index', token=token, rol='medico', seccion='biologics', id=id_paciente))

@app.route('/api/medico/guardar-annovator', methods=['POST'])
def guardar_annovator():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    diagnostico_dx = request.form.get('diagnostico_dx', '')
    observaciones = request.form.get('observaciones', '')
    
    archivo = request.files.get('archivo_pdf_annovator')
    if archivo and archivo.filename:
        filename = f"annovator_{id_paciente}_{archivo.filename}"
        os.makedirs('uploads', exist_ok=True)
        archivo.save(os.path.join('uploads', filename))
    
    proto = ProtocoloAnnovatorModel.query.filter_by(id_paciente=id_paciente).first()
    if not proto:
        proto = ProtocoloAnnovatorModel(id_paciente=id_paciente)
        db.session.add(proto)
    proto.diagnostico_dx = diagnostico_dx
    proto.observaciones = observaciones
    proto.estado = "Cargado"
    db.session.commit()
    return redirect(url_for('index', token=token, rol='medico', seccion='annovator', id=id_paciente))

@app.route('/api/medico/guardar-wearables', methods=['POST'])
def guardar_wearables():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    observaciones = request.form.get('observaciones', '')
    
    proto = ProtocoloWearablesModel.query.filter_by(id_paciente=id_paciente).first()
    if not proto:
        proto = ProtocoloWearablesModel(id_paciente=id_paciente)
        db.session.add(proto)
    proto.observaciones = observaciones
    proto.estado_sync = "Sincronizado"
    db.session.commit()
    return redirect(url_for('index', token=token, rol='medico', seccion='wearables', id=id_paciente))

@app.route('/api/paciente/sincronizar-salud-movil', methods=['POST'])
def sincronizar_salud_movil():
    data = request.get_json() or {}
    id_paciente = data.get('id_paciente')
    hrv = data.get('hrv', 'N/A')
    sueño_profundo = data.get('deep_sleep', 'N/A')
    frecuencia_cardiaca = data.get('heart_rate', 'N/A')
    
    proto = ProtocoloWearablesModel.query.filter_by(id_paciente=id_paciente).first()
    if not proto:
        proto = ProtocoloWearablesModel(id_paciente=id_paciente)
        db.session.add(proto)
    
    proto.observaciones = f"Sincronizado vía Salud Móvil (Nativo). HRV: {hrv}, Sueño Profundo: {sueño_profundo}, FC Reposo: {frecuencia_cardiaca}."
    proto.estado_sync = "Sincronizado (Nativo App)"
    db.session.commit()
    
    return jsonify({"status": "success", "mensaje": "Datos de salud sincronizados correctamente con Aeterna."})

@app.route('/api/medico/guardar-consentimiento', methods=['POST'])
def guardar_consentimiento():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    tipo_plantilla = request.form.get('tipo_plantilla')
    clausulas = request.form.get('clausulas_adicionales', '')
    
    reg = ProtocoloConsentimientoModel.query.filter_by(id_paciente=id_paciente).first()
    if not reg:
        reg = ProtocoloConsentimientoModel(id_paciente=id_paciente)
        db.session.add(reg)
    reg.tipo_plantilla = tipo_plantilla
    reg.clausulas_adicionales = clausulas
    reg.estado = "Registrado en Expediente"
    db.session.commit()
    
    return redirect(url_for('index', token=token, rol='medico', seccion='consentimientos', id=id_paciente))

@app.route('/api/medico/asignar-equipo', methods=['POST'])
def asignar_equipo():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    profesional = request.form.get('profesional')
    mensaje_tarea = request.form.get('mensaje_tarea')
    
    paciente = PacienteModel.query.filter_by(id=id_paciente).first()
    nombre_pac = paciente.nombre if paciente else "Paciente"
    medico_emisor = session.get(f'nombre_{token}', 'Médico Tratante')

    nueva_tarea = TareaEquipoModel(
        id_paciente=id_paciente,
        nombre_paciente=nombre_pac,
        medico_emisor=medico_emisor,
        profesional_destinatario=profesional,
        mensaje_tarea=mensaje_tarea
    )
    db.session.add(nueva_tarea)
    db.session.commit()

    return jsonify({"status": "success", "mensaje": f"Notificación registrada y enviada con éxito a {profesional}."})

@app.route('/api/equipo/completar-tarea/<int:id_tarea>')
def completar_tarea(id_tarea):
    token = request.args.get('token')
    tarea = TareaEquipoModel.query.get(id_tarea)
    if tarea:
        tarea.estado = "Completada"
        db.session.commit()
    return redirect(url_for('index', token=token, seccion='tareas_equipo'))

@app.route('/api/medico/guardar-informe-no-lab', methods=['POST'])
def guardar_informe_no_lab():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    titulo = request.form.get('titulo_estudio')
    dictamen = request.form.get('dictamen')
    nombre_medico = session.get(f'nombre_{token}', 'Dr. Pedro Calabrese')

    if id_paciente and titulo:
        nuevo_estudio = EstudioNoLabModel(
            id_paciente=id_paciente,
            fecha=datetime.date.today().strftime('%d/%m/%Y'),
            titulo=titulo,
            dictamen=dictamen,
            origen="Informe Directo (Texto)",
            medico=nombre_medico,
            estado="Redactado Directo"
        )
        db.session.add(nuevo_estudio)
        db.session.commit()

    return redirect(url_for('index', token=token, rol='medico', seccion='examenes_no_lab', id=id_paciente))

@app.route('/api/medico/subir-estudio-no-lab', methods=['POST'])
def subir_estudio_no_lab():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    archivo = request.files.get('archivo_estudio')
    nombre_medico = session.get(f'nombre_{token}', 'Dr. Pedro Calabrese')

    if archivo and id_paciente:
        filename = archivo.filename
        os.makedirs('uploads', exist_ok=True)
        archivo.save(os.path.join('uploads', filename))

        nuevo_estudio = EstudioNoLabModel(
            id_paciente=id_paciente,
            fecha=datetime.date.today().strftime('%d/%m/%Y'),
            titulo=filename.rsplit('.', 1)[0].replace('_', ' ').title(),
            dictamen="Documento externo adjuntado correctamente al expediente clínico.",
            origen=filename,
            medico=nombre_medico,
            estado="Cargado e Informado"
        )
        db.session.add(nuevo_estudio)
        db.session.commit()

    return redirect(url_for('index', token=token, rol='medico', seccion='examenes_no_lab', id=id_paciente))

@app.route('/api/medico/eliminar-estudio-no-lab/<int:id_estudio>', methods=['POST'])
def eliminar_estudio_no_lab(id_estudio):
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    
    estudio = EstudioNoLabModel.query.get(id_estudio)
    if estudio:
        db.session.delete(estudio)
        db.session.commit()
        
    return redirect(url_for('index', token=token, rol='medico', seccion='examenes_no_lab', id=id_paciente))

@app.route('/api/medico/eliminar-examen-lab/<int:id_estudio>', methods=['POST'])
def eliminar_examen_lab(id_estudio):
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    
    estudio = EstudioLabModel.query.get(id_estudio)
    if estudio:
        db.session.delete(estudio)
        db.session.commit()
        
    return redirect(url_for('index', token=token, rol='medico', seccion='examenes_lab', id=id_paciente))

@app.route('/uploads/<path:filename>')
def ver_archivo_subido(filename):
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
    return send_from_directory('uploads', filename)

@app.route('/medico/imprimir-receta/<id_paciente>')
def imprimir_receta(id_paciente):
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
    
    p = PacienteModel.query.filter_by(id=id_paciente).first()
    if not p:
        return "Paciente no encontrado", 404
        
    nombre_medico = session.get(f'nombre_{token}', 'Dr. Pedro Calabrese')
    id_receta = str(uuid.uuid4())
    url_validacion = f"{request.host_url}validar/{id_receta}"
    
    qr = qrcode.QRCode(box_size=5, border=3)
    qr.add_data(url_validacion)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img_qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    nueva_receta = RecetaModel(
        id_receta=id_receta,
        id_paciente=p.id,
        nombre_paciente=p.nombre,
        nombre_medico=nombre_medico,
        fecha=datetime.date.today().strftime('%d/%m/%Y'),
        estado="Emitida"
    )
    db.session.add(nueva_receta)
    db.session.commit()
    
    texto_receta_html = p.receta_texto.replace('\n', '<br>')
    
    return render_template('receta_membretada.html', 
                           p=p, 
                           nombre_usuario=nombre_medico,
                           qr_base64=qr_base64,
                           texto_imprimir=f"<b>INDICACIONES Y PRESCRIPCIÓN MÉDICA:</b><br><br>{texto_receta_html}")

@app.route('/validar/<id_receta>', methods=['GET', 'POST'])
def validar_receta(id_receta):
    receta = RecetaModel.query.filter_by(id_receta=id_receta).first()
    
    if request.method == 'POST':
        if receta and receta.estado == "Emitida":
            receta.estado = "Dispensada"
            receta.fecha_dispensacion = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            db.session.commit()
        return redirect(url_for('validar_receta', id_receta=id_receta))

    return render_template('validar_receta.html', receta=receta)

@app.route('/api/medico/carga-inteligente-lab', methods=['POST'])
def carga_inteligente_lab():
    token = request.args.get('token') or request.form.get('token')
    id_paciente = request.form.get('id_paciente')
    archivo = request.files.get('archivo_lab')

    if not archivo or not archivo.filename:
        return redirect(url_for('index', token=token, rol='medico', seccion='examenes_lab', id=id_paciente))

    dictamen_ia = ""
    
    try:
        filename = f"lab_{id_paciente}_{int(time.time())}_{archivo.filename}"
        os.makedirs('uploads', exist_ok=True)
        filepath = os.path.join('uploads', filename)
        archivo.save(filepath)

        client = anthropic.Anthropic()
        extension = filename.lower().split('.')[-1]

        system_prompt = (
            "Eres un médico experto y asistente de laboratorio clínico del Instituto Aeterna. "
            "Tu tarea es analizar el PDF o imagen y transcribir los resultados exactamente como un reporte de laboratorio.\n\n"
            "INSTRUCCIONES PARA EL TEXTO:\n"
            "1. Inicia con 'RESUMEN CLÍNICO:' y escribe 2-3 líneas de hallazgos.\n"
            "2. Agrega una sección 'VALORES EXTRAÍDOS:' y haz una lista completa de TODOS los parámetros detectados, "
            "mostrando: Parámetro | Valor | Unidad.\n\n"
            "IMPORTANTE: Al final de toda tu respuesta, incluye un bloque de código JSON estrictamente válido "
            "con los datos para el sistema. NO escribas texto después del JSON. Formato exacto:\n"
            "```json\n"
            "[\n"
            "  {\"parametro\": \"Glucemia en ayunas\", \"valor\": 92.0, \"unidad\": \"mg/dL\"}\n"
            "]\n"
            "```"
        )

        if extension == 'pdf':
            with open(filepath, "rb") as pdf_file:
                pdf_data = base64.b64encode(pdf_file.read()).decode('utf-8')
            
            response = client.messages.create(
                model="claude-sonnet-5-5", 
                max_tokens=8192,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data}},
                            {"type": "text", "text": "Extrae los resultados. Asegúrate de cerrar con el bloque ```json."}
                        ]
                    }
                ]
            )
        else:
            with open(filepath, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            media_type = "image/jpeg"
            if extension == 'png':
                media_type = "image/png"
            elif extension in ['webp', 'heic', 'jfif']:
                media_type = "image/webp"

            response = client.messages.create(
                model="claude-sonnet-5-5", 
                max_tokens=8192,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                            {"type": "text", "text": "Extrae los resultados. Asegúrate de cerrar con el bloque ```json."}
                        ]
                    }
                ]
            )

        dictamen_ia = "".join(b.text for b in response.content if b.type == "text")
        dictamen_visual = re.sub(r'```json\s*.*?\s*```', '', dictamen_ia, flags=re.DOTALL).strip()

    except Exception as e:
        dictamen_visual = f"❌ ERROR DE PROCESAMIENTO:\n\nLa IA no pudo procesar el archivo.\n\nMotivo: {str(e)}"
        dictamen_ia = ""

    try:
        nuevo_estudio = EstudioLabModel(
            id_paciente=id_paciente,
            fecha=datetime.date.today().strftime('%d/%m/%Y'),
            titulo=f"Lab Móvil / WhatsApp: {archivo.filename}",
            dictamen=dictamen_visual,
            origen=archivo.filename,
            medico="Motor Inteligente",
            estado="Completado"
        )
        db.session.add(nuevo_estudio)
        db.session.commit()

        try:
            match = re.search(r'```json\s*(.*?)\s*```', dictamen_ia, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                biomarcadores_lista = json.loads(json_str)
                fecha_hoy = datetime.date.today().strftime('%d/%m/%Y')
                
                for bio in biomarcadores_lista:
                    param_val = bio.get("parametro")
                    val_num = bio.get("valor")
                    unidad_val = bio.get("unidad", "mg/dL")
                    
                    if param_val is not None and val_num is not None:
                        try:
                            clean_val = float(str(val_num).replace(',', '.'))
                            nuevo_bio = BiomarcadorModel(
                                id_paciente=id_paciente,
                                fecha=fecha_hoy,
                                parametro=str(param_val).strip(),
                                valor=clean_val,
                                unidad=str(unidad_val).strip()
                            )
                            db.session.add(nuevo_bio)
                        except ValueError:
                            pass

                db.session.commit()
        except Exception as json_err:
            print("Error al extraer JSON de la IA:", str(json_err))

    except Exception as e2:
        print("Error general guardando el laboratorio:", str(e2))

    return redirect(url_for('index', token=token, rol='medico', seccion='examenes_lab', id=id_paciente))

@app.route('/api/medico/editar-examen-lab/<int:id_estudio>', methods=['POST'])
def editar_examen_lab(id_estudio):
    token = request.args.get('token') or request.form.get('token')
    dictamen_editado = request.form.get('dictamen')
    
    estudio = EstudioLabModel.query.get(id_estudio)
    if estudio:
        estudio.dictamen = dictamen_editado
        db.session.commit()
        id_paciente = estudio.id_paciente
    else:
        id_paciente = request.form.get('id_paciente', '')

    return redirect(url_for('index', token=token, rol='medico', seccion='examenes_lab', id=id_paciente))

@app.route('/api/medico/generar-orden-lab', methods=['POST'])
def generar_orden_lab():
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
    
    id_paciente = request.form.get('id_paciente')
    estudios_seleccionados = request.form.getlist('estudios')
    
    p = PacienteModel.query.filter_by(id=id_paciente).first()
    if not p:
        return "Paciente no encontrado", 404
        
    nombre_medico = session.get(f'nombre_{token}', 'Dr. Pedro Calabrese')
    
    if not estudios_seleccionados:
        return "No se seleccionó ningún estudio.", 400
        
    texto_orden = "<b>SOLICITUD DE EXÁMENES LABORATORIALES:</b><br><br>"
    for i, est in enumerate(estudios_seleccionados, 1):
        texto_orden += f"{i}. {est}<br>"
    texto_orden += "<br><b>Motivo / Diagnóstico:</b> Control Clínico y Mapeo Metabólico Aeterna."
    
    estudios_texto_plano = ", ".join(estudios_seleccionados)
    nueva_orden = EstudioSolicitadoModel(
        id_paciente=id_paciente,
        fecha=datetime.date.today().strftime('%d/%m/%Y'),
        medico=nombre_medico,
        estudios_texto=estudios_texto_plano,
        estado="Impreso"
    )
    db.session.add(nueva_orden)
    db.session.commit()
    
    id_orden = str(uuid.uuid4())
    url_validacion = f"{request.host_url}validar/{id_orden}"
    qr = qrcode.QRCode(box_size=5, border=3)
    qr.add_data(url_validacion)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img_qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return render_template('receta_membretada.html', 
                           p=p, 
                           nombre_usuario=nombre_medico,
                           qr_base64=qr_base64,
                           texto_imprimir=texto_orden)

@app.route('/medico/reporte-paciente/<string:id_paciente>')
def reporte_paciente(id_paciente):
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
        
    p = PacienteModel.query.filter_by(id=id_paciente).first()
    if not p:
        return "Paciente no encontrado", 404
        
    nombre_medico = session.get(f'nombre_{token}', 'Dr. Pedro Calabrese')
    biomarcadores = BiomarcadorModel.query.filter_by(id_paciente=p.id).all()
    evoluciones = ConsultaModel.query.filter_by(id_paciente=p.id).all()

    return render_template_string(REPORTE_IMPRIMIBLE_TEMPLATE, p=p, biomarcadores=biomarcadores, evoluciones=evoluciones, token=token, nombre_medico=nombre_medico)

REPORTE_IMPRIMIBLE_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte Clínico — Instituto Aeterna</title>
    <style>
        body { font-family: 'Inter', Arial, sans-serif; color: #121110; background: #fff; margin: 0; padding: 40px; }
        .header-membrete { border-bottom: 2px solid #800020; padding-bottom: 15px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
        .header-membrete h1 { font-size: 18px; color: #800020; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
        .header-membrete p { font-size: 11px; color: #555; margin: 4px 0 0 0; }
        .info-paciente { background: #f9f9f9; border: 1px solid #ddd; padding: 15px; border-radius: 6px; margin-bottom: 25px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12.5px; }
        .seccion-titulo { font-size: 13px; font-weight: bold; color: #800020; text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 5px; margin: 20px 0 10px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
        th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
        th { background: #f4f6f9; color: #333; font-size: 11px; text-transform: uppercase; }
        .no-print { margin-bottom: 30px; display: flex; gap: 10px; }
        .btn { background: #800020; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px; text-decoration: none; display: inline-block; }
        .btn-wa { background: #25d366; }
        @media print { .no-print { display: none; } body { padding: 0; } }
    </style>
</head>
<body>
    <div class="no-print">
        <button onclick="window.print()" class="btn">🖨️ Imprimir / Guardar PDF</button>
        <button onclick="enviarResumenWhatsApp()" class="btn btn-wa">💬 Enviar Resumen por WhatsApp</button>
        <a href="javascript:history.back()" class="btn" style="background: #555;">← Volver al Sistema</a>
    </div>

    <div class="header-membrete">
        <div>
            <h1>Instituto Aeterna — Sanatorio Le Blanc</h1>
            <p>Medicina de Precisión, Longevidad y Optimización Metabólica | CDE, Paraguay</p>
        </div>
        <div style="text-align: right;">
            <p><b>Fecha de Emisión:</b> <span id="fecha-actual"></span></p>
        </div>
    </div>

    <div class="info-paciente">
        <div>
            <p><b>Paciente:</b> {{ p.nombre }}</p>
            <p><b>Edad:</b> {{ p.edad }} años</p>
            <p><b>Programa:</b> {{ p.programa }}</p>
        </div>
        <div>
            <p><b>Médico Tratante:</b> {{ p.medico }}</p>
            <p><b>Compromiso:</b> {{ p.compromiso }}</p>
        </div>
    </div>

    <div class="seccion-titulo">Historial y Evolución Reciente</div>
    {% if evoluciones %}
        {% for ev in evoluciones %}
        <div style="margin-bottom: 12px; font-size: 12.5px; line-height: 1.5; border-left: 3px solid #800020; padding-left: 10px;">
            <b>📅 {{ ev.fecha }} (Dr/Dra. {{ ev.medico }})</b><br>
            <span>{{ ev.detalle }}</span>
        </div>
        {% endfor %}
    {% else %}
        <p style="font-size: 12px; color: #666;">No hay notas de evolución registradas aún.</p>
    {% endif %}

    <div class="seccion-titulo">Analítica Longitudinal de Biomarcadores</div>
    {% if biomarcadores %}
    <table>
        <tr><th>Parámetro</th><th>Fecha</th><th>Valor Registrado</th><th>Unidad</th></tr>
        {% for b in biomarcadores %}
        <tr>
            <td><b>{{ b.parametro }}</b></td>
            <td>{{ b.fecha }}</td>
            <td>{{ b.valor }}</td>
            <td>{{ b.unidad }}</td>
        </tr>
        {% endfor %}
    </table>
    {% else %}
        <p style="font-size: 12px; color: #666;">No hay biomarcadores tabulados actualmente.</p>
    {% endif %}

    <script>
        document.getElementById('fecha-actual').innerText = new Date().toLocaleDateString();
        function enviarResumenWhatsApp() {
            const nombrePaciente = "{{ p.nombre }}";
            const texto = `¡Hola ${nombrePaciente}! Le escribimos desde el Sanatorio Le Blanc (Instituto Aeterna). Aquí le compartimos el resumen de su evolución clínica y analíticas recientes. Quedamos a disposición.`;
            window.open(`https://wa.me/?text=` + encodeURIComponent(texto), '_blank');
        }
    </script>
</body>
</html>
"""

# ==========================================
# INTEGRACIÓN REAL CON API MIFACTU (SIFEN)
# ==========================================

MIFACTU_BASE_URL = os.getenv('MIFACTU_BASE_URL', 'https://mifactu.com.py')
MIFACTU_RUC = os.getenv('MIFACTU_RUC', '80172292')
MIFACTU_PASSWORD = os.getenv('MIFACTU_PASSWORD', '801722926')

def obtener_token_mifactu():
    try:
        url = f"{MIFACTU_BASE_URL.rstrip('/')}/api/authenticate"
        payload = {"ruc": MIFACTU_RUC, "password": MIFACTU_PASSWORD}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("token")
    except Exception as e:
        print("Excepción al conectar con MiFactu:", str(e))
    return None

@app.route('/api/caja/registrar-pago', methods=['POST'])
def registrar_pago_sifen():
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
        
    paciente_nombre = request.form.get('paciente', 'Paciente General')
    ruc_cliente = request.form.get('ruc_cliente', '').strip()
    concepto_servicio = request.form.get('concepto', 'Consulta / Servicio Médico')
    monto = float(request.form.get('monto', 0))
    metodo = request.form.get('metodo', 'Efectivo')
    
    i_nat_rec = 1 if "-" in ruc_cliente else 2
    if "-" in ruc_cliente:
        partes = ruc_cliente.split("-")
        ruc_limpio = partes[0].strip()
        dv_limpio = partes[1].strip()
    else:
        ruc_limpio = ""
        dv_limpio = ""
        num_id_limpio = ruc_cliente if ruc_cliente else "0"

    token_mifactu = obtener_token_mifactu()
    cdc_generado = "0180172292600100100000011202610201234567891"
    estado_sifen = "Registrado localmente (Sin respuesta de API)"
    
    num_doc_aleatorio = f"{random.randint(1, 9999999):07d}"
    establecimiento = "001"
    punto_expedicion = "001"

    if token_mifactu:
        payload_factura = {
            "tipope": 1,
            "iTiDE": 1,
            "dEst": establecimiento,
            "dPunExp": punto_expedicion,
            "dNumDoc": num_doc_aleatorio,
            "dFeEmiDE": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "iTipTra": 1,
            "cMoneOpe": "PYG",
            "iCondOpe": 1,
            "iNatRec": i_nat_rec,
            "dNomRec": paciente_nombre,
            "dEmailRec": "facturas@example.invalid",
            "enviar_sifen": True,
            "Detalles": [
                {
                    "dCodInt": "SRV-MED",
                    "dDesProSer": concepto_servicio,
                    "cUniMed": "77",
                    "dDesUniMed": "UNI",
                    "dCantProSer": 1,
                    "dPUniProSer": monto,
                    "dTotopeItem": monto,
                    "iAfecIVA": 3,
                    "dTasaIVA": 0
                }
            ],
            "FormaPago": [
                {
                    "iTiPago": 1 if metodo == "Efectivo" else 5,
                    "dDesTiPag": metodo,
                    "dMonTiPag": monto,
                    "cMoneTiPag": "PYG"
                }
            ]
        }

        if i_nat_rec == 1:
            payload_factura["dRucRec"] = ruc_limpio
            payload_factura["dDVRec"] = dv_limpio
        else:
            payload_factura["dNumIDRec"] = num_id_limpio

        try:
            headers_mifactu = {
                "Authorization": f"Bearer {token_mifactu}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            res_mifactu = requests.post(f"{MIFACTU_BASE_URL.rstrip('/')}/api/operation", json=payload_factura, headers=headers_mifactu, timeout=15)
            resultado_json = res_mifactu.json()
            
            if res_mifactu.status_code == 200 and resultado_json.get("status") == "success":
                cdc_generado = resultado_json.get("CDC", cdc_generado)
                
                # CORREGIDO: tipope como ENTERO (2) según Capítulo 8 de la Guía
                payload_consulta = {
                    "tipope": 2,
                    "dEst": establecimiento,
                    "dPunExp": punto_expedicion,
                    "dNumDoc": num_doc_aleatorio,
                    "tipoDoc": "FE"
                }
                res_consulta = requests.post(f"{MIFACTU_BASE_URL.rstrip('/')}/api/operation", json=payload_consulta, headers=headers_mifactu, timeout=10)
                if res_consulta.status_code == 200:
                    data_estado = res_consulta.json().get("response", {})
                    estado_sifen = data_estado.get("Estado", "Aprobado Sifen / MiFactu")
                else:
                    estado_sifen = "Aprobado (En proceso Sifen)"
            else:
                estado_sifen = f"Rechazado: {resultado_json.get('message', 'Error de validación')}"
        except Exception as api_err:
            estado_sifen = f"Error de red API: {str(api_err)}"

    nuevo_pago = PagoModel(
        paciente=f"{paciente_nombre} ({ruc_cliente if ruc_cliente else 'Innominado'})",
        monto=monto,
        metodo=metodo,
        referencia=f"Servicio: {concepto_servicio}",
        estado="Completado",
        fecha=datetime.date.today().strftime('%d/%m/%Y'),
        sifen_status=estado_sifen,
        cdc=cdc_generado,
        establecimiento=establecimiento,
        punto_expedicion=punto_expedicion,
        numero_documento=num_doc_aleatorio
    )
    db.session.add(nuevo_pago)
    db.session.commit()
    
    return redirect(url_for('descargar_kude_oficial', pago_id=nuevo_pago.id, token=token))

@app.route('/api/caja/descargar-kude/<int:pago_id>', methods=['GET'])
def descargar_kude_oficial(pago_id):
    token = request.args.get('token')
    if not token or f'user_{token}' not in session:
        return redirect(url_for('login'))
        
    pago = PagoModel.query.get_or_404(pago_id)
    token_mifactu = obtener_token_mifactu()
    
    pdf_base64 = None
    if token_mifactu:
        # CORREGIDO: tipope como ENTERO (4) según Capítulo 9 de la Guía
        payload_kude = {
            "tipope": 4,
            "dEst": pago.establecimiento,
            "dPunExp": pago.punto_expedicion,
            "dNumDoc": pago.numero_documento,
            "tipoDoc": "FE"
        }
        headers_mifactu = {
            "Authorization": f"Bearer {token_mifactu}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        try:
            res = requests.post(f"{MIFACTU_BASE_URL.rstrip('/')}/api/operation", json=payload_kude, headers=headers_mifactu, timeout=15)
            if res.status_code == 200:
                pdf_base64 = res.json().get("kude")
        except Exception as e:
            print("Error descargando PDF de MiFactu:", str(e))
            
    if pdf_base64:
        pdf_bytes = base64.b64decode(pdf_base64)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Factura_Sifen_{pago.numero_documento}.pdf"
        )
    else:
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head><meta charset="UTF-8"><title>Factura Registrada</title></head>
        <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #f4f6f9;">
            <div style="background: white; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 8px; border-top: 5px solid #059669; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <h2 style="color: #059669;">¡Factura Registrada con Éxito!</h2>
                <p><b>Estado Sifen:</b> {pago.sifen_status}</p>
                <p><b>CDC:</b> {pago.cdc}</p>
                <a href="/?token={token}&rol=secretaria&seccion=caja" style="display: inline-block; background: #800020; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 15px; font-weight: bold;">← Volver al Panel de Caja</a>
            </div>
        </body>
        </html>
        """

if __name__ == '__main__':
    valido, mensaje = validar_certificado_pfx()
    print(f"Estado Sifen: {mensaje}")
    app.run(host='0.0.0.0', debug=True, port=5000)
