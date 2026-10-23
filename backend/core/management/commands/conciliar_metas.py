"""Conciliar duplicados sin borrar filas ni alterar sus valores históricos."""
import json
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Count
from django.db.models.functions import Lower, Trim
from core.models import ConfiguracionMeta, Usuario, EventoLocal, ItemMeta, PeriodoGestion

class Command(BaseCommand):
    help='Simula por defecto. --apply requiere usuario administrador activo y motivo.'
    def add_arguments(self,parser):
        parser.add_argument('--apply',action='store_true');parser.add_argument('--usuario');parser.add_argument('--motivo')
    def handle(self,*args,**options):
        actor=None
        if options['apply']:
            actor=Usuario.objects.filter(username=options.get('usuario'),is_active=True,is_superuser=True).first()
            if not actor or not (options.get('motivo') or '').strip():raise CommandError('Aplicar requiere --usuario administrador activo y --motivo.')
        groups=list(ConfiguracionMeta.objects.filter(conciliada_con__isnull=True).annotate(clave=Lower(Trim('periodo'))).values('item_id','cargo_id','clave').annotate(total=Count('id')).filter(total__gt=1))
        report={'modo':'aplicar' if options['apply'] else 'simular','grupos':[]}
        for group in groups:
            with transaction.atomic():
                scope=ConfiguracionMeta.objects.filter(item_id=group['item_id'],cargo_id=group['cargo_id'],conciliada_con__isnull=True).annotate(clave=Lower(Trim('periodo'))).filter(clave=group['clave'])
                period_ids=set(scope.exclude(periodo_gestion__isnull=True).values_list('periodo_gestion_id',flat=True))
                list(PeriodoGestion.objects.select_for_update().filter(pk__in=period_ids).order_by('pk'))
                rows=list(ConfiguracionMeta.objects.select_for_update().filter(item_id=group['item_id'],cargo_id=group['cargo_id'],conciliada_con__isnull=True).annotate(clave=Lower(Trim('periodo'))).filter(clave=group['clave']).order_by('pk'))
                ItemMeta.objects.select_for_update().get(pk=group['item_id'])
                if len(rows)<2:continue
                if any(r.periodo_gestion_id for r in rows):
                    report['grupos'].append({'ids':[r.pk for r in rows],'criterio':'Calendarios vinculados: revisión manual, sin cambios.'});continue
                active=[r for r in rows if r.estado]
                signatures={(r.meta_esperada,r.ponderacion,r.periodo_gestion_id) for r in rows}
                canonical=active[0] if len(active)==1 else (active or rows)[0] if len(signatures)==1 else None
                entry={'item':group['item_id'],'periodo':rows[0].periodo,'ids':[r.pk for r in rows],'vigente':canonical.pk if canonical else None,'criterio':'única activa' if len(active)==1 else 'valores idénticos' if len(signatures)==1 else 'ambiguo: requiere decisión funcional','archivadas':[]}
                if canonical:
                    for r in rows:
                        if r.pk==canonical.pk:continue
                        entry['archivadas'].append(r.pk)
                        if options['apply']:
                            before={k:getattr(r,k) for k in ['item_id','periodo','periodo_gestion_id','meta_esperada','ponderacion','estado','version','conciliada_con_id']}
                            r.conciliada_con=canonical;r.estado=False;r.version+=1;r.save(update_fields=['conciliada_con','estado','version'])
                            after={k:getattr(r,k) for k in before};after['motivo']=options['motivo'].strip();after['criterio']=entry['criterio']
                            EventoLocal.objects.create(usuario=actor,delegacion=actor.delegacion,recurso='configuraciones-metas',registro=r.pk,accion='conciliar',antes=json.loads(json.dumps(before,cls=DjangoJSONEncoder)),despues=json.loads(json.dumps(after,cls=DjangoJSONEncoder)),origen='comando_administrativo')
                report['grupos'].append(entry)
        self.stdout.write(json.dumps(report,ensure_ascii=False,cls=DjangoJSONEncoder))
