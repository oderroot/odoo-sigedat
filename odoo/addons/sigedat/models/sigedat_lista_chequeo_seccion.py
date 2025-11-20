# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatListaChequeoSeccion(models.Model):
    _name = 'sigedat.lista_chequeo.seccion'
    _description = 'Sección de la Lista de Chequeo'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

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
        tracking=True,
        default=True,
    )
    abreviatura = fields.Char(
        string='Abreviatura',
        required=True,
    )

    # -------------------
    # methods
    # -------------------