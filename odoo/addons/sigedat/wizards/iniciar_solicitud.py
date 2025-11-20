# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class sigedat_wizard_iniciar_solicitud(models.TransientModel):
    _name = 'sigedat.wizard.iniciar_solicitud'
    _description = 'Sigedat - Wizard Iniciar Solicitud'

    # -------------------
    # Fields
    # -------------------

    tramite_id = fields.Many2one(
        string='Trámite',
        comodel_name='sigedat.tramite',
        ondelete='cascade',
        default=lambda self: self._context.get('tramite_id', False),
    )
    tipo_cita_id = fields.Many2one(
        string='Tipo de Cita',
        required=True,
        comodel_name='sigedat.cita.tipo',
    )
    tipo_cita_ids_permitidos = fields.Many2many(
        string='Tipos de Cita Permitidos',
        comodel_name='sigedat.cita.tipo',
        compute='_compute_tipo_cita_ids_permitidos',
    )
    tipo_tramite_id = fields.Many2one(
        string='Tipo de Trámite',
        required=True,
        comodel_name='sigedat.tramite.tipo',
        domain="[('tipo_cita_id', '=', tipo_cita_id)]",
    )
    es_asesoria = fields.Boolean(
        string='Es Asesoria',
        compute='_compute_es_asesoria'
    )

    @api.depends('tipo_tramite_id')
    def _compute_es_asesoria(self):
        for r in self:
            r.es_asesoria = 'asesor' in r.tipo_tramite_id.name.lower()

    @api.depends('tramite_id')
    def _compute_tipo_cita_ids_permitidos(self):
        for r in self:
            if not r.tramite_id:
                r.tipo_cita_ids_permitidos = self.env['sigedat.cita.tipo'].search([])
                continue
                
            # Buscar solicitudes devueltas PENDIENTES (sin resolver)
            solicitudes_devueltas_pendientes = r.tramite_id.solicitud_ids.filtered(
                lambda s: s.state == 'revision_con_observaciones' and 
                         s.tipo_cita_devolucion_id and
                         not r.tramite_id.solicitud_ids.filtered(
                             lambda sol: sol.tipo_cita_id.id == s.tipo_cita_devolucion_id.id and 
                                       sol.state in ['validado', 'validado_confirmado'] and
                                       sol.create_date > s.create_date
                         )
            )
            
            if solicitudes_devueltas_pendientes:
                # Solo restricción si hay devoluciones pendientes sin resolver
                tipos_permitidos_ids = list(set(solicitudes_devueltas_pendientes.mapped('tipo_cita_devolucion_id.id')))
                tipos_permitidos = self.env['sigedat.cita.tipo'].browse(tipos_permitidos_ids)
                r.tipo_cita_ids_permitidos = tipos_permitidos
            else:
                # Si no hay devoluciones pendientes, permitir todos los tipos de cita
                todos_tipos = self.env['sigedat.cita.tipo'].search([])
                r.tipo_cita_ids_permitidos = todos_tipos

    @api.onchange('tipo_cita_id')
    def _onchange_tipo_cita_id(self):
        self.tipo_tramite_id = None

    @api.onchange('tramite_id')
    def _onchange_tramite_id(self):
        """Aplicar dominio al campo tipo_cita_id basado en solicitudes devueltas PENDIENTES"""
        if not self.tramite_id:
            return
            
        # Buscar solicitudes devueltas PENDIENTES (sin resolver)
        solicitudes_devueltas_pendientes = self.tramite_id.solicitud_ids.filtered(
            lambda s: s.state == 'revision_con_observaciones' and 
                     s.tipo_cita_devolucion_id and
                     not self.tramite_id.solicitud_ids.filtered(
                         lambda sol: sol.tipo_cita_id.id == s.tipo_cita_devolucion_id.id and 
                                   sol.state in ['validado', 'validado_confirmado'] and
                                   sol.create_date > s.create_date
                     )
        )
        
        if solicitudes_devueltas_pendientes:
            # Solo restricción si hay devoluciones pendientes sin resolver
            tipos_permitidos_ids = list(set(solicitudes_devueltas_pendientes.mapped('tipo_cita_devolucion_id.id')))
            domain = [('id', 'in', tipos_permitidos_ids)]
            
            # Si el tipo de cita actual no está en los permitidos, limpiarlo
            if self.tipo_cita_id and self.tipo_cita_id.id not in tipos_permitidos_ids:
                self.tipo_cita_id = False
                
            return {'domain': {'tipo_cita_id': domain}}
        else:
            # Si no hay devoluciones pendientes, permitir todos los tipos de cita
            return {'domain': {'tipo_cita_id': []}}


    def iniciar_solicitud(self):
        if not self.tramite_id:
            raise ValidationError("Error en la comunicación con el trámite.")
            
        # Depuración: Mostrar información de las solicitudes
        _logger.info(f"=== DEPURACIÓN INICIAR SOLICITUD ===")
        _logger.info(f"Tipo de cita seleccionado: {self.tipo_cita_id.name}")
        _logger.info(f"Tipo de trámite seleccionado: {self.tipo_tramite_id.name}")
        
        for solicitud in self.tramite_id.solicitud_ids:
            _logger.info(f"Solicitud existente: {solicitud.name} - Estado: {solicitud.state} - Tipo cita: {solicitud.tipo_cita_id.name} - Tipo devolución: {solicitud.tipo_cita_devolucion_id.name if solicitud.tipo_cita_devolucion_id else 'N/A'}")
            
        # Validar restricciones de devolución SOLO si hay solicitudes devueltas SIN resolver
        solicitudes_devueltas_pendientes = self.tramite_id.solicitud_ids.filtered(
            lambda s: s.state == 'revision_con_observaciones' and 
                     s.tipo_cita_devolucion_id and
                     not self.tramite_id.solicitud_ids.filtered(
                         lambda sol: sol.tipo_cita_id.id == s.tipo_cita_devolucion_id.id and 
                                   sol.state in ['validado', 'validado_confirmado'] and
                                   sol.create_date > s.create_date
                     )
        )
        
        _logger.info(f"=== ANÁLISIS DE RESTRICCIONES ===")
        _logger.info(f"Solicitudes devueltas pendientes (sin resolver): {len(solicitudes_devueltas_pendientes)}")
        
        if solicitudes_devueltas_pendientes:
            _logger.info("🔒 RESTRICCIÓN ACTIVA: Hay devoluciones pendientes sin resolver")
            tipos_permitidos_ids = list(set(solicitudes_devueltas_pendientes.mapped('tipo_cita_devolucion_id.id')))
            _logger.info(f"   Tipos de cita permitidos: {tipos_permitidos_ids}")
            _logger.info(f"   Tipo de cita seleccionado ID: {self.tipo_cita_id.id}")
            
            for sol_dev in solicitudes_devueltas_pendientes:
                _logger.info(f"   📋 Devolución pendiente: {sol_dev.name} -> devuelta a: {sol_dev.tipo_cita_devolucion_id.name}")
            
            if self.tipo_cita_id.id not in tipos_permitidos_ids:
                tipos_permitidos_nombres = solicitudes_devueltas_pendientes.mapped('tipo_cita_devolucion_id.name')
                raise ValidationError(
                    f"Solo puede crear solicitudes de los siguientes tipos de cita devueltos por el revisor: {', '.join(set(tipos_permitidos_nombres))}. "
                    f"No puede crear una solicitud de tipo: {self.tipo_cita_id.name}"
                )
        else:
            _logger.info("🔓 SIN RESTRICCIONES: No hay devoluciones pendientes, puede crear cualquier tipo de solicitud")
                
        #INFO Valido que el trámite, no tenga solicitudes del mismo tipo en estado diferentes a: cancelado, rechazado o con observaciones
        # Verificar si existe una solicitud devuelta que permite crear este tipo de cita
        solicitud_devuelta_permite = self.tramite_id.solicitud_ids.filtered(
            lambda s: s.state == 'revision_con_observaciones' and 
                     s.tipo_cita_devolucion_id.id == self.tipo_cita_id.id
        )
        
        _logger.info(f"¿Existe solicitud devuelta que permite {self.tipo_cita_id.name}? {len(solicitud_devuelta_permite) > 0}")
        
        if solicitud_devuelta_permite:
            _logger.info("PERMITIDO: Existe devolución que permite crear este tipo de cita")
        else:
            # Solo validar duplicados si no hay devolución que lo permita
            solicitudes_mismo_tipo = self.tramite_id.solicitud_ids.filtered(
                lambda s: s.tipo_cita_id.id == self.tipo_cita_id.id and 
                         s.tipo_tramite_id.id == self.tipo_tramite_id.id and 
                         s.state not in ['cancelado', 'rechazado', 'revision_con_observaciones', 'orden_entrega_final']
            )
            
            _logger.info(f"Solicitudes activas del mismo tipo: {len(solicitudes_mismo_tipo)}")
            
            if solicitudes_mismo_tipo:
                _logger.info(f"ERROR: Bloqueando creación - solicitudes activas sin devolución")
                raise ValidationError(f"No se puede crear una solicitud adicional para el tipo de trámite: {self.tipo_tramite_id.name} y tipo de cita: {self.tipo_cita_id.name}, si el trámite anterior no esta: Cancelado, Rechazado o Devuelto con observaciones.")
            else:
                _logger.info("OK: No hay solicitudes activas del mismo tipo")

        #INFO Solo se debe poder iniciar la siguiente etapa de la revisión, si la anterior ha sido terminada satisfactoriamente (no incluye a las asesorias). El orden de las revisiones es: Topografía, record diseño, entrega diseño, record obra, entrega obra

        #INFO Inicializo las variables que me sirven de banderas
        tramite_con_observacion_id = None
        numero_lista_chequeo = 0
        primera_solicitud_id = self.tramite_id.solicitud_ids[0] if self.tramite_id.solicitud_ids else None

        #INFO Si la anterior solicitud del mismo trámite esta en 'Devuelta con observaciones' y no hay una solicitud del mismo trámite en 'Validado', se debe crear una nueva solicitud, precargando los mismos documentos, para que el externo, modifique los documentos que le quedaron mal

        #INFO Si es un trámite de topografía
        if self.tipo_tramite_id.abreviatura == 'revision_topografia':

            tramite_topografia_validado_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_tramite_id.id == self.tipo_tramite_id.id and s.state == 'validado')

            if tramite_topografia_validado_ids:
                raise ValidationError(f"No debe crear una nueva solicitud para el trámite: {self.tipo_tramite_id.name}, debido a que fue validado con anterioridad.")
            else:

                #INFO Si para el trámite no hay solicitudes validadas, busco si lo que se quiere hacer es crear un nuevo trámite para corregir las observaciones
                tramite_topografia_con_observacion_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_cita_devolucion_id.id == self.tipo_cita_id.id and s.state == 'revision_con_observaciones')

                if tramite_topografia_con_observacion_ids:
                    #INFO Crea la solicitud, duplicando los documentos de la primera solicitud devuelta según el tipo de cita de devolución
                    tramite_con_observacion_id = tramite_topografia_con_observacion_ids[-1]
                else:
                    #INFO Se esta creando el primer trámite para la revisión topográfica, por lo cual debo asignar un nuevo número de lista de chequeo

                    #INFO Obtengo un nuevo número asignar a la lista de chequeo, si es el primer trámite de la gestión del acuerdo
                    numero_lista_chequeo = self.env['ir.sequence'].sudo().next_by_code('numero_lista_chequeo.secuencia')

        #INFO Si es un trámite de record
        elif self.tipo_tramite_id.abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra']:

            #INFO Existe otro trámite de record abierto?
            tramite_record_abierto_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_tramite_id.abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra'] and s.state not in ['orden_entrega_final', 'revision_con_observaciones', 'rechazado', 'cancelado'])

            if tramite_record_abierto_ids:
                raise ValidationError(f"No se puede iniciar un trámite de record, si hay otro trámite abierto")

            #INFO Existe un trámite de topografia abierto y esta finalizado correctamente?
            tramite_topografia_validado_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_tramite_id.abreviatura == 'revision_topografia' and s.state == 'validado_confirmado')

            if not tramite_topografia_validado_ids:
                raise ValidationError(f"No se puede crear una solicitud de {self.tipo_tramite_id.name}, sin haber culminado satisfactoriamente el trámite de: Revisión Topografía.")

            #INFO No se valida si hay trámites record, en estado con orden de entrega final, ya que es posible que el revisor considere que el trámite esta para entrega final, pero el tercero encuentre una inconsistencia y vuelva a iniciar el trámite
            tramite_record_con_orden_entrega_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_tramite_id.abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra'] and s.state == 'orden_entrega_final')

            if not tramite_record_con_orden_entrega_ids:
                tramite_record_con_observacion_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_cita_devolucion_id.id == self.tipo_cita_id.id and s.state == 'revision_con_observaciones')

                if tramite_record_con_observacion_ids:
                    #INFO Crea la solicitud, duplicando los documentos de la primera solicitud devuelta según el tipo de cita de devolución
                    tramite_con_observacion_id = tramite_record_con_observacion_ids[-1]

            else:
                #INFO si tiene orden de entrega solo puede volver a comenzar un trámite del mismo tipo, asi mismo el siguiente trámite solo puede ser del misto tipo
                tipo_solicitud_tramite = tramite_record_con_orden_entrega_ids[0].tramite_abreviatura
                if self.tipo_tramite_id.abreviatura != tipo_solicitud_tramite:
                    raise ValidationError(f"No se puede iniciar otro trámite record, sin finalizar con entrega final el anterior.")

        #INFO Si es un trámite de entrega final
        elif self.tipo_tramite_id.abreviatura in ['asignacion_numero_record_disenio', 'asignacion_numero_record_obra']:

            #INFO Existe otro trámite de entrega final abierto?
            tramite_entrega_final_abierto_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_tramite_id.abreviatura in ['asignacion_numero_record_disenio', 'asignacion_numero_record_obra'] and s.state not in ['validado','rechazado','cancelado'])

            if tramite_entrega_final_abierto_ids:
                raise ValidationError(f"No se puede iniciar un trámite de entrega final, si hay otro trámite abierto")

            #INFO El trámite de record, fue finalizado correctamente?
            tramite_record_validado_ids = self.tramite_id.solicitud_ids.filtered(lambda s: s.tipo_tramite_id.abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra'] and s.state == 'orden_entrega_final')

            if not tramite_record_validado_ids:
                raise ValidationError(f"No se puede crear una solicitud de {self.tipo_tramite_id.name}, sin haber culminado satisfactoriamente el trámite de: Revisión de planos record.")
            else:
                #INFO Solo puede comenzar un trámite del mismo tipo, si termino el record de diseño, solamente puede comenzar entrega final de diseño
                tipo_solicitud_tramite_anterior = tramite_record_validado_ids[0].tramite_abreviatura.split('_')[-1]
                if not self.tipo_tramite_id.abreviatura.endswith(tipo_solicitud_tramite_anterior):
                    raise ValidationError(f"No se puede iniciar un trámite de entrega final, de un trámite record diferente al anterior.")
        else:
            raise ValidationError(f"Tipo de trámite no reconocido: {self.tipo_tramite_id.name}, por favor revise la configuración del mismo.")

        #INFO Cargo la información generica de todos los trámites
        solicitud = {
            'tramite_id': self.tramite_id.id,
            'tipo_tramite_id': self.tipo_tramite_id.id,
            'tipo_cita_id': self.tipo_cita_id.id,
        }

        #INFO Si es asesoria, de una vez debe llegar al estado creado
        if self.es_asesoria:
            solicitud['state'] = 'creado'



        #INFO Creo la solicitud, despues de las modificaciones anteriores
        solicitud_id = self.env['sigedat.tramite.solicitud'].create(solicitud)
        _logger.info(f"🔵 SOLICITUD CREADA: {solicitud_id.name} - Documentos iniciales: {len(solicitud_id.documento_ids)}")
        for doc in solicitud_id.documento_ids:
            _logger.info(f"   📄 Documento inicial: {doc.tipo_id.name if doc.tipo_id else 'Sin tipo'}")

        # HERENCIA DE DOCUMENTOS Y LISTA DE CHEQUEOS POR DEVOLUCIÓN
        # Verificar si es una solicitud creada por devolución y heredar documentos/lista
        # Si el revisor devolvió una solicitud al tipo de cita que se está creando,
        # la nueva solicitud debe heredar los documentos y lista de chequeos de la ÚLTIMA 
        # solicitud del MISMO tipo de cita que se está creando
        documentos_heredados = False  # Variable para controlar si ya se heredaron documentos
        solicitud_devuelta = self.tramite_id.solicitud_ids.filtered(
            lambda s: s.state == 'revision_con_observaciones' and 
                     s.tipo_cita_devolucion_id.id == self.tipo_cita_id.id
        )
        
        _logger.info(f"=== ANÁLISIS DE HERENCIA ===")
        _logger.info(f"Tipo de cita que se está creando: {self.tipo_cita_id.name}")
        _logger.info(f"¿Existe devolución para este tipo de cita? {len(solicitud_devuelta) > 0}")
        if solicitud_devuelta:
            for sol_dev in solicitud_devuelta:
                _logger.info(f"  - Solicitud devuelta: {sol_dev.name} (tipo original: {sol_dev.tipo_cita_id.name}) -> devuelta a: {sol_dev.tipo_cita_devolucion_id.name}")
        
        if solicitud_devuelta:
            # Buscar la ÚLTIMA solicitud del MISMO tipo de cita que se está creando
            # No la solicitud devuelta, sino la última solicitud de topografía (por ejemplo)
            todas_solicitudes_mismo_tipo = self.tramite_id.solicitud_ids.filtered(
                lambda s: s.tipo_cita_id.id == self.tipo_cita_id.id and s.id != solicitud_id.id
            )
            
            _logger.info(f"Solicitudes encontradas del tipo '{self.tipo_cita_id.name}':")
            for sol in todas_solicitudes_mismo_tipo:
                _logger.info(f"  - {sol.name} (estado: {sol.state}, fecha: {sol.create_date})")
            
            ultima_solicitud_mismo_tipo = todas_solicitudes_mismo_tipo.sorted('create_date', reverse=True)
            
            if ultima_solicitud_mismo_tipo:
                solicitud_origen = ultima_solicitud_mismo_tipo[0]
                _logger.info(f"✅ SELECCIONADA como origen: {solicitud_origen.name} (tipo: {solicitud_origen.tipo_cita_id.name})")
            else:
                _logger.info(f"❌ No se encontró solicitud anterior del tipo de cita '{self.tipo_cita_id.name}', no se hereda nada")
                solicitud_origen = None
            # Solo proceder si se encontró una solicitud origen del mismo tipo de cita
            if solicitud_origen:
                # Copiar SOLO documentos cuyas carpetas tengan el MISMO tipo de trámite y aplica_a_especial correcto
                documentos_copiados = []
                if solicitud_origen.documento_ids:
                    # Filtrar por tipo de trámite Y por aplica_a_especial según tiene_redes_acueducto
                    documentos_compatibles = solicitud_origen.documento_ids.filtered(
                        lambda doc: doc.carpeta_id and 
                                   doc.carpeta_id.tipo_tramite_id.id == self.tipo_tramite_id.id and
                                   (
                                       # Si tiene redes acueducto = 'si', carpeta debe ser aplica_a_especial = 'no'
                                       (self.tramite_id.tiene_redes_acueducto == 'si' and doc.carpeta_id.aplica_a_especial == 'no') or
                                       # Si tiene redes acueducto = 'no', carpeta debe ser aplica_a_especial = 'si'
                                       (self.tramite_id.tiene_redes_acueducto == 'no' and doc.carpeta_id.aplica_a_especial == 'si') or
                                       # Si no está definido, permitir todos (retrocompatibilidad)
                                       (not self.tramite_id.tiene_redes_acueducto)
                                   )
                    )
                    
                    _logger.info(f"   📊 ANÁLISIS DE HERENCIA:")
                    _logger.info(f"      Tipo trámite nueva solicitud: {self.tipo_tramite_id.name}")
                    _logger.info(f"      Tiene redes acueducto: {self.tramite_id.tiene_redes_acueducto}")
                    _logger.info(f"      Es especial (computado): {self.tramite_id.es_especial}")
                    _logger.info(f"      Total documentos en origen: {len(solicitud_origen.documento_ids)}")
                    _logger.info(f"      Documentos compatibles: {len(documentos_compatibles)}")
                    
                    # Log detallado de cada documento
                    for doc in solicitud_origen.documento_ids:
                        carpeta_tipo = doc.carpeta_id.tipo_tramite_id.name if doc.carpeta_id and doc.carpeta_id.tipo_tramite_id else 'Sin tipo'
                        carpeta_especial = doc.carpeta_id.aplica_a_especial if doc.carpeta_id else 'N/A'
                        tipo_correcto = doc.carpeta_id and doc.carpeta_id.tipo_tramite_id.id == self.tipo_tramite_id.id
                        especial_correcto = (
                            (self.tramite_id.tiene_redes_acueducto == 'si' and doc.carpeta_id and doc.carpeta_id.aplica_a_especial == 'no') or
                            (self.tramite_id.tiene_redes_acueducto == 'no' and doc.carpeta_id and doc.carpeta_id.aplica_a_especial == 'si') or
                            (not self.tramite_id.tiene_redes_acueducto)
                        )
                        compatible = tipo_correcto and especial_correcto
                        estado = "✅ SE HEREDARÁ" if compatible else "❌ SE OMITE"
                        razon = ""
                        if not tipo_correcto:
                            razon = " (tipo trámite incorrecto)"
                        elif not especial_correcto:
                            razon = f" (aplica_a_especial='{carpeta_especial}' no coincide con tiene_redes_acueducto='{self.tramite_id.tiene_redes_acueducto}')"
                        _logger.info(f"      📄 {estado}: {doc.tipo_id.name if doc.tipo_id else 'Sin tipo'} (Carpeta tipo: {carpeta_tipo}, aplica_a_especial: {carpeta_especial}){razon}")
                    
                    # Solo copiar documentos compatibles
                    for doc in documentos_compatibles:
                        documento_copia = doc.copy({
                            'solicitud_tramite_id': solicitud_id.id,
                        })
                        documentos_copiados.append(documento_copia.id)
                    
                    if documentos_compatibles:
                        _logger.info(f"   ✅ Documentos heredados exitosamente: {len(documentos_copiados)}")
                        documentos_heredados = True
                    else:
                        _logger.info(f"   ⚠️ No hay documentos compatibles para heredar")
                        documentos_heredados = False
                else:
                    _logger.info(f"   ⚠️ Solicitud origen no tiene documentos")
                    documentos_heredados = False
                    
                    # Log documentos después de heredar
                    _logger.info(f"🟢 DESPUÉS DE HERENCIA: {solicitud_id.name} - Total documentos: {len(solicitud_id.documento_ids)}")
                    for doc in solicitud_id.documento_ids:
                        _logger.info(f"   📄 Documento heredado: {doc.tipo_id.name if doc.tipo_id else 'Sin tipo'}")
                
                # Copiar lista de chequeos con validación inteligente
                if solicitud_origen.lista_item_ids:
                    items_copiados = []
                    
                    for item in solicitud_origen.lista_item_ids:
                        _logger.info(f"[HERENCIA] Copiando item: {item.lista_chequeo_id.name}, cumple: {item.cumple}, observaciones: {len(item.observacion_ids)}")
                        
                        # Log detallado de las observaciones originales
                        if item.observacion_ids:
                            for obs in item.observacion_ids:
                                _logger.info(f"  [HERENCIA] Observación original: {obs.id} - texto: '{obs.observacion}'")
                        
                        # Si el item no cumple pero no tiene observaciones, cambiar a 'na' temporalmente
                        if item.cumple == 'no' and not item.observacion_ids:
                            _logger.warning(f"[HERENCIA] Item {item.lista_chequeo_id.name} marcado como 'no' pero sin observaciones, cambiando a 'na'")
                            # Crear con 'na' para evitar el error
                            item_copia = item.copy({
                                'solicitud_tramite_id': solicitud_id.id,
                                'cumple': 'na',
                            })
                        else:
                            # Usar contexto especial para saltar validación durante la copia
                            item_copia = item.with_context(skip_observacion_validation=True).copy({
                                'solicitud_tramite_id': solicitud_id.id,
                            })
                        
                        # Verificar que las observaciones se copiaron (normalmente no se copian automáticamente)
                        _logger.info(f"[HERENCIA] Item copiado: {item_copia.id} - observaciones automáticas: {len(item_copia.observacion_ids)}")
                        
                        # COPIAR OBSERVACIONES MANUALMENTE (One2many no se copia automáticamente)
                        if item.observacion_ids:
                            _logger.info(f"[HERENCIA] Copiando manualmente {len(item.observacion_ids)} observaciones")
                            contador_observaciones = 0
                            for observacion in item.observacion_ids:
                                try:
                                    _logger.info(f"  [HERENCIA] Copiando observación {observacion.id}: '{observacion.observacion}'")
                                    # Usar sudo() para tener permisos de administrador al crear la observación
                                    nueva_observacion = observacion.sudo().copy({
                                        'item_id': item_copia.id,
                                    })
                                    contador_observaciones += 1
                                    _logger.info(f"  [HERENCIA] ✅ Observación copiada: {nueva_observacion.id} -> item: {nueva_observacion.item_id.id}")
                                except Exception as e:
                                    _logger.error(f"  [HERENCIA] ❌ Error copiando observación {observacion.id}: {str(e)}")
                            
                            # Forzar commit para asegurar que las observaciones se persistan
                            self.env.cr.commit()
                            
                            # Verificar resultado final
                            item_copia_actualizado = self.env['sigedat.lista_chequeo.item'].browse(item_copia.id)
                            _logger.info(f"[HERENCIA] RESULTADO: Item {item_copia_actualizado.lista_chequeo_id.name} ahora tiene {len(item_copia_actualizado.observacion_ids)} observaciones")
                            for obs_verificada in item_copia_actualizado.observacion_ids:
                                _logger.info(f"  [HERENCIA] ✅ Verificada: {obs_verificada.id} - '{obs_verificada.observacion}'")
                        else:
                            _logger.info(f"[HERENCIA] Item no tiene observaciones para copiar")
                        
                        items_copiados.append(item_copia.id)
                    
                    _logger.info(f"Items de lista copiados: {len(items_copiados)}")
                    
                # Si es una devolución, marcar la solicitud y copiar datos de planos
                if solicitud_devuelta:
                    solicitud_id.fue_devuelto = True
                    # Copiar datos de planos desde la solicitud origen (la última del mismo tipo)
                    if solicitud_origen:
                        solicitud_id.acueducto = solicitud_origen.acueducto
                        solicitud_id.alcantarillado_pluvial = solicitud_origen.alcantarillado_pluvial
                        solicitud_id.alcantarillado_sanitario = solicitud_origen.alcantarillado_sanitario
                        solicitud_id.combinado = solicitud_origen.combinado
                        solicitud_id.especiales = solicitud_origen.especiales
                        _logger.info(f"[HERENCIA] Datos de planos copiados desde {solicitud_origen.name}")
        else:
            _logger.info("No es una solicitud por devolución, no se heredan documentos")

        #INFO Si es un trámite de entrega final, esta no tiene lista de chequeo, por lo cual se usa la del record que la inicio
        if self.tipo_tramite_id.abreviatura in ['asignacion_numero_record_disenio', 'asignacion_numero_record_obra']:
            if tramite_record_validado_ids:

                for item in tramite_record_validado_ids[0].lista_item_ids:
                    i = {
                        'lista_chequeo_id': item.lista_chequeo_id.id,
                        'cumple': item.cumple,
                        'solicitud_tramite_id': solicitud_id.id,
                        'numero_lista_chequeo': item.numero_lista_chequeo or '',
                        'version_lista_chequeo': str(int(item.version_lista_chequeo or 0)+1),
                        }
                    # Usar contexto especial para saltar validación cuando se crea un ítem con 'no' pero sin observaciones iniciales
                    nuevo_item = self.env['sigedat.lista_chequeo.item'].with_context(skip_observacion_validation=True).create(i)

                    # Copiar observaciones en lugar de moverlas
                    if item.observacion_ids:
                        _logger.info(f"[ENTREGA FINAL] Copiando {len(item.observacion_ids)} observaciones para item {item.lista_chequeo_id.name}")
                        for observacion in item.observacion_ids:
                            nueva_observacion = observacion.sudo().copy({
                                'item_id': nuevo_item.id,
                            })
                            _logger.info(f"  Observación copiada: {nueva_observacion.id}")
                    else:
                        _logger.info(f"[ENTREGA FINAL] Item {item.lista_chequeo_id.name} no tiene observaciones")


                #INFO Se traen los datos de cantidad de planos del tramite de revisión planos record válido
                solicitud_id.acueducto = tramite_record_validado_ids[0].acueducto
                solicitud_id.alcantarillado_pluvial = tramite_record_validado_ids[0].alcantarillado_pluvial
                solicitud_id.alcantarillado_sanitario = tramite_record_validado_ids[0].alcantarillado_sanitario
                solicitud_id.combinado = tramite_record_validado_ids[0].combinado
                solicitud_id.especiales = tramite_record_validado_ids[0].especiales


        # INFO Verificar si ya existen items heredados antes de crear nuevos
        _logger.info(f"=== VERIFICACIÓN DE ITEMS EXISTENTES ===")
        _logger.info(f"Items actuales en solicitud {solicitud_id.name}: {len(solicitud_id.lista_item_ids)}")
        
        # Solo crear items automáticamente si NO hay items ya creados
        if not solicitud_id.lista_item_ids:
            #INFO El dominio por defecto es generico y no valida si aplica o no para especial, el cual sirve para los trámites especiales, ya que se deben cargar los items que aplican y adicionalmente los que no aplican para especial
            tipo_tramite_ids = [self.tipo_tramite_id.id]
            if 'revision_planos_record' in self.tipo_tramite_id.abreviatura:
                tipo_tramites = self.env['sigedat.tramite.tipo'].search([('abreviatura','ilike','revision_planos_record')])
                if tipo_tramites: tipo_tramite_ids = tipo_tramites.ids
            dominio_lista_chequeo =[
                    ('activo', '=', True),
                    ('tipo_tramite_id', 'in', tipo_tramite_ids),
                ]
            # #INFO Si el tipo de trámite no es especial, se deben filtrar únicamente los que no aplican para especial
            # if not self.tramite_id.es_especial:
            #     dominio_lista_chequeo.append(
            #         ('aplica_a_especial', '=', 'no')
            #     )
            # else:
            #     dominio_lista_chequeo.append(
            #         ('aplica_a_especial', '=', 'si')
            #     )
            items_lista_chequeo = self.env['sigedat.lista_chequeo'].search(dominio_lista_chequeo)
            for item in items_lista_chequeo:
                i = {
                    'lista_chequeo_id': item.id,
                    'cumple': 'si' if item.se_toma_tramite_anterior else 'na',
                    'solicitud_tramite_id': solicitud_id.id,
                    }
                if numero_lista_chequeo:
                    i['numero_lista_chequeo'] = f"{solicitud_id.area_id.abreviatura}{numero_lista_chequeo}"
                    i['version_lista_chequeo'] = '1'
                elif primera_solicitud_id:
                    i['numero_lista_chequeo'] = f"{primera_solicitud_id.lista_item_ids[0].numero_lista_chequeo}"
                    i['version_lista_chequeo'] = '1'
                else:
                    raise ValidationError(f"Error en la creación de la solicitud.")

                solicitud_id.lista_item_ids = [(0, 0, i)]
        else:
            _logger.info(f"  ITEMS YA HEREDADOS: La solicitud {solicitud_id.name} ya tiene {len(solicitud_id.lista_item_ids)} items")
            _logger.info("   Se omite la creación automática de items para evitar duplicados")
            
            # Log de los items existentes
            for item in solicitud_id.lista_item_ids:
                _logger.info(f"   Item existente: {item.lista_chequeo_id.name} (cumple: {item.cumple}, observaciones: {len(item.observacion_ids)})")

        #INFO Creo los documentos automáticamente SOLO si no se heredaron documentos compatibles
        # Verificar si ya existen documentos antes de crear nuevos
        _logger.info(f"=== VERIFICACIÓN DE DOCUMENTOS EXISTENTES ===")
        _logger.info(f"Documentos actuales en solicitud {solicitud_id.name}: {len(solicitud_id.documento_ids)}")
        _logger.info(f"Variable documentos_heredados: {documentos_heredados}")
        
        # Solo crear documentos automáticamente si NO hay documentos ya creados/heredados
        if not documentos_heredados and not solicitud_id.documento_ids:
            _logger.info("🔧 CREACIÓN AUTOMÁTICA DE DOCUMENTOS:")
            _logger.info(f"   Razón: No se heredaron documentos compatibles del tipo trámite '{self.tipo_tramite_id.name}'")
            if tramite_con_observacion_id:
                for d in tramite_con_observacion_id.documento_ids:
                    documento = {
                            'tipo_id': d.tipo_id.id,
                            'archivo': d.archivo,
                            'archivo_nombre': d.archivo_nombre,
                            'solicitud_tramite_id': solicitud_id.id,
                            'carpeta_id': d.carpeta_id.id,
                        }
                    solicitud_id.documento_ids = [(0, 0, documento)]
            else:
                #INFO Filtrar carpetas según tipo de trámite y si aplica a especial
                dominio_carpetas = [
                        ('activo', '=', True),
                        ('tipo_tramite_id', '=', self.tipo_tramite_id.id)
                    ]
                
                # Verificar tiene_redes_acueducto del trámite para filtrar carpetas
                if self.tramite_id.tiene_redes_acueducto == 'si':
                    # Si tiene redes de acueducto, solo carpetas que NO aplican a especial
                    dominio_carpetas.append(('aplica_a_especial', '=', 'no'))
                elif self.tramite_id.tiene_redes_acueducto == 'no':
                    # Si NO tiene redes de acueducto, solo carpetas que SI aplican a especial
                    dominio_carpetas.append(('aplica_a_especial', '=', 'si'))
                
                _logger.info(f"   BÚSQUEDA DE CARPETAS:")
                _logger.info(f"   Tipo de trámite de la solicitud: {self.tipo_tramite_id.name} (ID: {self.tipo_tramite_id.id})")
                _logger.info(f"   Tiene redes acueducto: {self.tramite_id.tiene_redes_acueducto}")
                _logger.info(f"   Es especial (computado): {self.tramite_id.es_especial}")
                _logger.info(f"   Dominio de búsqueda: {dominio_carpetas}")
                
                carpeta_ids = self.env['sigedat.carpeta'].search(dominio_carpetas)
                
                _logger.info(f"   Carpetas encontradas: {len(carpeta_ids)}")
                for carpeta in carpeta_ids:
                    _logger.info(f"     - {carpeta.name} (Tipo trámite: {carpeta.tipo_tramite_id.name})")
                
                for carpeta_id in carpeta_ids:
                    for t in carpeta_id.tipo_documento_ids:
                        _logger.info(f"   Creando documento automático: {t.name} (Carpeta: {carpeta_id.name})")
                        documento = {
                            'tipo_id': t.id,
                            'solicitud_tramite_id': solicitud_id.id,
                            'carpeta_id': carpeta_id.id,
                            }
                        solicitud_id.documento_ids = [(0, 0, documento)]
        elif documentos_heredados:
            _logger.info("DOCUMENTOS YA HEREDADOS:")
            _logger.info(f"   Se heredaron documentos compatibles del tipo trámite '{self.tipo_tramite_id.name}'")
            _logger.info("   Omitiendo creación automática de documentos")
        else:
            _logger.info("DOCUMENTOS YA EXISTENTES:")
            _logger.info(f"   La solicitud {solicitud_id.name} ya tiene {len(solicitud_id.documento_ids)} documentos")
            _logger.info("   Se omite la creación automática de documentos para evitar duplicados")
            
            # Log de los documentos existentes
            for doc in solicitud_id.documento_ids:
                carpeta_tipo = doc.carpeta_id.tipo_tramite_id.name if doc.carpeta_id and doc.carpeta_id.tipo_tramite_id else 'Sin tipo'
                _logger.info(f"   Documento existente: {doc.tipo_id.name if doc.tipo_id else 'Sin tipo'} (Carpeta tipo: {carpeta_tipo})")

        # VERIFICACIÓN FINAL: Asegurar que todos los documentos sean del tipo de trámite correcto Y aplica_a_especial correcto
        _logger.info(f" VERIFICACIÓN FINAL: {solicitud_id.name}")
        _logger.info(f"   Tipo trámite solicitud: {self.tipo_tramite_id.name}")
        _logger.info(f"   Tiene redes acueducto: {self.tramite_id.tiene_redes_acueducto}")
        _logger.info(f"   Total documentos asociados: {len(solicitud_id.documento_ids)}")

        documentos_incorrectos = []
        for doc in solicitud_id.documento_ids:
            carpeta_tipo = doc.carpeta_id.tipo_tramite_id.name if doc.carpeta_id and doc.carpeta_id.tipo_tramite_id else 'Sin tipo'
            carpeta_especial = doc.carpeta_id.aplica_a_especial if doc.carpeta_id else 'N/A'

            tipo_correcto = doc.carpeta_id and doc.carpeta_id.tipo_tramite_id.id == self.tipo_tramite_id.id
            especial_correcto = (
                (self.tramite_id.tiene_redes_acueducto == 'si' and doc.carpeta_id and doc.carpeta_id.aplica_a_especial == 'no') or
                (self.tramite_id.tiene_redes_acueducto == 'no' and doc.carpeta_id and doc.carpeta_id.aplica_a_especial == 'si') or
                (not self.tramite_id.tiene_redes_acueducto)
            )
            es_correcto = tipo_correcto and especial_correcto
            estado = "CORRECTO" if es_correcto else "INCORRECTO"
            
            razon = ""
            if not tipo_correcto:
                razon = " - Tipo trámite incorrecto"
            elif not especial_correcto:
                razon = f" - aplica_a_especial='{carpeta_especial}' no coincide con tiene_redes_acueducto='{self.tramite_id.tiene_redes_acueducto}'"
            
            _logger.info(f"   {estado}: {doc.tipo_id.name if doc.tipo_id else 'Sin tipo'} (Carpeta tipo: {carpeta_tipo}, aplica_a_especial: {carpeta_especial}){razon}")
            
            if not es_correcto:
                documentos_incorrectos.append(doc)
        
        if documentos_incorrectos:
            _logger.error(f"ADVERTENCIA: {len(documentos_incorrectos)} documentos tienen carpetas de tipo trámite incorrecto")
        else:
            _logger.info("ÉXITO: Todos los documentos tienen carpetas del tipo trámite correcto")
        
        _logger.info("=== FIN ANÁLISIS DOCUMENTOS ===")

        return solicitud_id
