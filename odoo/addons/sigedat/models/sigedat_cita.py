# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from datetime import datetime
from base64 import b64encode
from odoo.exceptions import UserError
from odoo.addons.base_conf.tools.mail import enviar_mensaje_con_plantilla

class SigedatCita(models.Model):
    _name = 'sigedat.cita'
    _description = 'Cita'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Número de cita',
        compute='_compute_name',
    )
    fecha_inicio = fields.Datetime(
        string='Fecha Inicio',
        required=True,
        tracking=True,
    )
    fecha_fin = fields.Datetime(
        string='Fecha Fin',
        required=True,
        tracking=True,
    )
    tipo_id = fields.Many2one(
        string='Tipo de Cita',
        required=True,
        comodel_name='sigedat.cita.tipo',
        tracking=True,
    )
    solicitud_tramite_id = fields.Many2one(
        string='Solicitud de trámite',
        comodel_name='sigedat.tramite.solicitud',
        tracking=True,
        required=True,
        default=lambda self: self._context.get('solicitud_tramite_id', False),
        ondelete='cascade',
    )
    tramite_id = fields.Many2one(
        related='solicitud_tramite_id.tramite_id',
    )
    aviso_sap = fields.Char(
        string='Aviso Sap',
        tracking=True,
    )
    state = fields.Selection(
        string='Estado',
        selection=[
            ('agendada', 'Agendada'),
            ('atendida', 'Atendida'),
            ('cancelada', 'Cancelada'),
        ],
        default='agendada',
        tracking=True,
    )
    revisor_id = fields.Many2one(
        string='Revisor Asignado',
        comodel_name='sigedat.revisor',
        ondelete='cascade',
        tracking=True,
    )
    es_visible_registro = fields.Boolean(
        string='Es registro visible',
        compute='_compute_es_visible_registro',
    )
    mensaje_confirmacion_cita = fields.Text(
        string='Mensaje de confirmacion',
        tracking=True,
    )

    _sql_constraints = [
        ('aviso_sap_no_repetido', 'unique(aviso_sap)', 'Este número de aviso sap, ya esta registrado.'),
    ]

    # -------------------
    # methods
    # -------------------
    def _compute_name(self):
        for r in self:
            r.name = f"Cita: {r.id}"


    # envío de notificación al crear una cita a través de la solicitud de trámite
    @api.model
    def create(self, vals):
        res = super(SigedatCita, self).create(vals)
        solicitud_tramite = res.solicitud_tramite_id
        if solicitud_tramite:
            solicitud_tramite.enviar_notificacion_cita(res.id, res.fecha_inicio)

        return res


    def _compute_es_visible_registro(self):
        #INFO Si el usuario logeado es externo, solo puede ver los registros creados por el mismo
        es_externo = self.env.user.has_group('sigedat.externo')
        usuario_actual_id = self.env.uid
        for r in self:
            if r.create_uid == usuario_actual_id and es_externo:
                r.es_visible_registro = True
            else:
                r.es_visible_registro = False


    @api.onchange('fecha_inicio')
    def _onchange_fecha_inicio(self):
        hoy = datetime.now()
        if self.fecha_inicio and self.fecha_inicio < hoy:
            self.fecha_inicio = None
            return {
                'warning': {
                    'title': 'Error',
                    'message': 'La fecha de inicio no puede se menor a la fecha actual.'
                }
            }


    @api.onchange('fecha_fin')
    def _onchange_fecha_fin(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            self.fecha_fin = None
            return {
                'warning': {
                    'title': 'Error',
                    'message': 'La fecha fin no puede se menor a la fecha de inicio.'
                }
            }


    def _cron_citas_diarias(self):
        plantilla = self.env.ref('sigedat.plantilla_citas_dia')
        ctx = self.env.context.copy()
        enviar_mensaje_con_plantilla(
                objeto=self.env['sigedat.cita'],
                contexto=ctx,
                plantilla=plantilla,
                )



