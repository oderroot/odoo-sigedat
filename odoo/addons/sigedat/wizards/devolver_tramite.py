# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SigedatWizardDevolverTramite(models.TransientModel):
    _name = 'sigedat.wizard.devolver_tramite'
    _description = 'Wizard para devolver trámite a tipo de cita específico'

    # -------------------
    # Fields
    # -------------------

    solicitud_id = fields.Many2one(
        'sigedat.tramite.solicitud',
        string='Solicitud',
        required=True,
        default=lambda self: self._context.get('active_id')
    )
    
    tipo_cita_devolucion_id = fields.Many2one(
        'sigedat.cita.tipo',
        string='Devolver a tipo de cita',
        required=True
    )
    
    motivo_devolucion = fields.Text(
        string='Motivo de devolución',
        required=True
    )

    current_tipo_cita = fields.Char(
        string='Tipo de cita actual',
        related='solicitud_id.tipo_cita_id.name',
        readonly=True
    )

    # -------------------
    # Methods
    # -------------------

    @api.onchange('solicitud_id')
    def _onchange_solicitud_id(self):
        if self.solicitud_id:
            # Definir opciones según el tipo de cita actual
            current_tipo = self.solicitud_id.tipo_cita_id.abreviatura
            domain = []
            
            if current_tipo == 'planos_record':
                # Puede devolver a Topografía o Planos Record
                domain = [('abreviatura', 'in', ['topografia', 'planos_record'])]
            elif current_tipo == 'entrega_final':
                # Puede devolver a cualquiera
                domain = [('abreviatura', 'in', ['topografia', 'planos_record', 'entrega_final'])]
            else:
                # Para otros tipos (como topografía), solo puede devolver al mismo tipo
                domain = [('id', '=', self.solicitud_id.tipo_cita_id.id)]
            
            return {'domain': {'tipo_cita_devolucion_id': domain}}

    def devolver_tramite(self):
        """Ejecuta la devolución del trámite con el tipo de cita seleccionado"""
        
        if not self.solicitud_id:
            raise ValidationError("No se ha seleccionado una solicitud válida.")
        
        if not self.tipo_cita_devolucion_id:
            raise ValidationError("Debe seleccionar el tipo de cita de devolución.")
        
        if not self.motivo_devolucion:
            raise ValidationError("Debe ingresar el motivo de la devolución.")

        # Cancelar citas agendadas existentes para este trámite y tipo de cita
        citas_existentes = self.env['sigedat.cita'].search([
            ('tramite_id', '=', self.solicitud_id.tramite_id.id),
            ('tipo_id', '=', self.solicitud_id.tipo_cita_id.id),
            ('state', '=', 'agendada')
        ])
        
        if citas_existentes:
            _logger.info(f"Cancelando {len(citas_existentes)} cita(s) existente(s) debido a devolución")
            for cita in citas_existentes:
                _logger.info(f"Cancelando cita: {cita.name} (tipo: {cita.tipo_id.name})")
                cita.write({
                    'state': 'cancelada',
                #    'observaciones': f'Cancelada automáticamente por devolución de solicitud. {self.motivo_devolucion}'
                })

        # Actualizar la solicitud con los datos de devolución
        self.solicitud_id.write({
            'state': 'revision_con_observaciones',
            'tipo_cita_devolucion_id': self.tipo_cita_devolucion_id.id,
            'motivo_devolucion': self.motivo_devolucion
        })
        
        # Generar reportes según el tipo de trámite (lógica existente)
        if self.solicitud_id.tramite_abreviatura == 'revision_topografia':
            self.solicitud_id.generar_reporte_lista_chequeo_topografia(es_firmado=False)
        elif self.solicitud_id.tramite_abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra']:
            self.solicitud_id.generar_reporte_lista_chequeo_sigue(es_firmado=False, esta_validado=False)
            
        # Enviar notificaciones
        self.solicitud_id.enviar_notificacion_cambio_estado('revision_con_observaciones')
        
        # Agregar mensaje en el chatter
        mensaje = f"Solicitud devuelta a tipo de cita: {self.tipo_cita_devolucion_id.name}. Motivo: {self.motivo_devolucion}"
        if citas_existentes:
            mensaje += f"\n{len(citas_existentes)} cita(s) cancelada(s) automáticamente."
        self.solicitud_id.message_post(body=mensaje)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
