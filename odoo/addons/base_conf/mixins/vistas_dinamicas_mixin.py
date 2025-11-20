# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
import json


class vistas_dinamicas_mixin(models.AbstractModel):
    _name = 'models.vistas_dinamicas.mixin'
    _description = 'Para editar campos(vista) desde python'


    def update_json_data(self, json_data=False, update_data={}):
        ''' It updates JSON data. It gets JSON data, converts it to a Python
        dictionary, updates this, and converts the dictionary to JSON data
        again. '''
        dict_data = json.loads(json_data) if json_data else {}
        dict_data.update(update_data)
        return json.dumps(dict_data, ensure_ascii=False)

    def set_modifiers(self, element=False, modifiers_upd={}):
        ''' It updates the JSON modifiers with the specified data to indicate
        if a XML tag is readonly or invisible or not. '''
        if type(element) == list:
            if len(element) > 0:
                element = element[0]
                if element is not False:  # Do not write only if element:
                    modifiers = element.get('modifiers') or {}
                    modifiers_json = self.update_json_data(
                        modifiers, modifiers_upd)
                    element.set('modifiers', modifiers_json)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        campos = self._context.get('campos_editar', None)
        botones = self._context.get('botones_editar', None)
        atributos_campos = self._context.get('atributos_campos', None)
        atributos_botones = self._context.get('atributos_botones', None)
        res = super(vistas_dinamicas_mixin, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for campo in campos:
                campo_editar = doc.xpath("//field[@name='{}']".format(campo))
                self.set_modifiers(campo_editar, atributos_campos)
            for boton in botones:
                boton_editar = doc.xpath("//button[@name='{}']".format(boton))
                self.set_modifiers(boton_editar, atributos_botones)

            res['arch'] = etree.tostring(doc)
        return res