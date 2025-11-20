# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
# from models.sigedat_tramite_solicitud import LISTA_SI_NO
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO
from odoo.addons.sigedat.wizards.crear_contrato import LISTA_TIPO_RECORD

_logger = logging.getLogger(__name__)

class SigedatTramite(models.Model):
    _name = 'sigedat.tramite'
    _description = 'Trámite'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )
    #INFO Grupo Acuerdo
    contrato_id = fields.Many2one(
        string='Acuerdo',
        required=True,
        comodel_name='sigedat.contrato',
        tracking=True,
    )
    fecha_inicio = fields.Date(
        related='contrato_id.fecha_inicio',
    )
    fecha_fin = fields.Date(
        related='contrato_id.fecha_fin',
    )
    objeto = fields.Text(
        string='Objeto',
        related='contrato_id.objeto',
    )
    tiene_frente = fields.Selection(
        string='¿Tiene frente?',
        related='contrato_id.tiene_frente',
    )
    frente_id = fields.Many2one(
        string='Frente',
        comodel_name='sigedat.frente',
        domain="[('contrato_id', '=', contrato_id)]",
        tracking=True,
    )
    numero_disenio = fields.Char(
        related='contrato_id.numero_disenio',
    )
    tipo_record = fields.Selection(
        related='contrato_id.tipo_record',
    )
    #INFO Grupo Contratista
    empresa_contratista = fields.Char(
        related='contrato_id.empresa_contratista',
    )
    correo_electronico_contratista = fields.Char(
        related='contrato_id.correo_electronico_contratista',
    )
    telefono_contratista = fields.Char(
        related='contrato_id.telefono_contratista',
    )
    #INFO Grupo Supervisor
    area_id = fields.Many2one(
        related='contrato_id.area_id',
    )
    supervisor = fields.Char(
        related='contrato_id.supervisor',
    )
    correo_electronico_supervisor = fields.Char(
        related='contrato_id.correo_electronico_supervisor',
    )
    #INFO Grupo Interventoría
    contrato_interventoria = fields.Char(
        related='contrato_id.contrato_interventoria',
    )
    nombre_empresa_interventor = fields.Char(
        related='contrato_id.nombre_empresa_interventor'
    )
    nombre_interventor = fields.Char(
        related='contrato_id.nombre_interventor',
    )
    correo_electronico_interventor = fields.Char(
        related='contrato_id.correo_electronico_interventor',
    )
    telefono_interventor = fields.Char(
        related='contrato_id.telefono_interventor',
    )
    #INFO Grupo
    latitud = fields.Float(
        string='Latitud',
        tracking=True,
        required=True,
        digits=(8, 4),
        help='Debido a la ubicación geográfica de Bogotá, la latitud debe ser un valor positivo, con una precision de al menos 4 decimales.'
    )
    longitud = fields.Float(
        string='Longitud',
        tracking=True,
        required=True,
        digits=(8, 4),
        help='Debido a la ubicación geográfica de Bogotá, la longitud debe ser un valor negativo, con una precision de al menos 4 decimales.'
    )
    state = fields.Selection(
        string='Estado',
        selection=[
            ('nuevo', 'Nuevo'),
            ('en_proceso', 'En Proceso'),
            ('cerrado', 'Cerrado')
        ],
        default='nuevo',
        tracking=True,
    )
    ubicacion = fields.Char(
        related='frente_id.ubicacion'
    )
    #INFO Pestaña Solicitudes de Trámite
    solicitud_ids = fields.One2many(
        string='Solicitudes de trámite',
        # required=True,
        comodel_name='sigedat.tramite.solicitud',
        inverse_name='tramite_id',
        tracking=True,
    )
    contacto_ids = fields.Many2many(
        string='Contacto',
        comodel_name='sigedat.tramite.contacto',
        relation='sigedat_tramite_contacto_rel',
        column1='contacto_id',
        column2='tramite_id',
    )
    #INFO Banderas
    equipo_apoyo_ids = fields.One2many(
        string='Equipo de apoyo',
        comodel_name='sigedat.equipo_apoyo',
        inverse_name='tramite_id',
        tracking=True,
    )
    forma_parte_equipo_apoyo = fields.Boolean(
        string='¿Es parte del equipo de apoyo?',
        compute='_compute_forma_parte_equipo_apoyo',
        store=True,
    )
    es_especial = fields.Boolean(
        string='¿Es especial?',
        compute='_compute_es_especial'
    )
    tiene_redes_acueducto = fields.Selection(
        string='¿Tiene redes y/o infraestructura de acueducto/alcantarillado?',
        selection=LISTA_SI_NO,
        tracking=True,
        required=True,
    )
    aplica_topografia = fields.Selection(
        string='¿El proyecto aplica para topografía?',
        selection=LISTA_SI_NO,
        tracking=True,
        required=True,
    )
    persona_ids = fields.Many2many(
        string='Persona',
        comodel_name='res.users',
        compute='_compute_persona_ids',
        relation='sigedat_tramite_persona_rel',
        column1='tramite_id',
        column2='persona_id',
        help='Usuarios que tienen acceso a este trámite.',
        store=True
    )


    # -------------------
    # methods
    # -------------------

    _sql_constraints = [
        ('tramite_no_repetido', 'unique(contrato_id,frente_id)', 'La gestión para el contrato y frente, ya esta registrado.'),
        ('latitud_positiva', 'check(latitud>=0)', 'El valor de la latitud no debe ser negativo.'),
        ('longitud_negativa', 'check(longitud<=0)', 'El valor de la longitud no debe ser positivo.'),
    ]


    @api.constrains('latitud', 'longitud')
    def _check_latitud_longitud(self):
        for record in self:
            if record.latitud == 0 or record.latitud < 4.24133927 or record.latitud > 5.04472740:
                raise ValidationError("El valor de latitud debe estar entre 4.24133927 y 5.04472740.")
            if record.longitud == 0 or record.longitud < -74.2949 or record.longitud > -73.6663:
                raise ValidationError("El valor de longitud debe estar entre -74.2949 y -73.6663.")



    def calc_equipo_apoyo(self, ctx):
        self._compute_forma_parte_equipo_apoyo()
        return True


    def _compute_forma_parte_equipo_apoyo(self):
        for r in self:
            r.forma_parte_equipo_apoyo = r.env.uid in r.equipo_apoyo_ids.mapped('persona_ids.usuario_id.id')


    @api.depends('equipo_apoyo_ids', 'equipo_apoyo_ids.persona_ids', 'equipo_apoyo_ids.persona_ids.usuario_id')
    def _compute_persona_ids(self):
        for r in self:
            # r.persona_ids = r.equipo_apoyo_ids.mapped('persona_ids.usuario_id.id')
            # Obtener los IDs de usuarios del equipo de apoyo
            usuarios_ids = r.equipo_apoyo_ids.mapped('persona_ids.usuario_id.id')
            # Asignar al campo Many2many usando comandos de Odoo
            r.persona_ids = [(6, 0, usuarios_ids)]


    # @api.depends('equipo_apoyo_ids','solicitud_ids')
    # def apoyos_solicitudes(self):
    #     for t in self:
    #         usuarios_apoyo = t.equipo_apoyo_ids.mapped('persona_ids.usuario_id.id')
    #         for s in t.solicitud_ids:
    #             s.apoyos_ids = [(4,u_id) for u_id in usuarios_apoyo]


    @api.model
    def create(self, values):
        result = super(SigedatTramite, self).create(values)
        if result:
            self.env['sigedat.tramite.cuadro_maestro'].create({
                'tramite_id': result.id
            })
        else:
            raise ValidationError(f"Error al intentar crear la gestión de acuerdo: {values}")
        return result


    def adiciona_keywords_en_search(self, args, offset, limit, order=False, count=False):
        new_args = []
        if not args:
            args = []
        raise ValidationError(f"entro: {self.id}")
        for arg in args:
            topografia_record = self.env.user.has_group('sigedat.topografia') or self.env.user.has_group('sigedat.record')

            if type(arg) is not tuple and type(arg) is not list:
                new_args += arg
                continue
            if arg[2] == 'MIS_ACUERDOS':
                if (topografia_record):
                    # new_args +=
                    for e in self.env['sigedat.equipo_apoyo'].search([('tramite_id', '=', self.id)]):
                        for p in e.persona_ids:
                            if p.usuario_id.id == self.env.uid:
                                new_args += self.id
                    # self.env['sigedat.tramite'].search([('equipo_apoyo_ids.persona_ids.usuario_id', 'in', self.env.uid)])
            else:
                new_args += [arg]
        return new_args

    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, context=None, count=False):
    #     new_args = self.adiciona_keywords_en_search(args, offset, limit, order, count)
    #     return super(SigedatTramite, self).search(new_args, offset, limit, context, count)

    def _compute_name(self):
        for r in self:
            r.name = f"Acuerdo: {r.contrato_id.name}"

    # @api.depends('contrato_id')
    # def _compute_tipo_record(self):
    #     for r in self:
    #         r.tipo_record = r.contrato_id.tipo_record_manual if r.contrato_id.tipo_record_manual else r.contrato_id.tipo_record_sap
    #         # r.tipo_record = dict(LISTA_TIPO_RECORD)[r.contrato_id.tipo_record_manual] if r.contrato_id.tipo_record_manual else r.contrato_id.tipo_record_sap

    def _compute_es_especial(self):
        for r in self:
            r.es_especial = r.tiene_redes_acueducto == 'no'


    @api.onchange('latitud')
    def _onchange_latitud(self):

        if self.latitud and (self.latitud < 4.24133927 or self.latitud > 5.04472740):
            _logger.warning(f"Se ingresó un valor de latitud por fuera del rango de valores para Bogotá y sus alrededores: {self.latitud}")
            # raise ValidationError("El valor de latitud debe estar entre 4.24133927 y 5.04472740.")
            raise ValidationError("El valor de latitud debe estar entre 4.24133927 y 5.04472740.")

        # Verificar que tenga exactamente 4 decimales
        if self.latitud > 0:
            latitud_str = str(self.latitud)
            if '.' in latitud_str:
                decimales = latitud_str.split('.')[1]
                if len(decimales) != 4:
                    _logger.warning(f"Se ingresó un valor de latitud sin 4 decimales: {self.latitud}")
                    raise ValidationError("La latitud debe tener exactamente 4 decimales. Ejemplo: 4.2414")
            else:
                _logger.warning(f"Se ingresó un valor de latitud sin decimales: {self.latitud}")
                raise ValidationError("La latitud debe tener exactamente 4 decimales. Ejemplo: 4.2414")


    @api.onchange('longitud')
    def _onchange_longitud(self):
        # Para validar que sean unas coordenadas válidas para Bogotá

        if self.longitud and (self.longitud < -74.2949 or self.longitud > -73.6663):
            _logger.warning(f"Se ingresó un valor de longitud por fuera del rango de valores para Bogotá y sus alrededores: {self.longitud}")
            raise ValidationError("El valor de longitud debe estar entre -74.2949 y -73.6663.")
            # raise ValidationError("Recuerde que debido a la ubicación geográfica de Bogotá, la longitud debe ser un valor negativo y con una precisión de al menos 4 decimales.")

        # Verificar que tenga exactamente 4 decimales
        if self.longitud > 0.0:
            longitud_str = str(self.longitud)
            if '.' in longitud_str:
                decimales = longitud_str.split('.')[1]
                if len(decimales) != 4:
                    _logger.warning(f"Se ingresó un valor de longitud sin 4 decimales: {self.longitud}")
                    raise ValidationError("La longitud debe tener exactamente 4 decimales. Ejemplo: -74.1234")
            else:
                _logger.warning(f"Se ingresó un valor de longitud sin decimales: {self.longitud}")
                raise ValidationError("La longitud debe tener exactamente 4 decimales. Ejemplo: -74.1234")


    @api.onchange('tiene_redes_acueducto')
    def _onchange_tiene_redes_acueducto(self):
        if self.tiene_redes_acueducto and self.tiene_redes_acueducto == 'si':
            self.aplica_topografia = 'si'
        else:
            self.aplica_topografia = ''


    def ver_cuadro_maestro(self):
        cuadro_maestro_id = self.env['sigedat.tramite.cuadro_maestro'].search([('tramite_id', '=', self.id)])
        if cuadro_maestro_id:
            return {
                'res_model': 'sigedat.tramite.cuadro_maestro',
                'res_id': cuadro_maestro_id.id,
                'context': {},
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
            }


    def wkf__en_proceso(self):
        #INFO: Valido que se haya cargado la Información de la pestaña generalidades
        if not self.latitud:
            _logger.warning("No se ingresó valor de latitud.")
            raise ValidationError("No se ingresó el valor de latitud.")
        if not self.longitud:
            _logger.warning("No se ingresó valor de longitud.")
            raise ValidationError("No se ingresó el valor de longitud.")
        if not self.tiene_frente:
            _logger.warning("No se indicó si tiene frente.")
            raise ValidationError("No se indicó si el acuerdo tiene frente.")
        if not self.tiene_redes_acueducto:
            _logger.warning("No se indicó si tiene redes de acueducto.")
            raise ValidationError("No se indicó si el acuerdo tiene redes de acueducto.")
        if not self.aplica_topografia:
            _logger.warning("No se indicó si aplica para topografía.")
            raise ValidationError("No se indicó si el acuerdo aplica para topografía.")

        self.state = 'en_proceso'


    def wkf__cerrado(self):
        self.state = 'cerrado'


    def ir_mapa(self):
        dominio = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not dominio:
            raise ValidationError('El parametro del dominio, no esta configurado.')
        url= f'{dominio}/sigedat/visor/coordenadas/{self.id}'
        return {
            'name':'Actualizar coordenadas',
            'res_model':'ir.actions.act_url',
            'type':'ir.actions.act_url',
            'target':'self',
            'url': url
        }
