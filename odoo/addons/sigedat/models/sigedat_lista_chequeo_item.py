# -*- coding: utf-8 -*-
##############################################################################
# see LICENSE.TXT
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.base_conf.tools.utilitarios import LISTA_SI_NO_NA

class SigedatListaChequeoItem(models.Model):
    _name = 'sigedat.lista_chequeo.item'
    _description = 'Item de la Lista de Chequeo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _domain_observacion(self):
        item_id = self._context.get('active_id', '0')
        item_ids = self.env['item_observacion_relacion'].search([('item_id', '=', item_id)])
        return [('id', 'in', item_ids.mapped('observacion_id'))]

    # -------------------
    # Fields
    # -------------------
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
    )
    lista_chequeo_id = fields.Many2one(
        string='Parámetro',
        required=True,
        comodel_name='sigedat.lista_chequeo',
        tracking=True,
        domain="[('activo', '=', True)]",
    )
    cumple = fields.Selection(
        string='Cumple',
        selection=LISTA_SI_NO_NA,
        default='na',
        required=True,
        tracking=True,
    )
    observacion_ids = fields.One2many(
        string='Observaciones',
        comodel_name='sigedat.lista_chequeo.item.observacion',
        tracking=True,
        inverse_name='item_id',
        #FIXME Solo debe mostrar las observaciones del mismo acuerdo
        # domain=_domain_observacion,
        # domain="[('item_id', '=', id)]",
    )
    solicitud_tramite_id = fields.Many2one(
        string='Solicitud de trámite',
        required=True,
        comodel_name='sigedat.tramite.solicitud',
        tracking=True,
        ondelete='cascade',
        domain=lambda self: self._context.get('solicitud_tramite_id', False),
    )
    numero_lista_chequeo = fields.Char(
        string='Número lista de chequeo',
        size=9,
    )
    version_lista_chequeo = fields.Char(
        string='Version lista chequeo',
        size=3,
    )
    seccion_id = fields.Many2one(
        related='lista_chequeo_id.seccion_id',
    )
    se_toma_tramite_anterior = fields.Boolean(
        related='lista_chequeo_id.se_toma_tramite_anterior'
    )
    permitido_entrega_posterior = fields.Boolean(
        related='lista_chequeo_id.permitido_entrega_posterior'
    )

    # -------------------
    # methods
    # -------------------

    @api.model
    def create(self, values):
        """
            Create a new record for a model SigedatListaChequeoItem
            @param values: provides a data for new record

            @return: returns a id of new record
        """
        # Saltar validación si estamos copiando desde otra solicitud
        if not self._context.get('skip_observacion_validation', False):
            if 'cumple' in values:
                if values['cumple'] == 'no' and not 'observacion_ids' in values:
                    raise ValidationError(f"Se debe ingresar al menos una observación para los ítems que no cumplen.")
                # elif values['cumple'] in ['si', 'na'] and 'observacion_ids' in values:
                #     if values['observacion_ids'] != [(6, 0, [])]:
                #         raise ValidationError(f"Si el ítem cumple o no aplica, no debe tener observaciones.")

        result = super(SigedatListaChequeoItem, self).create(values)
        solicitud_tramites_del_mismo_tipo = self.env['sigedat.tramite.solicitud'].search_count([('tramite_id','=',result.solicitud_tramite_id.tramite_id.id),('tipo_tramite_id','=',result.solicitud_tramite_id.tipo_tramite_id.id)])
        result.sudo().version_lista_chequeo = solicitud_tramites_del_mismo_tipo
        return result


    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise

            @param values: dict of new values to be set

            @return: True on success, False otherwise
        """
        # Saltar validación si estamos copiando desde otra solicitud
        if not self._context.get('skip_observacion_validation', False):
            if 'cumple' in values:
                if values['cumple'] == 'no' and not 'observacion_ids' in values:
                    raise ValidationError(f"Se debe ingresar al menos una observación para los ítems que no cumplen.")

        result = super(SigedatListaChequeoItem, self).write(values)
        return result

    def _compute_name(self):
        for r in self:
            r.name = f"Lista Chequeo: {r.lista_chequeo_id.name}"

