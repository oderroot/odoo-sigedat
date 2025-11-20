# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json
from base64 import b64encode

class Sap():

    def __init__(self, cliente):
        self.cliente = cliente
        #TODO toca crear los parametros del sistema xa usuario, clave, cliente_oauth, secreto_oauth, servidor, url_endpoint obtener token, consultar carpeta, insertar documento
        # set_param = self.env['ir.config_parameter'].sudo().set_param
        # set_param('base_conf_url_ws_firma', self.url_ws_firma)

    def es_valido_aviso(self, numero):
        ruta_servicio_validar_aviso = 'https://www.acueducto.com.co/wastestmod2/CallRFCSAPWS/resources/rfc/consultazmmvalidaraviso'
        token = '2GkoABTAIN1oqGMIj5pIXA=='
        
        datos = {
            "NUMERO": numero,
            "appName": self.cliente,
            "token": token,
            "ipRequest": ''
        }
        response = requests.post(ruta_servicio_validar_aviso, json=datos)
        if response.status_code == 200 and response.text:
            try:
                return json.loads(response.text)
            except Exception as e:
                raise ValidationError(f'Hubo un error: {e} al consultar el servicio.')
        else:
            raise ValidationError(f'El servicio devolvió un código de error: {response.status_code}')

    def obtener_contrato(self, numero):
        ruta_servicio_obtener_contrato = 'https://www.acueducto.com.co/wastestmod2/CallRFCSAPWS/resources/rfc/consultazmmcontrato'
        token = '7Ei2vkPcK3Hlsm0yJIwIDQ=='
        ip_cliente = ''

        datos = {
            "NUMERO": numero,
            "appName": self.cliente,
            "token": token,
            "ipRequest": ''
        }
        response = requests.post(ruta_servicio_obtener_contrato, json=datos)
        response.encoding = 'utf-8-sig'
        if response.status_code == 200 and response.text:
            try:
                return json.loads(response.text)
            except Exception as e:
                raise ValidationError(f'Hubo un error: {e} al consultar el servicio.')
        else:
            raise ValidationError(f'El servicio devolvió un código de error: {response.status_code}')