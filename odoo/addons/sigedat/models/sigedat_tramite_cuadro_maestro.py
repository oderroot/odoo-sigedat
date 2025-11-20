# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta, datetime

class SigedatTramiteCuadroMaestro(models.Model):
    _name = 'sigedat.tramite.cuadro_maestro'
    _description = 'Cuadro maestro'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------

    name = fields.Char(
        string='name',
        compute='_compute_name'
    )
    tramite_id = fields.Many2one(
        string='Trámite',
        comodel_name='sigedat.tramite',
        ondelete='cascade',
        tracking=True,
        required=True,
        default=lambda self: self._context.get('tramite_id', False),
    )
    contrato_id = fields.Many2one(
        string='Acuerdo',
        comodel_name='sigedat.contrato',
        related='tramite_id.contrato_id',
    )
    aviso_sap = fields.Char(
        string='Aviso SAP',
        compute='_compute_aviso_sap'
    )
    numero_lista_chequeo_topografia = fields.Char(
        string='Lista chequeo topografía',
        compute='_compute_numero_lista_chequeo_topografia'
    )
    numero_lista_chequeo_sigue = fields.Char(
        string='Lista chequeo SIGUE',
        compute='_compute_numero_lista_chequeo_sigue'
    )
    numero_contrato = fields.Char(
        string='Número contrato',
        related='contrato_id.name'
    )
    objeto_contrato = fields.Text(
        string='Objeto del contrato',
        related='contrato_id.objeto',
    )
    direccion_proyecto = fields.Char(
        string='Dirección proyecto',
        related='ultima_solicitud_topografia_id.direccion_proyecto',
    )
    tiene_frente = fields.Selection(
        string='¿Tiene frente?',
        related='contrato_id.tiene_frente',
    )
    frente_id = fields.Many2one(
        string='Frente o tramo',
        comodel_name='sigedat.frente',
        related='tramite_id.frente_id',
    )
    area_id = fields.Many2one(
        string="Zona",
        related='contrato_id.area_id'
    )
    #FIXME Este dato se saca del formato de asignación de número.
    localidad_id = fields.Many2one(
        related='ultima_solicitud_topografia_id.localidad_id',
    )
    barrio_id = fields.Many2one(
        related='ultima_solicitud_topografia_id.barrio_id',
    )
    fecha_inicio = fields.Date(
        string='Fecha firma contrato',
        related='contrato_id.fecha_inicio',
    )
    fecha_fin = fields.Date(
        related='contrato_id.fecha_fin',
    )
    plazo = fields.Char(
        string='Plazo',
        compute='_compute_plazo',
    )
    empresa_contratista = fields.Char(
        string='Contratista',
        related='contrato_id.empresa_contratista',
    )
    telefono_contratista = fields.Char(
        string='Teléfono contratista',
        related='contrato_id.telefono_contratista'
    )
    # falta direccion contratista, pedirla en el wizard de creacion de contrato?
    # telefono oficina no existe
    solicitante_id = fields.Many2one(
        string='Solicitante',
        comodel_name='res.users',
        ondelete='restrict',
        compute='_compute_solicitante'
    )
    nombre_empresa_interventor = fields.Char(
        string='Empresa interventoría',
        related='contrato_id.nombre_empresa_interventor'
    )
    nombre_interventor = fields.Char(
        string='Interventor',
        related='contrato_id.nombre_interventor'
    )
    supervisor = fields.Char(
        string='Coordinador EAAB',
        related='contrato_id.supervisor'
    )
    correo_electronico_contratista = fields.Char(
        string='Correo electrónico contratista',
        related='contrato_id.correo_electronico_contratista'
    )
    correo_electronico_interventor = fields.Char(
        string='Correo electrónico interventor',
        related='contrato_id.correo_electronico_interventor'
    )
    correo_electronico_supervisor = fields.Char(
        string='Correo electrónico coordinador EAAB',
        related='contrato_id.correo_electronico_supervisor'
    )
    #INFO Calculo cual fue el ultimo tramite de topografia y desde ahi saco los siguientes datos
    ultima_solicitud_topografia_id = fields.Many2one(
        comodel_name='sigedat.tramite.solicitud',
        ondelete='restrict',
        compute='_compute_ultima_solicitud_topografia'
    )
    #INFO Calculo cual fue el ultimo tramite de record y desde ahi saco los siguientes datos
    ultima_solicitud_sigue_id = fields.Many2one(
        comodel_name='sigedat.tramite.solicitud',
        ondelete='restrict',
        compute='_compute_ultima_solicitud_sigue'
    )
    #INFO Calculo cual fue el ultimo tramite de entrega final y desde ahi saco los siguientes datos
    ultima_solicitud_entrega_final_id = fields.Many2one(
        comodel_name='sigedat.tramite.solicitud',
        ondelete='restrict',
        compute='_compute_ultima_solicitud_entrega_final'
    )
    principal_topografia_id = fields.Many2one(
        string='Entregado a topografía por',
        related='ultima_solicitud_topografia_id.create_uid'
    )
    #FIXME Si son varios revisores, no los tomaria
    revisor_topografia_id = fields.Many2one(
        string='Revisor de topografía',
        related='ultima_solicitud_topografia_id.revisor_id'
    )
    fecha_recepcion_topografia = fields.Datetime(
        string='Fecha recepción Topografía',
        compute='_compute_fecha_recepcion_topografia'
    )
    fecha_asignacion_nivelacion = fields.Date(
        string='Fecha asignación nivelación',
        related='ultima_solicitud_topografia_id.fecha_asignacion_nivelacion'
    )
    topografo_asignado_nivelacion_id = fields.Many2one(
        string='Topografo asignado nivelacion',
        related='ultima_solicitud_topografia_id.topografo_asignado_nivelacion_id'
    )
    fecha_entrega_verificacion_nivelacion = fields.Date(
        string='Fecha entrega verificacion nivelacion',
        related='ultima_solicitud_topografia_id.fecha_entrega_verificacion_nivelacion'
    )
    dias_verificacion_nivelacion_topografia = fields.Integer(
        string='Días verificación nivelación topografía',
        compute='_compute_dias_verificacion_nivelacion_topografia'
    )
    numero_revisiones_topografia = fields.Integer(
        string='Número de revisiones Topografía',
        compute='_compute_numero_revisiones_topografia'
    )
    #INFO Fecha en la que el lider valida la solciitud y es diferente a la fecha en la que el revisor la aprueba
    fecha_validacion_topografia = fields.Date(
        string='Fecha validación final de topografía',
        related='ultima_solicitud_topografia_id.fecha_validacion'
    )
    #FIXME lo calcule como la fecha_validacion_topografia-fecha_recepcion_topografia, ya que asumo que es desde la primera cita
    dias_validacion_topografia = fields.Integer(
        string='Días validación topografía',
        compute='_compute_dias_validacion_topografia'
    )
    principal_sigue_id = fields.Many2one(
        string='Entregado en el sigue por',
        related='ultima_solicitud_sigue_id.create_uid'
    )
    revisor_sigue_id = fields.Many2one(
        string='Revisor de sigue',
        related='ultima_solicitud_sigue_id.revisor_id'
    )
    norte = fields.Char(
        related='ultima_solicitud_entrega_final_id.norte',
    )
    este = fields.Char(
        related='ultima_solicitud_entrega_final_id.este',
    )
    acueducto_3333 = fields.Char(
        related='ultima_solicitud_entrega_final_id.acueducto_3333',
    )
    alcantarillado_2000 = fields.Char(
        related='ultima_solicitud_entrega_final_id.alcantarillado_2000',
    )
    fecha_inicial_revision_sigue = fields.Date(
        string='Fecha inicial revisión Sigue',
        compute='_compute_fecha_inicial_revision_sigue'
    )
    numero_revisiones_sigue = fields.Integer(
        string='Número de revisiones SIGUE',
        compute='_compute_numero_revisiones_sigue'
    )
    # razones por las cuales no han sido aprobada la solicitud
    fecha_validacion_sigue = fields.Date(
        string='Fecha validación final de sigue',
        related='ultima_solicitud_sigue_id.fecha_validacion'
    )
    dias_entrega_sigue = fields.Integer(
        string='Dias entrega Sigue',
        compute='_compute_dias_entrega_sigue'
    )
    observacion = fields.Text(
        related='ultima_solicitud_entrega_final_id.observacion',
    )
    radicado_sigue = fields.Char(
        related='ultima_solicitud_entrega_final_id.radicado_sigue',
    )
    id_sigue = fields.Char(
        related='ultima_solicitud_entrega_final_id.id_sigue',
    )
    numero_obra_acueducto = fields.Char(
        related='ultima_solicitud_entrega_final_id.numero_obra_acueducto',
    )
    numero_obra_alcantarillado = fields.Char(
        related='ultima_solicitud_entrega_final_id.numero_obra_alcantarillado',
    )
    numero_proyecto_acueducto = fields.Char(
        related='ultima_solicitud_entrega_final_id.numero_proyecto_acueducto',
    )
    numero_proyecto_alcantarillado = fields.Char(
        related='ultima_solicitud_entrega_final_id.numero_proyecto_alcantarillado',
    )
    cantidad_planos_acueducto = fields.Integer(
        related='ultima_solicitud_entrega_final_id.acueducto',
    )
    cantidad_planos_alcantarillado_pluvial = fields.Integer(
        related='ultima_solicitud_entrega_final_id.alcantarillado_pluvial',
    )
    cantidad_planos_alcantarillado_sanitario = fields.Integer(
        related='ultima_solicitud_entrega_final_id.alcantarillado_sanitario',
    )
    cantidad_planos_combinado = fields.Integer(
        related='ultima_solicitud_entrega_final_id.combinado',
    )
    #FIXME En el otro formato dice proyectos especiales
    longitud_red_acueducto = fields.Float(
        related='ultima_solicitud_entrega_final_id.longitud_red_acueducto',
    )
    longitud_red_alcantarillado = fields.Float(
        related='ultima_solicitud_entrega_final_id.longitud_red_alcantarillado',
    )
    longitud_red_sanitario = fields.Float(
        related='ultima_solicitud_entrega_final_id.longitud_red_sanitario',
    )
    longitud_red_pluvial = fields.Float(
        related='ultima_solicitud_entrega_final_id.longitud_red_pluvial',
    )
    longitud_red_combinado = fields.Float(
        related='ultima_solicitud_entrega_final_id.longitud_red_combinado',
    )
    cantidad_unidades_medio_magnetico = fields.Char(
        related='ultima_solicitud_entrega_final_id.cantidad_unidades_medio_magnetico',
    )
    fecha_orden_entrega_final = fields.Date(
        string='Fecha orden entrega final',
        related='ultima_solicitud_entrega_final_id.fecha_validacion'
    )

    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"Acuerdo: {r.contrato_id.name}"

    @api.depends('fecha_asignacion_nivelacion', 'fecha_entrega_verificacion_nivelacion')
    def _compute_dias_verificacion_nivelacion_topografia(self):
        for r in self:
            if r.fecha_entrega_verificacion_nivelacion and r.fecha_asignacion_nivelacion:
                r.dias_verificacion_nivelacion_topografia = (r.fecha_entrega_verificacion_nivelacion - r.fecha_asignacion_nivelacion).days
            else:
                r.dias_verificacion_nivelacion_topografia = 0

    @api.depends('fecha_validacion_topografia', 'ultima_solicitud_topografia_id')
    def _compute_dias_validacion_topografia(self):
        for r in self:
            if r.ultima_solicitud_topografia_id.cita_id:
                if r.fecha_validacion_topografia and r.ultima_solicitud_topografia_id.fecha_inicio:
                    r.dias_validacion_topografia = (r.fecha_validacion_topografia - r.ultima_solicitud_topografia_id.fecha_inicio.date()).days
                else:
                    r.dias_validacion_topografia = 0
            else:
                r.dias_validacion_topografia = 0

    @api.depends('fecha_validacion_sigue', 'ultima_solicitud_sigue_id')
    def _compute_dias_entrega_sigue(self):
        for r in self:
            if r.ultima_solicitud_sigue_id.cita_id:
                r.dias_entrega_sigue = (r.fecha_validacion_sigue - r.ultima_solicitud_sigue_id.fecha_inicio.date()).days
            else:
                r.dias_entrega_sigue = 0

    def _compute_plazo(self):
        for r in self:
            r.plazo = (r.fecha_fin - r.fecha_inicio).days
            # if plazo < 30:
            #     r.plazo = f"{plazo} días"
            # elif plazo > 30 and plazo < 365:
            #     r.plazo = f"{plazo/30} meses"
            # else:
            #     r.plazo = f"{plazo/365} años"

    @api.depends('ultima_solicitud_entrega_final_id')
    def _compute_solicitante(self):
        for r in self:
            if r.ultima_solicitud_entrega_final_id:
                r.solicitante_id = r.ultima_solicitud_entrega_final_id.create_uid
            else:
                r.solicitante_id = None

    @api.depends('tramite_id')
    def _compute_fecha_recepcion_topografia(self):
        for r in self:
            revisiones_topografia = r.tramite_id.solicitud_ids.filtered(lambda s: s.tramite_abreviatura == 'revision_topografia').sorted(lambda s: s.create_date)
            r.fecha_recepcion_topografia = revisiones_topografia[0].fecha_inicio if revisiones_topografia else None

    @api.depends('tramite_id')
    def _compute_fecha_inicial_revision_sigue(self):
        for r in self:
            revisiones_sigue = r.tramite_id.solicitud_ids.filtered(lambda s: s.tramite_abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra']).sorted(lambda s: s.create_date)
            r.fecha_inicial_revision_sigue = revisiones_sigue[0].fecha_inicio if revisiones_sigue else None

    @api.depends('tramite_id')
    def _compute_ultima_solicitud_topografia(self):
        for r in self:
            revisiones_topografia = r.tramite_id.solicitud_ids.filtered(lambda s: s.tramite_abreviatura == 'revision_topografia').sorted(lambda s: s.create_date)
            r.ultima_solicitud_topografia_id = revisiones_topografia[-1] if revisiones_topografia else None

    @api.depends('tramite_id')
    def _compute_ultima_solicitud_sigue(self):
        for r in self:
            revisiones_sigue = r.tramite_id.solicitud_ids.filtered(lambda s: s.tramite_abreviatura == 'revision_planos_record').sorted(lambda s: s.create_date)
            r.ultima_solicitud_sigue_id = revisiones_sigue[-1] if revisiones_sigue else None

    @api.depends('tramite_id')
    def _compute_ultima_solicitud_entrega_final(self):
        for r in self:
            revisiones_entrega_final = r.tramite_id.solicitud_ids.filtered(lambda s: s.tramite_abreviatura == 'revision_planos_record_obra').sorted(lambda s: s.create_date)
            r.ultima_solicitud_entrega_final_id = revisiones_entrega_final[-1] if revisiones_entrega_final else None

    @api.depends('ultima_solicitud_topografia_id')
    def _compute_numero_revisiones_topografia(self):
        for r in self:
            if r.ultima_solicitud_topografia_id:
                if r.ultima_solicitud_topografia_id.lista_item_ids:
                    r.numero_revisiones_topografia = r.ultima_solicitud_topografia_id.lista_item_ids[0].version_lista_chequeo
                else:
                    r.numero_revisiones_topografia = 0
            else:
                r.numero_revisiones_topografia = 0

    @api.depends('ultima_solicitud_sigue_id')
    def _compute_numero_revisiones_sigue(self):
        for r in self:
            if r.ultima_solicitud_sigue_id:
                if r.ultima_solicitud_sigue_id.lista_item_ids:
                    r.numero_revisiones_sigue = r.ultima_solicitud_sigue_id.lista_item_ids[0].version_lista_chequeo
                else:
                    r.numero_revisiones_sigue = 0
            else:
                r.numero_revisiones_sigue = 0

    @api.depends('ultima_solicitud_entrega_final_id')
    def _compute_aviso_sap(self):
        for r in self:
            if r.ultima_solicitud_entrega_final_id.cita_id:
                r.aviso_sap = r.ultima_solicitud_entrega_final_id.cita_id.aviso_sap
            else:
                r.aviso_sap = ''

    @api.depends('ultima_solicitud_topografia_id')
    def _compute_numero_lista_chequeo_topografia(self):
        for r in self:
            if r.ultima_solicitud_topografia_id.lista_item_ids:
                r.numero_lista_chequeo_topografia = r.ultima_solicitud_topografia_id.lista_item_ids[0].numero_lista_chequeo
            else:
                r.numero_lista_chequeo_topografia = ''

    @api.depends('ultima_solicitud_sigue_id')
    def _compute_numero_lista_chequeo_sigue(self):
        for r in self:
            if r.ultima_solicitud_sigue_id.lista_item_ids:
                r.numero_lista_chequeo_sigue = r.ultima_solicitud_sigue_id.lista_item_ids[0].numero_lista_chequeo
            else:
                r.numero_lista_chequeo_sigue = ''
