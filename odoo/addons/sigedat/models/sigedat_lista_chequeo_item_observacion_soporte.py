# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError

EXTENSIONES_IMAGENES = ['jpg', 'png', 'gif', 'jpeg',]

class SigedatListaChequeoItemObservacionSoporte(models.Model):
    _name = 'sigedat.lista_chequeo.item.observacion.soporte'
    _description = 'Soporte de la Observación'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=False,
        compute='_compute_name',
    )
    archivo = fields.Binary(
        string='Archivo',
        required=True,
        attachment = True,
        tracking=True,
    )
    archivo_nombre = fields.Char(
        string='Nombre Archivo',
        tracking=True,
    )
    item_observacion_id = fields.Many2one(
        string='Item Observación',
        comodel_name='sigedat.lista_chequeo.item.observacion',
        default=lambda self: self._context.get('item_observacion_id', False),
        tracking=True,
    )

    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"Soporte: {r.id}"

    @api.onchange('archivo')
    def _onchange_archivo(self):
        for r in self:
            extensiones_permitidas = EXTENSIONES_IMAGENES
            # r.mensaje = f"Sr usuario, recuerde que el tipo documental: {r.tipo_documento_id.name}, "
            # r.mensaje += f"solo admite las extensiones: {extensiones_permitidas}" if extensiones_permitidas else "admite cualquier tipo de archivo."
            if r.archivo:
                if extensiones_permitidas and not r.archivo_nombre.split('.')[-1].lower() in extensiones_permitidas:
                    #INFO Debido a que no se cumple con los tipos de archivos permitidos, no dejo cargar el archivo
                    nombre_archivo = r.archivo_nombre
                    r.archivo = None
                    r.archivo_nombre = ''

                    raise ValidationError(f"El archivo cargado: {nombre_archivo}, no cumple con las extensiones permitidas: {extensiones_permitidas} para los soportes de las observaciones.")


