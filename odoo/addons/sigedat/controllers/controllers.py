# -*- coding: utf-8 -*-
from faulthandler import cancel_dump_traceback_later
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home, set_cookie_and_redirect
from odoo.exceptions import ValidationError
from odoo.addons.base_conf.tools.sam import Sam
from odoo.addons.base_conf.tools.validaciones import es_valido_correo_electronico
import hashlib
import json
import logging
import uuid
import werkzeug

_logger = logging.getLogger(__name__)
descripcion_evento = ''
direccion_ip_remota = ''
identificador_peticion = ''
URL_REDIRECCION_INICIO_SESION = '/web'
URL_REDIRECCION_CERRAR_SESION = 'https://www.acueducto.com.co'

#TODO: Se debe completar el listado de los nombres de los grupos que retorna el servicio
MAP_GRUPOS = {
    'Grp_Sige_Admin': {
        'nombre_grupo': 'Administrador',
        'es_interno': True,
    },
    'Grp_Sige_Revisor_Topo': {
        'nombre_grupo': 'Revisor',
        'es_interno': True,
    },
    'Grp_Sige_Revisor_Recod': {
        'nombre_grupo': 'Revisor',
        'es_interno': True,
    },
    'Grp_Sige_Lider': {
        'nombre_grupo': 'Líder Área',
        'es_interno': True,
    },
    'grp_ExtranetHome': {
        'nombre_grupo': 'Pricipal',
        'es_interno': False,
    },
    'grp_ExtranetEmpresa': {
        'nombre_grupo': 'Pricipal',
        'es_interno': False,
    },
}

class Extension_Home(Home):
    '''Extensión de la clase Home, para permitir recibir los parametros de login desde la cabecera.
    '''

    @http.route()
    def web_login(self, redirect=None, **kwargs):
        identificador_peticion = uuid.uuid1()
        direccion_ip_remota = request.httprequest.environ['REMOTE_ADDR']

        try:
            #INFO Tomo el usuario desde la cabecera
            usuario = kwargs.get('usuario')
            grupo = kwargs.get('grupo')
            base = kwargs.get('base')

            if usuario and base and grupo:

                #INFO La clave la calculo basado en el usuario + base
                clave = hashlib.sha224(f"{usuario}+{base}".encode()).hexdigest()
                #INFO Busco al usuario en la BD, si existe, lo dejo pasar, sino lo creo basado en la informacion del SAM y lo dejo pasar

                ################################
                # usuario = 'admin'
                # clave = 'admin'
                ################################
                #INFO Procedo a continuar con el proceso de autenticar al usuario en Odoo
                # INFO: Cierra sesion
                # request.session.logout(keep_db=True)
                uid = request.session.authenticate(base, usuario, clave)
                return set_cookie_and_redirect(URL_REDIRECCION_INICIO_SESION)
            else:
                descripcion_evento = f"No se encontró el inicio de sesión en la cabecera, se procede a pedir los datos para iniciar sesión manualmente."
                _logger.info(f"[{identificador_peticion}] {descripcion_evento}, desde la ip: {direccion_ip_remota}")
                return super(Extension_Home, self).web_login()

        except Exception as e:
            return http.request.render('sigedat.mensaje', {
                    'titulo' : 'Error',
                    'mensaje' : f'Se detectó un error: {e}',
                }
            )


class Sigedat(http.Controller):

    @http.route(['/web/session/logout'], type='http', website=True, methods=['GET'], auth='public', csrf=False)
    def cerrar_sesion(self, **kwargs):
        ''' Método que cierra sesion y redirige a una url especifica.
        '''
        request.session.logout()
        return werkzeug.utils.redirect(URL_REDIRECCION_CERRAR_SESION)

    @http.route(['/sigedat/web/login'], type='http', website=True, methods=['GET'], auth='public', csrf=False)
    def login_terminos_condiciones(self, **kwargs):
        ''' Método que recibe al usuario para aceptar terminos y condiciones.
        '''
        try:
            #INFO Recibo en el header la informacion del usuario
            identificador_peticion = uuid.uuid1()
            direccion_ip_remota = request.httprequest.environ['REMOTE_ADDR']
            identificacion_usuario = request.httprequest.headers.get('iv-user')
            grupo = request.httprequest.headers.get('iv-groups')
            base = request.env['ir.config_parameter'].sudo().get_param('base_conf.base_datos', '')
            #FIXME quemo los datos xa las pruebas, asi q toca borrar xa pasar a prod
            #identificacion_usuario = 'admin'
            #grupo = 'Grp_Sige_Admin'
            #base = 'sigedat'

            if identificacion_usuario and base:
                if not es_valido_correo_electronico(identificacion_usuario):
                    #INFO Asumo que llega directamente el nombre de usuario
                    usuario = identificacion_usuario
                else:
                    #INFO Como es una dirección de correo electronico, solo tomo el nombre del mismo
                    usuario = identificacion_usuario.split('@')[0]

                #INFO La clave la calculo basado en el usuario + base
                clave = hashlib.sha224(f"{usuario}+{base}".encode()).hexdigest()
                #INFO Busco al usuario en la BD, si existe, lo dejo pasar, sino lo creo basado en la informacion del SAM y lo dejo pasar
                usuario_ids = request.env['res.users'].sudo().search([('login', '=', usuario)])

                descripcion_evento = f"Se encontraron los usuarios: {usuario_ids}"
                _logger.info(f"[{identificador_peticion}] {descripcion_evento}, desde la ip: {direccion_ip_remota}")

                #INFO Si el usuario no existe, procedo a crearlo, basado en la informacion del SAM
                if not usuario_ids:
                    if request.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_sam', 'False') == 'False':
                        raise ValidationError(f"No esta activa la conexión con el servidor de SAM, por lo cual no se puede continuar.")

                    cliente = request.env['ir.config_parameter'].sudo().get_param('base_conf.cliente_sam', '')
                    ruta_servicio = request.env['ir.config_parameter'].sudo().get_param('base_conf.url_consultar_usuario_sam', '')
                    token = request.env['ir.config_parameter'].sudo().get_param('base_conf.token_consultar_usuario_sam', '')

                    sam = Sam(cliente, ruta_servicio, token)
                    respuesta = json.loads(sam.buscar_usuario(correo_electronico=identificacion_usuario))

                    descripcion_evento = f"El servicio de SAM, devolvio: {respuesta}"
                    _logger.info(f"[{identificador_peticion}] {descripcion_evento}, desde la ip: {direccion_ip_remota}")

                    if respuesta['status'] != 'ok':
                        descripcion_evento = f"El servicio de SAM, devolvio error: {respuesta['data']}"
                        _logger.error(f"[{identificador_peticion}] {descripcion_evento}, desde la ip: {direccion_ip_remota}")
                        raise ValidationError(f"{respuesta['data']}")
                    else:
                        #INFO Limpiar los datos del pesimo servicio de SAM
                        lista_item = respuesta['data']['data'].replace('}', '').replace('{', '').split(',')
                        datos_usuario = dict([tuple((i.split(':')[0].split('=')[0].strip(), i.split(':')[1].strip())) for i in lista_item])

                        #INFO Si no llego el grupo en el encabezado, trato de obtener el grupo desde el servicio SAM
                        if not grupo:
                            for g in respuesta['data']['gropus']:
                                if g in MAP_GRUPOS:
                                    grupo = g
                        #INFO Si despues de buscar el grupo en el encabezado  y en el servicio SAM, no encontré un grupo válido para el usuario, no lo dejo pasar.
                        if not grupo:
                            descripcion_evento = f"El usuario: {usuario}, no tiene un grupo válido para poder ingresar al sistema SIGEDAT."
                            _logger.error(f"[{identificador_peticion}] {descripcion_evento}, desde la ip: {direccion_ip_remota}")
                            raise ValidationError(f"{descripcion_evento}")

                        # Crear el usuario en odoo con la informacion obtenida del sam
                        partner_id = request.env['res.partner'].sudo().create(
                            {
                                'name': datos_usuario.get('givenname', ''),
                                'email': datos_usuario.get('mail', ''),
                            }
                        )
                        if datos_usuario.get('telexnumber', None):
                            partner_id.sudo().write(
                                {
                                'phone': datos_usuario.get('telexnumber', ''),
                                'mobile': datos_usuario.get('telexnumber', ''),
                                }
                            )
                        try:
                            usuario_id = request.env['res.users'].sudo().create(
                                {
                                    'login': usuario,
                                    'company_id': 1, #INFO Se asigna al EAAB, por defecto
                                    'partner_id': partner_id.id,
                                }
                            )
                        except:
                            pass #INFO Me devuelve una excepcion, sin embargo si lo crea

                        usuario_id.sudo().write(
                            {
                                'password': clave,
                                'state': 'active',

                            }
                        )
                        if not usuario_id:
                            raise ValidationError(f"No fue posible crear el usuario: {usuario}")
                        #INFO Valido si es un usuario externo o interno, basado en el grupo del mismo
                        categoria_id = request.env['ir.module.category'].sudo().search([('name','=','sigedat: Sistema de Gestión de Datos Técnicos')])
                        if categoria_id:
                            informacion_grupo = MAP_GRUPOS.get(grupo, None)
                            # raise ValidationError(f"info: {informacion_grupo}")
                            if informacion_grupo:
                                #INFO Si es un usuario externo, lo creo en el modelo persona
                                if not informacion_grupo.get('es_interno', False):
                                    persona_id = request.env['sigedat.persona'].sudo().create(
                                        {
                                            'usuario_id': usuario_id.id,
                                            'tipo_persona': 'juridica',
                                            'nombre': datos_usuario.get('cn', ''),
                                            'apellido': datos_usuario.get('sn', ''),
                                            'telefono_movil': datos_usuario.get('telexnumber', ''),
                                            'correo_electronico': datos_usuario.get('mail',''),
                                            'habeas_data': True,
                                            'terminos_condiciones': True,
                                        }
                                    )

                            #INFO Asigno el grupo que le corresponde al usuario
                                grupo_usuario_id = request.env['res.groups'].sudo().search([('name','=', MAP_GRUPOS[grupo].get('nombre_grupo', '')),('category_id','=',categoria_id[0].id)])
                            else:
                                descripcion_evento = f"El usuario: {usuario}, no tiene un grupo: {grupo} válido para poder ingresar al sistema SIGEDAT."
                                _logger.error(f"[{identificador_peticion}] {descripcion_evento}, desde la ip: {direccion_ip_remota}")
                                raise ValidationError(f"{descripcion_evento}")
                            if grupo_usuario_id:
                                grupo_usuario_id.users = [(4, usuario_id.id)]

                        else:
                            descripcion_evento = f"No se encontró la categoría de los grupos de seguridad del modulo o no se encontró el grupo: {grupo} que se debe asignar."
                            _logger.error(f"[{identificador_peticion}] {descripcion_evento}, desde la ip: {direccion_ip_remota}")
                            raise ValidationError(f"No se encontró la categoría o el grupo de usuario: {grupo}.")
                else:
                    #FIXME Le asigno la clave que deberia tener, NO SE SI SEA NECESARIO
                    usuario_id = usuario_ids[0]
                    usuario_id.sudo().write(
                            {
                                'password': clave,
                                'state': 'active',
                            }
                        )
            else:
                raise ValidationError(f"No se encontraron los datos para el inicio de sesion.")

            #INFO Envio los datos de iniciar sesión a la plantilla, para que esta posteriormente se los pase al controlador e inicie sesión.
            datos = {
                'usuario': usuario,
                'grupo': grupo,
                'base': base,
                'es_usuario_antiguo': 1 if usuario_ids else 0,
            }

            return http.request.render("sigedat.login", datos)
        except Exception as e:
            return http.request.render('sigedat.mensaje', {
                    'titulo' : 'Error',
                    'mensaje' : f'Se detectó un error: {e}',
                }
            )

    @http.route(['/envelopes/<string:id_carpeta>/notify'], type='http', website=True, methods=['POST'], auth='public', csrf=False)
    def estado_firma_gosign(self, id_carpeta, **kwargs):
        ''' Método que recibira la notificación por parte del servicio de Gosign, informando cuando se complete la recolección de las firmas, de tal forma que el módulo sigedat, pueda descargar el documento firmado y pueda cambiar de estado la solicitud.
        '''
        respuesta = {}
        try:
            datos = json.loads(request.httprequest.data)

            if not 'notificationType' in datos:
                respuesta['outcome'] = 'error'
                respuesta['message'] = f"No tiene los parametros correctos: {datos}"
                raise ValidationError(respuesta)

            if id_carpeta:
                id_solicitud = id_carpeta.split('_')[-1]
                solicitud_id = request.env['sigedat.tramite.solicitud'].search([('id', '=', id_solicitud)])


            if not solicitud_id:
                respuesta['outcome'] = 'error'
                respuesta['message'] = f"No se encontro la solicitud con id: {id_solicitud}"
                raise ValidationError(respuesta)

            if datos.get('notificationType') == 'VA_PROCESS_ENDED':
                respuesta['outcome'] = 'succeeded'
                respuesta['message'] = f"Se confirma la notificación de la solicitud {solicitud_id.name}"
                #INFO Ejecuto el metodo de cambio de estado, el cual se conecta con gosign para traer el archivo firmado, ponerlo en el campo correcto y cambiar de estado el registro
                if solicitud_id:
                    solicitud_id.sudo().wkf__validado_confirmado()
            else:
                respuesta['outcome'] = 'error'
                respuesta['message'] = f"No se han terminado de recolectar las firmas de la solicitud: {solicitud_id.name}"
        except Exception as e:
                respuesta['outcome'] = 'error'
                respuesta['message'] = f"{e.args[0]}"
        finally:
            json.dumps(respuesta)
            return request.make_response(json.dumps(respuesta),
                [
                    ('Content-Type', 'application/json'),
                ]
            )
