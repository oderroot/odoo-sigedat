# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import UserError




class sigedat_wizard_observacion_relacionada(models.TransientModel):
    _name = 'sigedat.wizard.observacion_relacionada'
    _description = 'Sigedat - Wizard Crear Soporte'



    # -------------------
    # Fields
    # -------------------
    
    observacion_ids = fields.Many2many(
        string='Observaciones',
        comodel_name='sigedat.lista_chequeo.item.observacion',
        relation='sigedat_wizard_obs_rel_rel',
        required=True,
        domain=lambda self: self._domain_observacion(),
    )



    def _domain_observacion(self):
        observacion_id = self._context.get('active_id', None)
        if observacion_id:
            observacion = self.env['sigedat.lista_chequeo.item.observacion'].browse([observacion_id])
            solicitud_tramite = observacion[0].item_id.solicitud_tramite_id
            lista_item_ids = solicitud_tramite.lista_item_ids
            observacion_solicitud_tramite_ids = lista_item_ids.observacion_ids.ids
            # Si está la observación activa, hay que quitarla del dominio
            if observacion_id in observacion_solicitud_tramite_ids:
                observacion_solicitud_tramite_ids.remove(observacion_id)
            return [('id', 'in', observacion_solicitud_tramite_ids)]
        return [('id', 'in', [])]  # Retorna un dominio vacío si no hay observación activa



    def observacion_relacionada(self):
        observacion_id = self._context.get('active_id', False)
        if not observacion_id:
            raise UserError("No se ha encontrado la observación.")

        observaciones_relacionadas = self.observacion_ids
        if not observaciones_relacionadas:
            raise UserError("Debe seleccionar al menos una observación.")
        
        observacion = self.env['sigedat.lista_chequeo.item.observacion'].browse(observacion_id)
        if not observacion:
            raise UserError("La observación seleccionada no existe.")
        
        # Agrega las observaciones seleccionadas a la observación actual
        observacion.observacion_ids = [(4, obs.id) for obs in observaciones_relacionadas]
    
