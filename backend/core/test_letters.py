"""Reglas del flujo de cartas con datos ficticios y sin almacenamiento remoto."""
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from .letter_models import Carta, validate_transition

class LetterRulesTests(SimpleTestCase):
    def test_explicit_transition(self):
        validate_transition('Ingresada','Derivada')
        with self.assertRaises(ValidationError):validate_transition('Ingresada','Finalizada')
    def test_terminal_locked(self):
        for state in ['Finalizada','No aplica']:
            with self.assertRaises(ValidationError):validate_transition(state,'En proceso')
    def test_closure_requires_result_and_date(self):
        c=Carta(estado='Finalizada')
        with self.assertRaises(ValidationError):c.clean()
    def test_code_generated(self):
        a,b=Carta(),Carta()
        self.assertTrue(a.codigo.startswith('CAR-'))
        self.assertNotEqual(a.codigo,b.codigo)

import uuid
from django.test import TestCase
from .models import Delegacion,Usuario,Rol
from .letter_models import Carta

class LetterAPITests(TestCase):
    def setUp(self):
        self.d=Delegacion.objects.create(nombre='Delegación ficticia cartas')
        self.role=Rol.objects.create(nombre='Funcionario cartas',permisos=['cartas.ver','cartas.crear','cartas.editar'])
        self.u=Usuario.objects.create_user(username='cartas_ficticio',delegacion=self.d,rol=self.role)
        self.other=Usuario.objects.create_user(username='otro_cartas',delegacion=self.d,rol=self.role)
        self.client.force_login(self.u)
    def send(self,url,data,method='post'):return getattr(self.client,method)(url,data,content_type='application/json')
    def create(self,**changes):
        d=dict(numero_carta='FICT-001',fecha='2026-01-01',remitente='Persona ficticia',destinatario='Oficina ficticia',materia='Ensayo ficticio',clave_idempotencia=uuid.uuid4().hex);d.update(changes)
        r=self.send('/api/cartas/',d);self.assertEqual(r.status_code,201,r.content);return r.json()['data'],d
    def test_default_owner_idempotency_and_immutable_code(self):
        c,data=self.create();self.assertEqual(c['responsable'],self.u.pk)
        r=self.send('/api/cartas/',data);self.assertEqual(r.status_code,200);self.assertTrue(r.json()['is_duplicate_prevented'])
        self.assertEqual(Carta.objects.count(),1)
        self.assertEqual(self.send(f'/api/cartas/{c["id"]}/',dict(_version=1,codigo='alterado'),'patch').status_code,400)
    def test_shared_read_owner_write_and_delegation_isolation(self):
        c,_=self.create();url=f'/api/cartas/{c["id"]}/';self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code,200)
        self.assertEqual(self.send(url,dict(_version=1,materia='Cambio'),'patch').status_code,403)
        self.other.delegacion=Delegacion.objects.create(nombre='Otra ficticia');self.other.save()
        self.assertEqual(self.client.get(url).status_code,404)
    def test_assignment_not_self_forbidden(self):
        r=self.send('/api/cartas/',dict(numero_carta='X',fecha='2026-01-01',remitente='A',destinatario='B',materia='C',responsable=self.other.pk,clave_idempotencia=uuid.uuid4().hex))
        self.assertEqual(r.status_code,400)
    def test_transition_closure_version_and_history(self):
        c,_=self.create();url=f'/api/cartas/{c["id"]}/'
        self.assertEqual(self.send(url+'estado/',dict(_version=1,estado='Finalizada')).status_code,400)
        r=self.send(url+'estado/',dict(_version=1,estado='En proceso'));self.assertEqual(r.status_code,200,r.content)
        self.assertEqual(self.send(url,dict(_version=1,materia='Stale'),'patch').status_code,409)
        self.assertEqual(self.send(url+'estado/',dict(_version=2,estado='Finalizada')).status_code,400)
        r=self.send(url+'estado/',dict(_version=2,estado='Finalizada',pronunciamiento='Resuelta en ensayo',fecha_cierre='2026-01-02'));self.assertEqual(r.status_code,200,r.content)
        self.assertEqual(self.send(url,dict(_version=3,materia='Cambio'),'patch').status_code,400)
        self.assertGreaterEqual(len(self.client.get(url).json()['data']['historial']),3)
    def test_bad_upload_without_storage(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        c,_=self.create()
        r=self.client.post(f'/api/cartas/{c["id"]}/documentos/',{'_version':'1','archivo':SimpleUploadedFile('falso.pdf',b'not pdf')})
        self.assertEqual(r.status_code,400)
    def test_private_upload_download_audit_and_foreign_scope(self):
        import tempfile
        from unittest.mock import patch
        from django.core.files.storage import FileSystemStorage
        from django.core.files.uploadedfile import SimpleUploadedFile
        from .letter_models import DocumentoCarta
        from .models import EventoLocal
        from io import BytesIO
        from pypdf import PdfWriter
        stream=BytesIO();writer=PdfWriter();writer.add_blank_page(width=200,height=200);writer.write(stream);pdf=stream.getvalue()
        c,_=self.create();url=f'/api/cartas/{c["id"]}/documentos/'
        with tempfile.TemporaryDirectory() as tmp,patch.object(DocumentoCarta._meta.get_field('archivo'),'storage',FileSystemStorage(location=tmp)):
            r=self.client.post(url,{'_version':'1','archivo':SimpleUploadedFile('ficticio.pdf',pdf)});self.assertEqual(r.status_code,200,r.content)
            doc=r.json()['data']['documentos'][0]
            self.assertNotIn('archivo',doc)
            download=self.client.get(doc['url']);self.assertEqual(download.status_code,200);self.assertTrue(b''.join(download.streaming_content).startswith(b'%PDF-'))
            self.assertTrue(EventoLocal.objects.filter(recurso='cartas',accion='descargar_documento',registro=c['id']).exists())
            self.assertEqual(self.client.post(url,{'_version':'1','archivo':SimpleUploadedFile('otro.pdf',pdf)}).status_code,409)
            self.u.delegacion=Delegacion.objects.create(nombre='Otra archivo ficticia');self.u.save()
            self.assertEqual(self.client.get(doc['url']).status_code,404)
    def test_manager_permission_assignment_reopening_and_reason(self):
        self.u.rol=Rol.objects.create(nombre='Delegado',permisos=['cartas.ver','cartas.crear','cartas.editar','cartas.gestionar','cartas.reasignar','cartas.reabrir']);self.u.save()
        c,_=self.create(responsable=self.other.pk);url=f'/api/cartas/{c["id"]}/'
        r=self.send(url+'estado/',dict(_version=1,estado='No aplica',pronunciamiento='Fuera de competencia',fecha_cierre='2026-01-02'));self.assertEqual(r.status_code,200,r.content)
        self.assertEqual(self.send(url+'reabrir/',dict(_version=2,motivo='')).status_code,400)
        r=self.send(url+'reabrir/',dict(_version=2,motivo='Corrección ficticia autorizada'));self.assertEqual(r.status_code,200,r.content)
        self.assertEqual(r.json()['data']['estado'],'En proceso');self.assertIsNone(r.json()['data']['fecha_cierre'])
        self.assertEqual(r.json()['data']['historial'][0]['datos']['motivo'],'Corrección ficticia autorizada')
