# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO

class SigedatListaChequeo(models.Model):
    _name = 'sigedat.lista_chequeo'
    _description = 'Lista de Chequeo'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    seccion_id = fields.Many2one(
        string='Sección',
        comodel_name='sigedat.lista_chequeo.seccion',
        ondelete='cascade',
        required=True,
        tracking=True,
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
    aplica_a_especial = fields.Selection(
        string='¿El trámite es especial?',
        selection=LISTA_SI_NO,
        required=True,
        default='no',
        tracking=True,
    )
    permitido_entrega_posterior = fields.Boolean(
        string='Se permite la entrega posteriormente',
        default=False,
    )
    se_toma_tramite_anterior = fields.Boolean(
        string='Se toma del trámite anterior',
        default=False,
    )

    # -------------------
    # methods
    # -------------------

