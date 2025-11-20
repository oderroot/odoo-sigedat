# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import time, date, timedelta, datetime
from pytz import timezone
import os

class sigedat_wizard_configuracion_general(models.TransientModel):
    _name = 'sigedat.wizard.configuracion_general'
    _description = 'Sigedat - Wizard Configuracion General'

    # -------------------
    # Fields
    # -------------------

    def _default_esta_activa_conexion_gosign(self):
        return self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_gosign', False) == 'True'

    def _default_esta_activa_conexion_sap(self):
        return self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_sap', False) == 'True'

    def _default_esta_activa_conexion_sam(self):
        return self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_sam', False) == 'True'

    def _default_base_datos(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.base_datos', '')

    def _default_etiqueta_firma_1(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.etiqueta_firma_1', '')

    def _default_etiqueta_firma_2(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.etiqueta_firma_2', '')

    def _default_cliente_sam(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.cliente_sam', '')

    def _default_url_consultar_usuario_sam(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.url_consultar_usuario_sam', '')

    def _default_token_consultar_usuario_sam(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.token_consultar_usuario_sam', '')

    def _default_cliente_sap(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.cliente_sap', '')

    def _default_url_validar_aviso_sap(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.url_validar_aviso_sap', '')

    def _default_token_validar_aviso_sap(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.token_validar_aviso_sap', '')

    def _default_url_obtener_contrato_sap(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.url_obtener_contrato_sap', '')

    def _default_token_obtener_contrato_sap(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.token_obtener_contrato_sap', '')

    def _default_usuario_gosign(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.usuario_gosign', '')

    def _default_clave_gosign(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.clave_gosign', '')

    def _default_cliente_oauth_gosign(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.cliente_oauth_gosign', '')

    def _default_secreto_oauth_gosign(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.secreto_oauth_gosign', '')

    def _default_url_obtener_token(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.url_obtener_token_gosign', '')

    def _default_url_firmar_documento(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.url_firmar_documento_gosign', '')

    def _default_url_obtener_documento_firmado(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.url_obtener_documento_firmado_gosign', '')

    def _default_ruta_copia_seguridad(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_conf.ruta_copia_seguridad', '')

    # Grupo plantilla correo
    plantilla_correo_id = fields.Many2one(
        string='Plantilla',
        comodel_name='mail.template',
        ondelete='cascade',
        domain="[('name', 'like', '%SIGEDAT:%')]",
    )
    direccion_correo_remitente = fields.Char(
        string='Correo remitente',
    )
    direccion_correo_destinatario = fields.Char(
        string='Correo destinatario',
    )
    asunto_correo = fields.Char(
        string='Asunto mensaje',
    )
    cuerpo_correo = fields.Text(
        string='Mensaje',
    )
    # Grupo SAM
    esta_activa_conexion_sam = fields.Boolean(
        default=_default_esta_activa_conexion_sam,
        help='Indica si se usaran los servicios de sam con el módulo.'
    )
    cliente_sam = fields.Char(
        string='Cliente SAM',
        required=True,
        default=_default_cliente_sam,
    )
    url_consultar_usuario_sam = fields.Char(
        string='Url consultar usuario SAM',
        required=True,
        default=_default_url_consultar_usuario_sam,
    )
    token_consultar_usuario_sam = fields.Char(
        string='Token consultar usuario SAM',
        required=True,
        default=_default_token_consultar_usuario_sam,
    )
    # Grupo SIGEDAT
    base_datos = fields.Char(
        string='Base de datos',
        required=True,
        default=_default_base_datos,
    )
    # Grupo SAP
    esta_activa_conexion_sap = fields.Boolean(
        default=_default_esta_activa_conexion_sap,
        help='Indica si se usaran los servicios de sap con el módulo.'
    )
    cliente_sap = fields.Char(
        string='Cliente SAP',
        required=True,
        default=_default_cliente_sap,
    )
    url_validar_aviso_sap = fields.Char(
        string='Url validar aviso SAP',
        required=True,
        default=_default_url_validar_aviso_sap,
    )
    token_validar_aviso_sap = fields.Char(
        string='Token validar aviso SAP',
        required=True,
        default=_default_token_validar_aviso_sap,
    )
    url_obtener_contrato_sap = fields.Char(
        string='Url obtener contrato SAP',
        required=True,
        default=_default_url_obtener_contrato_sap,
    )
    token_obtener_contrato_sap = fields.Char(
        string='Token obtener contrato SAP',
        required=True,
        default=_default_token_obtener_contrato_sap,
    )
    # Grupo GoSign
    esta_activa_conexion_gosign = fields.Boolean(
        default=_default_esta_activa_conexion_gosign,
        help='Indica si se usaran los servicios de GoSign con el módulo.'
    )
    usuario_gosign = fields.Char(
        string='Usuario Gosign',
        required=True,
        default=_default_usuario_gosign,
    )
    clave_gosign = fields.Char(
        string='Clave Gosign',
        required=True,
        default=_default_clave_gosign,
    )
    cliente_oauth_gosign = fields.Char(
        string='Cliente OAuth Gosign',
        required=True,
        default=_default_cliente_oauth_gosign,
    )
    secreto_oauth_gosign = fields.Char(
        string='Secreto OAuth Gosign',
        required=True,
        default=_default_secreto_oauth_gosign,
    )
    url_obtener_token = fields.Char(
        string='Url obtener token',
        required=True,
        default=_default_url_obtener_token,
    )
    url_firmar_documento = fields.Char(
        string='Url firmar documento',
        required=True,
        default=_default_url_firmar_documento,
    )
    url_obtener_documento_firmado = fields.Char(
        string='Url obtener documento',
        required=True,
        default=_default_url_obtener_documento_firmado,
    )
    etiqueta_firma_1 = fields.Char(
        string='Etiqueta a buscar para la firma del revisor',
        required=True,
        default=_default_etiqueta_firma_1,
    )
    etiqueta_firma_2 = fields.Char(
        string='Etiqueta a buscar para la firma del líder',
        required=True,
        default=_default_etiqueta_firma_2,
    )
    # Grupo copia de seguridad
    ruta_copia_seguridad = fields.Char(
        string='Ruta a la carpeta de copia de seguridad',
        required=True,
        default=_default_ruta_copia_seguridad,
    )

    @api.onchange('plantilla_correo_id')
    def _onchange_plantilla_correo_id(self):
        if self.plantilla_correo_id:
            self.direccion_correo_remitente = self.plantilla_correo_id.email_from
            self.direccion_correo_destinatario = self.plantilla_correo_id.email_to
            self.asunto_correo = self.plantilla_correo_id.subject
            self.cuerpo_correo = self.plantilla_correo_id.body_html

    def guardar_configuracion(self):

        if self.plantilla_correo_id and self.direccion_correo_remitente and self.direccion_correo_destinatario and self.asunto_correo and self.cuerpo_correo:
            self.plantilla_correo_id.email_from = self.direccion_correo_remitente
            self.plantilla_correo_id.email_to = self.direccion_correo_destinatario
            self.plantilla_correo_id.subject = self.asunto_correo
            self.plantilla_correo_id.body_html = self.cuerpo_correo

        self.env['ir.config_parameter'].sudo().set_param('sigedat.esta_activa_conexion_gosign', str(self.esta_activa_conexion_gosign))
        self.env['ir.config_parameter'].sudo().set_param('sigedat.esta_activa_conexion_sap', str(self.esta_activa_conexion_sap))
        self.env['ir.config_parameter'].sudo().set_param('sigedat.esta_activa_conexion_sam', str(self.esta_activa_conexion_sam))

        #INFO Guarda la configuración de SIGEDAT
        if self.base_datos:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.base_datos', self.base_datos)
        #INFO Guarda la configuración de sam
        if self.cliente_sam:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.cliente_sam', self.cliente_sam)
        if self.url_consultar_usuario_sam:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.url_consultar_usuario_sam', self.url_consultar_usuario_sam)
        if self.token_consultar_usuario_sam:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.token_consultar_usuario_sam', self.token_consultar_usuario_sam)
        #INFO Guarda la configuración de sap
        if self.cliente_sap:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.cliente_sap', self.cliente_sap)
        if self.url_validar_aviso_sap:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.url_validar_aviso_sap', self.url_validar_aviso_sap)
        if self.token_validar_aviso_sap:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.token_validar_aviso_sap', self.token_validar_aviso_sap)
        if self.url_obtener_contrato_sap:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.url_obtener_contrato_sap', self.url_obtener_contrato_sap)
        if self.token_obtener_contrato_sap:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.token_obtener_contrato_sap', self.token_obtener_contrato_sap)
        #INFO Guarda la configuración de gosign
        if self.usuario_gosign:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.usuario_gosign', self.usuario_gosign)
        if self.clave_gosign:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.clave_gosign', self.clave_gosign)
        if self.cliente_oauth_gosign:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.cliente_oauth_gosign', self.cliente_oauth_gosign)
        if self.secreto_oauth_gosign:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.secreto_oauth_gosign', self.secreto_oauth_gosign)
        if self.url_obtener_token:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.url_obtener_token_gosign', self.url_obtener_token)
        if self.url_firmar_documento:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.url_firmar_documento_gosign', self.url_firmar_documento)
        if self.url_obtener_documento_firmado:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.url_obtener_documento_firmado_gosign', self.url_obtener_documento_firmado)
        if self.etiqueta_firma_1:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.etiqueta_firma_1', self.etiqueta_firma_1)
        if self.etiqueta_firma_2:
            self.env['ir.config_parameter'].sudo().set_param('base_conf.etiqueta_firma_2', self.etiqueta_firma_2)
            # Guarda configuración de la copia de seguridad
        if self.ruta_copia_seguridad:
            if self.ruta_copia_seguridad.endswith(os.sep):
                self.ruta_copia_seguridad = self.ruta_copia_seguridad[:-1]
            self.env['ir.config_parameter'].sudo().set_param('base_conf.ruta_copia_seguridad', self.ruta_copia_seguridad)