# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
from odoo.addons.base_conf.tools.validaciones import es_valido_correo_electronico, es_valido_numero

#FIXME En la vista form, al momento de crear una nueva persona, deja como solo lectura algunos campos obligatorios.
class SigedatPersona(models.Model):
    _name = 'sigedat.persona'
    _description = 'Persona'
    _inherit = ['mail.thread', 'mail.activity.mixin' ]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        compute='_compute_name'
    )
    tipo_persona = fields.Selection(
        string='Tipo de Persona',
        required=True,
        selection=[
            ('natural', 'Natural'),
            ('juridica', 'Juridica')
        ],
        default='natural',
        tracking=True,
    )
    nombre = fields.Char(
        string='Nombre',
        tracking=True,
    )
    apellido = fields.Char(
        string='Apellido',
        tracking=True,
    )
    tipo_identificacion_id = fields.Many2one(
        string='Tipo de Identificación',
        comodel_name='sigedat.persona.tipo_identificacion',
        tracking=True,
    )
    numero_identificacion = fields.Char(
        string='Número de Identificación',
        tracking=True,
        help='Por favor ingrese el número de identificación, sin puntos, ni guiones.'
    )
    telefono_fijo = fields.Char(
        string='Teléfono Fijo',
        tracking=True,
    )
    telefono_movil = fields.Char(
        string='Teléfono Móvil',
        tracking=True,
    )
    direccion = fields.Char(
        string='Dirección',
        tracking=True,
    )
    correo_electronico = fields.Char(
        string='Correo electrónico principal',
        tracking=True,
    )
    habeas_data = fields.Boolean(
        string='Habeas Data',
        tracking=True,
    )
    terminos_condiciones = fields.Boolean(
        string='Términos y Condiciones',
        tracking=True,
    )
    usuario_id = fields.Many2one(
        string='Usuario',
        comodel_name='res.users',
        ondelete='cascade',
        #FIXME Debo revisar como hacer xa tomar el usuario por defecto y guardalo aca, xa poder filtrar en la vista
        # compute='_compute_usuario',
        tracking=True,
    )
    correo_notificacion = fields.Char(
        string='Correo Notificación',
        default=lambda self: self.correo_electronico,
        tracking=True,
    )
    es_administrador = fields.Boolean(
        string='¿Es Administrador?',
        compute='_compute_es_administrador'
    )

    _sql_constraints = [
        ('identificacion_no_repetida', 'unique(numero_identificacion)', 'Éste número de identificación ya está registrado.'),
        ('correo_principal_no_repetido', 'unique(correo_electronico)', 'Ésta dirección de correo ya esta registrado.'),
        ('correo_notificacion_no_repetido', 'unique(correo_notificacion)', 'Ésta dirección de correo ya esta registrado.'),
    ]

    # -------------------
    # methods
    # -------------------
    def _compute_name(self):
        for r in self:
            if r.tipo_persona == 'natural':
                r.name = f"{r.nombre} {r.apellido}"
            else:
                r.name = f"{r.nombre}"

    def _compute_usuario(self):
        for r in self:
            r.usuario_id = r.env.uid

    def _compute_es_administrador(self):
        #FIXME No esta tomando quien tiene el perfil de administrador
        for r in self:
            r.es_administrador = r.env.user.has_group('sigedat.administrador')

    @api.onchange('tipo_persona')
    def _onchange_tipo_persona(self):
        self.tipo_identificacion_id = None
        tipos_persona_juridica = self.env['sigedat.persona.tipo_identificacion'].search([('aplica_a', '=', 'juridica')]).ids
        if self.tipo_persona == 'juridica':
            return {'domain': {'tipo_identificacion_id': [('id', 'in', tipos_persona_juridica)]}}
        else:
            return {'domain': {'tipo_identificacion_id': [('id', 'not in', tipos_persona_juridica)]}}

    @api.onchange('numero_identificacion')
    def _onchange_numero_identificacion(self):
        if self.numero_identificacion:
            if not es_valido_numero(self.numero_identificacion, minimo=10000, maximo=2000000000):
                raise ValidationError(f'{self.numero_identificacion} no es un número de identificación válido.')

    @api.onchange('telefono_fijo')
    def _onchange_telefono_fijo(self):
        if self.telefono_fijo:
            if not es_valido_numero(self.telefono_fijo, minimo=2000000, maximo=9999999):
                raise ValidationError(f'{self.telefono_fijo} no es un número de teléfono válido. Los números fijos se componen de 7 números sin indicativo.')

    @api.onchange('telefono_movil')
    def _onchange_telefono_movil(self):
        if self.telefono_movil:
            if not es_valido_numero(self.telefono_movil, minimo=3000000001, maximo=3509999999):
                raise ValidationError(f'{self.telefono_movil} no es un número de teléfono válido. Los números móviles se componen de 10.')

    @api.onchange('correo_electronico')
    def _onchange_correo_electronico(self):
        if self.correo_electronico:
            if not es_valido_correo_electronico(self.correo_electronico.lower()):
                self.correo_electronico = ''
                raise ValidationError(f"La dirección de correo electrónico ingresado no es válido")


    @api.onchange('correo_notificacion')
    def _onchange_correo_notificacion(self):
        if self.correo_notificacion:
            if not es_valido_correo_electronico(self.correo_notificacion.lower()):
                self.correo_notificacion = ''
                raise ValidationError(f"La dirección de correo electrónico ingresado no es válido")


    def eliminar_apoyo(self):
        id = self.env.context.get('persona_id', 0)
        id_equipo = self.env.context.get('equipo_id', 0)
        if not id or not id_equipo:
            raise ValidationError(f"No llegó el id de la persona:{id} equipo:{id_equipo}")
        persona_id = self.env['sigedat.persona'].browse([id])
        equipo_id = self.env['sigedat.equipo_apoyo'].browse([id_equipo])
        if not equipo_id or not persona_id:
            raise ValidationError("No se encontró a la persona.")
        grupo = 'Topografía'
        grupo_id = self.env['res.groups'].search([('name', '=', grupo)])
        if not grupo_id:
            raise ValidationError(f"No se encontró el grupo: {grupo}")
        if not persona_id.usuario_id:
            raise ValidationError(f"La persona:{persona_id.name} no tiene un usuario del sistema asociado")
        # agrego un usuario al grupo
        # grupo_id.sudo().users = [(4,persona_id.usuario_id.id)]
        # elimino un usuario del grupo
        grupo_id.sudo().users = [(3,persona_id.usuario_id.id)]
        # elimino a la persona del grupo
        equipo_id.persona_ids = [(3,persona_id.id)]
