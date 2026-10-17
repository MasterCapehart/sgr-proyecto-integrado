"""Vistas por función basadas en las cabeceras del libro; no contienen personas."""
from django.views.decorators.http import require_http_methods
from . import local_api as api
BASE=[['id','N°'],['fecha','Fecha'],['solicitud','Actividad / solicitud / problema'],['accion','Acción'],['contacto','Contacto'],['telefono','Fono'],['ingreso_tubo','Ingreso a tubo'],['item_nombre','Ítem'],['unidad','Unidad'],['codigo','Código foto'],['imagen_verificacion','Imagen verif.'],['estado','Verificación']]
PROFILES={
 'GENERAL':{'nombre':'General','hoja':'Vista de trabajo común','columnas':BASE},
 'AP_ADM':{'nombre':'AP ADM.','hoja':'AP ADM.!A15:T15','columnas':BASE[:3]+BASE[4:6]+[['item_nombre','Ítem'],['accion','Detalle'],['derivado_a','Derivado a']]+BASE[8:]},
 'COOR_DISERCO':{'nombre':'COOR DISERCO','hoja':'COOR DISERCO!B19:S19','columnas':BASE[:3]+BASE[4:]},
 'T_OC':{'nombre':'T OC','hoja':'T OC1!A17:T17; T OC 2–4!A16:T16','columnas':BASE},
 'G_SOC':{'nombre':'G SOC','ruta':'/pages/casos-sociales.html','hoja':'G SOC 1–5; captura en Gestión social','columnas':BASE},
 'PLAN_CON':{'nombre':'PLAN y CON','hoja':'PLAN y CON!B15:R15','columnas':[['id','N°'],['fecha','Fecha'],['solicitud','Detalle'],['contacto','Contacto'],['telefono','Teléfono'],['ingreso_tubo','Ingreso a tubo'],['item_nombre','Ítem'],['unidad','Unidad']]+BASE[9:]},
 'GES_SEG':{'nombre':'GES SEG','hoja':'GES SEG!B16:S16','columnas':[['id','N°'],['fecha','Fecha'],['solicitud','Situación / solicitud / detalle'],['contacto','Organización o vecino'],['telefono','Teléfono'],['ingreso_tubo','Ingreso a tubo'],['item_nombre','Ítem'],['profesional_nombre','Profesional'],['unidad','Unidad']]+BASE[9:]},
}
@require_http_methods(['GET'])
def profiles(request):
    if not request.user.is_authenticated:return api.error('Inicia sesión.',401)
    if not api.allowed(request.user,'actividades','ver'):return api.error('No tienes permiso para consultar planillas.',403)
    assigned=(request.user.cargo.planilla if request.user.cargo_id else '') or 'GENERAL'
    return api.ok(results=[{'codigo':code,**p} for code,p in PROFILES.items() if request.user.is_superuser or code in ['GENERAL',assigned]],asignada=assigned,puede_elegir=request.user.is_superuser)
