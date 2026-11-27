"""Migrar configuraciones históricas de cargo a planes individuales revisables (Tarea DF08)."""
import json
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from core.models import ConfiguracionMeta, Usuario, EventoLocal, PeriodoGestion
from core.goal_models import AsignacionMeta

class Command(BaseCommand):
    help = 'Proponer o crear asignaciones individuales desde plantillas de cargo. --apply requiere --usuario y --motivo.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Persistir cambios en la base de datos.')
        parser.add_argument('--periodo', type=str, help='Código de periodo específico.')
        parser.add_argument('--usuario', type=str, help='Usuario administrador autor.')
        parser.add_argument('--motivo', type=str, help='Justificación de la migración.')

    def handle(self, *args, **options):
        actor = None
        if options['apply']:
            username = options.get('usuario')
            motivo = (options.get('motivo') or '').strip()
            actor = Usuario.objects.filter(username=username, is_active=True, is_superuser=True).first()
            if not actor or not motivo:
                raise CommandError('Aplicar requiere un --usuario administrador activo y un --motivo no vacío.')

        periods = PeriodoGestion.objects.filter(cerrado=False, estado=True)
        if options.get('periodo'):
            periods = periods.filter(codigo=options['periodo'])
        if not periods.exists():
            self.stdout.write(json.dumps({'mensaje': 'No hay periodos abiertos para procesar.', 'total': 0}))
            return

        report = {
            'modo': 'aplicar' if options['apply'] else 'simular',
            'periodos': [p.codigo for p in periods],
            'usuarios_evaluados': 0,
            'asignaciones_propuestas': 0,
            'asignaciones_creadas': 0,
            'asignaciones_omitidas_existentes': 0,
            'planes_pendientes_revision': 0,
            'detalles': []
        }

        for period in periods:
            users = Usuario.objects.filter(
                is_active=True, delegacion__isnull=False, cargo__isnull=False
            ).select_related('delegacion', 'cargo').order_by('username')
            
            for user in users:
                report['usuarios_evaluados'] += 1
                # Buscar configuraciones aplicables por cargo específico o fallback general
                specific_configs = list(ConfiguracionMeta.objects.filter(
                    cargo=user.cargo, estado=True, conciliada_con__isnull=True
                ).filter(
                    models_q_periodo(period)
                ).select_related('item'))

                # Si no hay específicas, buscar generales (cargo is null)
                configs = specific_configs
                if not configs:
                    configs = list(ConfiguracionMeta.objects.filter(
                        cargo__isnull=True, estado=True, conciliada_con__isnull=True
                    ).filter(
                        models_q_periodo(period)
                    ).select_related('item'))

                if not configs:
                    continue

                total_weight = sum(c.ponderacion for c in configs)
                is_plan_sound = (total_weight == Decimal('100.00')) and all(c.meta_esperada > 0 for c in configs)

                if not is_plan_sound:
                    report['planes_pendientes_revision'] += 1

                for cfg in configs:
                    # Verificar si ya existe asignación individual previa
                    existing = AsignacionMeta.objects.filter(
                        funcionario=user, item=cfg.item, periodo=period
                    ).first()
                    if existing:
                        report['asignaciones_omitidas_existentes'] += 1
                        continue

                    report['asignaciones_propuestas'] += 1
                    obs = 'Propuesta generada desde plantilla de cargo' if is_plan_sound else f'Propuesta de plantilla (Pendiente de revisión: suma de ponderaciones {total_weight}% != 100%)'
                    
                    entry = {
                        'funcionario': user.username,
                        'delegacion': user.delegacion.codigo,
                        'periodo': period.codigo,
                        'item': cfg.item.codigo,
                        'cantidad_objetivo': str(cfg.meta_esperada),
                        'ponderacion': str(cfg.ponderacion),
                        'estado': is_plan_sound,
                        'observacion': obs,
                        'origen_configuracion_id': cfg.pk
                    }
                    report['detalles'].append(entry)

                    if options['apply']:
                        with transaction.atomic():
                            asig = AsignacionMeta.objects.create(
                                funcionario=user,
                                item=cfg.item,
                                periodo=period,
                                delegacion=user.delegacion,
                                cantidad_objetivo=cfg.meta_esperada,
                                ponderacion=cfg.ponderacion,
                                observacion=obs,
                                estado=is_plan_sound,
                                autor=actor,
                                snapshot={
                                    'origen_configuracion_id': cfg.pk,
                                    'meta_esperada_plantilla': str(cfg.meta_esperada),
                                    'ponderacion_plantilla': str(cfg.ponderacion),
                                    'cargo_id': user.cargo_id,
                                    'cargo_nombre': user.cargo.nombre,
                                    'procedencia': 'plantilla_cargo'
                                }
                            )
                            report['asignaciones_creadas'] += 1
                            EventoLocal.objects.create(
                                usuario=actor,
                                delegacion=user.delegacion,
                                recurso='asignaciones-metas',
                                registro=asig.pk,
                                accion='migrar_desde_plantilla',
                                despues=entry,
                                origen='comando_administrativo'
                            )

        self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder))

def models_q_periodo(period):
    from django.db.models import Q
    return Q(periodo_gestion=period) | Q(periodo=period.codigo)
