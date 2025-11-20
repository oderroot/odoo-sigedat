# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatContratoTipo(models.Model):
    _name = 'sigedat.contrato.tipo'
    _description = 'Tipo de Contrato'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    abreviatura = fields.Char(
        string='Abreviatura',
        required=True,
        tracking=True,
    )
    informacion_viene_desde_sap = fields.Boolean(
        string='¿La información viene desde SAP',
    )

    # -------------------
    # methods
    # -------------------

