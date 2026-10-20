from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from core.models import Usuario
from core.area_items import configure


class Command(BaseCommand):
    help = 'Previsualiza o aplica las asociaciones de ítems a las doce áreas documentadas.'

    def add_arguments(self, parser):
        parser.add_argument('--usuario', required=True, help='Administrador activo responsable de la operación')
        parser.add_argument('--aplicar', action='store_true', help='Guardar; sin esta opción solo revisa')

    def handle(self, *args, **options):
        try:
            user = Usuario.objects.get(username=options['usuario'], is_active=True, is_superuser=True)
            request = RequestFactory().post('/aprovisionamiento/items-areas/')
            request.user = user; request.session = {}
            result = configure(request, apply=options['aplicar'])
        except (Usuario.DoesNotExist, ValidationError) as error:
            raise CommandError(str(error))
        self.stdout.write(str(result))
