#!/usr/bin/env python3
"""
Full Generator for all 10 SGR Mockups in HTML and high-resolution PNG rendering.
Replicates the visual structure and operational dynamics of the Excel system:
- Delegación Las Compañías, La Serena
- Tubo de Trabajo (agenda colectiva)
- Semáforo y Metas Trimestrales con ponderaciones
- Vistas de funcionario y bandejas de validación
"""

import os
import subprocess

BASE_DIR = os.path.abspath("/Users/danielflores/Desktop/Proyecto Integrado/Mockups_SGR")
HTML_DIR = os.path.join(BASE_DIR, "html")
PNG_DIR = os.path.join(BASE_DIR, "png")
EDGE_BIN = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"

os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(PNG_DIR, exist_ok=True)

SHARED_HEAD = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - SGR Municipalidad de La Serena</title>
  <style>
    :root {{
      --primary: #7A1C28; /* Granate La Serena */
      --primary-dark: #58121B;
      --primary-light: #9B2C3B;
      --secondary: #1E293B;
      --accent: #2563EB;
      --bg-main: #F1F5F9;
      --bg-card: #FFFFFF;
      --text-dark: #0F172A;
      --text-muted: #64748B;
      --border: #CBD5E1;
      --border-light: #E2E8F0;
      
      --excel-green-bg: #DCFCE7;
      --excel-green-text: #166534;
      --excel-green-border: #86EFAC;
      
      --excel-yellow-bg: #FEF9C3;
      --excel-yellow-text: #854D0E;
      --excel-yellow-border: #FDE047;
      
      --excel-red-bg: #FEE2E2;
      --excel-red-text: #991B1B;
      --excel-red-border: #FCA5A5;
      
      --excel-blue-bg: #DBEAFE;
      --excel-blue-text: #1E40AF;
      --excel-blue-border: #93C5FD;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    body {{
      background-color: var(--bg-main);
      color: var(--text-dark);
      font-size: 12px;
      line-height: 1.4;
      -webkit-font-smoothing: antialiased;
    }}

    /* Municipal Top Bar */
    .top-nav {{
      background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
      color: white;
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }}

    .top-nav .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .shield-badge {{
      width: 36px;
      height: 36px;
      background: white;
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: var(--primary);
      font-weight: 900;
      font-size: 11px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      border: 1px solid #E2E8F0;
      line-height: 1;
    }}

    .shield-badge span:first-child {{
      font-size: 14px;
    }}

    .top-nav .titles h1 {{
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}

    .top-nav .titles p {{
      font-size: 11px;
      color: #F1F5F9;
      opacity: 0.9;
    }}

    .top-nav .nav-tabs {{
      display: flex;
      gap: 5px;
    }}

    .top-nav .nav-tab {{
      padding: 6px 12px;
      border-radius: 4px;
      color: #F8FAFC;
      text-decoration: none;
      font-weight: 600;
      font-size: 11px;
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.1);
    }}

    .top-nav .nav-tab.active {{
      background: white;
      color: var(--primary);
      border-color: white;
    }}

    .top-nav .user-info {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .user-text {{
      text-align: right;
    }}

    .user-text .u-name {{
      font-size: 12px;
      font-weight: 700;
    }}

    .user-text .u-role {{
      font-size: 10px;
      color: #E2E8F0;
    }}

    .u-avatar {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #FFFFFF;
      color: var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 12px;
      border: 2px solid #F1F5F9;
    }}

    /* Sub-header Breadcrumb & Actions Bar */
    .sub-bar {{
      background: white;
      border-bottom: 1px solid var(--border-light);
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .breadcrumb {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--text-muted);
    }}

    .breadcrumb strong {{
      color: var(--text-dark);
    }}

    .badge-period {{
      background: #EFF6FF;
      color: #1D4ED8;
      border: 1px solid #BFDBFE;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
    }}

    /* Main Container */
    .container {{
      padding: 16px 24px;
      max-width: 1560px;
      margin: 0 auto;
    }}

    /* Cards */
    .card {{
      background: var(--bg-card);
      border-radius: 8px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      margin-bottom: 16px;
      overflow: hidden;
    }}

    .card-header {{
      padding: 10px 16px;
      background: #F8FAFC;
      border-bottom: 1px solid var(--border-light);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .card-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--secondary);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .card-body {{
      padding: 14px 16px;
    }}

    /* Tables styled like Excel */
    .table-container {{
      overflow-x: auto;
      border-radius: 4px;
      border: 1px solid var(--border);
    }}

    table.excel-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 11.5px;
      background: white;
    }}

    table.excel-table th {{
      background: #F1F5F9;
      color: #334155;
      font-weight: 700;
      padding: 8px 10px;
      border: 1px solid #CBD5E1;
      text-transform: uppercase;
      font-size: 10.5px;
      letter-spacing: 0.3px;
      white-space: nowrap;
    }}

    table.excel-table th.th-primary {{
      background: #FDF2F4;
      color: var(--primary);
      border-color: #F87171;
    }}

    table.excel-table td {{
      padding: 7px 10px;
      border: 1px solid #E2E8F0;
      color: #1E293B;
      vertical-align: middle;
    }}

    table.excel-table tr:hover td {{
      background-color: #F8FAFC !important;
    }}

    /* Excel row colors */
    .row-done td {{
      background-color: #F0FDF4;
    }}

    .row-process td {{
      background-color: #FFFBEB;
    }}

    .row-pending td {{
      background-color: #FEF2F2;
    }}

    .strike {{
      text-decoration: line-through;
      color: #64748B;
    }}

    /* Badges */
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.2px;
      white-space: nowrap;
    }}

    .badge-pending {{
      background: var(--excel-red-bg);
      color: var(--excel-red-text);
      border: 1px solid var(--excel-red-border);
    }}

    .badge-process {{
      background: var(--excel-yellow-bg);
      color: var(--excel-yellow-text);
      border: 1px solid var(--excel-yellow-border);
    }}

    .badge-done {{
      background: var(--excel-green-bg);
      color: var(--excel-green-text);
      border: 1px solid var(--excel-green-border);
    }}

    .badge-blue {{
      background: var(--excel-blue-bg);
      color: var(--excel-blue-text);
      border: 1px solid var(--excel-blue-border);
    }}

    .badge-gray {{
      background: #F1F5F9;
      color: #475569;
      border: 1px solid #CBD5E1;
    }}

    .badge-purple {{
      background: #F3E8FF;
      color: #6B21A8;
      border: 1px solid #D8B4FE;
    }}

    /* Buttons */
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      text-decoration: none;
    }}

    .btn-primary {{
      background: var(--primary);
      color: white;
    }}

    .btn-secondary {{
      background: white;
      color: #334155;
      border-color: #CBD5E1;
    }}

    .btn-success {{
      background: #059669;
      color: white;
    }}

    .btn-danger {{
      background: #DC2626;
      color: white;
    }}

    .btn-sm {{
      padding: 3px 8px;
      font-size: 10.5px;
    }}

    /* KPIs */
    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}

    .kpi-card {{
      background: white;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px 14px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}

    .kpi-title {{
      font-size: 10.5px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}

    .kpi-value {{
      font-size: 22px;
      font-weight: 800;
      color: var(--secondary);
      margin-top: 3px;
    }}

    .kpi-sub {{
      font-size: 10.5px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    /* Semáforo circle indicator */
    .semaforo-dot {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      display: inline-block;
      vertical-align: middle;
      border: 2px solid rgba(0,0,0,0.15);
    }}
    .dot-green {{ background: #10B981; box-shadow: 0 0 6px #10B981; }}
    .dot-yellow {{ background: #F59E0B; box-shadow: 0 0 6px #F59E0B; }}
    .dot-red {{ background: #EF4444; box-shadow: 0 0 6px #EF4444; }}

    /* Filters bar */
    .filters-bar {{
      display: flex;
      align-items: center;
      gap: 10px;
      background: white;
      padding: 10px 14px;
      border-radius: 6px;
      border: 1px solid var(--border);
      margin-bottom: 14px;
      flex-wrap: wrap;
    }}

    .form-group {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .form-group label {{
      font-size: 11px;
      font-weight: 700;
      color: #475569;
    }}

    .form-control {{
      padding: 5px 8px;
      border-radius: 4px;
      border: 1px solid var(--border);
      font-size: 11.5px;
      background: white;
    }}

    /* Mockup stamp watermark */
    .mockup-stamp {{
      position: fixed;
      bottom: 12px;
      right: 18px;
      background: rgba(15, 23, 42, 0.85);
      color: white;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      z-index: 9999;
      pointer-events: none;
      border: 1px solid rgba(255,255,255,0.2);
    }}
  </style>
</head>
<body>
"""

FOOTER = """
</body>
</html>
"""

def generate_m01():
    """M-01: Login y Selección de Delegación / Rol"""
    content = f"""
{SHARED_HEAD.format(title="M-01: Acceso al Sistema")}
<div class="mockup-stamp">SGR MOCKUP M-01 | PORTAL DE ACCESO Y AUTENTICACIÓN</div>

<div style="min-height: 100vh; display: flex; flex-direction: column; background: linear-gradient(135deg, #2C3E50 0%, #1A2530 100%);">
  <div style="padding: 20px 40px; display: flex; align-items: center; gap: 14px;">
    <div class="shield-badge" style="width: 44px; height: 44px;">
      <span>🏛️</span>
      <span style="font-size: 9px; font-weight: 900;">SERENA</span>
    </div>
    <div style="color: white;">
      <h2 style="font-size: 16px; font-weight: 800; letter-spacing: 0.5px;">ILUSTRE MUNICIPALIDAD DE LA SERENA</h2>
      <p style="font-size: 12px; color: #CBD5E1;">Sistema de Gestión de Resultados (SGR) - Delegaciones Territoriales</p>
    </div>
  </div>

  <div style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 20px;">
    <div style="background: white; width: 440px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); overflow: hidden; border: 1px solid #E2E8F0;">
      
      <div style="background: linear-gradient(135deg, #7A1C28 0%, #58121B 100%); color: white; padding: 24px; text-align: center;">
        <div style="display: inline-flex; width: 48px; height: 48px; background: rgba(255,255,255,0.15); border-radius: 50%; align-items: center; justify-content: center; font-size: 22px; margin-bottom: 8px;">
          🔐
        </div>
        <h3 style="font-size: 18px; font-weight: 800;">Iniciar Sesión</h3>
        <p style="font-size: 12px; color: #FEE2E2; margin-top: 4px;">Ingrese sus credenciales municipales autorizadas</p>
      </div>

      <div style="padding: 24px;">
        <div style="margin-bottom: 16px;">
          <label style="display: block; font-size: 11.5px; font-weight: 700; color: #334155; margin-bottom: 6px;">Delegación Municipal Asignada</label>
          <select class="form-control" style="width: 100%; padding: 8px 10px; font-weight: 600; border-color: #94A3B8;">
            <option selected>Delegación Municipal Las Compañías (Jurisdicción Principal)</option>
            <option>Delegación Municipal La Antena / San Joaquín</option>
            <option>Delegación Municipal Rural (Lambert / Ceres)</option>
            <option>Delegación Municipal La Pampa</option>
            <option>Edificio Consistorial Central</option>
          </select>
        </div>

        <div style="margin-bottom: 16px;">
          <label style="display: block; font-size: 11.5px; font-weight: 700; color: #334155; margin-bottom: 6px;">RUT o Correo Institucional</label>
          <input type="text" class="form-control" value="16.892.441-3" style="width: 100%; padding: 8px 10px;" placeholder="ej. 12.345.678-9">
        </div>

        <div style="margin-bottom: 16px;">
          <label style="display: block; font-size: 11.5px; font-weight: 700; color: #334155; margin-bottom: 6px;">Contraseña de Seguridad</label>
          <input type="password" class="form-control" value="••••••••••••" style="width: 100%; padding: 8px 10px;">
        </div>

        <div style="margin-bottom: 18px;">
          <label style="display: block; font-size: 11.5px; font-weight: 700; color: #334155; margin-bottom: 6px;">Perfil de Operación / Rol</label>
          <select class="form-control" style="width: 100%; padding: 8px 10px; font-weight: 600;">
            <option selected>Funcionario Operativo (Gestor Social / Territorial)</option>
            <option>Supervisor / Jefe de Delegación (Validador)</option>
            <option>Coordinador DISERCO / Operaciones</option>
            <option>Administrador del Sistema (TI Municipal)</option>
          </select>
        </div>

        <button class="btn btn-primary" style="width: 100%; padding: 10px; justify-content: center; font-size: 13px; font-weight: 700; background: #7A1C28;">
          INGRESAR AL SISTEMA SGR ➔
        </button>

        <div style="margin-top: 16px; padding: 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0; text-align: center;">
          <span style="font-size: 10.5px; color: #64748B;">
            🛡️ Conexión segura TLS 1.3 | Registro de acceso auditado según Ley N° 19.628 de Protección de Datos.
          </span>
        </div>
      </div>
    </div>
  </div>

  <div style="text-align: center; padding: 14px; color: #94A3B8; font-size: 11px;">
    Ilustre Municipalidad de La Serena © 2026 - Sistema de Gestión de Resultados v2.4 - Delegación Las Compañías
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m02():
    """M-02: Vista Funcionario - Mi Desempeño y Registro Territorial (Idéntico a Vista funcionario Gestor Social.png)"""
    content = f"""
{SHARED_HEAD.format(title="M-02: Mi Desempeño y Registro Territorial")}
<div class="mockup-stamp">SGR MOCKUP M-02 | VISTA FUNCIONARIO - BITÁCORA Y METAS (EXCEL REPLICA)</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>

  <div class="nav-tabs">
    <a href="#" class="nav-tab active">Mi Desempeño</a>
    <a href="#" class="nav-tab">Tubo de Trabajo</a>
    <a href="#" class="nav-tab">Semáforo General</a>
    <a href="#" class="nav-tab">Reportes</a>
  </div>

  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Carlos Gómez V.</div>
      <div class="u-role">Gestor Social | Territorio Latorre</div>
    </div>
    <div class="u-avatar">CG</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Funcionarios</span> &gt; <strong>Mi Registro Operativo y Metas</strong>
  </div>
  <div style="display: flex; gap: 8px; align-items: center;">
    <span class="badge-period">📅 Período Trimestre III (Julio - Septiembre 2026)</span>
    <button class="btn btn-primary btn-sm">+ Registrar Nueva Gestión</button>
  </div>
</div>

<div class="container">
  <!-- Top KPI Cards -->
  <div class="kpi-row">
    <div class="kpi-card" style="border-left: 4px solid #10B981;">
      <div class="kpi-title">Cumplimiento Ponderado</div>
      <div class="kpi-value" style="color: #065F46;">58.42%</div>
      <div class="kpi-sub"><span class="semaforo-dot dot-green"></span> <strong>AL DÍA</strong> (Meta esperada: 56.04%)</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #2563EB;">
      <div class="kpi-title">Días Hábiles del Trimestre</div>
      <div class="kpi-value">38 / 65</div>
      <div class="kpi-sub">58.46% de tiempo transcurrido</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #F59E0B;">
      <div class="kpi-title">Casos Operativos Atendidos</div>
      <div class="kpi-value">72</div>
      <div class="kpi-sub">56 concluidos | 16 en seguimiento</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #7A1C28;">
      <div class="kpi-title">Derivados a Tubo Colectivo</div>
      <div class="kpi-value">14</div>
      <div class="kpi-sub">Coordinados con DISERCO / OO.CC</div>
    </div>
  </div>

  <!-- TABLA 1: CUADRO DE METAS Y PONDERACIÓN TRIMESTRAL (EXACTA AL EXCEL) -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📊</span> METAS TRIMESTRALES INDIVIDUALES Y FACTOR DE PONDERACIÓN (CÁLCULO AUTOMÁTICO)
      </div>
      <span class="badge badge-done">Estado Funcionario: CUMPLIENDO REQUERIMIENTOS</span>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 50px; text-align: center;">N°</th>
              <th>LÍNEA ESTRATÉGICA / INDICADOR</th>
              <th style="text-align: center;">% PONDERACIÓN</th>
              <th style="text-align: center;">META CANTIDAD</th>
              <th style="text-align: center;">REALIZADO AL DÍA</th>
              <th style="text-align: center;">% CUMPLIMIENTO</th>
              <th style="text-align: center;">BONIFICACIÓN (+)</th>
              <th style="text-align: center;">PENALIZACIÓN (-)</th>
              <th style="text-align: center; background: #FEF3C7; color: #92400E;">AVANCE PONDERADO NETO</th>
              <th style="text-align: center;">ESTADO</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="text-align: center; font-weight: 700;">1</td>
              <td><strong>Atención y Fichaje Social en Terreno (Sector Latorre)</strong></td>
              <td style="text-align: center; font-weight: 700;">35%</td>
              <td style="text-align: center;">45 visitas</td>
              <td style="text-align: center; font-weight: 700;">28</td>
              <td style="text-align: center; font-weight: 700; color: #166534;">62.22%</td>
              <td style="text-align: center; color: #166534;">+2.00%</td>
              <td style="text-align: center; color: #991B1B;">0.00%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">23.77%</td>
              <td style="text-align: center;"><span class="badge badge-done">Meta Cumplida</span></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">2</td>
              <td><strong>Gestión y Entrega de Ayudas Sociales de Emergencia</strong></td>
              <td style="text-align: center; font-weight: 700;">25%</td>
              <td style="text-align: center;">30 casos</td>
              <td style="text-align: center; font-weight: 700;">18</td>
              <td style="text-align: center; font-weight: 700; color: #166534;">60.00%</td>
              <td style="text-align: center; color: #166534;">0.00%</td>
              <td style="text-align: center; color: #991B1B;">0.00%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">15.00%</td>
              <td style="text-align: center;"><span class="badge badge-done">Meta Cumplida</span></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">3</td>
              <td><strong>Derivación y Cierre en Tubo Colectivo (Agenda Multi-Área)</strong></td>
              <td style="text-align: center; font-weight: 700;">20%</td>
              <td style="text-align: center;">20 derivaciones</td>
              <td style="text-align: center; font-weight: 700;">11</td>
              <td style="text-align: center; font-weight: 700; color: #854D0E;">55.00%</td>
              <td style="text-align: center; color: #166534;">0.00%</td>
              <td style="text-align: center; color: #991B1B;">-0.50%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">10.50%</td>
              <td style="text-align: center;"><span class="badge badge-process">En Tolerancia</span></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">4</td>
              <td><strong>Validación de Evidencias Fotográficas con Georreferencia</strong></td>
              <td style="text-align: center; font-weight: 700;">20%</td>
              <td style="text-align: center;">95 evidencias</td>
              <td style="text-align: center; font-weight: 700;">44</td>
              <td style="text-align: center; font-weight: 700; color: #854D0E;">46.31%</td>
              <td style="text-align: center; color: #166534;">0.00%</td>
              <td style="text-align: center; color: #991B1B;">0.00%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">9.26%</td>
              <td style="text-align: center;"><span class="badge badge-process">Seguimiento</span></td>
            </tr>
            <tr style="background: #F8FAFC; font-weight: 800; border-top: 2px solid #CBD5E1;">
              <td colspan="2" style="text-align: right; text-transform: uppercase;">TOTALES PONDERADOS DE GESTIÓN:</td>
              <td style="text-align: center;">100%</td>
              <td style="text-align: center;">190 un.</td>
              <td style="text-align: center;">101 un.</td>
              <td style="text-align: center; font-size: 13px; color: #1E40AF;">55.88%</td>
              <td style="text-align: center; color: #166534;">+2.00%</td>
              <td style="text-align: center; color: #991B1B;">-0.50%</td>
              <td style="text-align: center; font-size: 14px; background: #FEF08A; color: #854D0E;">58.42%</td>
              <td style="text-align: center;"><span class="badge badge-done" style="background:#10B981; color:white;">SEMÁFORO VERDE</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- TABLA 2: BITÁCORA DE GESTIÓN TERRITORIAL Y REGISTRO OPERATIVO -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📝</span> BITÁCORA DE REGISTRO OPERATIVO EN TERRENO (SECTOR LATORRE / LAS COMPAÑÍAS)
      </div>
      <div style="display: flex; gap: 8px;">
        <input type="text" class="form-control" placeholder="🔍 Buscar por código, vecino o calle..." style="width: 260px;">
        <button class="btn btn-secondary btn-sm">Filtrar Estado</button>
        <button class="btn btn-primary btn-sm">+ Nuevo Folio</button>
      </div>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 40px; text-align: center;">N°</th>
              <th style="width: 80px;">FECHA</th>
              <th style="width: 85px;">CÓDIGO CASO</th>
              <th>VECINO / ORGANIZACIÓN</th>
              <th style="width: 100px;">TERRITORIO</th>
              <th>1RA GESTIÓN (RECEPCIÓN / VISITA)</th>
              <th>2DA GESTIÓN (INFORME SOCIAL)</th>
              <th>3RA GESTIÓN (ENTREGA / CIERRE)</th>
              <th style="text-align: center; width: 120px;">EVIDENCIA FOTO</th>
              <th style="text-align: center; width: 90px;">TUBO COLECTIVO</th>
              <th style="text-align: center; width: 100px;">ESTADO</th>
            </tr>
          </thead>
          <tbody>
            <tr class="row-done">
              <td style="text-align: center; font-weight: 700;">1</td>
              <td>24-09-2026</td>
              <td><strong style="color: #7A1C28;">SOC-711</strong></td>
              <td><strong>María Rojas Pastén</strong> (Pasaje Las Violetas #412)</td>
              <td>Latorre</td>
              <td class="strike">Visita domiciliaria aplicada</td>
              <td class="strike">Ficha RSH calificada tramo 40%</td>
              <td class="strike">Entrega canasta alimentos emergencia</td>
              <td style="text-align: center;"><span class="badge badge-done">📷 2 FOTOS (OK)</span></td>
              <td style="text-align: center;"><span class="badge badge-gray">NO</span></td>
              <td style="text-align: center;"><span class="badge badge-done">REALIZADO</span></td>
            </tr>
            <tr class="row-process">
              <td style="text-align: center; font-weight: 700;">2</td>
              <td>25-09-2026</td>
              <td><strong style="color: #7A1C28;">SOC-712</strong></td>
              <td><strong>Comité Allegados Nueva Esperanza</strong> (Sede Social)</td>
              <td>Latorre</td>
              <td>Reunión directiva diagnóstica</td>
              <td>Catastro de 18 familias derivado a Vivienda</td>
              <td style="color: #94A3B8;"><em>Pendiente respuesta Serviu</em></td>
              <td style="text-align: center;"><span class="badge badge-process">📷 1 FOTO (PEND)</span></td>
              <td style="text-align: center;"><span class="badge badge-purple">SÍ (TB-184)</span></td>
              <td style="text-align: center;"><span class="badge badge-process">EN PROCESO</span></td>
            </tr>
            <tr class="row-pending">
              <td style="text-align: center; font-weight: 700;">3</td>
              <td>26-09-2026</td>
              <td><strong style="color: #7A1C28;">SOC-713</strong></td>
              <td><strong>Juan Barraza Cortés</strong> (Av. Islón #890)</td>
              <td>Latorre</td>
              <td>Recepción requerimiento salud postrado</td>
              <td style="color: #94A3B8;"><em>En coordinación con CESFAM</em></td>
              <td style="color: #94A3B8;"><em>Sin iniciar</em></td>
              <td style="text-align: center;"><span class="badge badge-pending">⚠️ SIN FOTO</span></td>
              <td style="text-align: center;"><span class="badge badge-gray">NO</span></td>
              <td style="text-align: center;"><span class="badge badge-pending">PENDIENTE</span></td>
            </tr>
            <tr class="row-done">
              <td style="text-align: center; font-weight: 700;">4</td>
              <td>22-09-2026</td>
              <td><strong style="color: #7A1C28;">SOC-708</strong></td>
              <td><strong>Patricia Aguilera M.</strong> (Calle México #125)</td>
              <td>Latorre</td>
              <td class="strike">Inspección techumbre por filtración</td>
              <td class="strike">Informe social emitido de urgencia</td>
              <td class="strike">Entrega planchas de zinc y nylon</td>
              <td style="text-align: center;"><span class="badge badge-done">📷 3 FOTOS (OK)</span></td>
              <td style="text-align: center;"><span class="badge badge-gray">NO</span></td>
              <td style="text-align: center;"><span class="badge badge-done">REALIZADO</span></td>
            </tr>
            <tr class="row-process">
              <td style="text-align: center; font-weight: 700;">5</td>
              <td>26-09-2026</td>
              <td><strong style="color: #7A1C28;">SOC-714</strong></td>
              <td><strong>JJ.VV Villa El Romero</strong> (Plaza Central)</td>
              <td>Latorre</td>
              <td>Levantamiento necesidad operativo social</td>
              <td>Coordinación con Registro Social y OMIL</td>
              <td style="color: #94A3B8;"><em>Fecha fijada: 05 de Octubre</em></td>
              <td style="text-align: center;"><span class="badge badge-done">📷 2 FOTOS (OK)</span></td>
              <td style="text-align: center;"><span class="badge badge-purple">SÍ (TB-189)</span></td>
              <td style="text-align: center;"><span class="badge badge-process">EN PROCESO</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m03():
    """M-03: Modal / Carga y Validación de Evidencias Fotográficas con Hash y GPS"""
    content = f"""
{SHARED_HEAD.format(title="M-03: Carga de Evidencias Fotográficas")}
<div class="mockup-stamp">SGR MOCKUP M-03 | VALIDACIÓN DE EVIDENCIAS Y TRAZABILIDAD SHA-256</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>
  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Carlos Gómez V.</div>
      <div class="u-role">Gestor Social</div>
    </div>
    <div class="u-avatar">CG</div>
  </div>
</nav>

<div class="container" style="max-width: 1000px; margin-top: 10px;">
  <div class="card" style="box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 2px solid #CBD5E1;">
    <div class="card-header" style="background: #F8FAFC; border-bottom: 2px solid #E2E8F0;">
      <div class="card-title">
        <span>📸</span> <strong>ADJUNTAR Y VALIDAR EVIDENCIA FOTOGRÁFICA - CASO #SOC-711</strong>
      </div>
      <span class="badge badge-purple">Vinculado a Meta: Asistencia Social Directa</span>
    </div>
    <div class="card-body">
      
      <!-- Info Header -->
      <div style="background: #F1F5F9; padding: 12px; border-radius: 6px; margin-bottom: 16px; display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; font-size: 11.5px;">
        <div><strong>Beneficiario:</strong> Sra. María Rojas Pastén (Pasaje Las Violetas #412, Latorre)</div>
        <div><strong>Gestión:</strong> Entrega canasta alimentos emergencia</div>
        <div><strong>Fecha Terreno:</strong> 24-09-2026 11:30 hrs</div>
      </div>

      <!-- Drag & Drop Zone -->
      <div style="border: 2px dashed #94A3B8; border-radius: 8px; padding: 24px; text-align: center; background: #F8FAFC; margin-bottom: 18px; cursor: pointer;">
        <div style="font-size: 32px; margin-bottom: 6px;">📤</div>
        <div style="font-size: 13px; font-weight: 700; color: #1E293B;">Arrastre fotografías de terreno o haga clic para examinar</div>
        <div style="font-size: 11px; color: #64748B; margin-top: 4px;">
          Formatos válidos: JPG, PNG | Resolución mínima: 1280x720px | Detección automática de metadatos EXIF y GPS
        </div>
      </div>

      <!-- Evidencias Cargadas con Hash SHA-256 -->
      <h4 style="font-size: 12px; font-weight: 700; color: #334155; margin-bottom: 8px; text-transform: uppercase;">
        Evidencias Digitalizadas y Verificadas (2 Archivos)
      </h4>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px;">
        <!-- Card Foto 1 -->
        <div style="border: 1px solid #CBD5E1; border-radius: 6px; overflow: hidden; background: white;">
          <div style="height: 180px; background: linear-gradient(135deg, #CBD5E1, #94A3B8); display: flex; align-items: center; justify-content: center; position: relative;">
            <span style="font-size: 48px;">🏡</span>
            <div style="position: absolute; bottom: 8px; left: 8px; background: rgba(0,0,0,0.7); color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px;">
              FOTO 1: Visita e Inspección en Terreno
            </div>
            <div style="position: absolute; top: 8px; right: 8px; background: #10B981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 700;">
              ✓ GPS VÁLIDO
            </div>
          </div>
          <div style="padding: 10px; font-size: 11px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong>Archivo:</strong> <code>visita_terreno_soc711.jpg</code>
            </div>
            <div style="margin-bottom: 4px; color: #475569;">
              <strong>GPS:</strong> -29.8912, -71.2534 (Sector Latorre, Las Compañías)
            </div>
            <div style="margin-bottom: 4px; color: #475569;">
              <strong>Timestamp:</strong> 24-09-2026 11:34:12 hrs
            </div>
            <div style="background: #F1F5F9; padding: 4px 6px; border-radius: 4px; font-family: monospace; font-size: 9.5px; color: #334155; word-break: break-all;">
              SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
            </div>
          </div>
        </div>

        <!-- Card Foto 2 -->
        <div style="border: 1px solid #CBD5E1; border-radius: 6px; overflow: hidden; background: white;">
          <div style="height: 180px; background: linear-gradient(135deg, #E2E8F0, #CBD5E1); display: flex; align-items: center; justify-content: center; position: relative;">
            <span style="font-size: 48px;">📦</span>
            <div style="position: absolute; bottom: 8px; left: 8px; background: rgba(0,0,0,0.7); color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px;">
              FOTO 2: Acta y Entrega de Beneficio
            </div>
            <div style="position: absolute; top: 8px; right: 8px; background: #10B981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 700;">
              ✓ GPS VÁLIDO
            </div>
          </div>
          <div style="padding: 10px; font-size: 11px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong>Archivo:</strong> <code>acta_recepcion_soc711.jpg</code>
            </div>
            <div style="margin-bottom: 4px; color: #475569;">
              <strong>GPS:</strong> -29.8914, -71.2530 (Sector Latorre, Las Compañías)
            </div>
            <div style="margin-bottom: 4px; color: #475569;">
              <strong>Timestamp:</strong> 24-09-2026 12:15:05 hrs
            </div>
            <div style="background: #F1F5F9; padding: 4px 6px; border-radius: 4px; font-family: monospace; font-size: 9.5px; color: #334155; word-break: break-all;">
              SHA-256: 7c3d19f8e5b42a1068c2d901e45f91823bb01248a87c91d1e40562810a91fbc8
            </div>
          </div>
        </div>
      </div>

      <!-- Verification Checklist -->
      <div style="background: #F0FDF4; border: 1px solid #BBF7D0; padding: 12px; border-radius: 6px; margin-bottom: 18px;">
        <h5 style="color: #166534; font-size: 11.5px; font-weight: 700; margin-bottom: 6px;">
          ✓ Validación Automática de Criterios de Acreditación (CU-03 / HU-08)
        </h5>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px; color: #166534;">
          <div>✔ Geolocalización confirmada dentro de la jurisdicción territorial</div>
          <div>✔ Archivos fotográficos sin manipulación (Hash íntegro)</div>
          <div>✔ Fecha y hora congruentes con la bitácora de terreno</div>
          <div>✔ Aprobación requerida por Supervisor Territorial</div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        <button class="btn btn-secondary">Cancelar</button>
        <button class="btn btn-success" style="padding: 8px 18px; font-size: 12px; font-weight: 700;">
          💾 Confirmar Evidencias y Enviar a Bandeja de Validación
        </button>
      </div>

    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m04():
    """M-04: Tubo de Trabajo - Agenda Colectiva (Idéntico a Tubo de trabajo (agenda colectiva).png)"""
    content = f"""
{SHARED_HEAD.format(title="M-04: Tubo de Trabajo (Agenda Colectiva)")}
<div class="mockup-stamp">SGR MOCKUP M-04 | TUBO DE TRABAJO - AGENDA COLECTIVA MULTI-ÁREA</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>

  <div class="nav-tabs">
    <a href="#" class="nav-tab">Mi Desempeño</a>
    <a href="#" class="nav-tab active">Tubo de Trabajo (Agenda Colectiva)</a>
    <a href="#" class="nav-tab">Semáforo General</a>
    <a href="#" class="nav-tab">Reportes</a>
  </div>

  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Coordinación Delegacional</div>
      <div class="u-role">Vista Integral Multi-Área</div>
    </div>
    <div class="u-avatar">DL</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Compromisos Colectivos</span> &gt; <strong>Tubo de Trabajo Delegación Las Compañías</strong>
  </div>
  <div style="display: flex; gap: 8px; align-items: center;">
    <button class="btn btn-secondary btn-sm">📥 Exportar a Excel</button>
    <button class="btn btn-primary btn-sm">+ Nuevo Compromiso en Tubo</button>
  </div>
</div>

<div class="container">
  <!-- Status Counter Bar (Mirroring Excel) -->
  <div class="kpi-row">
    <div class="kpi-card" style="border-left: 4px solid #2563EB;">
      <div class="kpi-title">Total Solicitudes en Tubo</div>
      <div class="kpi-value">48</div>
      <div class="kpi-sub">Compromisos transversales</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #10B981;">
      <div class="kpi-title">Realizados / Cumplidos</div>
      <div class="kpi-value" style="color: #065F46;">29</div>
      <div class="kpi-sub">60.4% de tasa de resolución</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #F59E0B;">
      <div class="kpi-title">En Proceso / Cuadrilla</div>
      <div class="kpi-value" style="color: #854D0E;">12</div>
      <div class="kpi-sub">Con gestiones activas</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #EF4444;">
      <div class="kpi-title">Pendientes / Alerta</div>
      <div class="kpi-value" style="color: #991B1B;">7</div>
      <div class="kpi-sub">Requiere asignación inmediata</div>
    </div>
  </div>

  <!-- Filters Bar -->
  <div class="filters-bar">
    <div class="form-group">
      <label>Territorio:</label>
      <select class="form-control">
        <option selected>Todos los Territorios</option>
        <option>Territorio 1: Latorre</option>
        <option>Territorio 2: El Toqui</option>
        <option>Territorio 3: Vicente Zorrilla</option>
        <option>Territorio 4: Pinamar / Viña del Mar</option>
        <option>Territorio 5: Lambert / Rural</option>
      </select>
    </div>
    <div class="form-group">
      <label>Área Responsable:</label>
      <select class="form-control">
        <option selected>Todas las Áreas</option>
        <option>DISERCO / Operaciones</option>
        <option>Social / Familias</option>
        <option>Territorial OO.CC</option>
        <option>Seguridad Ciudadana</option>
      </select>
    </div>
    <div class="form-group">
      <label>Estado:</label>
      <select class="form-control">
        <option selected>Todos los Estados</option>
        <option>Pendiente (Rojo)</option>
        <option>En Proceso (Amarillo)</option>
        <option>Realizado (Verde con tachado)</option>
      </select>
    </div>
    <div class="form-group" style="flex: 1;">
      <input type="text" class="form-control" placeholder="🔍 Buscar por N° folio, requirente, calle o palabra clave..." style="width: 100%;">
    </div>
  </div>

  <!-- Main Excel Collective Table -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📋</span> PLANILLA COLECTIVA DE GESTIÓN Y RESOLUCIÓN TERRITORIAL (AGENDA COMPARTIDA)
      </div>
      <div style="font-size: 11px; color: #64748B;">
        Actualizado en tiempo real por los 12 gestores municipales
      </div>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 50px; text-align: center;">FOLIO</th>
              <th style="width: 80px;">FECHA</th>
              <th>SOLICITUD / PROBLEMA VECINAL</th>
              <th style="width: 75px; text-align: center;">ORIGEN</th>
              <th>SOLICITANTE / JJ.VV</th>
              <th style="width: 110px;">TERRITORIO</th>
              <th>ÁREA / RESPONSABLE</th>
              <th style="width: 90px; text-align: center;">PLAZO</th>
              <th>ÚLTIMA GESTIÓN REGISTRADA</th>
              <th style="width: 100px; text-align: center;">ESTADO</th>
              <th style="width: 70px; text-align: center;">DETALLE</th>
            </tr>
          </thead>
          <tbody>
            <!-- Row 1: Realizado con tachado exacto como Excel -->
            <tr class="row-done">
              <td style="text-align: center; font-weight: 700;">101</td>
              <td>12-09-2026</td>
              <td class="strike">Retiro de microbasural y escombros en bandejón central</td>
              <td style="text-align: center;"><span class="badge badge-gray">EXTERNO</span></td>
              <td class="strike">JJ.VV Villa El Romero</td>
              <td>Latorre</td>
              <td>DISERCO (M. Bravo)</td>
              <td style="text-align: center;">18-09-2026</td>
              <td class="strike">Operativo de tolva y cuadrilla ejecutado con éxito</td>
              <td style="text-align: center;"><span class="badge badge-done">REALIZADO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver</button></td>
            </tr>

            <!-- Row 2: En Proceso -->
            <tr class="row-process">
              <td style="text-align: center; font-weight: 700;">102</td>
              <td>15-09-2026</td>
              <td><strong>Bacheo y reparación de calzada en acceso principal</strong></td>
              <td style="text-align: center;"><span class="badge badge-gray">INTERNO</span></td>
              <td>Línea 21 Colectivos / Vecinos</td>
              <td>El Toqui</td>
              <td>Territorial OO.CC (R. Tapia)</td>
              <td style="text-align: center; font-weight: 700; color: #854D0E;">30-09-2026</td>
              <td>Mezcla asfáltica en frío solicitada a taller central</td>
              <td style="text-align: center;"><span class="badge badge-process">EN PROCESO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver</button></td>
            </tr>

            <!-- Row 3: Pendiente -->
            <tr class="row-pending">
              <td style="text-align: center; font-weight: 700;">103</td>
              <td>22-09-2026</td>
              <td><strong>Postación de alumbrado público con riesgo de caída</strong></td>
              <td style="text-align: center;"><span class="badge badge-gray">EXTERNO</span></td>
              <td>Vecino Don Mario Araya</td>
              <td>Vicente Zorrilla</td>
              <td>Seguridad / DISERCO</td>
              <td style="text-align: center; font-weight: 700; color: #991B1B;">27-09-2026</td>
              <td>Oficio derivado a empresa CGE pendiente respuesta</td>
              <td style="text-align: center;"><span class="badge badge-pending">PENDIENTE</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver</button></td>
            </tr>

            <!-- Row 4: Realizado con tachado -->
            <tr class="row-done">
              <td style="text-align: center; font-weight: 700;">104</td>
              <td>16-09-2026</td>
              <td class="strike">Instalación de reductores de velocidad (lomos de toro)</td>
              <td style="text-align: center;"><span class="badge badge-gray">EXTERNO</span></td>
              <td class="strike">Club Deportivo Unión Compañías</td>
              <td>Pinamar</td>
              <td>Tránsito / Territorial OO.CC</td>
              <td style="text-align: center;">25-09-2026</td>
              <td class="strike">Señalética y demarcación vial pintada</td>
              <td style="text-align: center;"><span class="badge badge-done">REALIZADO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver</button></td>
            </tr>

            <!-- Row 5: En Proceso -->
            <tr class="row-process">
              <td style="text-align: center; font-weight: 700;">105</td>
              <td>24-09-2026</td>
              <td><strong>Operativo integral de salud canina y desparasitación</strong></td>
              <td style="text-align: center;"><span class="badge badge-gray">INTERNO</span></td>
              <td>Agrupación Animalista Huellitas</td>
              <td>Latorre</td>
              <td>Medio Ambiente / Social</td>
              <td style="text-align: center; font-weight: 700;">04-10-2026</td>
              <td>Clínica veterinaria móvil agendada para 120 cupos</td>
              <td style="text-align: center;"><span class="badge badge-process">EN PROCESO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver</button></td>
            </tr>

            <!-- Row 6: Pendiente Crítico -->
            <tr class="row-pending">
              <td style="text-align: center; font-weight: 700;">106</td>
              <td>25-09-2026</td>
              <td><strong>Filtración severa en matriz de agua potable vecinal</strong></td>
              <td style="text-align: center;"><span class="badge badge-gray">EXTERNO</span></td>
              <td>Comité de APR Rural</td>
              <td>Lambert</td>
              <td>DISERCO / Emergencias</td>
              <td style="text-align: center; font-weight: 700; color: #991B1B;">28-09-2026</td>
              <td>Coordinando camión aljibe de apoyo provisional</td>
              <td style="text-align: center;"><span class="badge badge-pending">PENDIENTE</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver</button></td>
            </tr>

            <!-- Row 7: Realizado -->
            <tr class="row-done">
              <td style="text-align: center; font-weight: 700;">107</td>
              <td>18-09-2026</td>
              <td class="strike">Poda preventiva de árboles de gran envergadura</td>
              <td style="text-align: center;"><span class="badge badge-gray">INTERNO</span></td>
              <td class="strike">JJ.VV Los Copihues</td>
              <td>El Toqui</td>
              <td>DISERCO Parques y Jardines</td>
              <td style="text-align: center;">23-09-2026</td>
              <td class="strike">Poda y despeje de cables finalizada</td>
              <td style="text-align: center;"><span class="badge badge-done">REALIZADO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m05():
    """M-05: Detalle de Compromiso Colectivo y Chat de Coordinación Interdepartamental"""
    content = f"""
{SHARED_HEAD.format(title="M-05: Detalle de Compromiso y Coordinación")}
<div class="mockup-stamp">SGR MOCKUP M-05 | FICHA DETALLE DE COMPROMISO Y CHAT MULTI-ÁREA</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>
  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Marcelo Bravo</div>
      <div class="u-role">Coordinador DISERCO</div>
    </div>
    <div class="u-avatar">MB</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Tubo de Trabajo</span> &gt; <strong>Folio #102: Reparación de Calzada El Toqui</strong>
  </div>
  <div style="display: flex; gap: 8px;">
    <span class="badge badge-process" style="padding: 6px 12px; font-size: 11px;">ESTADO: EN PROCESO DE CUADRILLA</span>
    <button class="btn btn-success btn-sm">✓ Marcar como Realizado</button>
  </div>
</div>

<div class="container" style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px;">
  <!-- Left Side: Detail & Timeline -->
  <div>
    <!-- Detail Card -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>📋</span> DATOS GENERALES DEL COMPROMISO EN TUBO
        </div>
        <span class="badge badge-purple">Origen: Vecinal Directo</span>
      </div>
      <div class="card-body">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px;">
          <div>
            <div style="color: #64748B; font-weight: 700; font-size: 10.5px; text-transform: uppercase;">Requerimiento / Asunto</div>
            <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin-top: 2px;">
              Bacheo y reparación de calzada en acceso principal
            </div>
          </div>
          <div>
            <div style="color: #64748B; font-weight: 700; font-size: 10.5px; text-transform: uppercase;">Territorio y Ubicación</div>
            <div style="font-size: 13px; font-weight: 600; margin-top: 2px;">
              Sector El Toqui (Calle Lautaro esquina Colo Colo)
            </div>
          </div>
          <div>
            <div style="color: #64748B; font-weight: 700; font-size: 10.5px; text-transform: uppercase;">Solicitante</div>
            <div style="margin-top: 2px;">Línea 21 Colectivos y Junta de Vecinos El Toqui</div>
          </div>
          <div>
            <div style="color: #64748B; font-weight: 700; font-size: 10.5px; text-transform: uppercase;">Plazo Límite de Ejecución</div>
            <div style="margin-top: 2px; font-weight: 700; color: #854D0E;">30-09-2026 (Faltan 4 días)</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline of Gestiones -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>⏱️</span> HISTORIAL Y TRAZABILIDAD DE GESTIONES (CADENA DE RESOLUCIÓN)
        </div>
        <button class="btn btn-secondary btn-sm">+ Agregar Gestión</button>
      </div>
      <div class="card-body">
        <div style="border-left: 2px solid #CBD5E1; margin-left: 10px; padding-left: 18px; display: flex; flex-direction: column; gap: 18px;">
          
          <div style="position: relative;">
            <div style="position: absolute; left: -25px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: #10B981; border: 2px solid white;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748B;">
              <strong>1ra Gestión: Inspección Técnica en Terreno</strong>
              <span>15-09-2026 10:15 hrs</span>
            </div>
            <p style="margin-top: 4px; font-size: 12px;">
              Territorial OO.CC (Roberto Tapia) realiza cubicación: Se constata bache de 3.2m x 1.8m con profundidad de 8cm. Requiere retiro de material suelto y asfalto frío.
            </p>
            <span class="badge badge-done" style="margin-top: 4px;">📷 2 Fotos Adjuntas (Hash Validado)</span>
          </div>

          <div style="position: relative;">
            <div style="position: absolute; left: -25px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: #2563EB; border: 2px solid white;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748B;">
              <strong>2da Gestión: Solicitud de Insumos y Cuadrilla</strong>
              <span>20-09-2026 14:30 hrs</span>
            </div>
            <p style="margin-top: 4px; font-size: 12px;">
              DISERCO (Marcelo Bravo) ingresa solicitud de 15 sacos de asfalto en frío a bodega central. Programada cuadrilla municipal para día 28-09.
            </p>
            <span class="badge badge-blue" style="margin-top: 4px;">Documento #SOL-891-2026</span>
          </div>

          <div style="position: relative;">
            <div style="position: absolute; left: -25px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: #F59E0B; border: 2px solid white;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748B;">
              <strong>3ra Gestión: Coordinación con Tránsito y Cierre</strong>
              <span>25-09-2026 09:00 hrs</span>
            </div>
            <p style="margin-top: 4px; font-size: 12px;">
              Seguridad Ciudadana confirma patrulla para corte preventivo de pista durante los trabajos de bacheo.
            </p>
            <span class="badge badge-process" style="margin-top: 4px;">En Ejecución</span>
          </div>

        </div>
      </div>
    </div>
  </div>

  <!-- Right Side: Inter-department Chat -->
  <div>
    <div class="card" style="display: flex; flex-direction: column; height: 580px;">
      <div class="card-header" style="background: #1E293B; color: white;">
        <div style="font-weight: 700; font-size: 12.5px; display: flex; align-items: center; gap: 6px;">
          <span>💬</span> CHAT DE COORDINACIÓN ENTRE ÁREAS
        </div>
        <span style="font-size: 10px; background: #334155; padding: 2px 6px; border-radius: 10px;">3 Participantes</span>
      </div>
      
      <!-- Messages Container -->
      <div style="flex: 1; padding: 14px; overflow-y: auto; background: #F8FAFC; display: flex; flex-direction: column; gap: 12px;">
        
        <!-- Msg 1 -->
        <div style="align-self: flex-start; max-width: 85%;">
          <div style="font-size: 10px; font-weight: 700; color: #475569; margin-bottom: 2px;">Roberto Tapia (OO.CC) - 15/09 10:20</div>
          <div style="background: white; border: 1px solid #E2E8F0; padding: 8px 10px; border-radius: 6px; font-size: 11.5px;">
            Marcelo, el bache está peligroso para los colectivos. ¿Tienen cuadrilla disponible para esta semana?
          </div>
        </div>

        <!-- Msg 2 -->
        <div style="align-self: flex-end; max-width: 85%;">
          <div style="font-size: 10px; font-weight: 700; color: #7A1C28; margin-bottom: 2px; text-align: right;">Marcelo Bravo (DISERCO) - 15/09 11:05</div>
          <div style="background: #FEE2E2; border: 1px solid #FCA5A5; padding: 8px 10px; border-radius: 6px; font-size: 11.5px; color: #991B1B;">
            Estamos esperando que nos llegue asfalto en frío el jueves desde La Cantera. Lo agendo de inmediato para el lunes a primera hora.
          </div>
        </div>

        <!-- Msg 3 -->
        <div style="align-self: flex-start; max-width: 85%;">
          <div style="font-size: 10px; font-weight: 700; color: #2563EB; margin-bottom: 2px;">Andrea Cortés (Seguridad) - 25/09 09:12</div>
          <div style="background: #EFF6FF; border: 1px solid #BFDBFE; padding: 8px 10px; border-radius: 6px; font-size: 11.5px;">
            Coordinado con el móvil 4 de Seguridad para resguardo vial el lunes entre 09:00 y 13:00 hrs.
          </div>
        </div>

        <!-- Msg 4 -->
        <div style="align-self: flex-end; max-width: 85%;">
          <div style="font-size: 10px; font-weight: 700; color: #7A1C28; margin-bottom: 2px; text-align: right;">Marcelo Bravo (DISERCO) - 25/09 10:30</div>
          <div style="background: #FEE2E2; border: 1px solid #FCA5A5; padding: 8px 10px; border-radius: 6px; font-size: 11.5px; color: #991B1B;">
            Excelente, con eso cumplimos antes del plazo límite del 30 de septiembre.
          </div>
        </div>

      </div>

      <!-- Chat Input -->
      <div style="padding: 10px; border-top: 1px solid #E2E8F0; background: white; display: flex; gap: 6px;">
        <input type="text" class="form-control" placeholder="Escriba un mensaje para el equipo..." style="flex: 1;">
        <button class="btn btn-primary btn-sm">Enviar</button>
      </div>
    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m06():
    """M-06: Semáforo General de la Delegación (Idéntico a Semáforo.png)"""
    content = f"""
{SHARED_HEAD.format(title="M-06: Semáforo General de la Delegación")}
<div class="mockup-stamp">SGR MOCKUP M-06 | SEMÁFORO DE CUMPLIMIENTO INSTITUCIONAL (EXCEL REPLICA)</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>

  <div class="nav-tabs">
    <a href="#" class="nav-tab">Mi Desempeño</a>
    <a href="#" class="nav-tab">Tubo de Trabajo</a>
    <a href="#" class="nav-tab active">Semáforo General</a>
    <a href="#" class="nav-tab">Reportes</a>
  </div>

  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Dirección Delegacional</div>
      <div class="u-role">Delegado Municipal Las Compañías</div>
    </div>
    <div class="u-avatar">DM</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Supervisión Directiva</span> &gt; <strong>Semáforo de Cumplimiento Trimestre III</strong>
  </div>
  <div style="display: flex; gap: 8px; align-items: center;">
    <span class="badge-period">📅 Corte al Día 38 de 65 Hábiles (Julio - Septiembre 2026)</span>
    <button class="btn btn-secondary btn-sm">📥 Exportar Reporte</button>
  </div>
</div>

<div class="container">
  <!-- Top Executive Bar with Excel Target Formulas -->
  <div class="kpi-row">
    <div class="kpi-card" style="border-left: 4px solid #7A1C28; background: #FFF5F5;">
      <div class="kpi-title">META DIARIA ESPERADA AL DÍA</div>
      <div class="kpi-value" style="color: #7A1C28;">56.04%</div>
      <div class="kpi-sub">Fórmula: (Días Transcurridos 38 / 65 Días Totales)</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #F59E0B;">
      <div class="kpi-title">UMBRAL DE ADVERTENCIA</div>
      <div class="kpi-value" style="color: #B45309;">60.00%</div>
      <div class="kpi-sub">Mínimo para Semáforo Verde</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #10B981;">
      <div class="kpi-title">PROMEDIO DELEGACIÓN AL DÍA</div>
      <div class="kpi-value" style="color: #065F46;">58.92%</div>
      <div class="kpi-sub"><span class="semaforo-dot dot-yellow"></span> <strong>ALERTA AMARILLA</strong> (-1.08% vs umbral)</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #2563EB;">
      <div class="kpi-title">TOTAL FUNCIONARIOS ACTIVOS</div>
      <div class="kpi-value">12</div>
      <div class="kpi-sub">6 en Verde | 4 en Amarillo | 2 en Rojo</div>
    </div>
  </div>

  <!-- Main Excel Matrix Table -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>🚦</span> MATRIZ DE RENDIMIENTO POR FUNCIONARIO Y SEMÁFORO DE CONTROL OPERATIVO
      </div>
      <div style="display: flex; gap: 8px;">
        <span class="badge badge-done">Verde: &ge; 60%</span>
        <span class="badge badge-process">Amarillo: 50% - 59.9%</span>
        <span class="badge badge-pending">Rojo: &lt; 50%</span>
      </div>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 45px; text-align: center;">N°</th>
              <th>FUNCIONARIO / OPERADOR</th>
              <th>CARGO / ÁREA TERRITORIAL</th>
              <th style="text-align: center;">META ASIGNADA</th>
              <th style="text-align: center;">CASOS CERRADOS</th>
              <th style="text-align: center;">EN PROCESO</th>
              <th style="text-align: center;">DÍAS TRABAJADOS</th>
              <th style="text-align: center; background: #FEF9C3; color: #854D0E;">% AVANCE REAL</th>
              <th style="text-align: center;">DESVIACIÓN VS META DIARIA (56.04%)</th>
              <th style="text-align: center; width: 120px;">ESTADO SEMÁFORO</th>
              <th style="text-align: center;">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="text-align: center; font-weight: 700;">1</td>
              <td><strong>Carlos Gómez V.</strong></td>
              <td>Gestor Social (Territorio Latorre)</td>
              <td style="text-align: center;">120</td>
              <td style="text-align: center; font-weight: 700;">72</td>
              <td style="text-align: center;">16</td>
              <td style="text-align: center;">38</td>
              <td style="text-align: center; font-weight: 800; color: #166534; background: #DCFCE7;">60.00%</td>
              <td style="text-align: center; color: #166534; font-weight: 700;">+3.96%</td>
              <td style="text-align: center;"><span class="badge badge-done"><span class="semaforo-dot dot-green"></span> VERDE</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">2</td>
              <td><strong>Roberto Tapia S.</strong></td>
              <td>Territorial OO.CC (Territorio El Toqui)</td>
              <td style="text-align: center;">95</td>
              <td style="text-align: center; font-weight: 700;">56</td>
              <td style="text-align: center;">12</td>
              <td style="text-align: center;">38</td>
              <td style="text-align: center; font-weight: 800; color: #854D0E; background: #FEF9C3;">58.95%</td>
              <td style="text-align: center; color: #166534; font-weight: 700;">+2.91%</td>
              <td style="text-align: center;"><span class="badge badge-process"><span class="semaforo-dot dot-yellow"></span> AMARILLO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">3</td>
              <td><strong>Marcelo Bravo L.</strong></td>
              <td>Coordinador DISERCO / Operaciones</td>
              <td style="text-align: center;">150</td>
              <td style="text-align: center; font-weight: 700;">78</td>
              <td style="text-align: center;">24</td>
              <td style="text-align: center;">36 (2 lic.)</td>
              <td style="text-align: center; font-weight: 800; color: #991B1B; background: #FEE2E2;">52.00%</td>
              <td style="text-align: center; color: #991B1B; font-weight: 700;">-4.04%</td>
              <td style="text-align: center;"><span class="badge badge-pending"><span class="semaforo-dot dot-red"></span> ROJO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">4</td>
              <td><strong>Andrea Cortés M.</strong></td>
              <td>Gestora Seguridad Ciudadana</td>
              <td style="text-align: center;">80</td>
              <td style="text-align: center; font-weight: 700;">52</td>
              <td style="text-align: center;">8</td>
              <td style="text-align: center;">38</td>
              <td style="text-align: center; font-weight: 800; color: #166534; background: #DCFCE7;">65.00%</td>
              <td style="text-align: center; color: #166534; font-weight: 700;">+8.96%</td>
              <td style="text-align: center;"><span class="badge badge-done"><span class="semaforo-dot dot-green"></span> VERDE</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">5</td>
              <td><strong>Lorena Soto R.</strong></td>
              <td>Apoyo Administrativo y Atención Público</td>
              <td style="text-align: center;">210</td>
              <td style="text-align: center; font-weight: 700;">132</td>
              <td style="text-align: center;">18</td>
              <td style="text-align: center;">38</td>
              <td style="text-align: center; font-weight: 800; color: #166534; background: #DCFCE7;">62.86%</td>
              <td style="text-align: center; color: #166534; font-weight: 700;">+6.82%</td>
              <td style="text-align: center;"><span class="badge badge-done"><span class="semaforo-dot dot-green"></span> VERDE</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">6</td>
              <td><strong>Felipe Morales P.</strong></td>
              <td>Planificación y Control de Gestión</td>
              <td style="text-align: center;">50</td>
              <td style="text-align: center; font-weight: 700;">31</td>
              <td style="text-align: center;">6</td>
              <td style="text-align: center;">38</td>
              <td style="text-align: center; font-weight: 800; color: #166534; background: #DCFCE7;">62.00%</td>
              <td style="text-align: center; color: #166534; font-weight: 700;">+5.96%</td>
              <td style="text-align: center;"><span class="badge badge-done"><span class="semaforo-dot dot-green"></span> VERDE</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">7</td>
              <td><strong>Patricia Venegas G.</strong></td>
              <td>Gestora Social (Territorio Zorrilla)</td>
              <td style="text-align: center;">120</td>
              <td style="text-align: center; font-weight: 700;">68</td>
              <td style="text-align: center;">15</td>
              <td style="text-align: center;">38</td>
              <td style="text-align: center; font-weight: 800; color: #854D0E; background: #FEF9C3;">56.67%</td>
              <td style="text-align: center; color: #166534; font-weight: 700;">+0.63%</td>
              <td style="text-align: center;"><span class="badge badge-process"><span class="semaforo-dot dot-yellow"></span> AMARILLO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">8</td>
              <td><strong>Mauricio Rivera C.</strong></td>
              <td>Territorial OO.CC (Territorio Rural Lambert)</td>
              <td style="text-align: center;">90</td>
              <td style="text-align: center; font-weight: 700;">44</td>
              <td style="text-align: center;">11</td>
              <td style="text-align: center;">35 (3 fer.)</td>
              <td style="text-align: center; font-weight: 800; color: #991B1B; background: #FEE2E2;">48.89%</td>
              <td style="text-align: center; color: #991B1B; font-weight: 700;">-7.15%</td>
              <td style="text-align: center;"><span class="badge badge-pending"><span class="semaforo-dot dot-red"></span> ROJO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Ver Detalle</button></td>
            </tr>
            <tr style="background: #F8FAFC; font-weight: 800; border-top: 2px solid #CBD5E1;">
              <td colspan="3" style="text-align: right; text-transform: uppercase;">PROMEDIO GENERAL DE LA DELEGACIÓN:</td>
              <td style="text-align: center;">915</td>
              <td style="text-align: center;">539</td>
              <td style="text-align: center;">102</td>
              <td style="text-align: center;">38 prom.</td>
              <td style="text-align: center; font-size: 13.5px; background: #FEF08A; color: #854D0E;">58.92%</td>
              <td style="text-align: center; color: #166534; font-weight: 700;">+2.88% vs diaria</td>
              <td style="text-align: center;"><span class="badge badge-process"><span class="semaforo-dot dot-yellow"></span> AMARILLO</span></td>
              <td style="text-align: center;"><button class="btn btn-primary btn-sm">Auditar</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m07():
    """M-07: Resumen de la Delegación y Metas Estratégicas (Idéntico a Resumen de la delegación.png)"""
    content = f"""
{SHARED_HEAD.format(title="M-07: Resumen General de la Delegación")}
<div class="mockup-stamp">SGR MOCKUP M-07 | RESUMEN DELEGACIONAL Y PONDERACIÓN ESTRATÉGICA</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>

  <div class="nav-tabs">
    <a href="#" class="nav-tab">Mi Desempeño</a>
    <a href="#" class="nav-tab">Tubo de Trabajo</a>
    <a href="#" class="nav-tab">Semáforo General</a>
    <a href="#" class="nav-tab active">Resumen Delegación</a>
  </div>

  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Felipe Morales</div>
      <div class="u-role">Planificación y Control</div>
    </div>
    <div class="u-avatar">FM</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Planificación</span> &gt; <strong>Ponderaciones y Resumen Institucional</strong>
  </div>
  <div style="display: flex; gap: 8px;">
    <button class="btn btn-secondary btn-sm">⚙️ Ajustar Ponderaciones</button>
    <button class="btn btn-primary btn-sm">Generar Informe Trimestral</button>
  </div>
</div>

<div class="container">
  <div class="kpi-row">
    <div class="kpi-card" style="border-left: 4px solid #7A1C28;">
      <div class="kpi-title">Compromiso Total Delegación</div>
      <div class="kpi-value">915 Metas</div>
      <div class="kpi-sub">5 Áreas Funcionales</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #10B981;">
      <div class="kpi-title">Cumplimiento Global Ponderado</div>
      <div class="kpi-value" style="color: #065F46;">59.14%</div>
      <div class="kpi-sub">Meta esperada al corte: 56.04%</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #2563EB;">
      <div class="kpi-title">Días Hábiles Transcurridos</div>
      <div class="kpi-value">38 / 65</div>
      <div class="kpi-sub">27 días hábiles para el cierre</div>
    </div>
  </div>

  <!-- Main Strategy Table (Mirroring Resumen de la delegación.png) -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📑</span> CONSOLIDADO DE LÍNEAS ESTRATÉGICAS Y PONDERACIÓN MUNICIPAL
      </div>
      <span class="badge badge-done">Trimestre III (Q3 2026)</span>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 50px; text-align: center;">CÓDIGO</th>
              <th>DEPARTAMENTO / LÍNEA OPERATIVA</th>
              <th style="text-align: center; width: 110px;">PONDERACIÓN (%)</th>
              <th style="text-align: center; width: 110px;">CANTIDAD META</th>
              <th style="text-align: center; width: 110px;">LOGRADO AL DÍA</th>
              <th style="text-align: center; width: 120px;">% CUMPLIMIENTO</th>
              <th style="text-align: center; width: 130px; background: #FEF9C3; color: #854D0E;">PONDERACIÓN NETA</th>
              <th style="text-align: center; width: 110px;">SEMÁFORO</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="text-align: center; font-weight: 700;">DP-01</td>
              <td><strong>Área Social y Familia</strong> (Atenciones, fichaje social, subsidios de emergencia)</td>
              <td style="text-align: center; font-weight: 700;">25%</td>
              <td style="text-align: center;">240</td>
              <td style="text-align: center; font-weight: 700;">142</td>
              <td style="text-align: center; font-weight: 700; color: #166534;">59.17%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">14.79%</td>
              <td style="text-align: center;"><span class="badge badge-done">CUMPLIENDO</span></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">DP-02</td>
              <td><strong>Territorial y Organizaciones Comunitarias (OO.CC)</strong> (JJ.VV, comités, asambleas)</td>
              <td style="text-align: center; font-weight: 700;">25%</td>
              <td style="text-align: center;">220</td>
              <td style="text-align: center; font-weight: 700;">130</td>
              <td style="text-align: center; font-weight: 700; color: #166534;">59.09%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">14.77%</td>
              <td style="text-align: center;"><span class="badge badge-done">CUMPLIENDO</span></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">DP-03</td>
              <td><strong>Coordinación DISERCO / Operaciones</strong> (Tolvas, bacheo, podas, microbasurales)</td>
              <td style="text-align: center; font-weight: 700;">20%</td>
              <td style="text-align: center;">180</td>
              <td style="text-align: center; font-weight: 700;">98</td>
              <td style="text-align: center; font-weight: 700; color: #854D0E;">54.44%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">10.89%</td>
              <td style="text-align: center;"><span class="badge badge-process">ALERTA</span></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">DP-04</td>
              <td><strong>Seguridad Ciudadana e Inspección</strong> (Patrullajes mixtos, fiscalizaciones)</td>
              <td style="text-align: center; font-weight: 700;">15%</td>
              <td style="text-align: center;">140</td>
              <td style="text-align: center; font-weight: 700;">94</td>
              <td style="text-align: center; font-weight: 700; color: #166534;">67.14%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">10.07%</td>
              <td style="text-align: center;"><span class="badge badge-done">DESTACADO</span></td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">DP-05</td>
              <td><strong>Planificación, Control y Apoyo Administrativo</strong> (Auditoría, partes, reportes)</td>
              <td style="text-align: center; font-weight: 700;">15%</td>
              <td style="text-align: center;">135</td>
              <td style="text-align: center; font-weight: 700;">82</td>
              <td style="text-align: center; font-weight: 700; color: #166534;">60.74%</td>
              <td style="text-align: center; font-weight: 800; background: #FEF9C3;">9.11%</td>
              <td style="text-align: center;"><span class="badge badge-done">CUMPLIENDO</span></td>
            </tr>
            <tr style="background: #F8FAFC; font-weight: 800; border-top: 2px solid #CBD5E1;">
              <td colspan="2" style="text-align: right; text-transform: uppercase;">TOTAL CONSOLIDADO DELEGACIONAL:</td>
              <td style="text-align: center; font-size: 13px;">100%</td>
              <td style="text-align: center; font-size: 13px;">915</td>
              <td style="text-align: center; font-size: 13px;">546</td>
              <td style="text-align: center; font-size: 13px; color: #1E40AF;">59.67%</td>
              <td style="text-align: center; font-size: 14px; background: #FEF08A; color: #854D0E;">59.14%</td>
              <td style="text-align: center;"><span class="badge badge-done" style="background:#10B981; color:white;">VERDE GLOBAL</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m08():
    """M-08: Bandeja de Validación y Supervisión de Evidencias (Jefatura)"""
    content = f"""
{SHARED_HEAD.format(title="M-08: Bandeja de Validación y Supervisión")}
<div class="mockup-stamp">SGR MOCKUP M-08 | BANDEJA DE SUPERVISIÓN Y CONTROL DE CALIDAD</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>

  <div class="nav-tabs">
    <a href="#" class="nav-tab">Semáforo General</a>
    <a href="#" class="nav-tab">Tubo de Trabajo</a>
    <a href="#" class="nav-tab active">Bandeja de Validación</a>
    <a href="#" class="nav-tab">Auditoría</a>
  </div>

  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Ingrid Miranda</div>
      <div class="u-role">Jefatura Territorial / Supervisora</div>
    </div>
    <div class="u-avatar">IM</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Supervisión</span> &gt; <strong>Bandeja de Aprobación de Evidencias de Terreno</strong>
  </div>
  <div style="display: flex; gap: 8px;">
    <span class="badge badge-process" style="padding: 6px 10px;">⏳ 8 Registros Pendientes de Revisión</span>
  </div>
</div>

<div class="container" style="display: grid; grid-template-columns: 1fr 1.3fr; gap: 16px;">
  <!-- Left Side: Pending Queue -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📥</span> REGISTROS OPERATIVOS POR VALIDAR
      </div>
      <span class="badge badge-gray">Filtro: Hoy</span>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th>CÓDIGO</th>
              <th>FUNCIONARIO</th>
              <th>GESTIÓN REALIZADA</th>
              <th style="text-align: center;">EVIDENCIAS</th>
              <th style="text-align: center;">ACCIÓN</th>
            </tr>
          </thead>
          <tbody>
            <tr style="background: #EFF6FF; border-left: 4px solid #2563EB;">
              <td><strong style="color: #7A1C28;">SOC-711</strong></td>
              <td>Carlos Gómez (Social)</td>
              <td>Entrega canasta alimentos emergencia</td>
              <td style="text-align: center;"><span class="badge badge-done">2 FOTOS</span></td>
              <td style="text-align: center;"><button class="btn btn-primary btn-sm">Examinar</button></td>
            </tr>
            <tr>
              <td><strong style="color: #7A1C28;">TER-218</strong></td>
              <td>Roberto Tapia (OO.CC)</td>
              <td>Cubicación bacheo calle Lautaro</td>
              <td style="text-align: center;"><span class="badge badge-done">2 FOTOS</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Examinar</button></td>
            </tr>
            <tr>
              <td><strong style="color: #7A1C28;">DIS-094</strong></td>
              <td>Marcelo Bravo (DISERCO)</td>
              <td>Retiro escombros Villa El Romero</td>
              <td style="text-align: center;"><span class="badge badge-done">3 FOTOS</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Examinar</button></td>
            </tr>
            <tr>
              <td><strong style="color: #7A1C28;">SEG-141</strong></td>
              <td>Andrea Cortés (Seguridad)</td>
              <td>Rondín preventivo Plaza El Toqui</td>
              <td style="text-align: center;"><span class="badge badge-done">1 FOTO</span></td>
              <td style="text-align: center;"><button class="btn btn-secondary btn-sm">Examinar</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Right Side: Inspection & Approval Panel -->
  <div class="card">
    <div class="card-header" style="background: #F8FAFC;">
      <div class="card-title">
        <span>🔍</span> EXPEDIENTE DE CASO #SOC-711 (CARLOS GÓMEZ - GESTOR SOCIAL)
      </div>
      <span class="badge badge-blue">Revisión en Progreso</span>
    </div>
    <div class="card-body">
      
      <div style="background: #F1F5F9; padding: 12px; border-radius: 6px; margin-bottom: 14px; font-size: 11.5px;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
          <div><strong>Beneficiario:</strong> María Rojas Pastén</div>
          <div><strong>RUT:</strong> 9.412.589-K</div>
          <div><strong>Dirección:</strong> Pasaje Las Violetas #412, Latorre</div>
          <div><strong>Meta Acreditada:</strong> Asistencia Social Directa (+0.83%)</div>
        </div>
      </div>

      <!-- Evidence Inspection Grid -->
      <h5 style="font-size: 11.5px; font-weight: 700; color: #334155; margin-bottom: 8px; text-transform: uppercase;">
        Evidencias Fotográficas Acreditadas
      </h5>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
        <div style="border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px; background: white; text-align: center;">
          <div style="height: 120px; background: #E2E8F0; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 32px; margin-bottom: 6px;">
            🏡
          </div>
          <div style="font-size: 10.5px; font-weight: 700;">Foto 1: Visita Terreno</div>
          <div style="font-size: 9.5px; color: #166534; font-weight: 700;">✓ Hash Verificado | GPS OK</div>
        </div>
        <div style="border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px; background: white; text-align: center;">
          <div style="height: 120px; background: #E2E8F0; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 32px; margin-bottom: 6px;">
            📝
          </div>
          <div style="font-size: 10.5px; font-weight: 700;">Foto 2: Acta Firmada</div>
          <div style="font-size: 9.5px; color: #166534; font-weight: 700;">✓ Hash Verificado | GPS OK</div>
        </div>
      </div>

      <!-- Supervisor Notes Input -->
      <div style="margin-bottom: 16px;">
        <label style="display: block; font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 4px;">
          Observaciones de Supervisión / Dictamen:
        </label>
        <textarea class="form-control" rows="3" style="width: 100%; font-size: 11.5px;" placeholder="Ingrese comentarios para el funcionario (opcional si aprueba)...">Revisión conforme: Evidencia fotográfica georreferenciada correctamente y acta firmada por el requirente en archivo.</textarea>
      </div>

      <!-- Actions -->
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #E2E8F0; padding-top: 14px;">
        <button class="btn btn-danger btn-sm">❌ Observar / Rechazar</button>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-secondary btn-sm">Solicitar Ampliación</button>
          <button class="btn btn-success" style="padding: 8px 18px; font-size: 12px; font-weight: 700;">
            ✓ APROBAR Y COMPUTAR A META (+0.83%)
          </button>
        </div>
      </div>

    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m09():
    """M-09: Reportes Estadísticos y Exportación Oficial a Excel"""
    content = f"""
{SHARED_HEAD.format(title="M-09: Reportes Estadísticos y Exportación")}
<div class="mockup-stamp">SGR MOCKUP M-09 | MÓDULO DE REPORTES Y EXPORTACIÓN DE DATOS</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>

  <div class="nav-tabs">
    <a href="#" class="nav-tab">Mi Desempeño</a>
    <a href="#" class="nav-tab">Tubo de Trabajo</a>
    <a href="#" class="nav-tab">Semáforo General</a>
    <a href="#" class="nav-tab active">Reportes y Estadísticas</a>
  </div>

  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Felipe Morales</div>
      <div class="u-role">Planificación y Control</div>
    </div>
    <div class="u-avatar">FM</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Informes</span> &gt; <strong>Generador de Reportes y Estadísticas</strong>
  </div>
  <div style="display: flex; gap: 8px;">
    <button class="btn btn-secondary btn-sm">🖨️ Imprimir Resumen</button>
    <button class="btn btn-success btn-sm">📥 Descargar Planilla Excel (.xlsx)</button>
    <button class="btn btn-primary btn-sm">📄 Generar Informe PDF Oficial</button>
  </div>
</div>

<div class="container">
  <!-- Filters Bar -->
  <div class="filters-bar">
    <div class="form-group">
      <label>Período de Análisis:</label>
      <select class="form-control">
        <option selected>Trimestre III (Julio - Septiembre 2026)</option>
        <option>Trimestre II (Abril - Junio 2026)</option>
        <option>Trimestre I (Enero - Marzo 2026)</option>
        <option>Consolidado Anual 2026</option>
      </select>
    </div>
    <div class="form-group">
      <label>Territorio Específico:</label>
      <select class="form-control">
        <option selected>Toda la Delegación Las Compañías</option>
        <option>Territorio 1: Latorre</option>
        <option>Territorio 2: El Toqui</option>
        <option>Territorio 3: Vicente Zorrilla</option>
        <option>Territorio 4: Pinamar</option>
        <option>Territorio 5: Rural (Lambert / Ceres)</option>
      </select>
    </div>
  </div>

  <!-- Visual Analytics Grid -->
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
    
    <!-- Chart 1: Bar Chart Simulation -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>📊</span> CUMPLIMIENTO POR ÁREA VS META ESPERADA (56.04%)
        </div>
      </div>
      <div class="card-body">
        <div style="display: flex; flex-direction: column; gap: 14px; font-size: 11.5px;">
          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong>Seguridad Ciudadana</strong>
              <span style="font-weight: 700; color: #166534;">67.14%</span>
            </div>
            <div style="height: 16px; background: #E2E8F0; border-radius: 4px; overflow: hidden; position: relative;">
              <div style="width: 67.14%; height: 100%; background: #10B981;"></div>
            </div>
          </div>

          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong>Planificación y Control</strong>
              <span style="font-weight: 700; color: #166534;">60.74%</span>
            </div>
            <div style="height: 16px; background: #E2E8F0; border-radius: 4px; overflow: hidden; position: relative;">
              <div style="width: 60.74%; height: 100%; background: #10B981;"></div>
            </div>
          </div>

          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong>Área Social y Familia</strong>
              <span style="font-weight: 700; color: #166534;">59.17%</span>
            </div>
            <div style="height: 16px; background: #E2E8F0; border-radius: 4px; overflow: hidden; position: relative;">
              <div style="width: 59.17%; height: 100%; background: #10B981;"></div>
            </div>
          </div>

          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong>Territorial OO.CC</strong>
              <span style="font-weight: 700; color: #166534;">59.09%</span>
            </div>
            <div style="height: 16px; background: #E2E8F0; border-radius: 4px; overflow: hidden; position: relative;">
              <div style="width: 59.09%; height: 100%; background: #10B981;"></div>
            </div>
          </div>

          <div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong>DISERCO / Operaciones</strong>
              <span style="font-weight: 700; color: #854D0E;">54.44% (Bajo Meta Diaria)</span>
            </div>
            <div style="height: 16px; background: #E2E8F0; border-radius: 4px; overflow: hidden; position: relative;">
              <div style="width: 54.44%; height: 100%; background: #F59E0B;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart 2: Resolution Status Donut simulation -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <span>🎯</span> ESTADO DE RESOLUCIÓN EN TUBO DE TRABAJO (48 CASOS)
        </div>
      </div>
      <div class="card-body" style="display: flex; align-items: center; justify-content: space-around;">
        <div style="width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(#10B981 0% 60.4%, #F59E0B 60.4% 85.4%, #EF4444 85.4% 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <div style="width: 80px; height: 80px; background: white; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <span style="font-size: 16px; font-weight: 800; color: #1E293B;">48</span>
            <span style="font-size: 9.5px; color: #64748B;">Total Casos</span>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 11.5px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 12px; height: 12px; background: #10B981; border-radius: 2px;"></div>
            <strong>Realizados:</strong> 29 casos (60.4%)
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 12px; height: 12px; background: #F59E0B; border-radius: 2px;"></div>
            <strong>En Proceso:</strong> 12 casos (25.0%)
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 12px; height: 12px; background: #EF4444; border-radius: 2px;"></div>
            <strong>Pendientes / Alerta:</strong> 7 casos (14.6%)
          </div>
          <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #E2E8F0; color: #64748B;">
            ⏱️ Tiempo promedio de cierre: <strong>4.8 días hábiles</strong>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Excel Structure Table for Export -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📑</span> VISTA PREVIA DEL FORMATO DE EXPORTACIÓN EXCEL (.XLSX)
      </div>
      <span class="badge badge-done">Compatibilidad 100% con Plantilla Original</span>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>TERRITORIO</th>
              <th>SOLICITANTE</th>
              <th>REQUERIMIENTO</th>
              <th>RESPONSABLE</th>
              <th style="text-align: center;">FECHA INGRESO</th>
              <th style="text-align: center;">FECHA CIERRE</th>
              <th style="text-align: center;">ESTADO</th>
              <th style="text-align: center;">EVIDENCIA HASH</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>TB-101</td>
              <td>Latorre</td>
              <td>JJ.VV Villa El Romero</td>
              <td>Retiro microbasural y escombros</td>
              <td>DISERCO (M. Bravo)</td>
              <td style="text-align: center;">12-09-2026</td>
              <td style="text-align: center;">18-09-2026</td>
              <td style="text-align: center;"><span class="badge badge-done">REALIZADO</span></td>
              <td style="font-family: monospace; font-size: 10px;">e3b0c442...855</td>
            </tr>
            <tr>
              <td>TB-102</td>
              <td>El Toqui</td>
              <td>Línea 21 Colectivos</td>
              <td>Bacheo de calzada calle Lautaro</td>
              <td>OO.CC (R. Tapia)</td>
              <td style="text-align: center;">15-09-2026</td>
              <td style="text-align: center;">-</td>
              <td style="text-align: center;"><span class="badge badge-process">EN PROCESO</span></td>
              <td style="font-family: monospace; font-size: 10px;">7c3d19f8...bc8</td>
            </tr>
            <tr>
              <td>TB-104</td>
              <td>Pinamar</td>
              <td>Club Unión Compañías</td>
              <td>Demarcación y lomos de toro</td>
              <td>Tránsito / OO.CC</td>
              <td style="text-align: center;">16-09-2026</td>
              <td style="text-align: center;">25-09-2026</td>
              <td style="text-align: center;"><span class="badge badge-done">REALIZADO</span></td>
              <td style="font-family: monospace; font-size: 10px;">f482a901...12a</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def generate_m10():
    """M-10: Auditoría, Seguridad y Trazabilidad (CU-10 / HU-31)"""
    content = f"""
{SHARED_HEAD.format(title="M-10: Auditoría y Trazabilidad")}
<div class="mockup-stamp">SGR MOCKUP M-10 | BITÁCORA DE AUDITORÍA Y TRAZABILIDAD INMUTABLE</div>

<nav class="top-nav">
  <div class="brand">
    <div class="shield-badge">
      <span>🏛️</span>
      <span style="font-size: 8px;">SERENA</span>
    </div>
    <div class="titles">
      <h1>SGR - GESTIÓN DE RESULTADOS</h1>
      <p>Delegación Las Compañías | Ilustre Municipalidad de La Serena</p>
    </div>
  </div>

  <div class="nav-tabs">
    <a href="#" class="nav-tab">Semáforo General</a>
    <a href="#" class="nav-tab">Tubo de Trabajo</a>
    <a href="#" class="nav-tab">Reportes</a>
    <a href="#" class="nav-tab active">Auditoría y Seguridad</a>
  </div>

  <div class="user-info">
    <div class="user-text">
      <div class="u-name">Administrador TI</div>
      <div class="u-role">Seguridad Municipal</div>
    </div>
    <div class="u-avatar">TI</div>
  </div>
</nav>

<div class="sub-bar">
  <div class="breadcrumb">
    <span>Inicio</span> &gt; <span>Seguridad</span> &gt; <strong>Registro de Auditoría Inmutable (Ley N° 19.628 / CU-10)</strong>
  </div>
  <div style="display: flex; gap: 8px;">
    <span class="badge badge-done">🛡️ Cadena de Bloques Interna: ÍNTEGRA</span>
    <button class="btn btn-secondary btn-sm">Exportar Log Criptográfico</button>
  </div>
</div>

<div class="container">
  <!-- Top Stats -->
  <div class="kpi-row">
    <div class="kpi-card" style="border-left: 4px solid #1E293B;">
      <div class="kpi-title">Eventos Registrados Hoy</div>
      <div class="kpi-value">142</div>
      <div class="kpi-sub">100% de operaciones registradas</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #10B981;">
      <div class="kpi-title">Validaciones de Jefatura</div>
      <div class="kpi-value" style="color: #065F46;">28</div>
      <div class="kpi-sub">Firmadas digitalmente</div>
    </div>
    <div class="kpi-card" style="border-left: 4px solid #EF4444;">
      <div class="kpi-title">Intentos de Modificación No Autorizada</div>
      <div class="kpi-value" style="color: #991B1B;">0</div>
      <div class="kpi-sub">Políticas RBAC activas</div>
    </div>
  </div>

  <!-- Filters -->
  <div class="filters-bar">
    <div class="form-group">
      <label>Usuario / RUT:</label>
      <input type="text" class="form-control" placeholder="Todos los usuarios" style="width: 160px;">
    </div>
    <div class="form-group">
      <label>Acción:</label>
      <select class="form-control">
        <option selected>Todas las Acciones</option>
        <option>INSERT (Creación de Caso)</option>
        <option>UPDATE (Avance de Gestión)</option>
        <option>APPROVE (Validación de Evidencia)</option>
        <option>LOGIN (Acceso al Sistema)</option>
      </select>
    </div>
    <div class="form-group">
      <label>Módulo:</label>
      <select class="form-control">
        <option selected>Todos los Módulos</option>
        <option>Tubo de Trabajo</option>
        <option>Mi Desempeño</option>
        <option>Evidencias Fotográficas</option>
        <option>Configuración Metas</option>
      </select>
    </div>
    <div class="form-group" style="flex: 1;">
      <input type="text" class="form-control" placeholder="🔍 Buscar por IP, ID de entidad o descripción..." style="width: 100%;">
    </div>
  </div>

  <!-- Audit Table -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">
        <span>📜</span> BITÁCORA FORENSE DE EVENTOS Y TRAZABILIDAD INMUTABLE
      </div>
      <span style="font-size: 11px; color: #64748B;">Cumple con Estándar ISO 27001 / OWASP Top 10</span>
    </div>
    <div class="card-body" style="padding: 0;">
      <div class="table-container">
        <table class="excel-table">
          <thead>
            <tr>
              <th style="width: 60px; text-align: center;">ID LOG</th>
              <th style="width: 130px;">FECHA Y HORA</th>
              <th style="width: 140px;">USUARIO / RUT</th>
              <th style="width: 90px;">ROL</th>
              <th style="width: 110px;">DIRECCIÓN IP</th>
              <th style="width: 80px; text-align: center;">ACCIÓN</th>
              <th style="width: 90px;">ENTIDAD</th>
              <th>DETALLE DE LA OPERACIÓN (ESTADO ANTERIOR ➔ NUEVO)</th>
              <th style="width: 120px; text-align: center;">FIRMA HASH</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="text-align: center; font-weight: 700;">#98421</td>
              <td>26-09-2026 12:45:10</td>
              <td>Ingrid Miranda (14.238.190-2)</td>
              <td>Supervisor</td>
              <td>192.168.10.45</td>
              <td style="text-align: center;"><span class="badge badge-done">APPROVE</span></td>
              <td><code>SOC-711</code></td>
              <td>Aprobó 2 evidencias fotográficas. Ponderación acreditada: +0.83% a Carlos Gómez.</td>
              <td style="text-align: center;"><code style="font-size: 9px; color: #166534;">✓ a1f4...9b0</td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">#98420</td>
              <td>26-09-2026 11:35:02</td>
              <td>Carlos Gómez (16.892.441-3)</td>
              <td>Gestor Social</td>
              <td>192.168.10.72</td>
              <td style="text-align: center;"><span class="badge badge-blue">INSERT</span></td>
              <td><code>EVID-892</code></td>
              <td>Subió 2 fotografías (JPG) con georreferencia válida (-29.8912, -71.2534).</td>
              <td style="text-align: center;"><code style="font-size: 9px; color: #166534;">✓ 7c3d...bc8</td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">#98419</td>
              <td>26-09-2026 10:14:30</td>
              <td>Marcelo Bravo (13.784.512-8)</td>
              <td>DISERCO</td>
              <td>192.168.10.58</td>
              <td style="text-align: center;"><span class="badge badge-process">UPDATE</span></td>
              <td><code>TB-102</code></td>
              <td>Modificó estado: [PENDIENTE] ➔ [EN PROCESO]. Agregó comentario de cuadrilla.</td>
              <td style="text-align: center;"><code style="font-size: 9px; color: #166534;">✓ 4d2e...31a</td>
            </tr>
            <tr>
              <td style="text-align: center; font-weight: 700;">#98418</td>
              <td>26-09-2026 08:30:15</td>
              <td>Roberto Tapia (15.120.489-0)</td>
              <td>OO.CC</td>
              <td>192.168.10.63</td>
              <td style="text-align: center;"><span class="badge badge-gray">LOGIN</span></td>
              <td><code>SESIÓN</code></td>
              <td>Inicio de sesión exitoso desde Delegación Las Compañías (Subred Interna).</td>
              <td style="text-align: center;"><code style="font-size: 9px; color: #166534;">✓ b82c...99f</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
{FOOTER}
"""
    return content

def main():
    mockups = [
        ("M-01_Login_Acceso", generate_m01),
        ("M-02_Mi_Desempeno_Registro", generate_m02),
        ("M-03_Carga_Evidencias", generate_m03),
        ("M-04_Tubo_Trabajo_Agenda", generate_m04),
        ("M-05_Detalle_Compromiso_Chat", generate_m05),
        ("M-06_Semaforo_Delegacion", generate_m06),
        ("M-07_Resumen_Delegacion_Metas", generate_m07),
        ("M-08_Bandeja_Validacion", generate_m08),
        ("M-09_Reportes_Estadisticas", generate_m09),
        ("M-10_Auditoria_Trazabilidad", generate_m10),
    ]

    print("=== Generating HTML Files ===")
    for name, gen_fn in mockups:
        html_path = os.path.join(HTML_DIR, f"{name}.html")
        html_code = gen_fn()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_code)
        print(f"Generated HTML: {html_path}")

    print("\n=== Rendering High-Res PNGs with Microsoft Edge Headless ===")
    for name, _ in mockups:
        html_path = os.path.join(HTML_DIR, f"{name}.html")
        png_path = os.path.join(PNG_DIR, f"{name}.png")
        file_url = f"file://{html_path}"
        
        cmd = [
            EDGE_BIN,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1440,920",
            f"--screenshot={png_path}",
            file_url
        ]
        
        print(f"Rendering {name}.png...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(png_path):
            size_kb = os.path.getsize(png_path) / 1024
            print(f"  ✓ SUCCESS: {png_path} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ FAILED: {res.stderr}")

    print("\nAll 10 Mockups Generated and Rendered!")

if __name__ == "__main__":
    main()
