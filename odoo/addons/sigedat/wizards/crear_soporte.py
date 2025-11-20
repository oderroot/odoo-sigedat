# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError




class sigedat_wizard_crear_soporte(models.TransientModel):
    _name = 'sigedat.wizard.crear_soporte'
    _description = 'Sigedat - Wizard Crear Soporte'



    # -------------------
    # Fields
    # -------------------
    
    archivo = fields.Binary(
        string='Archivo',
        required=True,
        attachment = True,
    )




    def crear_soporte(self):
        observacion_id = self._context.get('active_id', False)
        if not observacion_id:
            raise UserError("No se ha encontrado la observación.")
        soporte = self.env['sigedat.lista_chequeo.item.observacion.soporte'].create({
            'archivo': self.archivo,
            'archivo_nombre': 'Soporte de Observación',
            'item_observacion_id': observacion_id,
        })
        observacion = self.env['sigedat.lista_chequeo.item.observacion'].browse(observacion_id)
        # borrar soporte anterior si existe
        if observacion.soporte_id:
            if observacion.soporte_id.archivo:
                observacion.soporte_id.unlink()

        observacion.soporte_id = soporte.id
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'sigedat.lista_chequeo.item.observacion',
        #     'view_mode': 'form',
        #     'res_id': observacion.id,
        #     'target': 'current',
        # }

