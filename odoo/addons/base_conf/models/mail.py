# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, tools

class Message(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _name = 'mail.message'
    _inherit = 'mail.message'

    def unlink(self):
        # No eliminar estos datos
        return True


class MailTracking(models.Model):
    """Mantiene los cambios hechos en los campos de un modelo"""
    _name = 'mail.tracking.value'
    _inherit = 'mail.tracking.value'

    def unlink(self):
        # No eliminar estos datos
        return True
