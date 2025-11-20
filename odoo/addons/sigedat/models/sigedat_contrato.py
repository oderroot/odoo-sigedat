# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
# from models.sigedat_tramite_solicitud import LISTA_SI_NO
from odoo import models, fields, api

from odoo.addons.sigedat.wizards.crear_contrato import LISTA_TIPO_RECORD
from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO

class SigedatContrato(models.Model):
    _name = 'sigedat.contrato'
    _description = 'Contrato'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    state = fields.Selection(
        string='Estado',
        selection=[
            ('previo', 'previo'),
            ('ejecucion', 'ejecucion'),
            ('terminado', 'terminado'),
        ],
        default='previo',
        tracking=True,
        required=True,
    )
    tipo_id = fields.Many2one(
        string='Tipo',
        comodel_name='sigedat.contrato.tipo',
        tracking=True,
        required=True,
    )
    tipo = fields.Char(
        related='tipo_id.abreviatura'
    )
    name = fields.Char(
        string='Número',
        tracking=True,
        size=255,
    )
    fecha_inicio = fields.Date(
        string='Fecha inicio',
    )
    fecha_fin = fields.Date(
        string='Fecha fin',
    )
    objeto = fields.Text(
        string='Objeto',
        tracking=True,
        required=True,
    )
    #INFO Grupo Contratista
    empresa_contratista = fields.Char(
        string='Empresa/contratista',
        size=255,
        tracking=True,
    )
    correo_electronico_contratista = fields.Char(
        string='Correo electrónico',
        size=100,
        tracking=True,
    )
    telefono_contratista = fields.Char(
        string='Teléfono',
        size=15,
        tracking=True,
    )
    #INFO Grupo Supervisor
    area_id = fields.Many2one(
        string='Área',
        comodel_name='sigedat.area',
        tracking=True,
    )
    supervisor = fields.Char(
        string='Nombre',
        size=255,
        tracking=True,
    )
    correo_electronico_supervisor = fields.Char(
        string='Correo electrónico',
        size=100,
        tracking=True,
    )
    #INFO Grupo Interventoría
    contrato_interventoria = fields.Char(
        string='Contrato interventoría',
        size=255,
        tracking=True,
    )
    nombre_empresa_interventor = fields.Char(
        string='Nombre empresa',
        size=255,
    )
    nombre_interventor = fields.Char(
        string='Nombre contacto',
        size=255,
        tracking=True,
    )
    correo_electronico_interventor = fields.Char(
        string='Correo electrónico',
        size=100,
        tracking=True,
    )
    telefono_interventor = fields.Char(
        string='Teléfono',
        size=15,
        tracking=True,
    )
    tiene_frente = fields.Selection(
        string='¿Tiene Frente?',
        required=True,
        selection=LISTA_SI_NO,
        default='no',
        tracking=True,
    )
    frente_ids = fields.One2many(
        string='Frentes',
        comodel_name='sigedat.frente',
        inverse_name='contrato_id',
        tracking=True,
    )
    tipo_record = fields.Selection(
        string='Tipo Record',
        selection=LISTA_TIPO_RECORD,
        tracking=True,
    )
    numero_disenio = fields.Char(
        string='Número de diseño',
        size=255,
        tracking=True,
    )
    _sql_constraints = [
        ('numero_acuerdo_no_repetido', 'unique(name)', 'Este número de acuerdo ya se encuentra registrado en la base de datos.'),
        ('fecha_valida', 'check(fecha_inicio <= fecha_fin)', 'No es posible, que la fecha de inicio, sea mayor que la fecha fin'),
    ]
    # -------------------
    # methods
    # -------------------

