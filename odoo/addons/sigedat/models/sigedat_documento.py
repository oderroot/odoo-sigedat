# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)



LISTA_EXTENSIONES_ARCHIVOS_IMAGEN_SOPORTADOS = ['jpg', 'jpeg', 'png']

class SigedatDocumento(models.Model):
    _name = 'sigedat.documento'
    _description = 'Documento'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'orden ASC'

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )
    tipo_id = fields.Many2one(
        string='Tipo de Documento',
        comodel_name='sigedat.documento.tipo',
        ondelete='cascade',
        required=True,
        tracking=True,
        domain="[('activo', '=', True)]",
        default=lambda self: self._context.get('tipo_id', False),
    )
    ruta_carpeta = fields.Char(
        string='Carpeta',
        compute='_compute_ruta_carpeta'
    )
    carpeta_id = fields.Many2one(
        string='Carpeta',
        comodel_name='sigedat.carpeta',
        ondelete='cascade',
    )
    obligatorio = fields.Boolean(
        string='Obligatorio',
        related='tipo_id.obligatorio',
    )
    archivo = fields.Binary(
        string='Documento',
        attachment = True,
        tracking=True,
    )
    archivo_nombre = fields.Char(
        string='Documento',
        tracking=True,
    )
    solicitud_tramite_id = fields.Many2one(
        string='Solicitud de trámite',
        comodel_name='sigedat.tramite.solicitud',
        tracking=True,
        ondelete='cascade',
        default=lambda self: self._context.get('solicitud_tramite_id', False),
    )
    state = fields.Selection(
        related='solicitud_tramite_id.state'
    )
    tipo_documento = fields.Selection(
        string='Tipo de documento',
        selection=[
            ('imagen', 'Imagen'),
            ('pdf', 'PDF'),
            ('otro', 'Otro'),
        ],
        compute='_compute_tipo_documento',
    )
    imagen = fields.Binary(
        string='Imagen',
        related='archivo'
    )
    pdf = fields.Binary(
        string='pdf',
        related='archivo'
    )
    otro = fields.Binary(
        string='otro',
        related='archivo'
    )
    orden = fields.Integer(
        string='Orden',
        required=False
    )

    # -------------------
    # methods
    # -------------------

    @api.model
    def create(self, values):
        result = super(SigedatDocumento, self).create(values)
        try:
            orden = result.carpeta_id.name.split('.')[0]
            if orden.isdigit():
                result.orden = orden
            else:
                raise ValidationError(f'El nombre de la carpeta ({result.carpeta_id.name}) debe iniciar con un número.')
        except ValidationError as e:
            _logger.warning('No fué posible asignar orden: {}'.format(e))
        return result



    def unlink(self):
        usuario_es_externo = self.env.user.has_group('sigedat.usuario_externo')
        if usuario_es_externo:
            # raise ValidationError('Un usuario con rol de externo no puede eliminar registros de documentos.')
            # Ahora el externo si puede eliminar, únicamente en los documenbtos one2many siempre que quede por lo menos un documento
            tramite = self[0].solicitud_tramite_id
            docs_por_tipo = {}
            permitido = True
            for doc in self:
                tipo = doc.tipo_id
                if tipo not in docs_por_tipo:
                    docs_por_tipo[tipo] = [doc]
                else:
                    docs_por_tipo[tipo].append(doc)

            for tipo, docs in docs_por_tipo.items():
                documentos_del_mismo_tipo = tramite.documento_ids.filtered(lambda d: d.tipo_id == tipo)
                if len(docs) >= len(documentos_del_mismo_tipo):
                    permitido = False

            if permitido:
                return super(SigedatDocumento, doc).unlink()
            else:
                raise ValidationError('Un usuario con rol de externo no puede eliminar todos los documentos del mismo tipo.')

        return super(SigedatDocumento, self).unlink()



    def _compute_tipo_documento(self):
        for r in self:
            if r.archivo:
                if r.archivo_nombre.lower().endswith('pdf'):
                    r.tipo_documento = 'pdf'
                elif r.archivo_nombre.lower().split('.')[-1] in LISTA_EXTENSIONES_ARCHIVOS_IMAGEN_SOPORTADOS:
                    r.tipo_documento = 'imagen'
                else:
                    r.tipo_documento = 'otro'
            else:
                r.tipo_documento = ''


    def _compute_ruta_carpeta(self):
        for r in self:
            nombre_carpeta = ' '
            c = r.carpeta_id
            while  True:
                nombre_carpeta = f"{c.name}/{nombre_carpeta}"
                if c.carpeta_padre_id:
                    c = c.carpeta_padre_id
                else:
                    break
            r.ruta_carpeta = nombre_carpeta


    def _compute_name(self):
        for r in self:
            r.name = f"{r.tipo_id.name} - {r.id}"


    def previsualizar_documento(self):
        return {
            'name': 'Documento',
            'res_model': 'sigedat.documento',
            'res_id': self.id,
            'context': {},
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
        }
