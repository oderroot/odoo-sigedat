# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re

def es_valido_correo_electronico(correo):
    if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', correo):
        return False
    else:
        return True

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
        readonly=True,
    )
    grupo_id = fields.Many2one(
        string='Grupo',
        required=True,
        comodel_name='sigedat.grupo',
        domain="[('activo', '=', True)]",
    )
    correo_electronico = fields.Char(
        string='Correo electrónico',
        required=True,
    )
    persona_id = fields.Many2one(
        string='Persona',
        required=True,
        comodel_name='sigedat.persona',
    )
    mensaje = fields.Char(
        string='Mensaje',
    )


    @api.onchange('correo_electronico')
    def _onchange_correo_electronico(self):
        if self.correo_electronico:
            if not es_valido_correo_electronico(self.correo_electronico):
                raise ValidationError(f"La dirección de correo electrónico ingresado, no es válido, por favor verifiquela.")
            persona_reg = self.env['sigedat.persona'].search([('correo_electronico', '=', self.correo_electronico)])
            if persona_reg.usuario_id.id == self.env.uid:
                raise ValidationError(f"No es posible que ud mismo se agregue como parte del equipo de apoyo.")
            if not persona_reg:
                # self.correo_electronico = ''
                raise ValidationError(f'Usuario no encontrado, debe registrarse primero.')
            else:
                if len(persona_reg) > 1:
                    raise ValidationError(f"Hay: {len(persona_reg)} personas con la misma dirección de correo electrónico: {persona_reg.correo_electronico}, lo cual es un error, por favor verifique el listado de personas registradas en el sistema y haga los ajustes necesarios.")
                self.mensaje = f"El correo electrónico: {self.correo_electronico}, esta relacionada con la persona: {persona_reg.name}"
                self.persona_id = persona_reg.id


    def agregar_persona(self):
        if not self.grupo_id or not self.persona_id or not self.correo_electronico:
            raise ValidationError("No están los datos completos, para agregar a la persona, por favor verifiquelos.")
        if not self.tramite_id:
            raise ValidationError("Error en la comunicación con el trámite.")
        # INFO: Agrego a la persona al grupo interno relacionado
        if not self.persona_id.usuario_id:
            raise ValidationError(f"La persona indicada: {self.persona_id}, no tiene un usuario válido para iniciar sesión en el sistema.")
        self.sudo().grupo_id.grupo_id.users = [(4, self.persona_id.usuario_id.id)]
        equipo_id = self.tramite_id.equipo_apoyo_ids.filtered(lambda e: e.grupo_id.id == self.grupo_id.id)
        if not equipo_id:
            datos_equipo = {
                'persona_ids': [(4, self.persona_id.id)],
                'grupo_id': self.grupo_id.id,
            }
            self.tramite_id.equipo_apoyo_ids = [(0, 0, datos_equipo)]
        else:
            equipo_id.persona_ids = [(4, self.persona_id.id)]

