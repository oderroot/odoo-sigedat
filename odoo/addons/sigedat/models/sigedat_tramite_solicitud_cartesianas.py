# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from base64 import b64encode, b64decode
from datetime import timedelta, datetime
import logging
import shutil
from odoo.addons.base_conf.tools.reportes import Reporte
from odoo.addons.base_conf.tools.utilitarios import normalizar_cadena, LISTA_SI_NO
from odoo.addons.base_conf.tools.mail import enviar_mensaje_con_plantilla
from odoo.addons.base_conf.tools.archivos import comprimir_carpeta

_logger = logging.getLogger(__name__)
RUTA_BASE = '/tmp'

class SigedatTramiteSolicitudCartesianas(models.Model):
    _name = 'sigedat.tramite.solicitud.cartesiana'
    _description = 'Cartesianas de la solicitud de trámite'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
    )
    norte = fields.Float(
        string='norte',
    )
    este = fields.Float(
        string='este',
    )
    cota_geometrica = fields.Float(
        string='Cota geometrica',
    )
    solicitud_id = fields.Many2one(
        string='Solicitud',
        comodel_name='sigedat.tramite.solicitud',
        ondelete='cascade',
    )

    # -------------------
    # methods
    # -------------------
