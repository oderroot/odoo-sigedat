# -*- coding: utf-8 -*-
import logging
import requests
import json

from odoo.addons.base_conf.tools.utilitarios import eliminar_caracteres_no_ascii_cadena
from appy.pod.renderer import Renderer
import shutil
import os
from odoo.exceptions import ValidationError
import uuid
import base64

_logger = logging.getLogger(__name__)


class Reporte:
    """ Clase creada para el manejo de toda la funcionalidadrelacionada con generar reportes
    """

    def __init__(self, modelo, ruta_base_plantilla, nombre_plantilla, datos, ruta_base_trabajo='/tmp/reportes'):
        self.modelo = modelo
        self.ruta_base_plantilla = ruta_base_plantilla
        self.nombre_plantilla = nombre_plantilla
        self.datos = datos
        self.ruta_base_trabajo = ruta_base_trabajo

    def __limpiar_carpeta_trabajo(self):
        # Elimino la carpeta con todo su contenido
        if os.path.exists(self.ruta_base_trabajo):
            shutil.rmtree(self.ruta_base_trabajo)

    def generar_reporte(self, formato_salida):
        """
        """
        self.formato_reporte = formato_salida
        ruta_plantilla = self.modelo.env['ir.config_parameter'].sudo().get_param(self.ruta_base_plantilla, '')

        if not ruta_plantilla:
            raise Warning('Falta configurar el parámetro de plantilla {}'.format(self.ruta_base_plantilla))

        # Elimino los reportes anteriores del disco
        self.__limpiar_carpeta_trabajo()
        os.makedirs(self.ruta_base_trabajo)

        # Si el archivo tiene caracteres no ascii los cambia por una raya
        # nombre_reporte = eliminar_caracteres_no_ascii_cadena(nombre_plantilla, '-')
        nombre_reporte = f"{self.nombre_plantilla.split('.')[0]}.{self.formato_reporte}"

        # Genero el reporte en odf, basado en la plantilla y los datos pasados
        ruta_base_plantilla = os.path.join(ruta_plantilla, self.nombre_plantilla)
        self.ruta_reporte = os.path.join(self.ruta_base_trabajo, nombre_reporte)
        try:
            renderer = Renderer(ruta_base_plantilla, {'datos':self.datos}, self.ruta_reporte)
            renderer.run()
        except Exception as e:
            raise ValidationError(f"Se produjo un error: {e}, al generar el reporte.")
        with open(self.ruta_reporte, 'rb') as f:
            self.contenido_archivo = base64.b64encode(f.read())

    def descargar_reporte(self, nombre_reporte):
        """
        """
        wizard_archivo_id = self.modelo.env['base_conf.wizard.descargar_archivo']
        registro = wizard_archivo_id.create(
                {
                    'nombre_archivo': "{}.{}".format(nombre_reporte, self.formato_reporte),
                    'contenido_archivo': self.contenido_archivo,
                }
            )
        if registro:
            return {
                    'type' : 'ir.actions.act_url',
                    'url': '/web/content/base_conf.wizard.descargar_archivo/{}/contenido_archivo/{}'.format(registro.id, registro.nombre_archivo),
                    'target': 'new',
                    }
        else:
            raise Warning('Error al descargar el reporte')