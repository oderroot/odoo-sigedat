# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError



class sigedat_wizard_agregar_persona(models.TransientModel):
    _name = 'sigedat.wizard.agregar_persona'
    _description = 'Sigedat - Wizard Agregar Persona'

    # -------------------
    # Fields
    # -------------------

    tramite_id = fields.Many2one(
        string='Trámite',
        comodel_name='sigedat.tramite',
        ondelete='cascade',
        default=lambda self: self._context.get('tramite_id', False),
    )
    grupo_id = fields.Many2one(
        string='Grupo',
        required=True,
        comodel_name='sigedat.grupo',
        domain="[('activo', '=', True)]",
    )
    persona_id = fields.Many2one(
        string='Persona',
        required=True,
        comodel_name='sigedat.persona',
        domain="[('tipo_persona', '=', 'natural'),('usuario_id', '!=', False)]",
    )

    def agregar_persona(self):
        if not self.tramite_id:
            raise ValidationError("Error en la comunicación con el trámite.")
        # INFO: Agrego a la persona al grupo interno relacionado
        self.sudo().grupo_id.grupo_id.users = [(4,self.persona_id.usuario_id.id)]
        equipo_id = self.tramite_id.equipo_apoyo_ids.filtered(lambda e: e.grupo_id.id == self.grupo_id.id)
        if not equipo_id:
            datos_equipo = {
                'persona_ids': [(4, self.persona_id.id)],
                'grupo_id': self.grupo_id.id,
            }
            self.tramite_id.equipo_apoyo_ids = [(0, 0, datos_equipo)]
        else:
            equipo_id.persona_ids = [(4, self.persona_id.id)]

