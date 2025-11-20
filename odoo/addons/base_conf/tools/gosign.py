# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json
from base64 import b64encode

class BearerAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

class Gosign():

    def __init__(self, usuario, clave, cliente_oauth, secreto_oauth, url_obtener_token):
        self.usuario = usuario
        self.clave = clave
        self.cliente_oauth = cliente_oauth
        self.secreto_oauth = secreto_oauth
        self.sistema_generador = 'ACU'
        self.url_obtener_token = url_obtener_token
        #TODO toca crear los parametros del sistema xa usuario, clave, cliente_oauth, secreto_oauth, servidor, url_endpoint obtener token, consultar carpeta, insertar documento
        # set_param = self.env['ir.config_parameter'].sudo().set_param
        # set_param('base_conf_url_ws_firma', self.url_ws_firma)

    def obtener_token(self):
        # ruta_servicio_obtener_token = f'https://gosigncl-be.infocert.it/gosign/oauth/token?grant_type=password&username={self.usuario}&password={self.clave}&client_id={self.cliente_oauth}&client_secret={self.cliente_oauth}'
        if not self.url_obtener_token:
            raise ValidationError('No esta configurada la url del servicio de GoSign para obtener el token')

        ruta_servicio_obtener_token = self.url_obtener_token.format(self.usuario, self.clave, self.cliente_oauth, self.secreto_oauth)

        response = requests.post(ruta_servicio_obtener_token)
        if response.status_code == 200 and response.text:
            try:
                respuesta = json.loads(response.text)
                if 'access_token' in respuesta:
                    return respuesta['access_token']
                else:
                    raise ValidationError(f'No se obtuvo el token al consultar el servicio.')
            except Exception as e:
                raise ValidationError(f'Hubo un error: {e} al consultar el servicio.')
        else:
            raise ValidationError(f'El servicio devolvió un código: {response.status_code} con error: {response.text}')

    def obtener_carpeta(self, id_carpeta):
        self.token = self.obtener_token()
        ruta_servicio_obtener_carpeta = f'https://gosigncl-be.infocert.it/gosign/secure/oauth/api/v2/envelopes/{id_carpeta}/withDocuments'
        response = requests.get(ruta_servicio_obtener_carpeta, auth=BearerAuth(self.token))
        if response.status_code == 200 and response.text:
            try:
                return json.loads(response.text)
            except Exception as e:
                raise ValidationError(f'Hubo un error: {e} al consultar el servicio.')
        else:
            raise ValidationError(f'El servicio devolvió un código: {response.status_code} con error: {response.text}')

    def agregar_documento(self, url_firmar_documento, asunto_carpeta, titulo_documento, id_carpeta, documento, persona_firma_1, persona_firma_2='', texto_firma='Por favor, revise el documento y firme', etiqueta_firma_1='', etiqueta_firma_2='',ubicacion_firma_1="TOP_RIGHT_NORTH_EAST", ubicacion_firma_2="TOP_RIGHT_NORTH_EAST", modo_envio="IMMEDIATE", nivel_seguridad="INTERNAL_PDF", tipo_carpeta='CORPORATE', es_prioritario=True):
        self.token = self.obtener_token()
        ruta_servicio_enviar_documento_firma = f'https://gosigncl-be.infocert.it/gosign/secure/oauth/api/v2/envelopes?='
        Doc1_Content = documento.decode('ascii')
        headers={
            'Content-type':'application/json',
            'Accept':'application/json'
        }
        datos = {
            "envelope": {
                "useType": tipo_carpeta,
                "externalId": f"{id_carpeta}",
                "subject": f"{asunto_carpeta} - {id_carpeta}",
                "sysGenerator": self.sistema_generador,
                "sendingMode": modo_envio,
                "trustLevel": nivel_seguridad,
                "starred": es_prioritario,
                "expirationFirstReminder": 1,
                "expireAt": 1630360800000,
                "confString": None,
                "joinDocuments": None,
                "documents": [
                    {
                        "externalId": f"{id_carpeta}_01",
                        "title": f"{titulo_documento}",
                        "mimeType": "application/pdf",
                        "originalFname": "nombre_archivo.pdf",
                        "uri": None,
                        "bytes": f"{Doc1_Content}"
                    }
                ],
                "docClass": None,
                "commonMessages": {
                    "text": f"{texto_firma}",
                    "userMessages": None
                },
                "procDef": {
                    "tasks": []
                }
            },
            "responseWithEnvelope": False
        }
        # INFO Si se especifica la etiqueta para la firma, asumo que la firma es por etiqueta y no por imagen
        if persona_firma_1:
            if etiqueta_firma_1:
                datos["envelope"]["procDef"]["tasks"].append(
                    {
                        "type": "HUMAN",
                        "confString":
                            "{\"receiveInvitationMailToSign\":true,\"receiveCompletedEnvelopeMail\":false}",
                        "order": 1,
                        "actorExpr": f"{persona_firma_1}U",
                        "action": "WORK",
                        "howMany": 1,
                        "signatureType": "SIMPLE",
                        "actionDefs": [
                            {
                                "docExternalId": f"{id_carpeta}_01",
                                "type": "SIGN",
                                "mandatory": True,
                                "confString": "{\"customSignatureText\":\"Solo firme si esta deacuerdo\"}",
                                "appearance": {
                                    "invisible": False,
                                    "annotationContent": None,
                                    "tagAppearance": {
                                        "cornerType": "SINGLE_BOTTOM_LEFT_CORNER_TYPE",
                                        "startTagPattern": f"{etiqueta_firma_1}",
                                        "xoffset": 0,
                                        "yoffset": 0
                                    }
                                }
                            }
                        ]
                    }
                )
            else:
                datos["envelope"]["procDef"]["tasks"].append(
                    {
                        "type": "HUMAN",
                        "confString":
                            "{\"receiveInvitationMailToSign\":true,\"receiveCompletedEnvelopeMail\":false}",
                        "order": 1,
                        "actorExpr": f"{persona_firma_1}U",
                        "action": "WORK",
                        "howMany": 1,
                        "signatureType": "SIMPLE",
                        "actionDefs": [
                            {
                                "docExternalId": f"{id_carpeta}_01",
                                "type": "SIGN",
                                "mandatory": True,
                                "confString": "{\"customSignatureText\":\"Solo firme si esta deacuerdo\"}",
                                "appearance": {
                                    "invisible": False,
                                    "annotationContent": None,
                                    "compassAppearance": {
                                        "page": -2,
                                        "position": f"{ubicacion_firma_1}"
                                    },
                                }
                            }
                        ]
                    }
                )
        if persona_firma_2:
            if etiqueta_firma_2:
                datos["envelope"]["procDef"]["tasks"].append(
                    {
                        "type": "HUMAN",
                        "confString":
                            "{\"receiveInvitationMailToSign\":true,\"receiveCompletedEnvelopeMail\":false}",
                        "order": 1,
                        "actorExpr": f"{persona_firma_2}U",
                        "action": "WORK",
                        "howMany": 1,
                        "signatureType": "SIMPLE",
                        "actionDefs": [
                            {
                                "docExternalId": f"{id_carpeta}_01",
                                "type": "SIGN",
                                "mandatory": True,
                                "confString": "{\"customSignatureText\":\"Solo firme si esta deacuerdo\"}",
                                "appearance": {
                                    "invisible": False,
                                    "annotationContent": None,
                                    "tagAppearance": {
                                        "cornerType": "SINGLE_BOTTOM_LEFT_CORNER_TYPE",
                                        "startTagPattern": f"{etiqueta_firma_2}",
                                        "xoffset": 0,
                                        "yoffset": 0
                                    }
                                }
                            }
                        ]
                    }
                )
            else:
                datos["envelope"]["procDef"]["tasks"].append(
                    {
                        "type": "HUMAN",
                        "confString":
                            "{\"receiveInvitationMailToSign\":true,\"receiveCompletedEnvelopeMail\":false}",
                        "order": 1,
                        "actorExpr": f"{persona_firma_2}U",
                        "action": "WORK",
                        "howMany": 1,
                        "signatureType": "SIMPLE",
                        "actionDefs": [
                            {
                                "docExternalId": f"{id_carpeta}_01",
                                "type": "SIGN",
                                "mandatory": True,
                                "confString": "{\"customSignatureText\":\"Solo firme si esta deacuerdo\"}",
                                "appearance": {
                                    "invisible": False,
                                    "annotationContent": None,
                                    "compassAppearance": {
                                        "page": -2,
                                        "position": f"{ubicacion_firma_2}"
                                    },
                                }
                            }
                        ]
                    }
                )

        # datos = {
        #     "envelope": {
        #         "useType": tipo_carpeta,
        #         "externalId": f"{id_carpeta}",
        #         "subject": f"{asunto_carpeta} - {id_carpeta}",
        #         "sysGenerator": self.sistema_generador,
        #         "sendingMode": modo_envio,
        #         "trustLevel": nivel_seguridad,
        #         "starred": es_prioritario,
        #         "expirationFirstReminder": 1,
        #         "expireAt": 1630360800000,
        #         "confString": None,
        #         "joinDocuments": None,
        #         "documents": [
        #             {
        #                 "externalId": f"{id_carpeta}_01",
        #                 "title": f"Enviado desde python: {id_carpeta}",
        #                 "mimeType": "application/pdf",
        #                 "originalFname": "nombre_archivo.pdf",
        #                 "uri": None,
        #                 "bytes": f"{Doc1_Content}"
        #             }
        #         ],
        #         "docClass": None,
        #         "commonMessages": {
        #             "text": f"Por favor, revise los documentos {id_carpeta} y firme",
        #             "userMessages": None
        #         },
        #         "procDef": {
        #             "tasks": [
        #                 {
        #                     "type": "HUMAN",
        #                     "confString":
        #                         "{\"receiveInvitationMailToSign\":false,\"receiveCompletedEnvelopeMail\":false}",
        #                     "order": 1,
        #                     "actorExpr": f"{persona_firma_1}U",
        #                     "action": "WORK",
        #                     "howMany": 1,
        #                     "certType": "I",
        #                     "signatureType": "SIMPLE",
        #                     "actionDefs": [
        #                         {
        #                             "docExternalId": f"{id_carpeta}_01",
        #                             "type": "SIGN",
        #                             "mandatory": True,
        #                             "confString": "{\"customSignatureText\":\"Solo firme si esta deacuerdo\"}",
        #                             "appearance": {
        #                                 "compassAppearance": {
        #                                     "page": -2,
        #                                     "position": "TOP_RIGHT_NORTH_EAST"
        #                                 },
        #                                 "invisible": False,
        #                                 "annotationContent": None
        #                             }
        #                         }
        #                     ]
        #                 },
        #                 {
        #                 "type": "HUMAN",
        #                 "confString": "{\"receiveInvitationMailToSign\":false,\"receiveCompletedEnvelopeMail\":false}",
        #                 "order":2,
        #                 "actorExpr": f"{persona_firma_2}U",
        #                 "action": "WORK",
        #                 "howMany": 1,
        #                 "certType": "I",
        #                 "actionDefs": [
        #                     {
        #                         "docExternalId": f"{id_carpeta}_01",
        #                         "type": "SIGN",
        #                         "mandatory": True,
        #                         "confString": "{\"customSignatureText\":\"Solo firme si esta deacuerdo(python)\"}",
        #                         "appearance": {
        #                             "compassAppearance": {
        #                                 "page": -2,
        #                                 "position": "BOTTOM_LEFT_SOUTH_WEST"
        #                             },
        #                             "invisible": False,
        #                             "annotationContent": None
        #                         }
        #                     }
        #                 ]
        #             },
        #             ]
        #         }
        #     },
        #     "responseWithEnvelope": False
        # }
        response = requests.post(ruta_servicio_enviar_documento_firma, auth=BearerAuth(self.token), json=datos, headers=headers)
        if response.status_code == 200 and response.text:
            try:
                respuesta = json.loads(response.text)
                return respuesta
            except Exception as e:
                raise ValidationError(f'Hubo un error: {e} al consultar el servicio.')
        else:
            raise ValidationError(f'El servicio devolvió un código: {response.status_code} con error: {response.text}')