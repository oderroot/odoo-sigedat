# -*- coding: utf-8 -*-

from odoo import models, fields

class base_conf_wizard_descargar_archivo(models.TransientModel):
    '''
    Modelo Transiente en el cual se podran guardar temporalmente los archivos que se necesiten descargar
    '''
    _name = 'base_conf.wizard.descargar_archivo'
    _inherit = ['mail.thread',]
    _description = "Descargar un archivo"
    # Fields
    contenido_archivo = fields.Binary(
        attachment = True
    )
    nombre_archivo = fields.Char(
        string = 'Nombre de Archivo',
    )
