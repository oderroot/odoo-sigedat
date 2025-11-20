# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO

class SigedatCarpeta(models.Model):
    _name = 'sigedat.carpeta'
    _description = 'Carpeta'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    sequence = fields.Integer(
        string='sequence',
    )
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    carpeta_padre_id = fields.Many2one(
        string='Carpeta Padre',
        required=False,
        comodel_name='sigedat.carpeta',
        tracking=True,
        domain="[('activo', '=', True)]",
    )
    tipo_tramite_id = fields.Many2one(
        string='Tipo de trámite',
        required=True,
        comodel_name='sigedat.tramite.tipo',
        tracking=True,
    )
    activo = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
    )
    tipo_documento_ids = fields.Many2many(
        string='Tipo de Documento',
        required=False,
        comodel_name='sigedat.documento.tipo',
        tracking=True,
        domain="[('activo', '=', True)]",
    )
    aplica_a_especial = fields.Selection(
        string='¿El trámite es especial?',
        selection=LISTA_SI_NO,
        required=True,
        default='no',
        tracking=True,
    )

    # -------------------
    # methods
    # -------------------

