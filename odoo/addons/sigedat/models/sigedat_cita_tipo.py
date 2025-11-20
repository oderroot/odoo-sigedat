# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatCitaTipo(models.Model):
    _name = 'sigedat.cita.tipo'
    _description = 'Tipo de Cita'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Tipo de Cita',
        required=True,
        tracking=True,
    )
    tipo_tramite_ids = fields.One2many(
        string='Tipo de trámite',
        required=True,
        comodel_name='sigedat.tramite.tipo',
        inverse_name='tipo_cita_id',
        tracking=True,
    )
    abreviatura = fields.Char(
        string='Abreviatura',
        required=True,
    )

    # -------------------
    # methods
    # -------------------

