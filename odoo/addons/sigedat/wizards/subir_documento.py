# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

LISTA_SI_NO = [('si', 'Si'),('no', 'No')]

class sigedat_wizard_documento(models.TransientModel):
    _name = 'sigedat.wizard.documento'
    _description = 'Sigedat - Wizard Documento'

    tipo_id = fields.Many2one(
        string='Tipo de Documento',
        comodel_name='sigedat.documento.tipo',
        ondelete='cascade',
        domain="[('activo', '=', True)]",
        default=lambda self: self._context.get('tipo_id', False),
    )
    archivo = fields.Binary(
        string='Documento',
        attachment = True,
    )
    archivo_nombre = fields.Char(
        string='Documento',
    )
    subir_archivo_id = fields.Many2one(
        string='Subir Archivo',
        comodel_name='sigedat.wizard.subir_documento',
        ondelete='cascade',
    )


    @api.onchange('archivo')
    def _onchange_archivo(self):
        for r in self:
            extensiones_permitidas = r.tipo_id.extension_ids.mapped('name')
            if r.archivo and r.archivo_nombre:
                if extensiones_permitidas and not r.archivo_nombre.lower().split('.')[-1] in extensiones_permitidas:
                    #INFO Debido a que no se cumple con los tipos de archivos permitidos, no dejo cargar el archivo
                    nombre_archivo = r.archivo_nombre
                    r.archivo = None
                    r.archivo_nombre = ''

                    raise ValidationError(f"El archivo cargado: {nombre_archivo}, no cumple con las extensiones permitidas: {extensiones_permitidas} para el tipo de documento: {r.tipo_id.name}")



class sigedat_wizard_subir_documento(models.TransientModel):
    _name = 'sigedat.wizard.subir_documento'
    _description = 'Sigedat - Wizard Subir Documento'

    # -------------------
    # Fields
    # -------------------

    def _domain_documento(self):
        id_documento = self.env.context.get('documento_id', None)
        id_solicitud = self.env.context.get('solicitud_id', None)
        documento_id = self.env['sigedat.documento'].browse(id_documento)
        id_tipo_documento = documento_id.tipo_id.id
        documento_ids = self.env['sigedat.documento'].search([('tipo_id', '=', id_tipo_documento),('solicitud_tramite_id', '=', id_solicitud)])
        return [('id','in',documento_ids.ids)]

    solicitud_id = fields.Many2one(
        string='Solicitud',
        comodel_name='sigedat.tramite.solicitud',
        ondelete='restrict',
        default=lambda self: self._context.get('solicitud_id', False),
    )
    documento_id = fields.Many2one(
        string='Documento',
        comodel_name='sigedat.documento',
        ondelete='restrict',
        default=lambda self: self._context.get('documento_id', False),
    )
    tipo_documento_id = fields.Many2one(
        string='Tipo documento',
        comodel_name='sigedat.documento.tipo',
        ondelete='cascade',
        related='documento_id.tipo_id'
    )
    cantidad = fields.Selection(
        string='¿Cuantos archivos puede cargar?',
        related='tipo_documento_id.cantidad',
    )
    se_esta_editando_archivo = fields.Boolean(
        default=lambda self: self._context.get('se_esta_editando_archivo', False),
    )
    archivo = fields.Binary(
        string='Documento',
    )
    archivo_nombre = fields.Char(
    )
    descripcion = fields.Text(
        string='Descripción',
        related='tipo_documento_id.descripcion'
    )
    documento_ids = fields.One2many(
        string='Documento',
        comodel_name='sigedat.wizard.documento',
        inverse_name='subir_archivo_id',
    )
    mensaje = fields.Text(
        string='Mensaje',
    )


    @api.onchange('archivo')
    def _onchange_archivo(self):
        for r in self:
            extensiones_permitidas = r.tipo_documento_id.extension_ids.mapped('name')
            r.mensaje = f"Sr usuario, recuerde que el tipo documental: {r.tipo_documento_id.name}, "
            r.mensaje += f"solo admite las extensiones: {extensiones_permitidas}" if extensiones_permitidas else "admite cualquier tipo de archivo."
            if r.archivo and r.documento_id:
                if extensiones_permitidas and not r.archivo_nombre.lower().split('.')[-1] in extensiones_permitidas:
                    #INFO Debido a que no se cumple con los tipos de archivos permitidos, no dejo cargar el archivo
                    nombre_archivo = r.archivo_nombre
                    r.archivo = None
                    r.archivo_nombre = ''

                    raise ValidationError(f"El archivo cargado: {nombre_archivo}, no cumple con las extensiones permitidas: {extensiones_permitidas} para el tipo de documento: {r.tipo_documento_id.name}")



    def subir_archivo(self):
        if not self.documento_id:
            raise ValidationError('No se tiene la referencia al documento.')
        #INFO Si todo esta correcto con el archivo, lo agrego al registro
        if self.se_esta_editando_archivo or self.cantidad == 'uno':
            if not self.archivo:
                raise ValidationError("No fue cargado el archivo, por favor verifique.")
            self.documento_id.write(
                {
                    'archivo': self.archivo,
                    'archivo_nombre': self.archivo_nombre,
                    'carpeta_id': self.documento_id.carpeta_id.id,
                }
            )
        else:
            if not self.documento_ids:
                raise ValidationError("No fue cargado el archivo, por favor verifique.")
            if len(self.documento_ids) > 1:
                self.documento_id.write(
                    {
                        'archivo': self.documento_ids[0].archivo,
                        'archivo_nombre': self.documento_ids[0].archivo_nombre,
                        'carpeta_id': self.documento_id.carpeta_id.id,
                    }
                )
                for d in self.documento_ids[1:]:
                    self.solicitud_id.documento_ids = [(0, 0, {
                        'solicitud_tramite_id': self.solicitud_id.id,
                        'tipo_id': self.tipo_documento_id.id,
                        'archivo': d.archivo,
                        'archivo_nombre': d.archivo_nombre,
                        'carpeta_id': self.documento_id.carpeta_id.id,
                        'orden': self.documento_id.orden,
                    })]
            else:
                self.documento_id.write(
                    {
                        'archivo': self.documento_ids[0].archivo,
                        'archivo_nombre': self.documento_ids[0].archivo_nombre,
                        'carpeta_id': self.documento_id.carpeta_id.id,
                    }
                )
