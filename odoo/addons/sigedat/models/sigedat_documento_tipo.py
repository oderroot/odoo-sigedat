# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO


class SigedatDocumentoTipo(models.Model):
    _name = 'sigedat.documento.tipo'
    _description = 'Tipo de Documento'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(
        string='sequence',
    )
    descripcion = fields.Text(
        string='Descripción',
        tracking=True,
    )
    activo = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
    )
    obligatorio = fields.Boolean(
        string='Obligatorio',
        tracking=True,
    )
    cantidad = fields.Selection(
        string='Cantidad',
        selection=[
            ('uno', 'Uno'),
            ('varios', 'Varios'),
        ],
        tracking=True,
        required=True,
    )
    extension_ids = fields.Many2many(
        string='Extensiones',
        required=True,
        comodel_name='sigedat.documento.tipo.extension',
        tracking=True,
    )

    # -------------------
    # methods
    # -------------------

