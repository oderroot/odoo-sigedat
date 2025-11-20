# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import time, date, timedelta, datetime
from pytz import timezone
from workalendar.america import Colombia
from odoo.addons.base_conf.tools.sap import Sap
import math




class sigedat_wizard_mostrar_mensaje(models.TransientModel):
    _name = 'sigedat.wizard.mostrar_mensaje'
    _description = 'Sigedat - Wizard Mensaje'



    # -------------------
    # Fields
    # -------------------
    mensaje = fields.Text(
        string='Mensaje',
        default=lambda self: self._context.get('mensaje', 'No se ha proporcionado un mensaje.'),
    )

    # -------------------
    # Methods
    # -------------------


    # def mostrar_mensaje(self):
    #     mensaje = self._context.get('mensaje', 'No se ha proporcionado un mensaje.')
    #     self.mensaje = mensaje

    
