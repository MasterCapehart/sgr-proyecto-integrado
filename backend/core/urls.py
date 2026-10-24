from django.urls import path
from . import local_api as api
urlpatterns = [
 path('auditoria/',api.audit),path('csrf/',api.csrf),path('login/',api.access),path('logout/',api.exit_access),
 path('recuperacion/',api.recovery),path('recuperacion/estado/',api.recovery_status),
 path('recuperacion/verificar/',api.recovery,{'step':'verificar'}),
 path('recuperacion/cambiar/',api.recovery,{'step':'cambiar'}),
 path('contexto/',api.context),path('atenciones/contexto/',api.context),
 path('contexto/cambiar-delegacion/',api.change_context),path('opciones/',api.options),
]
from . import area_catalog, code_reservation
urlpatterns += [path('cargos/referencia-excel/', area_catalog.reference)]

for resource in api.RESOURCES:
 urlpatterns += [
  path(resource+'/reservar-codigo/',code_reservation.reserve,{'resource':resource}),
  path(resource+'/',api.crud,{'resource':resource}),
  path(resource+'/export/',api.crud,{'resource':resource,'action':'export'}),
  path(resource+'/<int:pk>/',api.crud,{'resource':resource}),
  path(resource+'/<int:pk>/toggle-estado/',api.crud,{'resource':resource,'action':'toggle-estado'}),
 ]

from . import domain_api as domain
urlpatterns += [path('operacion/opciones/',domain.options)]
for resource in domain.MODELS:
 urlpatterns += [path('operacion/'+resource+'/',domain.records,{'resource':resource}),path('operacion/'+resource+'/export/',domain.records,{'resource':resource,'action':'export'}),path('operacion/'+resource+'/<int:pk>/',domain.records,{'resource':resource}),path('operacion/'+resource+'/<int:pk>/mensajes/',domain.messages,{'resource':resource})]
urlpatterns += [path('operacion/evidencias/<int:pk>/archivo/',domain.download),path('operacion/evidencias/<int:pk>/revisar/',domain.review)]

from . import excel_api
urlpatterns += [path('casos-sociales/',excel_api.cases),path('casos-sociales/<str:code>/',excel_api.cases),path('operacion/actividades/<int:pk>/derivacion/',excel_api.derivation)]
from . import closure_api
urlpatterns += [path('alertas/',closure_api.alerts),path('alertas/<int:pk>/revisar/',closure_api.mark_alert),path('gobierno/',closure_api.governance),path('operacion/evidencias/<int:pk>/anular/',closure_api.annul),path('operacion/compromisos/<int:pk>/reabrir/',closure_api.reopen)]
for resource in closure_api.CATALOGS:
 urlpatterns += [path(resource+'/<int:pk>/historial/',closure_api.history,{'resource':resource})]

from . import kpis
urlpatterns += [path('indicadores/',kpis.overview)]

from . import feedback_api,matrix_profiles
urlpatterns += [path('planillas/',matrix_profiles.profiles),path('reclamos/',feedback_api.records),path('reclamos/export/',feedback_api.records,{'action':'export'}),path('reclamos/<int:pk>/',feedback_api.records)]

urlpatterns += [path('reclamos/opciones/',feedback_api.options)]

from . import deploy_api
urlpatterns += [path("version/", deploy_api.version), path("health/", deploy_api.health)]

from . import period_api
urlpatterns += [path('periodos/<int:pk>/cerrar/',period_api.transition,{'action':'cerrar'}),path('periodos/<int:pk>/reabrir/',period_api.transition,{'action':'reabrir'})]

from . import personal_progress
urlpatterns += [path('mi-progreso/', personal_progress.overview)]

from . import capture_followup
urlpatterns += [path('seguimiento/opciones/',capture_followup.options),path('operacion/compromisos/<int:pk>/origenes/',capture_followup.origins)]

from . import capture_form
urlpatterns += [path('captura/', capture_form.create)]
urlpatterns += [path('captura/opciones/', capture_form.options)]

from . import capture_codes
urlpatterns += [path('captura/reservar-codigo/', capture_codes.reserve)]

from . import neighbors
urlpatterns += [path('vecinos/', neighbors.create), path('vecinos/buscar/', neighbors.search)]

from . import community_api
urlpatterns += [path('vecinos/directorio/',community_api.resource,{'resource':'vecinos'})]
for community_resource in ['vecinos','organizaciones','pertenencias']:
    if community_resource!='vecinos':urlpatterns += [path(community_resource+'/',community_api.resource,{'resource':community_resource})]
    urlpatterns += [path(community_resource+'/<int:pk>/',community_api.resource,{'resource':community_resource}),path(community_resource+'/<int:pk>/estado/',community_api.resource,{'resource':community_resource,'action':'estado'})]

from . import milestone_api
urlpatterns += [path('hitos/opciones/',milestone_api.options),path('hitos/',milestone_api.records),path('hitos/<int:pk>/',milestone_api.records),path('hitos/<int:hito_id>/tareas/',milestone_api.tasks),path('hitos/tareas/<int:pk>/',milestone_api.tasks),path('hitos/tareas/<int:pk>/avances/',milestone_api.tasks,{'action':'avances'}),path('hitos/tareas/<int:pk>/tubo/',milestone_api.tasks,{'action':'tubo'})]

from . import eligibility_api
urlpatterns += [path('clasificacion-actividades/evaluar/',eligibility_api.preview),path('clasificacion-actividades/',eligibility_api.catalog),path('clasificacion-actividades/<int:pk>/',eligibility_api.catalog)]

from . import congratulations_api
urlpatterns += [path('reclamos/<int:pk>/respaldos/',congratulations_api.upload),path('reclamos/<int:pk>/respaldos/<int:backing>/archivo/',congratulations_api.download),path('reclamos/<int:pk>/revision/',congratulations_api.review)]
from . import absence_api
urlpatterns += [path('ausencias/opciones/',absence_api.options),path('ausencias/resumen/',absence_api.overview),path('ausencias/calendarios/',absence_api.calendars),path('ausencias/calendarios/<int:pk>/',absence_api.calendars),path('ausencias/',absence_api.records),path('ausencias/<int:pk>/',absence_api.records)]

from . import collective
urlpatterns += [path('cumplimiento/colectivo/',collective.overview)]

from . import weight_review
urlpatterns += [path('configuraciones-metas/revision-ponderaciones/',weight_review.overview)]
