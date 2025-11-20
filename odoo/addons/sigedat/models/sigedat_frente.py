# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatFrente(models.Model):
    _name = 'sigedat.frente'
    _description = 'Frente'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    contrato_id = fields.Many2one(
        string='Acuerdo',
        required=True,
        comodel_name='sigedat.contrato',
        default=lambda self: self._context.get('contrato_id', False),
        tracking=True,
    )
    ubicacion = fields.Char(
        string='Descripción de la ubicación del frente',
        tracking=True,
    )


    # -------------------
    # methods
    # -------------------

