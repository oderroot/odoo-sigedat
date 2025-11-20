# -*- coding: utf-8 -*-

from odoo import models, fields

# Para el uso del wizard se debe enviar en el contexto los valores de:

# p.e.: context="{'registro_id': id, 'campo_direccion': 'campo_dir','titulo':'Se rechaza el movimiento', 'mensaje':'Por favor ingrese la direccion de... '}"
# donde "campo_direccion" es el nombre del campo en el cual se desea que quede la direccion capturada por el wizard

LISTA_LETRAS_ABECEDARIO_SELECT = [
            ('a', 'A'),
            ('b', 'B'),
            ('c', 'C'),
            ('d', 'D'),
            ('e', 'E'),
            ('f', 'F'),
            ('g', 'G'),
            ('h', 'H'),
            ('i', 'I'),
            ('j', 'J'),
            ('k', 'K'),
            ('l', 'L'),
            ('m', 'M'),
            ('n', 'N'),
            ('o', 'O'),
            ('p', 'P'),
            ('q', 'Q'),
            ('r', 'R'),
            ('s', 'S'),
            ('t', 'T'),
            ('u', 'U'),
            ('v', 'V'),
            ('w', 'W'),
            ('x', 'X'),
            ('y', 'Y'),
            ('z', 'Z'),
        ]

LISTA_CALLE_CARRERA_SELECT = [
            ('cl', 'CL'),
            ('kr', 'KR'),
            ('dg', 'DG'),
            ('tv', 'TV'),
            ('ac', 'AC'),
            ('ak', 'AK'),
        ]

class base_conf_wizard_registrar_mensaje(models.TransientModel):
    _name = 'base_conf.wizard.registrar_direccion'
    _inherit = ['mail.thread',]
    _description = "Registrar una direccion"

    # Fields
    titulo = fields.Char(
        required=True,
        readonly=True,
        default=lambda self: self._context.get('titulo', ''),
    )
    mensaje = fields.Text(
        required=True,
        readonly=True,
        default=lambda self: self._context.get('mensaje', ''),
    )
    campo_1 = fields.Selection(
        required=True,
        selection=LISTA_CALLE_CARRERA_SELECT
    )
    campo_2 = fields.Integer(
        required=True,
        size=2,
    )
    campo_3 = fields.Selection(
        selection=LISTA_LETRAS_ABECEDARIO_SELECT
    )
    campo_4 = fields.Boolean(
        required=True,
    )
    campo_5 = fields.Selection(
        selection=LISTA_LETRAS_ABECEDARIO_SELECT
    )
    campo_6 = fields.Selection(
        selection=[
            ('sur', 'Sur'),
            ('este', 'Este'),
        ]
    )
    campo_7 = fields.Integer(
        required=True,
        string=""
    )
    campo_8 = fields.Selection(
        selection=LISTA_LETRAS_ABECEDARIO_SELECT
    )
    campo_9 = fields.Integer(
      string=""
    )
    campo_10 = fields.Selection(
        selection=[
            ('sur', 'Sur'),
            ('este', 'Este'),
        ]
    )

    def registrar_direccion(self, context):
        modelo = self.env[context.get('active_model')]
        reg = modelo.browse(context.get('registro_id'))
        campo_direccion = context.get('campo_direccion')
        if reg and hasattr(reg, campo_direccion):
            reg[campo_direccion] = "{} {} {} {} {} {} {} {} {}".format(self.campo_1, self.campo_2, self.campo_3 or '', (self.campo_4 and 'BIS') or '', self.campo_5 or '', self.campo_6 or '', self.campo_7, self.campo_8 or '', self.campo_9, self.campo_10 or '').upper()

        # self.env['mail.message'].create({
        #     'res_id': context.get('registro_id'),
        #     'model': context.get('active_model'),
        #     'subject': self.titulo,
        #     'type': 'comment',
        #     'body': self.mensaje,
        # })
        # record = self.env[context.get('active_model')].browse(context.get('registro_id'))
        # if context.get('key'):
        #     record[context.get('key')] = (context.get('value'))

        return {'type': 'ir.actions.act_window_close'}
