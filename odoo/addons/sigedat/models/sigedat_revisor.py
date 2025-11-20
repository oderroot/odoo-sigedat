# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatRevisor(models.Model):
    _name = 'sigedat.revisor'
    _description = 'Revisor'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    def _domain_revisor(self):
        revisor_ids = self.env.ref('sigedat.revisor').users
        return [('id','in',revisor_ids.ids)]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=False,
        compute='_compute_name',
    )
    persona_id = fields.Many2one(
        string='Revisor',
        required=True,
        comodel_name='res.users',
        domain=_domain_revisor,
        tracking=True,
    )
    no_disponibilidad_ids = fields.One2many(
        string='No Disponibilidad',
        required=False,
        comodel_name='sigedat.revisor.no_disponibilidad',
        inverse_name='revisor_id',
        tracking=True,
    )
    tipo_cita_id = fields.Many2one(
        string='Tipo de Cita',
        required=True,
        comodel_name='sigedat.cita.tipo',
        tracking=True,
    )



    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"{r.persona_id.name}"

