# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from tempfile import template
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from base64 import b64encode, b64decode
from datetime import timedelta, datetime
import logging
import shutil
import os
from odoo.addons.base_conf.tools.reportes import Reporte
from odoo.addons.base_conf.tools.utilitarios import normalizar_cadena, LISTA_SI_NO, crear_imagen_en_disco_desde_memoria, obtener_lista_fraccionada
from odoo.addons.base_conf.tools.mail import enviar_mensaje_con_plantilla
from odoo.addons.base_conf.tools.archivos import comprimir_carpeta
from odoo.addons.base_conf.tools.gosign import BearerAuth, Gosign


_logger = logging.getLogger(__name__)
RUTA_BASE = '/tmp'
RUTA_CARPETA_TRABAJO="/tmp/img_reporte"
ANCHO_MAXIMO_IMAGEN = 800
ALTO_MAXIMO_IMAGEN = 350



class SigedatTramiteSolicitud(models.Model):
    _name = 'sigedat.tramite.solicitud'
    _description = 'Solicitud de trámite'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    tramite_id = fields.Many2one(
        string='Trámite',
        comodel_name='sigedat.tramite',
        tracking=True,
        required=True,
        default=lambda self: self._context.get('tramite_id', False),
    )
    name = fields.Char(
        string='Número',
        compute='_compute_name',
    )
    contrato_id = fields.Many2one(
        string='Acuerdo',
        comodel_name='sigedat.contrato',
        related='tramite_id.contrato_id',
    )
    numero_contrato = fields.Char(
        string='Número acuerdo',
        related='contrato_id.name'
    )
    objeto_contrato = fields.Text(
        related='contrato_id.objeto',
    )
    tiene_frente = fields.Selection(
        string='¿Tiene frente?',
        related='contrato_id.tiene_frente',
    )
    frente_id = fields.Many2one(
        string='Frente',
        comodel_name='sigedat.frente',
        related='tramite_id.frente_id',
    )
    empresa_contratista = fields.Char(
        related='contrato_id.empresa_contratista',
    )
    correo_electronico_contratista = fields.Char(
        related='contrato_id.correo_electronico_contratista'
    )
    telefono_contratista = fields.Char(
        related='contrato_id.telefono_contratista'
    )
    area_id = fields.Many2one(
        string="Área",
        related='contrato_id.area_id'
    )
    tipo_cita_id = fields.Many2one(
        string='Tipo de cita',
        comodel_name='sigedat.cita.tipo',
        tracking=True,
        required=True,
        readonly=True,
        states={
            'temporal': [('readonly', False),]
            }
    )
    tipo_tramite_id = fields.Many2one(
        string='Tipo de trámite',
        comodel_name='sigedat.tramite.tipo',
        tracking=True,
        required=True,
        readonly=True,
        states={
            'temporal': [('readonly', False),]
            }
    )
    tramite_abreviatura = fields.Char(
        string='tramite_abreviatura',
        related='tipo_tramite_id.abreviatura'
    )
    state = fields.Selection(
        string='Estado',
        selection=[
            ('temporal', 'Temporal'),
            ('creado', 'Creado'),
            ('pendiente_revision', 'Pendiente de revisión'),
            ('en_revision', 'En revisión'),
            ('revision_en_espera', 'Revisión en espera'),
            ('revision_con_observaciones', 'Revisión con observaciones'),
            ('orden_entrega_final', 'Con orden de entrega final'),
            ('en_aprobacion', 'En validación'),
            ('devolucion_aprobacion', 'Devolución validacion'),
            ('validado', 'Validado'),
            ('validado_confirmado', 'Validado confirmado'),
            ('rechazado', 'Rechazado'),
            ('cancelado', 'Cancelado'),
        ],
        default='temporal',
        tracking=True,
    )
    #INFO Pestaña Documentos
    documento_ids = fields.One2many(
        string='Documentos',
        comodel_name='sigedat.documento',
        inverse_name='solicitud_tramite_id',
        tracking=True,
    )
    #INFO Pestaña Lista Chequeo
    lista_item_ids = fields.One2many(
        string='Lista de chequeo',
        comodel_name='sigedat.lista_chequeo.item',
        inverse_name='solicitud_tramite_id',
        tracking=True,
    )
    #INFO Pestaña Cita Agendada
    cita_id = fields.Many2one(
        string='Cita',
        comodel_name='sigedat.cita',
        ondelete='cascade',
        tracking=True,
    )
    id_cita = fields.Integer(
        related='cita_id.id',
    )
    mensaje_confirmacion_cita = fields.Text(
        string='Mensaje cita',
        related='cita_id.mensaje_confirmacion_cita'
    )
    fecha_inicio = fields.Datetime(
        string='Fecha inicio',
        related='cita_id.fecha_inicio',
    )
    fecha_fin = fields.Datetime(
        string='Fecha fin',
        related='cita_id.fecha_fin',
    )
    revisor_id = fields.Many2one(
        related='cita_id.revisor_id'
    )
    es_asesoria = fields.Boolean(
        string='Es asesoria',
        compute='_compute_es_asesoria'
    )
    comprimido = fields.Binary(
        attachment=True
    )
    comprimido_nombre = fields.Char(
        string='Comprimido nombre',
    )
    #INFO Pestaña Datos de aprobación
    #INFO Grupo General
    aprobado_id = fields.Many2one(
        string='Aprobado por',
        comodel_name='sigedat.revisor',
        ondelete='cascade',
    )
    fecha_aprobacion = fields.Date(
        string='Fecha aprobación',
    )
    validado_id = fields.Many2one(
        string='Validado por',
        comodel_name='res.users',
        ondelete='cascade',
    )
    fecha_validacion = fields.Date(
        string='Fecha validación',
    )
    formato_lista_chequeo = fields.Binary(
        string='Lista chequeo',
        attachment=True
    )
    formato_lista_chequeo_nombre = fields.Char(
    )
    aplica_topografia = fields.Selection(
        related='tramite_id.aplica_topografia',
        # string='¿El proyecto aplica para topografía?',
        # selection=LISTA_SI_NO,
    )
    #INFO Grupo IGAC
    notas = fields.Text(
        string='Notas',
    )
    vertice_origen_nivelacion = fields.Char(
        string='Vertice origen nivelación',
    )
    cota_geometrica = fields.Char(
        string='Cota geométrica',
    )
    verificada_por = fields.Char(
        string='Verificada por',
    )
    numero_validacion = fields.Char(
        string='Número de validación',
    )
    #INFO Grupo topografia
    fecha_asignacion_nivelacion = fields.Date(
        string='Fecha asignacion nivelacion',
    )
    topografo_asignado_nivelacion_id = fields.Many2one(
        string='Topografo asignado nivelacion',
        comodel_name='sigedat.persona',
        ondelete='cascade',
    )
    fecha_entrega_verificacion_nivelacion = fields.Date(
        string='Fecha entrega verificacion nivelacion',
    )
    #INFO Grupo Planas cartesianas locales
    norma_planas_cartesianas = fields.Char(
        string='Coordenadas planas cartesianas',
    )
    cartesiana_ids = fields.One2many(
        string='Cartesianas',
        comodel_name='sigedat.tramite.solicitud.cartesiana',
        inverse_name='solicitud_id',
    )
    observacion = fields.Text(
        string='Observacion',
    )
    #INFO Grupo Cantidad de planos
    acueducto = fields.Integer(
        string='Acueducto',
    )
    alcantarillado_pluvial = fields.Integer(
        string='Alcantarillado pluvial',
    )
    alcantarillado_sanitario = fields.Integer(
        string='Alcantarillado sanitario',
    )
    combinado = fields.Integer(
        string='Combinado',
    )
    especiales = fields.Integer(
        string='Especiales',
    )
    total = fields.Integer(
        string='Total',
        compute='_compute_total'
    )
    #INFO Grupo Entrega final
    direccion_proyecto = fields.Char(
        string='Direccion proyecto',
    )
    localidad_id = fields.Many2one(
        string='Localidad',
        comodel_name='base.localidad',
        ondelete='cascade',
    )
    barrio_id = fields.Many2one(
        string='Barrio',
        comodel_name='base.barrio',
        domain="[('localidad_id','=',localidad_id)]",
        ondelete='cascade',
    )
    norte = fields.Char(
        string='Norte',
    )
    este = fields.Char(
        string='Este',
    )
    acueducto_3333 = fields.Char(
        string='3333 Acueducto',
    )
    alcantarillado_2000 = fields.Char(
        string='2000 Alcantarillado',
    )
    observacion = fields.Text(
        string='Observaciones',
    )
    radicado_sigue = fields.Char(
        string='Radicado sigue',
    )
    id_sigue = fields.Char(
        string='Id Sigue',
    )
    numero_obra_acueducto = fields.Char(
        string='Numero obra acueducto',
    )
    numero_obra_alcantarillado = fields.Char(
        string='Numero obra alcantarillado',
    )
    numero_proyecto_acueducto = fields.Char(
        string='Numero de proyecto acueducto',
    )
    numero_proyecto_alcantarillado = fields.Char(
        string='Numero de proyecto alcantarillado',
    )
    longitud_red_acueducto = fields.Float(
        string='Longitud red acueducto (Km)',
    )
    longitud_red_alcantarillado = fields.Float(
        string='Longitud red alcantarillado (Km)',
    )
    longitud_red_sanitario = fields.Float(
        string='Longitud red sanitario (Km)',
    )
    longitud_red_pluvial = fields.Float(
        string='Longitud red pluvial (Km)',
    )
    longitud_red_combinado = fields.Float(
        string='Longitud red combinado (Km)',
    )
    cantidad_unidades_medio_magnetico = fields.Char(
        string='Cantidad unidades medio magnetico',
    )
    # Banderas
    fue_devuelto = fields.Boolean(
        string='Fue devuelto',
    )
    formato_lista_chequeo_firmado_manual = fields.Binary(
        string='Lista chequeo firmado',
        attachment=True
    )
    formato_lista_chequeo_firmado_manual_nombre = fields.Char(
    )
    formato_lista_chequeo_firmado_manual_check = fields.Boolean(
        string='Lista chequeo firmado validado',
    )
    apoyos_ids = fields.Many2many(
        string='Usuarios de apoyo',
        comodel_name='res.users',
    )
    ploteo_boton_orden_final = fields.Boolean(
        string='Botón orden final',
    )
    es_admin = fields.Boolean(
        string='Es Administrador de SIGEDAT',
        compute='_compute_es_admin',
    )
    color_tree = fields.Char(
        string='Color del árbol',
        compute='_compute_color_tree',
    )
    tipo_cita_devolucion_id = fields.Many2one(
        'sigedat.cita.tipo',
        string='Tipo de cita de devolución'
    )
    motivo_devolucion = fields.Text(
        string='Motivo de devolución'
    )



    # -------------------
    # methods
    # -------------------

    def _compute_name(self):
        for r in self:
            r.name = f"Acuerdo:{r.contrato_id.name}"



    @api.depends('fecha_inicio')
    def _compute_color_tree(self):
        for s in self:
            s.color_tree = 'green'
            if s.fecha_inicio and (s.fecha_inicio + timedelta(days=7)) < fields.Datetime.now():
                s.color_tree = 'orange'
            elif s.fecha_inicio and (s.fecha_inicio + timedelta(days=14)) < fields.Datetime.now():
                s.color_tree = 'red'




    @api.depends('acueducto', 'alcantarillado_pluvial', 'alcantarillado_sanitario', 'combinado', 'especiales')
    def _compute_total(self):
        for r in self:
            r.total = r.acueducto + r.alcantarillado_pluvial + r.alcantarillado_sanitario + r.combinado + r.especiales


    @api.depends('tipo_tramite_id')
    def _compute_es_asesoria(self):
        for r in self:
            r.es_asesoria = 'asesor' in r.tipo_tramite_id.name.lower()



    def crear_vista_previa_informe(self):
        if self.tramite_abreviatura == 'revision_topografia':
            self.generar_reporte_lista_chequeo_topografia(es_firmado=False)
        elif self.tramite_abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra']:
            self.generar_reporte_lista_chequeo_sigue(es_firmado=False, esta_validado=False)
        elif self.tramite_abreviatura in ['asignacion_numero_record_disenio','asignacion_numero_record_obra']:
            self.generar_reporte_lista_chequeo_sigue(es_firmado=False, esta_validado=False)
            # self.generar_reporte_lista_chequeo_entrega_final()



    @api.onchange('lista_item_ids')
    def _boton_orden_final_onchange(self):
        if self.lista_item_ids.filtered(lambda i: i.cumple != 'si' and 'se autoriza ploteo' in i.name.lower()):
            self.ploteo_boton_orden_final = False
        else:
            self.ploteo_boton_orden_final = True


    @api.onchange('formato_lista_chequeo_firmado_manual_check')
    def _formato_lista_chequeo_firmado_manual_check_onchange(self):
        if not self.env.user.has_group('sigedat.lider_area'):
            raise UserError('Sólo un usuario lider puede modificar este campo')
        

    # @api.onchange('documento_ids')
    # def _onchange_documento_ids(self):
    #     if


    def _compute_es_admin(self):
        self.es_admin = self.env.user.has_group('sigedat.administrador')



    def enviar_notificacion(self, mensaje, asunto, ctx={}):
        mail_template = self.env.ref('sigedat.plantilla_tramite_solicitud')
        correo_externo = self.create_uid.partner_id.email
        correos_apoyo = self.tramite_id.persona_ids.mapped('partner_id.email')
        correos_contactos = self.tramite_id.contacto_ids.mapped('correo_electronico')
        correos = correos_apoyo + correos_contactos + [correo_externo, self.tramite_id.correo_electronico_contratista, self.tramite_id.correo_electronico_supervisor, self.tramite_id.correo_electronico_interventor]

        # Filtrar correos válidos
        correos_validos = [email for email in correos if email]

        # Unir correos con comas
        correos_string = ','.join(correos_validos)

        try:
            if correos_string:
                # Enviar un solo correo a múltiples destinatarios
                mail_template.with_context(
                    correos=correos_string,
                    mensaje=mensaje,
                    asunto=asunto,
                ).send_mail(self.id, force_send=True)
        except Exception as e:
            raise ValidationError(f"No fue posible enviar la notificacion, por: {e}")


    def enviar_notificacion_cita(self, cita_id, fecha_inicio, ctx={}):
        tipo_tramite = self.tipo_tramite_id.name
        contrato = self.tramite_id.name
        numero_cita = cita_id
        nombre_externo = self.create_uid.name

        mensaje = f"""La DITG le informa que el usuario {nombre_externo} ha solicitado una nueva cita para {tipo_tramite} del contrato {contrato} para el día y hora {fecha_inicio}.\nRecuerde que el ID de su cita es el {numero_cita}"""
        asunto = f"Asignación para cita de {tipo_tramite} {numero_cita}"
        self.enviar_notificacion(mensaje, asunto)


    def enviar_notificacion_cambio_estado(self, estado, ctx={}):
        contrato = self.tramite_id.name
        numero_cita = self.cita_id.id
        tipo_tramite = self.tipo_tramite_id.name
        contrato = self.tramite_id.name

        if estado == 'validado_confirmado':
            asunto = f"Validación Exitosa - {tipo_tramite} de la cita {numero_cita}"
            if self.tipo_cita_id.name == 'Topografía':
                mensaje = f"La DITG le informa que el una vez realizada la verificación de la información cargada en la plataforma para el/la {tipo_tramite} del contrato {contrato}, esta CUMPLE con los estándares mínimos de calidad necesarios para su aceptación. Por favor continuar con el trámite de REVISIÓN DE PLANOS en el SIGEDAT."
            elif self.tipo_cita_id.name == 'Planos Record':
                mensaje = f"La DITG le informa que el una vez realizada la verificación de la información cargada en la plataforma para el/la {tipo_tramite} del contrato {contrato}, esta CUMPLE con los estándares mínimos de calidad necesarios para su aceptación. Por favor continuar con el trámite de ENTREGA FINAL en el SIGEDAT"
            elif self.tipo_cita_id.name == 'Entrega Final':
                # mensaje = f"La DITG le informa que el una vez realizada la verificación de la información cargada en la plataforma para el/la {tipo_tramite} del contrato {contrato}, esta CUMPLE con los estándares mínimos de calidad necesarios para su aceptación."
                mensaje = f"La DITG le informa que se ha recibido a satisfacción el proyecto y se ha asignado el numero de diseño u obra según corresponda el cual puede ser consultado en la aplicación."
           
        elif estado == 'revision_con_observaciones':
            asunto = f"Observaciones de {tipo_tramite} a la cita {numero_cita}"
            mensaje = f"La DITG le informa que una vez realizada la verificación de la información cargada en la plataforma para el/la {tipo_tramite} del contrato {contrato}, esta NO CUMPLE con los estándares mínimos de calidad necesarios para su aceptación. Por favor valide las observaciones relacionadas con la cita {numero_cita} en el SIGEDAT."
        else:
            return False

        self.enviar_notificacion(mensaje, asunto)



    def write(self, vals):
        if 'estado' in vals:
            self.notificar_cambio_estado()
        res = super(SigedatTramiteSolicitud, self).write(vals)
        return res



    #### Cambios de estados  ######
    ###############################

    def wkf_creado(self):
        for d in self.documento_ids.filtered(lambda d: d.tipo_id.obligatorio == True):
            if not d.archivo:
                _logger.warning(f"No se cargó el archivo: {d.tipo_id.name}, el cual es obligatorio.")
                raise ValidationError(f"El archivo: {d.tipo_id.name} no fue cargado y es obligatorio.")
        self.state = 'creado'



    def wkf__pendiente_revision(self):
        self.state = 'pendiente_revision'



    def wkf__en_revision(self):
        self.state = 'en_revision'



    def wkf__validado_confirmado(self):

        if not self.formato_lista_chequeo_firmado_manual_check:
            raise ValidationError('El campo de "Lista chequeo firmado manual validado" debe estar chequeado.')

        if self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_gosign', 'False') == 'True':
            #INFO Se llega a este estado de forma automatica, una vez, el servicio de gosign, me confirme que fue firmado el documento
            usuario_api = self.env['ir.config_parameter'].sudo().get_param('base_conf.usuario_gosign', '')
            clave_api = self.env['ir.config_parameter'].sudo().get_param('base_conf.clave_gosign', '')
            cliente_oauth = self.env['ir.config_parameter'].sudo().get_param('base_conf.cliente_oauth_gosign', '')
            secreto_oauth = self.env['ir.config_parameter'].sudo().get_param('base_conf.secreto_oauth_gosign', '')
            url_obtener_token = self.env['ir.config_parameter'].sudo().get_param('base_conf.url_obtener_token_gosign', '')
            url_firmar_documento = self.env['ir.config_parameter'].sudo().get_param('base_conf.url_firmar_documento_gosign', '')
            #todo aprobado por, validado por
            if not usuario_api or not clave_api or not secreto_oauth or not cliente_oauth or not url_obtener_token or not url_firmar_documento:
                raise ValidationError(f"No esta configurado correctamente el servicio de firmas con GoSign.")

            gs = Gosign(usuario_api, clave_api, cliente_oauth, secreto_oauth, url_obtener_token)
            nombre_archivo = f"{self.tramite_id.name.replace(' ', '_')}_{self.id}"
            respuesta = gs.obtener_carpeta(id_carpeta=nombre_archivo)
            if respuesta and "documents" in respuesta and respuesta["documents"]:
                for documento in respuesta["documents"]:
                    if 'bytes' in documento:
                        self.formato_lista_chequeo = documento.get('bytes')
                        self.formato_lista_chequeo_nombre = f"{nombre_archivo}_firmado.pdf"
                    else:
                        raise ValidationError(f"El servicio no devolvió los bytes del documento: {documento['externalId']}")
            else:
                raise ValidationError(f"El servicio no devolvió documentos con id: {nombre_archivo}")

        estado = 'validado_confirmado'
        self.enviar_notificacion_cambio_estado(estado)
        self.state = estado



    def wkf__revision_en_espera(self):
        self.state = 'revision_en_espera'



    def wkf__revision_con_observaciones(self):
        #INFO Se debe generar el formato sin firmas y de acuerdo al tramite
        if self.tramite_abreviatura == 'revision_topografia':
            self.generar_reporte_lista_chequeo_topografia(es_firmado=False)
        elif self.tramite_abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra', 'asignacion_numero_record_obra', 'asignacion_numero_record_disenio']:
            self.generar_reporte_lista_chequeo_sigue(es_firmado=False, esta_validado=False)
        if self.cita_id:
            self.cita_id.state = 'atendida'
        if self.formato_lista_chequeo:
            estado = 'revision_con_observaciones'
            self.enviar_notificacion_cambio_estado(estado)
            self.state = estado
        else:
            raise ValidationError(f"Error al generar el documento.")



    def wkf__orden_entrega_final(self):
        #INFO Se debe validar que esten cargados los archivos requeridos para el tramite record
        if self.tramite_abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra']:
            items_no_cumplen = self.lista_item_ids.filtered(lambda i: i.cumple == 'no' and not i.permitido_entrega_posterior)
            if items_no_cumplen:
                raise ValidationError(f"Hay items de la lista de chequeo que no se cumplieron, por lo cual no es posible enviar el trámite a orden de entrega.")

            item_autoriza_ploteo = self.lista_item_ids.filtered(lambda i: i.cumple != 'si' and 'se autoriza ploteo' in i.name.lower())
            if item_autoriza_ploteo:
                raise ValidationError(f"El ´ttem de Se autoriza ploteo no se cumple, por lo cual no es posible enviar el trámite a orden de entrega.")

        try:
            plantilla = self.env.ref('sigedat.plantilla_entrega_final_solicitud')
            ctx = self.env.context.copy()
            ctx['direccion_notificacion'] = f"{self.revisor_id.persona_id.email}, {self.correo_electronico_contratista}"
            enviar_mensaje_con_plantilla(
                    objeto=self,
                    contexto=ctx,
                    plantilla=plantilla,
                    )
        except Exception as e:
            raise ValidationError(f"No fue posible enviar la notificacion a: {ctx['direccion_notificacion']}, por: {e}")

        #INFO Se debe generar el formato de lista de chequeo para el trámite record con firmas
        self.generar_reporte_lista_chequeo_sigue(es_firmado=True, esta_validado=True)
        if self.formato_lista_chequeo:
            if self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_gosign', 'False') == 'True':
                usuario_api = self.env['ir.config_parameter'].sudo().get_param('base_conf.usuario_gosign', '')
                clave_api = self.env['ir.config_parameter'].sudo().get_param('base_conf.clave_gosign', '')
                cliente_oauth = self.env['ir.config_parameter'].sudo().get_param('base_conf.cliente_oauth_gosign', '')
                secreto_oauth = self.env['ir.config_parameter'].sudo().get_param('base_conf.secreto_oauth_gosign', '')
                url_obtener_token = self.env['ir.config_parameter'].sudo().get_param('base_conf.url_obtener_token_gosign', '')
                url_firmar_documento = self.env['ir.config_parameter'].sudo().get_param('base_conf.url_firmar_documento_gosign', '')
                etiqueta_firma_1 = self.env['ir.config_parameter'].sudo().get_param('base_conf.etiqueta_firma_1_gosign', '##firma_revisor##')

                if not usuario_api or not clave_api or not secreto_oauth or not cliente_oauth or not url_obtener_token or not url_firmar_documento or not etiqueta_firma_1:
                    raise ValidationError(f"No esta configurado correctamente el servicio de firmas con GoSign.")

                gs = Gosign(usuario_api, clave_api, cliente_oauth, secreto_oauth, url_obtener_token)

                #FIXME Estoy en un ambiente de pruebas o de produccion?
                if True:
                    persona_firma_1 = 'manager1'
                else:
                    try:
                        persona_firma_1 = self.aprobado_id.pesona_id.login.split('@')[0]
                    except:
                        raise ValidationError(f"No se encontró la persona que debe firmar.")

                if not persona_firma_1 or not etiqueta_firma_1:
                    raise ValidationError(f"No se encontró la información de las personas que deben firmar el documento.")

                respuesta = gs.agregar_documento(url_firmar_documento=url_firmar_documento, asunto_carpeta='Documento subido desde SIGEDAT', titulo_documento=f'Lista chequeo {self.tramite_id.name}', id_carpeta=f"{self.tramite_id.name.replace(' ', '_')}_{self.id}", documento=self.formato_lista_chequeo, persona_firma_1=persona_firma_1, etiqueta_firma_1=etiqueta_firma_1)

                if 'code' not in respuesta or respuesta['code'] != 'OK':
                    raise ValidationError(f"Hubo un error al cargar el documento al servicio de gosign.")

            self.fecha_aprobacion = datetime.today()
            self.aprobado_id = self.env['sigedat.revisor'].search([('persona_id', '=', self.env.uid)])
            if self.cita_id:
                self.cita_id.state = 'atendida'
            self.state = 'orden_entrega_final'
        else:
            raise ValidationError(f"Error al generar el documento.")



    def wkf__en_aprobacion(self):
        #INFO Se debe verificar que todos los items esten en 'si' o en 'n/a' para poderlo enviar aprobación, a excepcion de los items permitidos previamente
        if self.lista_item_ids.filtered(lambda i: not i.lista_chequeo_id.permitido_entrega_posterior).filtered(lambda i: i.cumple == 'no'):
            raise ValidationError(f"No se puede enviar a validación una solicitud de trámite que tiene items que no cumplen.")

        #INFO Se deben validar que los grupos IGAC y cartesianas hayan sido diligenciados para topografia y que si aplique para topografia, para record, se valida que los campos del grupo cantidad de planos, esten cargados, en entrega final se debe validar que los campos del grupo entrega final esten diligenciados
        if self.tramite_abreviatura == 'revision_topografia':

            if self.aplica_topografia == 'si':

                if not self.vertice_origen_nivelacion or not self.cota_geometrica or not self.verificada_por or not self.numero_validacion:
                    raise ValidationError(f"No fueron diligenciados todos los campos del grupo IGAC, por favor diligencielos antes de continuar.")

                if not self.cartesiana_ids:
                    raise ValidationError(f"No fueron diligenciadas las planas cartesianas, por favor diligencielas antes de continuar.")
            else:
                #FIXME: si no aplica a topografia, que se hace?
                pass
        elif self.tramite_abreviatura in ['revision_planos_record_disenio', 'revision_planos_record_obra']:

            if not self.total:
                raise ValidationError(f"No fueron diligenciados los campos de cantidad de planos, por favor diligencielos antes de continuar.")

        elif self.tramite_abreviatura in ['asignacion_numero_record_disenio', 'asignacion_numero_record_obra']:

            if not self.direccion_proyecto or not self.localidad_id or not self.norte or not self.este:
                raise ValidationError(f"No fueron diligenciados todos los campos de la ubicación del proyecto, por favor diligencielos antes de continuar.")

            if not self.acueducto_3333 or not self.alcantarillado_2000:
                raise ValidationError(f"No fueron diligenciados todos los campos de las planchas, por favor diligencielos antes de continuar.")

            if not self.radicado_sigue or not self.id_sigue or not self.numero_obra_acueducto or not self.numero_obra_alcantarillado or not self.numero_proyecto_acueducto or not self.numero_proyecto_alcantarillado:
                raise ValidationError(f"No fueron diligenciados todos los campos de la asignación de número de obra, por favor diligencielos antes de continuar.")

            # if not self.longitud_red_acueducto or not self.longitud_red_sanitario or not self.longitud_red_pluvial or not self.longitud_red_combinado or not self.cantidad_unidades_medio_magnetico:
            #     raise ValidationError(f"No fueron diligenciados todos los campos de las longitudes, por favor diligencielos antes de continuar.")

        self.fecha_aprobacion = datetime.today()
        self.aprobado_id = self.env['sigedat.revisor'].search([('persona_id', '=', self.env.uid)])
        if self.cita_id:
            self.cita_id.state = 'atendida'

        # Se re genera el informe lista de chequeo
        self.crear_vista_previa_informe()
        self.state = 'en_aprobacion'



    def wkf__devolucion_aprobacion(self):
        try:
            plantilla = self.env.ref('sigedat.plantilla_devolucion_aprobacion_solicitud')
            ctx = self.env.context.copy()
            ctx['direccion_notificacion'] = f"{self.revisor_id.persona_id.email}"
            enviar_mensaje_con_plantilla(
                    objeto=self,
                    contexto=ctx,
                    plantilla=plantilla,
                    )
        except Exception as e:
            raise ValidationError(f"No fue posible enviar la notificacion a: {ctx['direccion_notificacion']}, por: {e}")

        self.state = 'devolucion_aprobacion'



    def wkf_validado(self):
        if not self.formato_lista_chequeo_firmado_manual:
            raise ValidationError('Aún no hay formato de lista de chequeo firmado.')

        #TODO Se debe enviar notificacion de la validacion del tramite, a quien?

        #INFO Se genera el reporte de lista de chequeo del trámite
        if self.tramite_abreviatura == 'revision_topografia':
            self.generar_reporte_lista_chequeo_topografia(es_firmado=True)

        elif self.tramite_abreviatura in ['asignacion_numero_record_disenio', 'asignacion_numero_record_obra']:
            self.generar_reporte_lista_chequeo_entrega_final()

        if self.formato_lista_chequeo:
            if self.env['ir.config_parameter'].sudo().get_param('sigedat.esta_activa_conexion_gosign', 'False') == 'True':
                usuario_api = self.env['ir.config_parameter'].sudo().get_param('base_conf.usuario_gosign', '')
                clave_api = self.env['ir.config_parameter'].sudo().get_param('base_conf.clave_gosign', '')
                cliente_oauth = self.env['ir.config_parameter'].sudo().get_param('base_conf.cliente_oauth_gosign', '')
                secreto_oauth = self.env['ir.config_parameter'].sudo().get_param('base_conf.secreto_oauth_gosign', '')
                url_obtener_token = self.env['ir.config_parameter'].sudo().get_param('base_conf.url_obtener_token_gosign', '')
                url_firmar_documento = self.env['ir.config_parameter'].sudo().get_param('base_conf.url_firmar_documento_gosign', '')
                etiqueta_firma_1 = self.env['ir.config_parameter'].sudo().get_param('base_conf.etiqueta_firma_1_gosign', '##firma_revisor##')
                etiqueta_firma_2 = self.env['ir.config_parameter'].sudo().get_param('base_conf.etiqueta_firma_2_gosign', '##firma_lider##')

                if not usuario_api or not clave_api or not secreto_oauth or not cliente_oauth or not url_obtener_token or not url_firmar_documento or not etiqueta_firma_1 or not etiqueta_firma_2:
                    raise ValidationError(f"No esta configurado correctamente el servicio de firmas con GoSign.")

                gs = Gosign(usuario_api, clave_api, cliente_oauth, secreto_oauth, url_obtener_token)

                #FIXME Estoy en un ambiente de pruebas o de produccion? se debe validar si el login lo guardo como lo debo enviar a gosign o debo tomar solo una parte de este
                if True:
                    persona_firma_1 = 'manager1'
                    persona_firma_2 = 'manager2'
                else:
                    try:
                        persona_firma_1 = self.aprobado_id.pesona_id.login.split('@')[0]
                        persona_firma_2 = self.validado_id.pesona_id.login.split('@')[0]
                    except:
                        raise ValidationError(f"No se encontró la persona que debe firmar.")

                if not persona_firma_1 or not persona_firma_2 or not etiqueta_firma_1 or not etiqueta_firma_2:
                    raise ValidationError(f"No se encontró la información de las personas que deben firmar el documento.")

                respuesta = gs.agregar_documento(url_firmar_documento=url_firmar_documento, asunto_carpeta='Documento subido desde SIGEDAT', titulo_documento=f'Lista chequeo {self.tramite_id.name}', id_carpeta=f"{self.tramite_id.name.replace(' ', '_')}_{self.id}", documento=self.formato_lista_chequeo, persona_firma_1=persona_firma_1, persona_firma_2=persona_firma_2, etiqueta_firma_1=etiqueta_firma_1, etiqueta_firma_2=etiqueta_firma_2)

                if 'code' not in respuesta or respuesta['code'] != 'OK':
                    raise ValidationError(f"Hubo un error al cargar el documento al servicio de gosign.")

            self.fecha_validacion = datetime.today()
            self.validado_id = self.env['res.users'].search([('id', '=', self.env.uid)])


            # Por ahora se omite el comprimido
            # INFO: Creo la copia de seguridad del comprimido en la ruta preconfigurada de copia de seguridad
            # ruta_copia_seguridad = self.env['ir.config_parameter'].sudo().get_param('base_conf.ruta_copia_seguridad', '')

            # if not ruta_copia_seguridad:
            #     raise ValidationError(f"No fue establecida una ruta para la copia de seguridad de la información, por favor configurela, antes de continuar.")

            # if not os.path.isdir(ruta_copia_seguridad):
            #     raise ValidationError(f"No fue encontrada dentro del servidor, una ruta para la copia de seguridad de la información, por favor creela, antes de continuar.")

            # if not self.comprimido:
            #     raise ValidationError("No hay comprimido.")

            # try:
            #     with open(f"{ruta_copia_seguridad}{os.sep}{self.comprimido_nombre}", "wb") as f:
            #         f.write(b64decode(self.comprimido))
            # except Exception as e:
            #     raise ValidationError(f"Se producto el error: {e}, al intentar guardar la copia de seguridad.")

            self.state = 'validado'
        else:
            raise ValidationError(f"Error al generar el documento.")

    def wkf_cancelado(self):
        '''El usuario externo puede pedir la cancelacion de la cita una vez agendada'''
        #TODO Se debe pedir la justificacion de la cancelacion
        self.cita_id.mensaje_confirmacion_cita = f'La cita fue cancelada satisfactoriamente por: {self.env.uid}'
        self.cita_id.state = 'cancelada'
        self.cita_id = None

        if self.cita_id:
            self.cita_id.state = 'cancelada'

        self.state = 'cancelado'

    def wkf_rechazado(self):
        #TODO Se debe pedir la justificacion del rechazo. Se puede rechazar si fue aprobada la lista de chequeo?
        if self.cita_id:
            self.cita_id.state = 'cancelada'

        self.state = 'rechazado'

        try:
            plantilla = self.env.ref('sigedat.plantilla_rechazada_solicitud')
            ctx = self.env.context.copy()
            ctx['direccion_notificacion'] = f"{self.revisor_id.persona_id.email}, {self.correo_electronico_contratista}"
            enviar_mensaje_con_plantilla(
                    objeto=self,
                    contexto=ctx,
                    plantilla=plantilla,
                    )
        except Exception as e:
            raise ValidationError(f"No fue posible enviar la notificacion a: {ctx['direccion_notificacion']}, por: {e}")

    def comprimir_descargar(self):
        self.crear_estructura_carpetas()

    def _cron_solicitud_temporal_inactiva(self):
        plantilla_ayer = self.env.ref('sigedat.plantilla_solicitud_temporal_inactiva_1')
        plantilla_hace_2_dias = self.env.ref('sigedat.plantilla_solicitud_temporal_inactiva_2')
        plantilla_hace_3_dias = self.env.ref('sigedat.plantilla_solicitud_temporal_inactiva_3')
        ayer = datetime.today() - timedelta(days=1)
        hace_2_dias = datetime.today() - timedelta(days=2)
        hace_3_dias = datetime.today() - timedelta(days=3)
        solicitud_temporal_ayer_ids = self.env['sigedat.tramite.solicitud'].search([('state', '=', 'temporal'), ('create_date', '=', ayer)])
        solicitud_temporal_hace_2_dia_ids = self.env['sigedat.tramite.solicitud'].search([('state', '=', 'temporal'), ('create_date', '=', hace_2_dias)])
        solicitud_temporal_hace_3_dia_ids = self.env['sigedat.tramite.solicitud'].search([('state', '=', 'temporal'), ('create_date', '=', hace_3_dias)])
        ctx = self.env.context.copy()

        #INFO Envio notificacion a las solicitudes que llevan un dia en estado temporal
        for s in solicitud_temporal_ayer_ids:
            try:
                enviar_mensaje_con_plantilla(
                        objeto=s,
                        contexto=ctx,
                        plantilla=plantilla_ayer,
                        )
            except Exception as e:
                _logger.warning(f"No pudo enviarse el mensaje de notificación para las solicitudes por: {e}")

        #INFO Envio notificacion a las solicitudes que llevan dos dias en estado temporal
        for s in solicitud_temporal_hace_2_dia_ids:
            try:
                direccion = self.env['sigedat.persona'].search([('usuario_id', '=', s.create_uid.id)]).correo_electronico
            except Exception:
                _logger.warning(f"Hubo un problema al consultar la dirección de correo electrónico del usuario: {s.create_uid.name}, por favor solucionelo.")
            ctx.update(
                    {
                        'direccion': direccion,
                    }
                )
            try:
                enviar_mensaje_con_plantilla(
                        objeto=s,
                        contexto=ctx,
                        plantilla=plantilla_hace_2_dias,
                        )
            except Exception as e:
                _logger.warning(f"No pudo enviarse el mensaje de notificación para las solicitudes por: {e}")

        #INFO Cancelo las solicitudes que llevan tres dias en estado temporal
        for s in solicitud_temporal_hace_3_dia_ids:
            try:
                direccion = self.env['sigedat.persona'].search([('usuario_id', '=', s.create_uid.id)]).correo_electronico
            except Exception:
                _logger.warning(f"Hubo un problema al consultar la dirección de correo electrónico del usuario: {s.create_uid.name}, por favor solucionelo.")
            ctx.update(
                    {
                        'direccion': direccion,
                    }
                )
            try:
                enviar_mensaje_con_plantilla(
                        objeto=s,
                        contexto=ctx,
                        plantilla=plantilla_hace_3_dias,
                        )
            except Exception as e:
                _logger.warning(f"No pudo enviarse el mensaje de notificación para las solicitudes por: {e}")

            s.wkf_cancelado()

        #INFO Cancelar solicitudes con mas de los dias permitidos
        #FIXME La cantidad de dias es fijo? se deja ellimite a 3? o si no toca conf ese limite en el servidor
        try:
            limite_dias = int(self.env['ir.config_parameter'].sudo().get_param('sigedat.numero_dias_cancelar_solicitud', 0))
            if limite_dias:
                max_dias = datetime.today() - timedelta(days=limite_dias)
                solicitud_cancelar_ids = self.env['sigedat.tramite.solicitud'].search([('state', '=', 'temporal'), ('create_date', '<=', max_dias)])
                for s in solicitud_cancelar_ids:
                    s.wkf_cancelado()
        except Exception:
            _logger.warning("No esta configurado correctamente el parámetro numero de dias antes de cancelar la solicitud temporal.")

    def crear_estructura_carpetas(self):
        _logger.warning(f"solicitud: {self.name}, documentos: {self.documento_ids}")
        #INFO Limpio la ruta de trabajo
        ruta_trabajo = normalizar_cadena(os.path.join(RUTA_BASE, self.name, self.tipo_tramite_id.name), reemplazar_palabra=':', por_palabra='')

        if os.path.isdir(ruta_trabajo):
            shutil.rmtree(ruta_trabajo)

        #INFO Creo la carpeta raiz
        try:
            os.makedirs(ruta_trabajo, 0o744, exist_ok=False)
        except Exception as e:
            raise ValidationError(f"error: {e}, al crear la carpeta: {ruta_trabajo}")

        #INFO Recorro todos los documentos cargados a la solicitud
        for documento_id in self.documento_ids:
            ruta_completa = ''
            #INFO Si existe una carpeta padre la creo
            carpeta_id = documento_id.carpeta_id

            _logger.warning(f"documento: {documento_id.name}, carpeta: {carpeta_id.name}, archivo: {documento_id.archivo_nombre}")

            if carpeta_id.name:
                if carpeta_id.carpeta_padre_id:
                    ruta_completa = normalizar_cadena(os.path.join(ruta_trabajo, carpeta_id.carpeta_padre_id.name, carpeta_id.name))
                else:
                    ruta_completa = normalizar_cadena(os.path.join(ruta_trabajo, carpeta_id.name, documento_id.tipo_id.name))

            if ruta_completa:
                if not os.path.isdir(ruta_completa):
                    try:
                        os.makedirs(ruta_completa, 0o744, exist_ok=False)
                    except:
                        raise ValidationError(f"Error al crear la carpeta: {ruta_completa} con los archivos de la solicitud.")
            else:
                continue

            #INFO Verifico que la carpeta en donde necesito ubicar los archvos exista y me posiciono alla,para crear los archivos
            if not os.path.isdir(ruta_completa):
                raise ValidationError(f"No existe la carpeta: {ruta_completa} en la cual crear los archivos.")

            os.chdir(ruta_completa)

            if documento_id.archivo:
                try:
                    with open(f"{ruta_completa}{os.sep}{documento_id.archivo_nombre}", 'bw') as f:
                        f.write(b64decode(documento_id.archivo))
                except Exception as e:
                    raise ValidationError(f"Error: {e}, al intentar escribir el archivo: {documento_id.archivo_nombre} en disco.")


        os.chdir(RUTA_BASE)
        nombre_archivo_salida = normalizar_cadena(f"{self.name}_{self.tipo_tramite_id.name}_{datetime.now().strftime('%d-%m-%Y')}", reemplazar_palabra=':', por_palabra='')
        ruta_archivo_salida = os.path.join(RUTA_BASE, nombre_archivo_salida)
        comprimir_carpeta(ruta_archivo_salida=RUTA_BASE, ruta_carpeta_comprimir=ruta_trabajo, archivo_salida=nombre_archivo_salida)
        ruta_archivo_salida_con_extension = f"{ruta_archivo_salida}.zip"

        try:
            self.comprimido = b64encode(open(ruta_archivo_salida_con_extension, 'rb').read())
        except Exception as e:
            raise ValidationError(f"Error: {e} al tratar de guardar el comprimido.")

        self.comprimido_nombre = nombre_archivo_salida

        #INFO Borro del DD las carpetas y archivos creados previamente
        if ruta_trabajo and os.path.isdir(ruta_trabajo):
            try:
                shutil.rmtree(ruta_trabajo)
            except:
                raise ValidationError(f"Error al tratar de eliminar la carpeta de trabajo: {ruta_trabajo}")

        if os.path.isfile(ruta_archivo_salida_con_extension):
            try:
                os.remove(ruta_archivo_salida_con_extension)
            except:
                raise ValidationError(f"Error al eliminar el comprimido generado: {ruta_archivo_salida_con_extension}")



    def generar_reporte_lista_chequeo_topografia(self, es_firmado=True):
        plantilla_sin_firma = 'Reporte_lista_chequeo_topografia_sin_firma.odt'
        plantilla_con_firma = 'Reporte_lista_chequeo_topografia_con_firma.odt'

        observacion_model = self.env['sigedat.lista_chequeo.item.observacion']

        if es_firmado:
            plantilla = plantilla_con_firma
        else:
            plantilla = plantilla_sin_firma

        ruta_base = 'ruta_base_plantilla_sigedat'
        formato_reporte = 'pdf'

        version_lista_chequeo = self.lista_item_ids[-1].version_lista_chequeo or '' if self.lista_item_ids else ''
        numero_lista_chequeo = self.lista_item_ids[-1].numero_lista_chequeo or '' if self.lista_item_ids else ''
        hoy = datetime.today().strftime('%Y-%m-%d')

        nombre_reporte = f"{numero_lista_chequeo}_{version_lista_chequeo}_{hoy}"

        datos = {
            'version_lista_chequeo': version_lista_chequeo,
            'tipo_obra': 'X' if self.tramite_id.tipo_record in ['obra', 'disenio_obra'] else '',
            'tipo_disenio':  'X' if self.tramite_id.tipo_record in ['disenio', 'disenio_obra'] else '',
            'numero_lista_chequeo': numero_lista_chequeo,
            'numero_contrato': self.contrato_id.name or '',
            'area_contrato': self.contrato_id.area_id.name or '',
            'nombre_record': self.contrato_id.objeto or '',
            'frente': self.tramite_id.frente_id.name or 'No tiene',
            'numero_disenio': self.contrato_id.numero_disenio or '',
            'nombre_contratista': self.contrato_id.empresa_contratista or '',
            'entregado_por': self.cita_id.create_uid.name if self.cita_id else 'No tiene cita',
            'revisado_por': self.aprobado_id.name or '',
            'supervisado_por': self.contrato_id.supervisor or '',
            'fecha_chequeo': self.fecha_inicio.strftime("%d-%m-%Y") if self.fecha_inicio else '',
            'items_generales': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte: {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'inicial')
            ],
            'fecha_expedicion_formato_dia': '',
            'fecha_expedicion_formato_mes': '',
            'fecha_expedicion_formato_anio': '',
            'items_planimetria': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte: {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'planimetria')
            ],
            'items_altimetria': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'altimetria')
            ],
            'items_gns_gps': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'gns_gps')
            ],
            'items_batimetria': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'batimetria')
            ],
            'items_fotogrametria': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'fotogrametria')
            ],
            'items_rpas': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'rpas')
            ],
            'items_informe': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'informe')
            ],
            'items_lidar': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'lidar')
            ],
            'notas': self.notas or '',
            'icag_vertice_origen': self.vertice_origen_nivelacion or '',
            'icag_cota_geometrica': self.cota_geometrica or '',
            'icag_verificada_por': self.verificada_por or '',
            'icag_numero_validacion': self.numero_validacion or '',
            'norma_planas_cartesianas': f"PLANAS CARTESIANAS LOCALES BOGOTA {self.norma_planas_cartesianas}",
            'planas_cartesianas': [
                {
                    'punto': c.name or '',
                    'norte': c.norte or '',
                    'este': c.este or '',
                    'cota_geometrica': c.cota_geometrica or '',
                } for c in self.cartesiana_ids
            ],
            'observacion': self.observacion or '',
            'estado_topografia_en_verificacion': 'X' if self.state not in ['en_aprobacion','validado', 'validado_confirmado'] else '',
            'estado_topografia_validado': 'X' if self.state in ['en_aprobacion','validado', 'validado_confirmado'] else '',
            'nombre_revisor': self.revisor_id.name or '',
            'soportes': [
                {
                    'ruta_foto': crear_imagen_en_disco_desde_memoria(observacion.archivo, ancho_requerido=ANCHO_MAXIMO_IMAGEN, alto_requerido=ALTO_MAXIMO_IMAGEN, ruta_carpeta_trabajo=RUTA_CARPETA_TRABAJO) if observacion else None,
                    'nombre_foto': observacion.observacion + '\n' + '\n'.join([ob_r.observacion for ob_r in observacion_model.search([('observacion_ids', 'in', [observacion.id])])]) if observacion else '',
                    'nombre_item': observacion.item_id.lista_chequeo_id.name or '',
                } for observacion in self.lista_item_ids.filtered(lambda s: s.cumple=='no').mapped('observacion_ids') if observacion.archivo
                # for observacion in self.lista_item_ids.filtered(lambda s: s.cumple=='no').observacion_ids if self.lista_item_ids.filtered(lambda s: s.cumple=='no') else []
            ]
        }

        reporte = Reporte(
            self,
            ruta_base,
            plantilla,
            datos,
        )

        reporte.generar_reporte(formato_reporte)
        self.formato_lista_chequeo = reporte.contenido_archivo
        self.formato_lista_chequeo_nombre = nombre_reporte
        return reporte.descargar_reporte(nombre_reporte)



    def generar_reporte_lista_chequeo_sigue(self, es_firmado=True, esta_validado=False):
        plantilla_con_firma = 'Reporte_lista_chequeo_SIGUE_con_firma.odt'
        plantilla_sin_firma = 'Reporte_lista_chequeo_SIGUE_sin_firma.odt'

        observacion_model = self.env['sigedat.lista_chequeo.item.observacion']

        if es_firmado:
            plantilla = plantilla_con_firma
        else:
            plantilla = plantilla_sin_firma

        ruta_base = 'ruta_base_plantilla_sigedat'
        formato_reporte = 'pdf'

        version_lista_chequeo = self.lista_item_ids[-1].version_lista_chequeo or '' if self.lista_item_ids else ''
        numero_lista_chequeo = self.lista_item_ids[-1].numero_lista_chequeo or '' if self.lista_item_ids else ''
        numero_lista_chequeo = numero_lista_chequeo+'S'
        hoy = datetime.today().strftime('%Y-%m-%d')

        nombre_reporte = f"{numero_lista_chequeo}_{version_lista_chequeo}_{hoy}"
        # nombre_reporte = f'reporte_lista_chequeo_sigue_{self.id}'

        fecha_firma = self.tramite_id.fecha_inicio
        fecha_fin = self.tramite_id.fecha_fin
        plazo = round((fecha_fin - fecha_firma).days/30, 2)

        autoriza_ploteo = self.lista_item_ids.filtered(lambda i: i.lista_chequeo_id.name == 'Se autoriza ploteo?')[-1]
        if autoriza_ploteo:
            autoriza_ploteo = autoriza_ploteo.cumple

        datos = {
            'version_lista_chequeo': version_lista_chequeo,
            'tipo_obra': 'X' if self.tramite_id.tipo_record in ['obra', 'disenio_obra'] else '',
            'tipo_disenio':  'X' if self.tramite_id.tipo_record in ['disenio', 'disenio_obra'] else '',
            'numero_lista_chequeo': numero_lista_chequeo,
            'nombre_record': self.contrato_id.objeto or '',
            'numero_contrato': self.contrato_id.name or '',
            'area_contrato': self.contrato_id.area_id.name or '',
            'fecha_firma': fecha_firma,
            'plazo': plazo,
            'nombre_interventoria': self.contrato_id.nombre_empresa_interventor or '',
            'numero_proyecto_acueducto': self.numero_validacion or '',
            'fecha_chequeo': self.fecha_inicio.strftime("%d-%m-%Y") if self.fecha_inicio else '',
            'revisado_por': self.revisor_id.persona_id.name,     # self.aprobado_id.name or '',
            'frente': self.tramite_id.frente_id.name or 'No tiene',
            'autoriza_ploteo': autoriza_ploteo or '',
            'items_generales': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                # } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'generales')
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'generales')
            ],
            'cant_planos_acueducto': self.acueducto or '',
            'cant_planos_alcantarillado_pluvial': self.alcantarillado_pluvial or '',
            'cant_planos_alcantarillado_sanitario': self.alcantarillado_sanitario or '',
            'cant_planos_combinado': self.combinado or '',
            'cant_planos_especiales': self.especiales or '',
            'cant_planos_total': self.total or '',
            'items_anexo_predial': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'anexo_predial')
            ],
            'items_alcantarillado': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'alcantarillado')
            ],
            'items_acueducto': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte: {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'acueducto')
            ],
            'items_proyectos_especiales': [
                {
                    'parametro': i.lista_chequeo_id.name or '',
                    'si_cumple': 'X' if i.cumple == 'si' else '',
                    'no_cumple': 'X' if i.cumple == 'no' else '',
                    'na_cumple': 'X' if i.cumple == 'na' else '',
                    # 'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {[', '.join([f'{num_soporte}' for num_soporte, s in enumerate(o.soporte_ids, start=1)])] if o.archivos else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                    'observaciones': "\n".join([f"{o.observacion}, ver soporte(s): {o.archivo_nombre if o.archivo else ''}" for o in i.observacion_ids]) or '' if i.cumple == 'no' else '',
                } for i in self.lista_item_ids.filtered(lambda i: i.seccion_id.abreviatura == 'proyectos_especiales')
            ],

            'estado_no_validado': 'X' if self.state not in ['en_aprobacion','validado', 'validado_confirmado'] else '',
            'estado_validado': 'X' if self.state in ['en_aprobacion','validado', 'validado_confirmado'] else '',

            'nombre_revisor': self.revisor_id.name or '',
            # 'soportes': [
            #     {
            #         'ruta_foto': crear_imagen_en_disco_desde_memoria(soporte.archivo, ancho_requerido=ANCHO_MAXIMO_IMAGEN, alto_requerido=ALTO_MAXIMO_IMAGEN, ruta_carpeta_trabajo=RUTA_CARPETA_TRABAJO) if soporte else None,
            #         'nombre_foto': soporte.item_observacion_id.observacion,
            #         'nombre_item': soporte.item_observacion_id.item_id.lista_chequeo_id.name or '',
            #     } for soporte in self.lista_item_ids.filtered(lambda s: s.cumple=='no').mapped('observacion_ids')
            # ]
            'soportes': [
                {
                    'ruta_foto': crear_imagen_en_disco_desde_memoria(observacion.archivo, ancho_requerido=ANCHO_MAXIMO_IMAGEN, alto_requerido=ALTO_MAXIMO_IMAGEN, ruta_carpeta_trabajo=RUTA_CARPETA_TRABAJO) if observacion else None,
                    # 'nombre_foto': observacion.observacion + '\n' + '\n'.join([ob_r.observacion for ob_r in observacion.observacion_ids]),
                    'nombre_foto': observacion.observacion + '\n' + '\n'.join([ob_r.observacion for ob_r in observacion_model.search([('observacion_ids', 'in', [observacion.id])])]) if observacion else '',
                    'nombre_item': observacion.item_id.lista_chequeo_id.name or '',
                } for observacion in self.lista_item_ids.filtered(lambda s: s.cumple=='no').mapped('observacion_ids') if observacion.archivo
            ]
        }

        reporte = Reporte(
            self,
            ruta_base,
            plantilla,
            datos,
        )

        reporte.generar_reporte(formato_reporte)
        self.formato_lista_chequeo = reporte.contenido_archivo
        self.formato_lista_chequeo_nombre = nombre_reporte
        return reporte.descargar_reporte(nombre_reporte)


    def generar_reporte_lista_chequeo_entrega_final(self):
        if self.tramite_abreviatura not in ['asignacion_numero_record_disenio', 'asignacion_numero_record_obra']:
            raise ValidationError(f"No se puede generar el formato de entrega final, para un trámite de: {self.tramite_id.name}")
        else:
            if self.tipo_tramite_id.abreviatura == 'asignacion_numero_record_disenio':
                plantilla = 'plantilla_entrega_final_disenio.ods'
            elif self.tipo_tramite_id.abreviatura == 'asignacion_numero_record_obra':
                plantilla = 'plantilla_entrega_final_obra.ods'

        ruta_base = 'ruta_base_plantilla_sigedat'
        formato_reporte = 'pdf'
        nombre_reporte = f'reporte_lista_chequeo_final_{self.id}'

        datos = {
            'nombre_contratista': self.empresa_contratista or '',
            'fecha_solicitud': '',
            'nombre_proyecto': '',
            'telefono_contratista': self.telefono_contratista or '',
            'numero_acuerdo': self.numero_contrato or '',
            'area': self.area_id.name or '',
            'localidad': self.localidad_id.name or '',
            'barrio': self.barrio_id.name or '',
            'direccion_proyecto': self.direccion_proyecto or '',
            # coordenadas
            # especificaciones proyecto
            # 'acueducto_3333': self.acueducto_3333 or '',
            # 'alcantarillado_2000': self.alcantarillado_2000 or '',
            # 'especiales_10000': '',
            # 'cantidad_planos_acueducto': self.acueducto or 0,
            # 'cantidad_planos_pluvial': self.alcantarillado_pluvial or 0,
            # 'cantidad_planos_combinado': self.combinado or 0,
            # 'cantidad_planos_especiales': self.especiales or 0,
            # 'cantidad_planos_sanitario': self.alcantarillado_sanitario or 0,
            # 'cantidad_medio_magnetico': self.cantidad_unidades_medio_magnetico or '',
            # 'longitud_red_acueducto': self.longitud_red_acueducto or '',
            # 'longitud_red_pluvial': self.longitud_red_pluvial or '',
            # 'longitud_red_sanitario': self.longitud_red_sanitario or '',
            # 'longitud_red_combinado': self.longitud_red_combinado or '',
            # 'numero_nodos_existentes': '',
            # 'numero_pozos_pluvial_existentes': '',
            # 'numero_pozos_pluvial_nuevos': '',
            # 'numero_sumideros_pluvial_existentes': '',
            # 'numero_sumideros_pluvial_nuevos': '',
            # 'numero_pozos_sanitario_existentes': '',
            # 'numero_pozos_sanitario_nuevos': '',
            # 'numero_sumidero_sanitario_existentes': '',
            # 'numero_sumidero_sanitario_nuevos': '',
            # 'numero_pozos_combinado_existentes': '',
            # 'numero_pozos_combinado_nuevo': '',
            # 'numero_sumidero_combinado_existentes': '',
            # 'numero_sumidero_combinado_nuevos': '',
            'correo_interventor': self.tramite_id.correo_electronico_interventor or '',
            'nombre_interventor': self.tramite_id.nombre_empresa_interventor or '',
            'correo_supervisor': self.tramite_id.correo_electronico_supervisor or '',
            'nombre_supervisor': self.tramite_id.supervisor or '',
            'correo_contratista': self.tramite_id.correo_electronico_contratista or '',
            'direccion_contratista': '',
            'telefono_contratista': self.tramite_id.telefono_contratista or '',
            #nombre_contratista
            # 'fecha_asignacion_sigue': self.fecha_asignacion_nivelacion or '',
            # 'nombre_lider_sigue': '',
            # 'nombre_revisor': self.revisor_id.name or '',
            'numero_lista_chequeo': self.lista_item_ids[-1].numero_lista_chequeo or '' if self.lista_item_ids else '',
            'numero_radicado': self.radicado_sigue or '',
            'observacion': self.observacion or '',
        }

        #INFO Si es entrega de diseño
        if self.tipo_tramite_id.abreviatura == 'asignacion_numero_record_disenio':
            datos.update(
                {
                'numero_disenio_acueducto': self.numero_proyecto_acueducto or 0,
                'numero_disenio_especial': '',
                'numero_disenio_alcantarillado': self.numero_proyecto_alcantarillado or 0,
                }
            )

        #INFO si es entrega de obra
        elif self.tipo_tramite_id.abreviatura == 'asignacion_numero_record_obra':
            datos.update(
                {
                'numero_obra_acueducto': self.numero_obra_acueducto or 0,
                'numero_obra_especial': '',
                'numero_obra_alcantarillado': self.numero_obra_alcantarillado or 0,
                }
            )

        reporte = Reporte(
            self,
            ruta_base,
            plantilla,
            datos,
        )

        reporte.generar_reporte(formato_reporte)
        self.formato_lista_chequeo = reporte.contenido_archivo
        self.formato_lista_chequeo_nombre = nombre_reporte
        return reporte.descargar_reporte(nombre_reporte)
