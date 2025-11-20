# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatArea(models.Model):
    _name = 'sigedat.area'
    _description = 'Area'
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

    # -------------------
    # methods
    # -------------------

