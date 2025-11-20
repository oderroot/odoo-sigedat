# -*- coding: utf-8 -*-

from odoo import models, fields, api

# en Odoo 11 se elimina signal_workflow() y se reemplaza directamente la variable de estado en el modelo
# ejem: context="{'registro_id': id, 'key': 'state', 'value':'anulado' ,'titulo':'Se rechaza el movimiento'}"
# donde "key" es el nombre de la variable y "value" el nuevo valor a tomar

class base_conf_wizard_registrar_mensaje(models.TransientModel):
    ''' Clase que permite capturar y guardar el mensaje ingresado por el usuario.

    Para el uso del wizard se debe enviar en el contexto:

    registro_id : Integer - id del registro donde se registra la nota. Obligatorio.
    titulo : String - Titulo que quiera que este en la ventana para registrar el mensaje. Obligatorio.
    prefijo : String - Prefijo es el texto que se le pone al principio a todos los mensajes que ingresa el usuario. Es opcional.
    sufijo : String - Sufijo es el texto que se le pone al final a todos los mensajes que ingresa el usuario. Es opcional el campo.
    campo_mensaje : String - Nombre del campo del modelo al cual pertenece el registro, en donde se almacenara el mensaje, si no se indica, se almacena en el tracking. Es opcional el campo.
    metodo_ejecutar_antes : String - Metodo del modelo al cual pertenece el registro, el cual se ejecutara antes de grabar el mensaje en el registro o en el tracking. Es opcional el campo.
    metodo_ejecutar_despues : String - Metodo del modelo al cual pertenece el registro, el cual se ejecutara despues de grabar el mensaje en el registro o en el tracking. Es opcional el campo.
    mensaje_por_defecto : String - Valor por defecto a mostrar en el campo del mensaje
    key : String - Es el nombre del campo en donde se guarda el estado. Opcional si se envia el metodo para hacer el cambio del estado.
    value : String - El nuevo valor a que tomara el campo del estado. Opcional si se envia el metodo para hacer el cambio de estado.

    ej. context="{'registro_id': id, 'titulo':'Ingrese el motivo del rechazo', 'prefijo': 'Solicitud rechazada desde Almacén: ', 'metodo_ejecutar_despues': 'wkf_rechazado'}"

    '''
    _name = 'base_conf.wizard.registrar_mensaje'
    _description = 'Registrar un mensaje'
    _inherit = ['mail.thread',]

    # Fields
    mensaje = fields.Text(
        required=True,
        default=lambda self: self._context.get('mensaje_por_defecto', ''),
    )
    titulo = fields.Char(
        required=True,
        readonly=True,
        default=lambda self: self._context.get('titulo', None),
    )

    def action_create(self):
        context = self._context
        prefijo = context.get('prefijo', '')
        sufijo = context.get('sufijo', '')
        campo_mensaje = context.get('campo_mensaje', '')
        metodo_ejecutar_antes = context.get('metodo_ejecutar_antes', '')
        metodo_ejecutar_despues = context.get('metodo_ejecutar_despues', '')
        # Si se llamo al wizard, pasandole varios registros, se debe ejecutar sobre cada uno de ellos
        if 'registro_ids' in context:

            for reg_id in context.get('registro_ids',[]):
                    self.env['mail.message'].create({
                    'res_id': reg_id,
                    'model': context.get('active_model'),
                    'subject': self.titulo,
                    'body': "{} {} {}".format(prefijo, self.mensaje, sufijo),
                })
            records = self.env[context.get('active_model')].browse(context.get('registro_ids',[]))
            # FIXME En el odoo 12, no se manejan esas señales, revisar
            if context.get('signals'):
                signals = context.get('signals')
                for signal in signals:
                    records.signal_workflow(signal)
        else:
            reg = self.env[context.get('active_model')].browse(context.get('registro_id'))
            # Si envio metodo_ejecutar_antes, asumo que debo ejecutar dicho metodo antes de procesar el mensaje
            if reg and metodo_ejecutar_antes and hasattr(reg, metodo_ejecutar_antes):
                getattr(reg, metodo_ejecutar_antes)()
            # Si se envia el campo_mensaje, se debe poner el texto dentro de ese campo y no en el tracking
            if reg and campo_mensaje and hasattr(reg, campo_mensaje):
                mensaje = "{} {} {}".format(prefijo, self.mensaje, sufijo)
                setattr(reg, campo_mensaje, mensaje)

            # Si no se envia el campo_mensaje, se asume que se debe poner el texto solo en el tracking
            else:
                self.env['mail.message'].create({
                    'res_id': context.get('registro_id'),
                    'model': context.get('active_model'),
                    'subject': self.titulo,
                    'body': "{} {} {}".format(prefijo, self.mensaje, sufijo),
                })
                record = self.env[context.get('active_model')].browse(context.get('registro_id'))
                if context.get('key'):
                    record[context.get('key')] = (context.get('value'))
            # Si envio metodo_ejecutar_despues, asumo que debo ejecutar dicho metodo despues de procesar el mensaje
            if reg and metodo_ejecutar_despues and hasattr(reg, metodo_ejecutar_despues):
                getattr(reg, metodo_ejecutar_despues)()
        return {'type': 'ir.actions.act_window_close'}
