# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatDocumentoTipoExtension(models.Model):
    _name = 'sigedat.documento.tipo.extension'
    _description = 'Extension del Tipo de Documento'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )

    # -------------------
    # methods
    # -------------------

