# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re

def validar_correo_electronico(correo):
    if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', correo):
        raise ValidationError('Correo electrónico no válido.')

def es_valido_caracteres_alfabeticos_con_espacios(cadena):
    if re.match('^([a-z ]+)+$', cadena.lower()):
        return True
    return False

class sigedat_wizard_agregar_contacto(models.TransientModel):
    _name = 'sigedat.wizard.agregar_contacto'
    _description = 'Sigedat - Wizard Agregar Contacto'

    # -------------------
    # Fields
    # -------------------

    tramite_id = fields.Many2one(
        string='Trámite',
        ondelete='cascade',
        comodel_name='sigedat.tramite',
        required=True,
        default=lambda self: self._context.get('tramite_id', False),
    )
    name = fields.Char(
        string='Nombre contacto',
        required=True,
    )
    correo_electronico = fields.Char(
        string='Correo electrónico',
        required=True,
    )

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            if not es_valido_caracteres_alfabeticos_con_espacios(self.name):
                raise ValidationError(f'El nombre: {self.name}, no es válido.')

    @api.onchange('correo_electronico')
    def _onchange_correo_electronico(self):
        if self.correo_electronico:
            validar_correo_electronico(self.correo_electronico)

    def agregar_contacto(self):
        if not self.tramite_id:
            raise ValidationError("Error en la comunicación con el trámite.")
        contacto_id = self.env['sigedat.tramite.contacto'].search([('correo_electronico', '=', self.correo_electronico)])
        if len(contacto_id) == 1:
            if self.tramite_id.contacto_ids.filtered(lambda c: c.correo_electronico == self.correo_electronico):
                raise ValidationError(f"El contacto con correo electrónico: {self.correo_electronico}, ya existe.")
            else:
                self.tramite_id.contacto_ids = [(4, contacto_id.id)]
        else:
            self.tramite_id.contacto_ids = [(0, 0,
                {
                    'name':self.name,
                    'correo_electronico':self.correo_electronico,
                }
            )]
