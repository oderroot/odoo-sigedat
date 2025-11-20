# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatPersonaTipoIdentificacion(models.Model):
    _name = 'sigedat.persona.tipo_identificacion'
    _description = 'Tipo de Identificacion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Tipo de Identificación',
        required=True,
        tracking=True,
    )
    aplica_a = fields.Selection(
        string='Aplica a',
        selection=[
            ('natural', 'Natural'),
            ('juridica', 'Juridica'),
        ],
        required=True,
        tracking=True,
    )
    
    _sql_constraints = [
        ('tipo_identificacion_no_repetido', 'unique(name)', 'Este tipo de identificacion ya se encuentra registrado en la base de datos.'),
    ]
    # -------------------
    # methods
    # -------------------

