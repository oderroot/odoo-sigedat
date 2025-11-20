# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import time, date, timedelta, datetime
from pytz import timezone
from workalendar.america import Colombia
from odoo.addons.base_conf.tools.sap import Sap
import math


cal = Colombia()
DIAS_SEMANA = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
NUM_DIAS_MOSTRAR_AGENDAMIENTO = 30



def get_hora(dato):
    horas = int(math.floor(dato))
    minutos = int(round((dato % 1) * 60))
    if minutos == 0:
        minutos = '00'
    return f"{horas + 5}:{minutos}"


class sigedat_wizard_agendar_cita(models.TransientModel):
    _name = 'sigedat.wizard.agendar_cita'
    _description = 'Sigedat - Wizard Agendar Cita'

    def _compute_fecha_disponible(self):
        hoy = date.today()
        dia_actual = hoy.weekday()
        fechas = []

        id_solicitud = self.env.context.get('active_id')
        solicitud_id = self.env['sigedat.tramite.solicitud'].browse([id_solicitud])
        tramite_id = solicitud_id.tramite_id
        id_tipo_tramite = solicitud_id.tipo_tramite_id.id

        if not solicitud_id:
            raise ValidationError(f"Error al consultar la solicitud de trámite.")
        #INFO Por defecto se deben tener en cuenta, todos los revisores en la busqueda de citas, a menos que sea una cita para un trámite devuelto
        # Ahora se debe fijar que el revisor no esté agendado
        # permitir_otros_revisores = True
        #INFO Si el agendamiento es para una solicitud de un trámite ya devuelto, se debe procurar que lo atienda el mismo revisor de la solicitud anterior

        #INFO Para que el sistema trate de asignar el mismo revisor de una solicitud anterior del mismo tipo de tramite, se quita esta condición
        # if solicitud_id.fue_devuelto:
        #INFO Obtengo el revisor de la ultima solicitud de trámite, para poder filtrar las fechas que ese revisor tiene disponible
        permitir_otros_revisores = False
        revisor_id = None


        # Si hay una solicitud anterior en el mismo tramite del mismo tipo de tramite, trae el revisor, si no permite traer otros revisores:
        try:
            # revisor_id = tramite_id.solicitud_ids.filtered(lambda s: s.state == 'revision_con_observaciones')[-1].revisor_id
            # Por ahora se deja el mismo revisor del último trámite del mismo tipo de trámite
            revisor_id = tramite_id.solicitud_ids.filtered(lambda s: s.tipo_tramite_id.id == id_tipo_tramite)[-1].revisor_id
        except Exception:
            permitir_otros_revisores = True

        #trae los bloques del revisor de la solicitud anterior del mismo tramite y tipo de tramite, si no hay bloques, debe permitir otro revisor
        if revisor_id:
            bloque_ids = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', id_tipo_tramite), ('revisor_ids', 'in', revisor_id.id)])
            #INFO Si la busqueda de disponibilidad para el revisor, no devolvio nada, debe hacer la busqueda normal, para todos los revisores
            if not bloque_ids:
                permitir_otros_revisores = True
        else:
            permitir_otros_revisores = True


        if permitir_otros_revisores:
            bloque_ids = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', id_tipo_tramite)])
        if not permitir_otros_revisores:
            revisor_bloque_ids = [revisor_id]
        else:
            revisor_bloque_ids = bloque_ids.mapped('revisor_ids')

        dias_atencion = set()
        es_primera_semana = True

        #INFO Obtengo un listado de los dias de atencion
        for bloque in bloque_ids:
            for dia in DIAS_SEMANA:
                if getattr(bloque, dia):
                    dias_atencion.add(dia)
        i=0
        dia_disponible = False
        fechas_cargadas = []
        while(True):
            if es_primera_semana:
                for dia in DIAS_SEMANA[dia_actual:]:
                    if dia in dias_atencion:
                        fecha = hoy + timedelta(days=i)
                        for revisor_id in revisor_bloque_ids:
                            if revisor_id.no_disponibilidad_ids.filtered(lambda nd: nd.fecha_inicio <= fecha and nd.fecha_fin >= fecha):
                                dia_disponible = False
                                continue
                            #INFO Solo se agregan las fechas, si el revisor esta libre ese dia
                            # fecha_ = fecha
                            cita_revisor_dia_ids = self.env['sigedat.cita'].search([('revisor_id', '=', revisor_id.id), ('fecha_inicio', '=', fecha), ('fecha_fin', '=', fecha)])
                            if not cita_revisor_dia_ids:
                                dia_disponible = True
                                break
                            else:
                                dia_disponible = False
                        if cal.is_working_day(fecha) and dia_disponible:
                            if fecha < hoy + timedelta(days=15):
                                if fecha.strftime("%d/%m/%Y") not in fechas_cargadas:
                                    fechas_cargadas.append(fecha.strftime("%d/%m/%Y"))
                                    fechas.append((i, fecha.strftime("%d/%m/%Y")))
                    i += 1
                es_primera_semana = False

            else:
                for dia in DIAS_SEMANA:
                    if dia in dias_atencion:
                        fecha = hoy + timedelta(days=i)
                        for revisor_id in revisor_bloque_ids:
                            if revisor_id.no_disponibilidad_ids.filtered(lambda nd: nd.fecha_inicio <= fecha and nd.fecha_fin >= fecha):
                                if revisor_id.no_disponibilidad_ids.filtered(lambda nd: nd.fecha_inicio <= fecha and nd.fecha_fin >= fecha):
                                    dia_disponible = False
                                    continue
                                #INFO Solo se agregan las fechas, si el revisor esta libre ese dia
                                cita_revisor_dia_ids = self.env['sigedat.cita'].search([('revisor_id', '=', revisor_id.id), ('fecha_inicio', '=', fecha), ('fecha_fin', '=', fecha)])
                                if not cita_revisor_dia_ids:
                                    dia_disponible = True
                                    break
                                else:
                                    dia_disponible = False

                            if cal.is_working_day(fecha) and dia_disponible:
                                if fecha < hoy + timedelta(days=15):
                                    if fecha.strftime("%d/%m/%Y") not in fechas_cargadas:
                                        fechas_cargadas.append(fecha.strftime("%d/%m/%Y"))
                                        fechas.append((i, fecha.strftime("%d/%m/%Y")))
                    i += 1
            if i >= NUM_DIAS_MOSTRAR_AGENDAMIENTO:
                break

        self.revisor_id = revisor_id.id

        return fechas




    # -------------------
    # Fields
    # -------------------

    mensaje = fields.Text(
        string='Mensaje',
    )
    solicitud_tramite_id = fields.Many2one(
        string='Solicitud de trámite',
        comodel_name='sigedat.tramite.solicitud',
        required=True,
        default=lambda self: self._context.get('solicitud_tramite_id', False),
    )
    tipo_cita_id = fields.Many2one(
        string='Tipo Cita',
        comodel_name='sigedat.cita.tipo',
        required=True,
        default=lambda self: self._context.get('tipo_cita_id', False),
    )
    tipo_tramite_id = fields.Many2one(
        string='Tipo trámite',
        comodel_name='sigedat.tramite.tipo',
        required=True,
        default=lambda self: self._context.get('tipo_tramite_id', False),
    )
    fecha_disponible = fields.Selection(
        _compute_fecha_disponible,
        string='Fecha Disponible',
        required=True,
    )
    bloque_id = fields.Many2one(
        string='Hora disponible',
        comodel_name='sigedat.tramite.tipo.bloque_atencion',
        required=True,
    )
    aviso_sap = fields.Char(
        string='Aviso sap',
        # required=True,
    )
    revisor_id = fields.Many2one(
        string='Revisor Asignado',
        comodel_name='sigedat.revisor',
    )
    # es_admin = fields.Boolean(
    #     string='Es Administrador',
    #     # compute=lambda self: self.env.user.has_group('sigedat.administrador')
    # )



    # def _compute_es_admin(self):
    #     self.es_admin = self.env.user.has_group('sigedat.administrador')


    @api.onchange('aviso_sap')
    def _onchange_aviso_sap(self):
        # #INFO: Valido que el número sap, solo tenga 9 caracteres alfanumericos
        # if self.aviso_sap:
        #     if not self.aviso_sap.isdigit():
        #         raise ValidationError(f"El aviso sap esta compuesto solo por números.")
        #     if len(self.aviso_sap) != 9:
        #         raise ValidationError(f"El aviso sap esta compuesto por 9 digitos de la forma: 4000#####.")
        #     if self.aviso_sap[:4] != '4000':
        #         raise ValidationError(f"El aviso sap esta compuesto por 9 digitos de la forma: 4000#####.")
        #     if self.env['sigedat.cita'].search([('aviso_sap', '=', self.aviso_sap)]):
        #         self.aviso_sap = ' '
        #         raise ValidationError(f"Este número de aviso sap, ya fue usado en una cita anterior.")
        #     #INFO: Consulta el aviso en sap
        #     if self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_sap', 'False') == 'True':
        #         sap = Sap('SIGEDAT')
        #         respuesta = sap.es_valido_aviso(f"000{self.aviso_sap}")
        #         if not 'OK' in respuesta:
        #             raise ValidationError(f"Ocurrio un problema: {respuesta} al consumir el servicio de SAP.")
        #         elif respuesta.get('OK') != 'X':
        #             raise ValidationError(f"No existe el aviso sap: {self.aviso_sap}")
        pass


    def get_bloques(self):
        tipo_tramite_id = self.env.context.get('tipo_tramite_id', 0)
        dia_seleccionado = date.today() + timedelta(days=self.fecha_disponible)
        bloque_ids = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', tipo_tramite_id)]).filtered(lambda b: getattr(b, DIAS_SEMANA[dia_seleccionado.weekday()]) == True)
        bloques = []
        revisores_tipo_tramite = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', tipo_tramite_id)]).mapped('revisor_ids')
        for bloque in bloque_ids:
            hora_i = get_hora(bloque.hora_inicio)
            hora_f = get_hora(bloque.hora_fin)
            fecha_inicial = f"{dia_seleccionado} {hora_i}:00"
            fecha_final = f"{dia_seleccionado} {hora_f}:00"
            citas_revisor_id = self.env['sigedat.cita'].search([('revisor_id', 'in', revisores_tipo_tramite.ids), ('fecha_inicio', '=', fecha_inicial), ('fecha_fin', '=', fecha_final)])
            if len(citas_revisor_id) >= len(revisores_tipo_tramite):
                continue
            else:
                bloques.append(bloque.id)
        return bloques


    @api.onchange('fecha_disponible')
    def _onchange_fecha_disponible(self):
        self._compute_fecha_disponible()
        #self._compute_es_admin()
        self.bloque_id = None
        bloques = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', self.tipo_tramite_id.id)])
        dias_atencion = ''
        if not bloques:
            raise ValidationError(f'No se encontraron bloques para el trámite: {self.tipo_tramite_id.name} configurados.')
        else:
            for bloque in bloques:
                dias_atencion += f"{bloque.name}; "
        self.mensaje = f"Sr usuario recuerde que el trámite: {self.tipo_tramite_id.name} tiene los horarios de atención: {dias_atencion}"[:-2]

        #INFO Calculo las horas a mostrar, dependiendo de la fecha seleccionada
        #FIXME Aparecen las horas de los bloques configurados, pero no deben aparecer las horas de los bloques que no tienen ningun revisor asignado
        if self.fecha_disponible:
            # hoy = date.today()
            # tipo_tramite_id = self.env.context.get('tipo_tramite_id', 0)
            # dia_seleccionado = hoy + timedelta(days=self.fecha_disponible)
            # Filtra los días entre semana:
            bloques = self.get_bloques()
            # bloque_ids = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', tipo_tramite_id)]).filtered(lambda b: getattr(b, DIAS_SEMANA[dia_seleccionado.weekday()]) == True)
            # bloques = []
            # revisores_tipo_tramite = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', tipo_tramite_id)]).mapped('revisor_ids')
            # for bloque in bloque_ids:
            #     hora_i = get_hora(bloque.hora_inicio)
            #     hora_f = get_hora(bloque.hora_fin)
            #     fecha_inicial = f"{dia_seleccionado} {hora_i}:00"
            #     fecha_final = f"{dia_seleccionado} {hora_f}:00"
            #     citas_revisor_id = self.env['sigedat.cita'].search([('revisor_id', 'in', revisores_tipo_tramite.ids), ('fecha_inicio', '=', fecha_inicial), ('fecha_fin', '=', fecha_final)])
            #     if len(citas_revisor_id) >= len(revisores_tipo_tramite):
            #         continue
            #     else:
            #         bloques.append(bloque.id)
            return {'domain': {'bloque_id': [('id', 'in', bloques)]}}
        else:
            return {'domain': {'bloque_id': [('id', 'in', [])]}}



    @api.onchange('bloque_id')
    def _onchange_bloque_id(self):
        # Revisar según el bloque seleccionado que revisor está disponible, es decir que no tenga citas que se crucen con los bloques seleccionados
        if self.bloque_id:
            hora_inicio = time(self.bloque_id.obtener_hora('hora_inicio', devolver_tupla=True)[0], int(self.bloque_id.obtener_hora('hora_inicio', devolver_tupla=True)[1]))
            hora_fin = time(self.bloque_id.obtener_hora('hora_fin', devolver_tupla=True)[0], int(self.bloque_id.obtener_hora('hora_fin', devolver_tupla=True)[1]))
            #convertir estas fecchas datetime.time a datetime
            hora_inicio = datetime.combine(datetime.now(), hora_inicio)
            hora_fin = datetime.combine(datetime.now(), hora_fin)

            #INFO Hay citas programadas para el rango de fecha y hora?
            citas = self.env['sigedat.cita'].search([('fecha_inicio', '>=', str(hora_inicio)), ('fecha_fin', '<=', str(hora_fin)), ('state', '!=', 'cancelada')])
            # todos_los_revisores = self.env['sigedat.revisor'].search([])
            bloques = self.get_bloques()
            # revisores_tipo_tramite = self.env['sigedat.tramite.tipo.bloque_atencion'].search([('tipo_tramite_id', '=', tipo_tramite_id)]).mapped('revisor_ids')
            revisores_tipo_tramite = self.env['sigedat.tramite.tipo.bloque_atencion'].browse(bloques).mapped('revisor_ids')
            revisores_tipo_tramite_ids = revisores_tipo_tramite.ids
            for cita in citas:
                if cita.revisor_id.id in revisores_tipo_tramite_ids:
                    revisores_tipo_tramite_ids.remove(cita.revisor_id.id)

            if revisores_tipo_tramite_ids:
                self.revisor_id = revisores_tipo_tramite_ids[0]
            else:
               self.revisor_id = None 




    def agendar_cita(self):
        if not self.bloque_id.revisor_ids:
            raise ValidationError(f"El bloque: {self.bloque_id.name}, no tiene revisores asignados.")
        hoy = date.today()
        hora_cero = time(0, 0)
        tz = timezone('UTC')
        hora_inicio = time(self.bloque_id.obtener_hora('hora_inicio', devolver_tupla=True)[0], int(self.bloque_id.obtener_hora('hora_inicio', devolver_tupla=True)[1]))
        hora_fin = time(self.bloque_id.obtener_hora('hora_fin', devolver_tupla=True)[0], int(self.bloque_id.obtener_hora('hora_fin', devolver_tupla=True)[1]))
        #INFO Hay citas programadas para el mismo acuerdo y trámite en estado agendado?
        cita_ids = self.env['sigedat.cita'].search([('tipo_id', '=', self.tipo_cita_id.id), ('state', '=', 'agendada'), ('tramite_id','=', self.solicitud_tramite_id.tramite_id.id)])
        if cita_ids:
            raise ValidationError(f"Ya existen citas agendadas con el tipo de cita: {self.tipo_cita_id.name} para la solicitud: {self.solicitud_tramite_id.name}, por lo cual no es posible agendar más citas por el momento.")
        #INFO Fechas usadas para hacer el filtrado de citas en el dia
        fecha_inicio_cero = datetime.combine(hoy + timedelta(days=int(self.fecha_disponible)), hora_cero)
        fecha_fin_cero = datetime.combine(hoy + timedelta(days=int(self.fecha_disponible)), hora_cero)
        #INFO Obtengo la fecha basado en la fecha y hora seleccionada y la localizo a Colombia
        fecha_inicio_cita = datetime.combine(hoy + timedelta(days=int(self.fecha_disponible)), hora_inicio)
        fecha_fin_cita = datetime.combine(hoy + timedelta(days=int(self.fecha_disponible)), hora_fin)
        #INFO Hay citas programadas para el mismo trámite a la misma hora o que se solapen?
        cita_ids = self.env['sigedat.cita'].search([('tipo_id', '=', self.tipo_cita_id.id), ('fecha_inicio', '>=', fecha_inicio_cita), ('fecha_fin', '<=', fecha_fin_cita), ('state', '!=', 'cancelada')])
        revisor_ocupado_ids = None
        if cita_ids:
            #INFO Obtengo los revisores ocupados en ese horario
            revisor_ocupado_ids = cita_ids.mapped('revisor_id.id')

        #TODO: Asignar el revisor, de acuerdo a la disponibilidad de los mismos
        lista_revisores_disponibles = []
        revisor_seleccionado_id = None

        if self.solicitud_tramite_id.fue_devuelto:
            try:
                revisor_seleccionado_id = self.solicitud_tramite_id.tramite_id.solicitud_ids.filtered(lambda s: s.state == 'revision_con_observaciones')[-1].revisor_id
            except Exception:
                revisor_seleccionado_id = None
            if revisor_seleccionado_id:
                #INFO Valido la no disponibilidad del revisor, si no, debo contemplar a los demas revisores
                for no_disponible_id in revisor_seleccionado_id.no_disponibilidad_ids:
                    no_disponible_inicio = datetime.combine(no_disponible_id.fecha_inicio, hora_cero)
                    no_disponible_fin = datetime.combine(no_disponible_id.fecha_fin, hora_cero)
                    if fecha_fin_cita <= no_disponible_inicio or fecha_inicio_cita >= no_disponible_fin:
                        if not revisor_ocupado_ids:
                            lista_revisores_disponibles.append(revisor_seleccionado_id)
                        elif revisor_seleccionado_id.id not in revisor_ocupado_ids:
                            lista_revisores_disponibles.append(revisor_seleccionado_id)

        if not lista_revisores_disponibles:
            for revisor_id in self.bloque_id.revisor_ids:
                #INFO Si el revisor no tiene 'no disponiblilidades', se agrega de una vez a la lista de disponibles
                if not revisor_id.no_disponibilidad_ids:
                    lista_revisores_disponibles.append(revisor_id)
                #INFO Verifico la 'no disponibilidad' del revisor
                for no_disponible_id in revisor_id.no_disponibilidad_ids:
                    no_disponible_inicio = datetime.combine(no_disponible_id.fecha_inicio, hora_cero)
                    no_disponible_fin = datetime.combine(no_disponible_id.fecha_fin, hora_cero)
                    if fecha_fin_cita <= no_disponible_inicio or fecha_inicio_cita >= no_disponible_fin:
                        if not revisor_ocupado_ids:
                            lista_revisores_disponibles.append(revisor_id)
                        elif revisor_id.id not in revisor_ocupado_ids:
                            lista_revisores_disponibles.append(revisor_id)

        if not lista_revisores_disponibles:
            raise ValidationError(f"No se encontró disponibilidad de revisor para la cita con fecha de inicio: {fecha_inicio_cita.astimezone(tz).strftime('%d/%m/%Y %H:%M')} y fecha fin: {fecha_fin_cita.astimezone(tz).strftime('%d/%m/%Y %H:%M')}")
        if revisor_seleccionado_id:
            #INFO Busco la citas que pueda tener el revisor preseleccionado
            cita_dia_ids = self.env['sigedat.cita'].search([('fecha_inicio', '=', fecha_inicio_cita + timedelta(hours=5)), ('fecha_fin', '=', fecha_fin_cita + timedelta(hours=5)), ('revisor_id', '=', revisor_seleccionado_id.id), ('state', '=', 'agendada')])
            #INFO Si tiene citas para la misma fecha, procedo a buscar citas con los otros revisores disponibles
            if cita_dia_ids:
                revisor_seleccionado_id = None

        #INFO Si no hay un revisor preseleccionado, busco las citas que tienen los revisores disponibles en el dia, para verificar cual es el que tiene menos citas y asignarsela a el
        revisor_con_menos_citas = {}
        if not revisor_seleccionado_id:
            cita_dia_ids = self.env['sigedat.cita'].search([('fecha_inicio', '<=', fecha_inicio_cero), ('fecha_fin', '<=', fecha_fin_cero),])
            # revisor_con_menos_citas['revisor'] = revisor_seleccionado_id.id

            for revisor_id in lista_revisores_disponibles:
                if not revisor_con_menos_citas:
                    revisor_con_menos_citas = {
                        'revisor': revisor_id,
                        'cantidad_citas': len(cita_dia_ids.filtered(lambda c: c.revisor_id.id == revisor_id.id))
                    }
                elif revisor_con_menos_citas['cantidad_citas'] >= len(cita_dia_ids.filtered(lambda c: c.revisor_id.id == revisor_id.id)):
                    revisor_con_menos_citas = {
                        'revisor': revisor_id,
                        'cantidad_citas': len(cita_dia_ids.filtered(lambda c: c.revisor_id.id == revisor_id.id))
                    }
        else:
            revisor_con_menos_citas['revisor'] = revisor_seleccionado_id
        cita = {
            #INFO Se debe indicar sumar explicitamente las 5 horas de diferencia, ya que el guarda por defecto en UTC y no deja localizar la hora a Colombia
            'fecha_inicio': fecha_inicio_cita + timedelta(hours=5),
            'fecha_fin': fecha_fin_cita + timedelta(hours=5),
            'tipo_id': self.tipo_cita_id.id,
            'solicitud_tramite_id': self.solicitud_tramite_id.id,
            'aviso_sap': self.aviso_sap or '',
            'revisor_id': revisor_con_menos_citas['revisor'].id,
            'mensaje_confirmacion_cita': f"Su cita fue agendada para el: {fecha_inicio_cita.astimezone(tz).strftime('%d/%m/%Y')} de: {fecha_inicio_cita.astimezone(tz).strftime('%H:%M')} a {fecha_fin_cita.astimezone(tz).strftime('%H:%M')}",
        }
        try:
            cita_id = self.env['sigedat.cita'].create(cita)
            #INFO Despues de agendar la cita, cambio el estado de la solicitud a pendiente de revision
            self.solicitud_tramite_id.wkf__pendiente_revision()
        except Exception as e:
            raise UserError(f"Error al agendar la cita: {e}")
        self.solicitud_tramite_id.cita_id = cita_id.id

        mensaje = f"Su cita {self.tipo_tramite_id.name} con número {cita_id.id} fue agendada para el: {fecha_inicio_cita.astimezone(tz).strftime('%d/%m/%Y')} de: {fecha_inicio_cita.astimezone(tz).strftime('%H:%M')} a {fecha_fin_cita.astimezone(tz).strftime('%H:%M')}. \n\n"
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sigedat.wizard.mostrar_mensaje',
            'view_mode': 'form',
            'target': 'new',
            'context': {'mensaje': mensaje},
        }
