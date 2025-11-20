# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import time, date, timedelta, datetime
from pytz import timezone
from workalendar.america import Colombia
from odoo.addons.base_conf.tools.sap import Sap
import math




class sigedat_wizard_asignar_revisor(models.TransientModel):
    _name = 'sigedat.wizard.asignar_revisor'
    _description = 'Sigedat - Wizard Asignar revisor'



    # -------------------
    # Fields
    # -------------------
    revisor_id = fields.Many2one(
        string='Revisor Asignado',
        comodel_name='sigedat.revisor',
        default=lambda self: self._context.get('revisor_id',False)
    )




    def asignar_revisor(self):
        solicitud_tramite_id = self._context.get('solicitud_tramite_id', False)
        if not solicitud_tramite_id:
            raise UserError("No se ha encontrado la solicitud de trámite para asignar el revisor.")
        solicitud_tramite = self.env['sigedat.tramite.solicitud'].browse(solicitud_tramite_id)
        solicitud_tramite.cita_id.revisor_id = self.revisor_id

