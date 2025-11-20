# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO

class SigedatTramiteTipo(models.Model):
    _name = 'sigedat.tramite.tipo'
    _description = 'Tipo de trámite'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name ASC'


    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        required=True,
        tracking=True,
    )
    bloque_atencion_ids = fields.One2many(
        string='Bloque de atención',
        required=True,
        comodel_name='sigedat.tramite.tipo.bloque_atencion',
        inverse_name='tipo_tramite_id',
        tracking=True,
    )
    revisor_ids = fields.Many2many(
        string='Revisores',
        required=True,
        comodel_name='sigedat.revisor',
        compute='_compute_revisor'
    )
    tipo_cita_id = fields.Many2one(
        string='Tipo de Cita',
        required=True,
        comodel_name='sigedat.cita.tipo',
        tracking=True,
    )
    abreviatura = fields.Char(
        string='Abreviatura',
        required=True,
    )

    # -------------------
    # methods
    # -------------------

    @api.depends('bloque_atencion_ids')
    def _compute_revisor(self):
        revisor_ids = []
        for r in self:
            revisor_ids = [r.id for r in r.bloque_atencion_ids.mapped('revisor_ids')]
            r.revisor_ids = [(6, 0, revisor_ids)]

