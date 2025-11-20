# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class SigedatRevisorNoDisponibilidad(models.Model):
    _name = 'sigedat.revisor.no_disponibilidad'
    _description = 'No Disponibilidad del Revisor'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )
    fecha_inicio = fields.Date(
        string='Fecha Inicio',
        required=True,
        tracking=True,
    )
    fecha_fin = fields.Date(
        string='Fecha Fin',
        required=True,
        tracking=True,
    )
    revisor_id = fields.Many2one(
        string='Revisor',
        required=True,
        comodel_name='sigedat.revisor',
        ondelete='cascade',
        default=lambda self: self.env.context.get('revisor_id', False),
    )

    _sql_constraints = [
        ('fecha_valida', 'check(fecha_inicio <= fecha_fin)', 'No es posible, que la fecha de inicio, sea mayor que la fecha fin'),
    ]

    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"No disponibilidad: {r.id}"

    @api.onchange('fecha_inicio')
    def _onchange_fecha_inicio(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio >= self.fecha_fin:
                raise ValidationError(f'{self.fecha_inicio}, no puede ser mayor que la fecha fin: {self.fecha_fin}.')

    @api.onchange('fecha_fin')
    def _onchange_fecha_fin(self):
        if self.fecha_fin and self.fecha_fin:
            if self.fecha_fin <= self.fecha_inicio:
                raise ValidationError(f'{self.fecha_inicio}, no puede ser mayor que la fecha fin: {self.fecha_fin}.')