# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import re
from odoo.addons.base_conf.tools.validaciones import es_valido_caracteres_alfabeticos_con_espacios, es_valido_correo_electronico, es_valido_caracteres_alfanumericos, es_anio_valido, es_valido_numero
from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO
from odoo.addons.base_conf.tools.sap import Sap
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

LISTA_TIPO_RECORD = [
                        ('disenio', 'Diseño'),
                        ('obra', 'Obra'),
                        # ('disenio_obra', 'Diseño y obra'),
                    ]
MIN_ANIO = 2000
MAX_ANIO = 2022
MAX_ANIO = datetime.today().year

class sigedat_wizard_crear_contrato(models.TransientModel):
    _name = 'sigedat.wizard.crear_contrato'
    _description = 'Sigedat - Wizard Crear Contrato'

    # -------------------
    # Fields
    # -------------------
    tipo_id = fields.Many2one(
        string='Tipo',
        required=True,
        comodel_name='sigedat.contrato.tipo',
    )
    tipo = fields.Char(
        related='tipo_id.abreviatura'
    )
    #INFO Grupo Acuerdo
    numero = fields.Char(
        string='Número',
        help='Por favor ingrese solo el número completo, sin caracteres como guiones o puntos',
    )
    anio = fields.Char(
        string='Año',
        size=4,
    )
    fecha_inicio = fields.Date(
        string='Fecha inicio',
    )
    fecha_fin = fields.Date(
        string='Fecha fin',
    )
    objeto = fields.Text(
        string='Objeto',
    )
    tipo_record = fields.Selection(
        string='Tipo record',
        selection=LISTA_TIPO_RECORD,
    )
    numero_disenio = fields.Char(
        string='Número de diseño',
        size=255,
    )
    #INFO Grupo Contratista
    empresa_contratista = fields.Char(
        string='Nombre',
        size=255,
    )
    correo_electronico_contratista = fields.Char(
        string='Correo electrónico',
        size=100,
    )
    telefono_contratista = fields.Char(
        string='Teléfono',
        size=10,
    )
    #INFO Grupo Supervisor
    area_id = fields.Many2one(
        string='Área',
        comodel_name='sigedat.area',
    )
    supervisor = fields.Char(
        string='Nombre',
        size=255,
    )
    correo_electronico_supervisor = fields.Char(
        string='Correo electrónico',
        size=100,
    )
    #INFO Grupo Interventoría
    tiene_interventoria = fields.Selection(
        string='Tiene interventoria',
        selection=LISTA_SI_NO,
        default='no',
    )
    contrato_interventoria = fields.Char(
        string='Contrato interventoría',
        size=255,
    )
    nombre_empresa_interventor = fields.Char(
        string='Nombre empresa',
        size=255,
    )
    nombre_interventor = fields.Char(
        string='Nombre contacto',
        size=255,
    )
    correo_electronico_interventor = fields.Char(
        string='Correo electrónico',
        size=100,
    )
    telefono_interventor = fields.Char(
        string='Teléfono',
        size=10,
    )
    prefijo_acueducto = fields.Selection(
        string='Prefijo acueducto',
        selection=[
            ('1-01', '1-01'),
            ('1-02', '1-02'),
            ('1-05', '1-05'),
            ('2-01', '2-01'),
            ('2-02', '2-02'),
            ('2-05', '2-05'),
        ]
    )
    tiene_frente = fields.Selection(
        string='¿Tiene frente?',
        required=True,
        selection=LISTA_SI_NO,
        default='no',
    )
    es_contrato_sap = fields.Boolean(
        default=False,
    )
    numero_contrato = fields.Char(
    )


    def crear_contrato(self):
        contrato = {
                'tipo_id': self.tipo_id.id,
            }

        #INFO Determino las validaciones que se deben hacer y el origen de la Información, basado en el tipo de acuerdo
        if self.tipo == 'idu':
            #INFO: Se agrega el prefijo IDU, 4 Números y el año en 4 digitos. p.e. IDU-0000-AÑO

            #INFO Valido el año ingresado
            #TODO Se debe crear una ventana de configuracion para ajustar la fecha
            if es_anio_valido(self.anio, MIN_ANIO, MAX_ANIO):
                self.numero_contrato = f"IDU-{self.numero}-{self.anio}"
                if len(self.numero) != 4:
                    self.numero = ''
                    raise ValidationError(f"El número del contrato no es válido, el número debe tener 4 digitos")

                contrato['name'] = self.numero_contrato or ''
            else:
                self.numero = ''
                raise ValidationError(f"El año debe estar entre {MIN_ANIO} y {MAX_ANIO}")
            if self.numero_disenio:
                contrato['numero_disenio'] = self.numero_disenio
        elif self.tipo == 'carta_compromiso':
            #INFO: Trae la Información del servicio de SAP, con prefijo 999, 5 Números - 5 Números y el año en 4 digitos. 9-99-00000-00000-AÑO
            #
            #INFO Valido el año ingresado
            if es_anio_valido(self.anio, MIN_ANIO, MAX_ANIO):
                self.numero_contrato = f"9-99-{self.numero[:5]}-{self.numero[5:]}-{self.anio}"
                if len(self.numero) not in [9, 10]:
                    self.numero = ''
                    raise ValidationError(f"El número del acuerdo no es válido, el número debe tener entre 9 y 10 digitos")

                contrato['name'] = self.numero_contrato or ''
        elif self.tipo == 'acueducto':
            #INFO Trae la Información del servicio de SAP, con prefijo 1/2-01/02, 5 Números - 5 Números y el año en 4 digitos. p.e. 1/2-01/02-00000-00000-AÑO
            prefijo = self.prefijo_acueducto
            anio = self.anio
            self.numero_contrato = f"{prefijo}-{self.numero[:5]}-{self.numero[5:]}-{anio}"

            #INFO Valido el año ingresado
            if es_anio_valido(self.anio, MIN_ANIO, MAX_ANIO):
                if len(self.numero) not in [9, 10]:
                    self.numero = ''
                    raise ValidationError(f"El número del acuerdo no es válido, el número debe tener entre 9 y 10 digitos")

                contrato['name'] = self.numero_contrato or ''
        elif self.tipo == 'disponibilidad_servicio':
            #INFO Trae la Información del servicio de SAP
            self.numero_contrato = f"{self.numero}"

            contrato['name'] = self.numero_contrato or ''
        elif self.tipo == 'convenio':
            #INFO Sin ninguna validación y se ingresa la Información de forma manual
            self.numero_contrato = f"{self.numero}"

            contrato['name'] = self.numero_contrato or ''

            if self.numero_disenio:
                contrato['numero_disenio'] = self.numero_disenio

        if self.env['sigedat.contrato'].search([('name', '=', self.numero_contrato)]):
            raise ValidationError(f'El número de contrato: {self.numero_contrato}, ya esta registrado en el sistema.')
        contrato.update(
            {
                'objeto': self.objeto,
                'fecha_inicio': self.fecha_inicio,
                'fecha_fin': self.fecha_fin,
                'tipo_record': self.tipo_record,
                'empresa_contratista': self.empresa_contratista,
                'correo_electronico_contratista': self.correo_electronico_contratista,
                'telefono_contratista': self.telefono_contratista,
                'area_id': self.area_id.id,
                'supervisor': self.supervisor,
                'correo_electronico_supervisor': self.correo_electronico_supervisor,
                'tiene_frente': self.tiene_frente,
            }
        )
        if self.tiene_interventoria == 'si':
                contrato.update(
                    {
                        'contrato_interventoria': self.contrato_interventoria,
                        'nombre_empresa_interventor': self.nombre_interventor,
                        'nombre_interventor': self.nombre_interventor,
                        'correo_electronico_interventor': self.correo_electronico_interventor,
                        'telefono_interventor': self.telefono_interventor,
                    }
                )
        try:
            contrato_id = self.env['sigedat.contrato'].create(contrato)
        except Exception as e:
            raise ValueError(f"No fue posible crear el acuerdo: {contrato} por: {e}")

        return {
            'name': 'Nuevo Acuerdo',
            'res_model': 'sigedat.contrato',
            'res_id': contrato_id.id,
            'context': {},
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
        }

    def obtener_contrato_sap(self):
        self.es_contrato_sap = False
        if self.numero and self.anio:
            if self.tipo == 'acueducto':
                if self.prefijo_acueducto:
                    self.numero_contrato = f"{self.prefijo_acueducto}-{self.numero[:5]}-{self.numero[5:]}-{self.anio}"
                    self.es_contrato_sap = True
                else:
                    raise ValidationError(f"No se ingreso el número completo del contrato.")
            elif self.tipo == 'carta_compromiso':
                self.numero_contrato = f"9-99-{self.numero[:5]}-{self.numero[5:]}-{self.anio}"
                self.es_contrato_sap = True
        elif self.tipo == 'disponibilidad_servicio' and self.numero:
            self.numero_contrato = f"{self.numero}"
            self.es_contrato_sap = True
        else:
            raise ValidationError(f"No se diligencio el número del acuerdo o el año del mismo.")
        #INFO Obtengo la Información del acuerdo desde el servicio web
        if self.es_contrato_sap:
            if self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_sap', 'False') == 'True':
                sap = Sap('SIGEDAT')
                respuesta = sap.obtener_contrato(self.numero_contrato)
                if "mensajeError" in respuesta:
                    raise ValidationError(f"Ocurrió un error: {respuesta} al consultar la información del contrato: {self.numero_contrato}")
                else:
                    #INFO Asumo que la respuesta es correcta
                    try:
                        self.fecha_inicio = datetime.strptime(respuesta.get("FECHA_INICIO", ''), "%Y-%m-%d")
                        plazo_valor = respuesta.get("PLAZO", '').get("PLAZO")
                        plazo_unidad = respuesta.get("PLAZO", '').get("UNIDAD_PLAZO")
                        if plazo_unidad == '1':
                            #INFO Dias
                            self.fecha_fin = self.fecha_inicio + relativedelta(days=+int(plazo_valor))
                        elif plazo_unidad == '2':
                            #INFO Meses
                            self.fecha_fin = self.fecha_inicio + relativedelta(months=+int(plazo_valor))
                        elif plazo_unidad == '3':
                            #INFO Años
                            self.fecha_fin = self.fecha_inicio + relativedelta(years=+int(plazo_valor))
                    except Exception:
                        #INFO Si la fecha viene mal del servicio, simplemene no pongo nada en la fecha inicial, ni calculo la final
                        pass
                    # try:
                    #     tipo_contrato = int(respuesta.get("TIPO", '').get("CLASE"))
                    # except Exception:
                    #     raise ValidationError(f"El tipo de contrato: {respuesta.get('TIPO', '').get('CLASE')}")

                    # if tipo_contrato == 1:
                    #     self.tipo_record = 'obra'
                    # elif tipo_contrato == 2:
                    #     self.tipo_record = 'disenio'
                    # else:
                    #     self.tipo_record = 'disenio_obra'

                    self.objeto = respuesta.get("OBJETO", '').get("OBJETO1")
                    self.empresa_contratista = respuesta.get("CONTRATISTA").get("NOMBRE")
                    self.correo_electronico_contratista = respuesta.get("CONTRATISTA").get("CORREO")
                    self.telefono_contratista = respuesta.get("CONTRATISTA").get("TELEFONO")
                    self.supervisor = respuesta.get("SUPERVISOR").get("NOMBRE")
                    self.correo_electronico_supervisor = respuesta.get("SUPERVISOR").get("CORREO")
                    self.tiene_interventoria = 'si' if respuesta.get("INTERVENTOR", '').get("CONTRATO") else 'no'
                    if self.tiene_interventoria == 'si':
                        self.contrato_interventoria = respuesta.get("INTERVENTOR").get("CONTRATO")
                        self.nombre_empresa_interventor = respuesta.get("INTERVENTOR").get("NOMBRE")
                        self.telefono_interventor = respuesta.get("INTERVENTOR").get("TELEFONO")
            else:
                raise ValidationError("No esta habilitada la conexión con el servicio de SAP, por favor habilítela, e intente nuevamente.")
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'sigedat.wizard.crear_contrato',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }


    @api.onchange('tipo_id')
    def _onchange_tipo_id(self):
        if self.tipo_id:
            esta_activa_conexion_sap = self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_sap', False) == 'True'
            if not esta_activa_conexion_sap and self.tipo_id.informacion_viene_desde_sap:
                raise ValidationError("Esta deshabilitada la conexión con el servicio web de SAP, por lo cual no puede seleccionar un tipo de acuerdo que se deba consultar en SAP.")


    @api.onchange('fecha_inicio')
    def _onchange_fecha_inicio(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio >= self.fecha_fin:
                raise ValidationError(f'{self.fecha_inicio}, no puede ser mayor que la fecha fin: {self.fecha_fin}.')


    @api.onchange('fecha_fin')
    def _onchange_fecha_fin(self):
        if self.fecha_fin and self.fecha_fin:
            if self.fecha_fin <= self.fecha_inicio:
                raise ValidationError(f'{self.fecha_inicio}, no puede ser mayor que la fecha fin: {self.fecha_fin}.')


    @api.onchange('anio')
    def _onchange_anio(self):
        if self.anio:
            if not es_anio_valido(self.anio, MIN_ANIO, MAX_ANIO):
                anio = self.anio
                self.anio = None
                raise ValidationError(f'{anio}, no es un año válido, el valor del año debe estar comprendido entre: {MIN_ANIO} y {MAX_ANIO}.')


    @api.onchange('empresa_contratista')
    def _onchange_empresa_contratista(self):
        if self.empresa_contratista:
            if not es_valido_caracteres_alfanumericos(self.empresa_contratista):
                raise ValidationError(f'{self.empresa_contratista}, no es un nombre de empresa válido.')


    # @api.onchange('supervisor')
    # def _onchange_supervisor(self):
    #     if self.supervisor:
    #         if not es_valido_caracteres_alfabeticos_con_espacios(self.supervisor):
    #             raise ValidationError(f'{self.supervisor}, no es un nombre válido.')

    # @api.onchange('nombre_interventor')
    # def _onchange_nombre_interventor(self):
    #     if self.nombre_interventor:
    #         if not es_valido_caracteres_alfabeticos_con_espacios(self.nombre_interventor):
    #             raise ValidationError(f'{self.nombre_interventor}, no es un nombre válido.')


    @api.onchange('telefono_contratista')
    def _onchange_telefono_contratista(self):
        if self.telefono_contratista:
            if not es_valido_numero(self.telefono_contratista, minimo=2000000):
                raise ValidationError(f'{self.telefono_contratista} no es un número de teléfono válido. Los números fijos se componen de 7 números sin indicativo y los moviles de 10.')

    @api.onchange('telefono_interventor')
    def _onchange_telefono_interventor(self):
        if self.telefono_interventor:
            if not es_valido_numero(self.telefono_interventor, minimo=2000000):
                raise ValidationError(f'{self.telefono_interventor} no es un número de teléfono válido. Los números fijos se componen de 7 números sin indicativo y los moviles de 10.')

    @api.onchange('numero')
    def _onchange_numero(self):
        if self.numero and not self.tipo:
            raise ValidationError(f"Se debe establecer primero el tipo de acuerdo, antes de ingresar el número.")
        if self.tipo and self.numero:
            if self.tipo == 'idu':
                if not self.numero.isdigit():
                    self.numero = ''
                    raise ValidationError(f"El número ingresado: {self.numero}, no es válido. Por favor revisar la estructura del acuerdo basado en el tipo de acuerdo.")
                if len(self.numero) != 4:
                    self.numero = ''
                    raise ValidationError(f"El número del acuerdo: {self.numero}, no es válido. Por favor revisar la estructura de acuerdo basado en el tipo de acuerdo.")
            elif self.tipo in ['carta_compromiso', 'acueducto', ]:
                if not self.numero.isdigit():
                    self.numero = ''
                    raise ValidationError(f"El número ingresado: {self.numero}, no es válido. Por favor revisar la estructura de acuerdo basado en el tipo de acuerdo.")
                if len(self.numero) not in [9, 10]:
                    raise ValidationError(f"El número del acuerdo: {self.numero}, no es válido. Por favor revisar la estructura de acuerdo basado en el tipo de acuerdo.")

    @api.onchange('correo_electronico_interventor')
    def _onchange_correo_electronico_interventor(self):
        if self.correo_electronico_interventor:
            if not es_valido_correo_electronico(self.correo_electronico_interventor.lower()):
                self.correo_electronico_interventor = ''
                raise ValidationError(f"La dirección de correo electrónico ingresado no es válido")

    @api.onchange('correo_electronico_supervisor')
    def _onchange_correo_electronico_supervisor(self):
        if self.correo_electronico_supervisor:
            if not es_valido_correo_electronico(self.correo_electronico_supervisor.lower()):
                self.correo_electronico_supervisor = ''
                raise ValidationError(f"La dirección de correo electrónico ingresado no es válido")

    @api.onchange('correo_electronico_contratista')
    def _onchange_correo_electronico_contratista(self):
        if self.correo_electronico_contratista:
            if not es_valido_correo_electronico(self.correo_electronico_contratista.lower()):
                self.correo_electronico_contratista = ''
                raise ValidationError(f"La dirección de correo electrónico ingresado no es válido")