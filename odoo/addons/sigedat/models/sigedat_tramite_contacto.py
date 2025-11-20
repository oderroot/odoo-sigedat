# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatTramiteContacto(models.Model):
    _name = 'sigedat.tramite.contacto'
    _description = 'Contacto del trámite'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    correo_electronico = fields.Char(
        string='Correo electrónico',
        required=True,
        tracking=True,
    )

    # -------------------
    # methods
    # -------------------

