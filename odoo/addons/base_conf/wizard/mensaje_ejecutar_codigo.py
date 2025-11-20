# -*- coding: utf-8 -*-

from odoo import models, fields, api

class base_conf_wizard_mensaje_codigo(models.TransientModel):
    '''
    Wizard para mostrar un mensjaje (como si fuera un warning) y ejecutar un código por debajo.
    '''
    _name = 'base_conf.wizard.mensaje_codigo'
    _description = "Mensaje de alerta"
    mensaje = fields.Text(
        required=True
    )
    codigo = fields.Text(
        required=True,
    )

    @api.model
    def mostrar_mensaje(self, mensaje, codigo, titulo):
        wizard = self.create({
            'mensaje': mensaje,
            'codigo': codigo,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': titulo,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': wizard.id,
            'res_model': 'base_conf.wizard.mensaje_codigo',
            # 'view_id': view_id, # False
            'views': [(False, 'form')],
            'domain': [],
            'context': self.env.context,
            'target': 'new',
            'nodestroy': False,
            'flags': {
                'form': {'action_buttons': False},
                }
            }

    def ejecutar_codigo(self):
        codigo = self.codigo
        print(codigo)
        return eval(self.codigo)
