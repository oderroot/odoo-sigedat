# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json
from base64 import b64encode

class Sam():

    def __init__(self, cliente, ruta_servicio, token):
        self.cliente = cliente
        self.ruta_servicio = ruta_servicio
        self.token = token

    def buscar_usuario(self, correo_electronico):
        if not correo_electronico:
            raise ValidationError(f"No se estableció el correo electrónico por el cual buscar al usuario.")

        datos = {
            "appName": self.cliente,
            "userLogin": correo_electronico,
            "token": self.token,
        }
        try:
            response = requests.post(self.ruta_servicio, json=datos)
            if response.status_code == 200 and response.text:
                respuesta = json.loads(response.text)
                raise ValidationError(f"sam: {respuesta}")
                if 'msgError' in respuesta:
                    raise ValidationError(f"Ocurrió un problema: {respuesta['msgError']} al consumir el servicio del SAM.")
                else:
                    return json.dumps(
                        {
                            'status': 'ok',
                            'data': respuesta,
                        }
                    )
            else:
                raise ValidationError(f'El servicio devolvió un código: {response.status_code}, con error: {response.text}')
        except Exception as e:
            return json.dumps(
                {
                    'status': 'error',
                    'data': f'{e}'
                }
            )
