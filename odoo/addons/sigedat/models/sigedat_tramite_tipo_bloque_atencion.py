# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import math

DIAS_SEMANA = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

def obtener_hora_minuto(dato, devolver_tupla=False):
    if not isinstance(dato, float):
        raise ValidationError(f"El valor: {dato} no es un número válido")
    horas = int(math.floor(dato))
    minutos = int(round((dato % 1) * 60))
    #INFO Si minutos = 0, toca rellenar a 00
    if minutos == 0:
        minutos = '00'
    if devolver_tupla:
        return horas,minutos
    else:
        return f"{horas}:{minutos}"


class SigedatTramiteTipoBloqueAtencion(models.Model):
    _name = 'sigedat.tramite.tipo.bloque_atencion'
    _description = 'Bloque de Atención del Trámite'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )
    hora_inicio = fields.Float(
        string='Hora Inicio',
        required=True,
        tracking=True,
    )
    hora_fin = fields.Float(
        string='Hora Fin',
        required=True,
        tracking=True,
    )
    revisor_ids = fields.Many2many(
        string='Revisores',
        comodel_name='sigedat.revisor',
        tracking=True,
    )
    lunes = fields.Boolean(
        string='Lunes',
        required=False,
        tracking=True,
    )
    martes = fields.Boolean(
        string='Martes',
        required=False,
        tracking=True,
    )
    miercoles = fields.Boolean(
        string='Miércoles',
        required=False,
        tracking=True,
    )
    jueves = fields.Boolean(
        string='Jueves',
        required=False,
        tracking=True,
    )
    viernes = fields.Boolean(
        string='Viernes',
        required=False,
        tracking=True,
    )
    sabado = fields.Boolean(
        string='Sábado',
        required=False,
        tracking=True,
    )
    domingo = fields.Boolean(
        string='Domingo',
        required=False,
        tracking=True,
    )
    tipo_tramite_id = fields.Many2one(
        string='Tipo de trámite',
        required=True,
        comodel_name='sigedat.tramite.tipo',
        tracking=True,
        default=lambda self: self._context.get('tipo_tramite_id', False),
    )


    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"{obtener_hora_minuto(r.hora_inicio)} - {obtener_hora_minuto(r.hora_fin)}"
            # disponibilidad = ''
            # for dia in DIAS_SEMANA:
            #     if getattr(r, dia):
            #         disponibilidad += f"{dia}, "[:-2]
            #     r.name = f"{disponibilidad} entre las {obtener_hora_minuto(r.hora_inicio)} y {obtener_hora_minuto(r.hora_fin)}"



    def obtener_hora(self, nombre_atributo, devolver_tupla=False):
        return obtener_hora_minuto(getattr(self, nombre_atributo), devolver_tupla)


    # Aca es donde se hace el filtro de revisor por tipo de cita parala asignación automatica aleatorea por tipo de cita en la creación/agendamiento de cita
    @api.onchange('tipo_tramite_id')
    def _domain_revisores(self):
        if self.tipo_tramite_id:
            return {
                'domain': {
                    'revisor_ids': [('tipo_cita_id', '=', self.tipo_tramite_id.tipo_cita_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'revisor_ids': [('tipo_cita_id', '=', 0)]
                }
            }




    @api.model
    def create(self, values):
        #INFO: Se debe validar que se haya seleccionado algun dia de la semana.
        fue_seleccionado_dia = False
        for dia in DIAS_SEMANA:
            if values.get(dia, False):
                fue_seleccionado_dia = True
        if not fue_seleccionado_dia:
            raise ValidationError("No fue seleccionado ningún día de la semana.")

        #INFO: Se valida que no se solape la hora inicio o fin con otro bloque ya creado para el mismo trámite
        bloques = self.search([('tipo_tramite_id', '=', values['tipo_tramite_id'])])
        for bloque in bloques:
            for dia in DIAS_SEMANA:
                if values.get(dia, False) and getattr(bloque, dia):
                    if ((bloque.hora_inicio <= values['hora_inicio'] and bloque.hora_fin >= values['hora_fin']) or (bloque.hora_inicio <= values['hora_fin'] and bloque.hora_fin >= values['hora_inicio']) or (bloque.hora_inicio > values['hora_inicio'] and bloque.hora_inicio < values['hora_fin'])):
                        raise ValidationError(f"No se puede crear este bloque, ya que se solapa con el bloque: {bloque.id} del día: {dia} en el horario: {bloque.hora_inicio} - {bloque.hora_fin}")
        #INFO Si el nuevo bloque, no se solapa con ningun otro, creelo
        result = super(SigedatTramiteTipoBloqueAtencion, self).create(values)

        return result

