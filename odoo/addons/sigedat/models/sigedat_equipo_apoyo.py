# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api

class SigedatEquipoApoyo(models.Model):
    _name = 'sigedat.equipo_apoyo'
    _description = 'Equipo de Apoyo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )
    persona_ids = fields.Many2many(
        string='Personas',
        required=True,
        comodel_name='sigedat.persona',
        tracking=True,
    )
    grupo_id = fields.Many2one(
        string='Grupo',
        required=True,
        comodel_name='sigedat.grupo',
        tracking=True,
    )
    tramite_id = fields.Many2one(
        string='Trámite',
        comodel_name='sigedat.tramite',
        ondelete='cascade',
        required=True,
        default=lambda self: self._context.get('tramite_id', False),
    )
    activo = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
    )

    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"Equipo: {r.grupo_id.name}"


    @api.model
    def create(self, vals):
        if not vals.get('tramite_id') or not vals.get('persona_ids'):
            self.clear_caches()
            return super(SigedatEquipoApoyo, self).create(vals)

        personas_ids = vals.get('persona_ids')
        equipo_apoyo = super(SigedatEquipoApoyo, self).create(vals)

        # Se elimmina porque este campo ya no se usa:
        # usuarios_apoyo = [p.usuario_id for p in self.env['sigedat.persona'].browse([personas_ids[0][1]])]
        # for s in equipo_apoyo.tramite_id.solicitud_ids:
        #     s.apoyos_ids = [(4,u.id) for u in usuarios_apoyo]

        return equipo_apoyo

