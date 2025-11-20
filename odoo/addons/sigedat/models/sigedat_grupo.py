# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatGrupo(models.Model):
    _name = 'sigedat.grupo'
    _description = 'Grupo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    activo = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
    )
    grupo_id = fields.Many2one(
        string='Grupo Interno',
        comodel_name='res.groups',
        ondelete='cascade',
        required=True,
        domain="[('full_name', 'like', 'sigedat')]",
        tracking=True,
    )
    
    
    # -------------------
    # methods
    # -------------------

