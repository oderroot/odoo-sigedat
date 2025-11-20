# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError

EXTENSIONES_IMAGENES = ['jpg', 'png', 'gif', 'jpeg',]


class SigedatListaChequeoItemObservacion(models.Model):
    _name = 'sigedat.lista_chequeo.item.observacion'
    _description = 'Observación del Item'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=False,
        compute='_compute_name',
    )
    observacion = fields.Text(
        string='Observación',
        required=True,
        tracking=True,
    )
    # soporte_ids = fields.One2many(
    #     string='Soportes',
    #     required=False,
    #     comodel_name='sigedat.lista_chequeo.item.observacion.soporte',
    #     inverse_name='item_observacion_id',
    #     tracking=True,
    # )
    # soporte_id = fields.Many2one(
    #     string='Soporte',
    #     required=False,
    #     comodel_name='sigedat.lista_chequeo.item.observacion.soporte',
    #     tracking=True,
    # )
    archivo = fields.Binary(
        string='Archivo',
        required=False,
        attachment = True,
        tracking=True,
    )
    archivo_nombre = fields.Char(
        string='Nombre Archivo',
        tracking=True,
    )
    item_id = fields.Many2one(
        string='Items Relacionados',
        required=False,
        comodel_name='sigedat.lista_chequeo.item',
        tracking=True,
    )
    cumple = fields.Selection(
        related='item_id.cumple',
    )
    observacion_ids = fields.Many2many(
        string='Observaciones Relacionadas',
        required=False,
        comodel_name='sigedat.lista_chequeo.item.observacion',
        relation='observacion_relacion',
        column1='obs_id',
        column2='obs_rel_id',
        tracking=True,
        # domain=lambda self: self._get_dominio_observaciones(),
    )
    # en_proceso_relacion = fields.Boolean(
    #     string='En proceso de relación', 
    #     default=False,
    #     help='Indica si la observación está en proceso de relacionar con otras observaciones'
    # )


    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"Observación: {r.id}"


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


    # # metodo create para validar que el registro de observación tenga archivo, si no tiene archivo debe estar relacionada a un registro de observación que si tenga archivo
    # @api.model
    # def create(self, vals):
    #     # Verificar si se está creando sin archivo
    #     if not vals.get('archivo'):
    #         # Obtener las observaciones relacionadas según el formato de Many2many
    #         observacion_ids = vals.get('observacion_ids', [])
            
    #         # Procesar los comandos de Many2many (pueden venir como [(6, 0, [ids])] o [(4, id)])
    #         ids_relacionadas = []
    #         for comando in observacion_ids:
    #             if isinstance(comando, (list, tuple)) and len(comando) >= 2:
    #                 if comando[0] == 6:  # Comando (6, 0, [ids]) - replace
    #                     ids_relacionadas.extend(comando[2] if comando[2] else [])
    #                 elif comando[0] == 4:  # Comando (4, id) - link
    #                     ids_relacionadas.append(comando[1])
            
    #         # Si hay observaciones relacionadas, verificar que al menos una tenga archivo
    #         if ids_relacionadas:
    #             observaciones_relacionadas = self.env['sigedat.lista_chequeo.item.observacion'].browse(ids_relacionadas)
    #             if not any(obs.archivo for obs in observaciones_relacionadas):
    #                 raise ValidationError(
    #                     "Hay una o más observaciones sin imagen y sin relación a una observación existente que tenga imagen."
    #                 )
    #         else:
    #             # Si no tiene archivo ni observaciones relacionadas, es inválido
    #             raise ValidationError(
    #                 "Hay una o más observaciones sin imagen y sin relación a una observación existente que tenga imagen."
    #             )
        
    #     return super(SigedatListaChequeoItemObservacion, self).create(vals)



    # @api.depends('item_id')
    # def _get_dominio_observaciones(self):
    #     dominio = []
    #     tramite_id = self.env.context.get('tramite_id', False)
    #     solicitud_id = self.env.context.get('solicitud_tramite_id', False)
    #     if not solicitud_id:
    #         if self.item_id:
    #             solicitud_id = self.item_id.solicitud_tramite_id.id
    #     if solicitud_id:
    #         dominio = [('item_id.solicitud_tramite_id', '=', solicitud_id)]
    #     elif tramite_id:
    #         dominio = [('item_id.solicitud_tramite_id.tramite_id', '=', tramite_id)]
        
    #     #         item_ids = solicitud_id.lista_item_ids.ids
    #     #         dominio = [('item_id', 'in', item_ids)]
    #     #         observaciones_ids = [i.observacion_ids.ids for i in self.env['sigedat.tramite.solicitud'].browse(solicitud_id.id)[0].lista_item_ids if i.observacion_ids]
    #     #         observaciones_ids_plana = []
    #     #         for elemento in observaciones_ids:
    #     #             if isinstance(elemento, list):
    #     #                 observaciones_ids_plana.extend(elemento)
    #     #             else:
    #     #                 observaciones_ids_plana.append(elemento)
                
    #     #         # Retornar el dominio para las observaciones relacionadas
    #     #         dominio = [('id', 'in', observaciones_ids_plana)]
    #     if dominio:
    #         return dominio
    #     else:
    #         return [('id', '=', 55)]
