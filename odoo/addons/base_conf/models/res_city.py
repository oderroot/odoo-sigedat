# -*- encoding: utf-8 -*-

from odoo import models, fields, api

# TODO La localidad no tiene relacion con la ciudad a la que pertenece
class BaseLocalidad(models.Model):
    _name = 'base.localidad'
    _description = 'Localidad'
    _inherit = ['models.soft_delete.mixin']

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    codigo = fields.Char(
        string='Código',
        required=True,
        size=30,
    )
    _sql_constraints = [
        ('unique_localidad', 'unique(name)', 'Esta localidad ya está registrada'),
    ]

    @api.model
    def create(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        return super(BaseLocalidad, self).create(vals)

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        return super(BaseLocalidad, self).write(vals)

class BaseBarrio(models.Model):
    _name = 'base.barrio'
    _description = 'Barrio'
    _inherit = ['models.soft_delete.mixin']

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    codigo = fields.Char(
        string='Código',
        size=30,
    )
    localidad_id = fields.Many2one(
        'base.localidad',
        string='Localidad',
        required=True,
    )
    _sql_constraints = [
        ('unique_barrio', 'unique(name, localidad_id, active)', 'Este barrio ya está registrado'),
    ]

    @api.model
    def create(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        return super(BaseBarrio, self).create(vals)

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        return super(BaseBarrio, self).write(vals)