# -*- coding: utf-8 -*-

from odoo import models, fields, api

class base_conf_firma_ws(models.TransientModel):
    _name = 'base_conf.firma_ws'
    _inherit = 'res.config.settings'

    url_ws_firma = fields.Char(
        string='URL WebService firma',
        size=200,
        help='URL para el webservice de firma.',
    )
    user_firma = fields.Char(
        string='Usuario de consulta de firma',
        size=200,
        help='Usuario con permisos de consulta en firma.',
    )
    pass_firma = fields.Char(
        string='Contraseña Usuario firma',
        size=200,
        help='Contraseña del usuario de firma.',
    )

    def guardar(self):
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('base_conf_url_ws_firma', self.url_ws_firma)
        set_param('base_conf_firma_usuario', self.user_firma)
        set_param('base_conf_firma_pass', self.pass_firma)
