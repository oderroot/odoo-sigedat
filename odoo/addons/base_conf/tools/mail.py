# -*- coding: utf-8 -*-

from base64 import b64encode
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


def enviar_nota(objeto, cuerpo_nota):
    """Función que genera una nota de seguimiento en odoo."""
    if objeto and cuerpo_nota:
        try:
            objeto.message_post(
                body=cuerpo_nota,
            )
        except Exception as e:
            msg = str(e)
            _logger.exception("No se pudo enviar la nota")


def enviar_enviar_mensaje_sin_plantilla(objeto, remitente, destinatario, titulo, mensaje, adjuntos=[], tipo='plain'):
        # adjuntos: list of (filename, filecontents, mime)
                # # https://developer.mozilla.org/es/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        # tipo: 'plain' o 'html' es el tipo mime para el texto del cuerpo,
                # debe concordar con el formato del cuerpo. por defecto es 'plain',
                # haciendo el contenido "text/plain".
    try:
        email = objeto.env['ir.mail_server'].build_email(
            email_from=remitente,
            email_to=[destinatario],
            subject=titulo,
            body=mensaje,
            attachments=adjuntos,
            subtype=tipo,
        )
        objeto.env['ir.mail_server'].send_email(email)
        return True
    except Exception as e:
        raise ValidationError(f'No fue posible enviar correo electrónico, por: {e}')


def enviar_mensaje_con_plantilla(objeto, contexto, plantilla, boton_plantilla={}, nombre_adj="", contenido_adj=""):
    #TODO quitar parametro boton_plantilla, ya que no se usa
    if objeto and contexto and plantilla:
        try:
            if nombre_adj:
                objeto.sudo().with_context(contexto).message_post_with_template(
                    plantilla.id,
                    notify=True,
                    composition_mode='mass_mail',
                    attachment_ids=[(0, 0, {'name':nombre_adj, 'datas_fname': nombre_adj, 'datas': b64encode(contenido_adj)})]
                    )
            else:
                objeto.sudo().with_context(contexto).message_post_with_template(
                    plantilla.id,
                    notify=True,
                    composition_mode='mass_mail',
                    )
        except Exception as e:
            raise ValidationError(f"No fue posible enviar correo electrónico, por: {e}")
