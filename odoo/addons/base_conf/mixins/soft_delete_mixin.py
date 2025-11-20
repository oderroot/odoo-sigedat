# -*- coding: utf-8 -*-

from odoo import models, fields, api


class soft_delete_mixin(models.AbstractModel):
    _name = 'models.soft_delete.mixin'
    _description = 'Aplica borrado logico a los modelos'

    active = fields.Boolean(
        string='¿Registro Activo en la Base de Datos?',
        help='''Si está inactivo, el registro no será incluido en las consultas normales (borrado lógico)''',
        default=True,
        track_visibility='onchange',
    )

    def unlink(self):
        if self.env.uid == 1 and self.env.context.get('force_unlink', False):
            return super(soft_delete_mixin, self).unlink()
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        return self.write({ 'active': False })
