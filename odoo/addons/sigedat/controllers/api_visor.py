from itertools import filterfalse
import odoo
from odoo import http, fields
from odoo.http import request
import json
import requests

class controller(http.Controller):

    @http.route('/sigedat/visor/coordenadas/<int:tramite_id>', type='http', auth='public', website=True, methods=['GET'], csrf=False)
    def index_(self, tramite_id, **kwargs):
        values = {}
        values.update(kwargs=kwargs.items())
        #if http.request.session.get('tramite_id', False):
        #    http.request.session['tramite_id'] = False
        values['tramite_id'] = tramite_id
        response = http.request.render('sigedat.index', values)
        response.headers.add('Cache-Control', 'max-age=0, no-cache, no-store, must-revalidate')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires','Mon, 26 Jul 1997 05:00:00 GMT')
        return response

    @http.route('/sigedat/visor', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def index_post(self, **kwargs):
        datos = kwargs
        return http.request.render("sigedat.index", {'datos': datos})

    @http.route('/sigedat/visor', type='http', auth='public', website=True, methods=['GET'], csrf=False, cors="*")
    def visor(self, **kwargs):
        values = {}
        values.update(kwargs=kwargs.items())
        response = http.request.render('sigedat.visor', values)
        response.headers.add('Cache-Control', 'max-age=0, no-cache, no-store, must-revalidate')
        response.headers.add('Pragma', 'no-cache')
        response.headers.add('Expires','Mon, 26 Jul 1997 05:00:00 GMT')
        return response

    @http.route('/sigedat/visor/get_tramite', auth='public', methods=['POST'], website=True, csrf=False, cors="*")
    def get_tramite(self, **kwargs):
        tramite_model = http.request.env['sigedat.tramite']
        tramites = tramite_model.sudo().search([('state','=', 'en_proceso')])
        lista_tramites = []
        #FIXME: Si se requieren que se muestren mas tramites en diferentes estados a en proces, se debe modificar esta informacion
        try:
            for tramite in tramites:
                lista_tramites.append({
                    'id': tramite.id,
                    'acuerdo': tramite.contrato_id.name,
                    'objeto': tramite.objeto,
                    'frente': tramite.frente_id.name or 'N/A',
                    'state': 'EN PROCESO',#tramite.state,
                    'longitud': tramite.longitud,
                    'latitud': tramite.latitud,
                })
            return json.dumps({
                'status': 'OK',
                'data': lista_tramites,
            })
        except Exception as e:
            return json.dumps({
                'status': 'ERROR',
                'data': 'No fué posible consultar los trámites: {}'.format(e),
            })

    @http.route('/sigedat/visor/enviar_coordenadas', auth='public', methods=['POST'], website=True, csrf=False, cors="*")
    def enviar_coordenadas(self, **kwargs):
        latitud = kwargs.get('lat')
        longitud = kwargs.get('lng')
        tramite_id = kwargs.get('tramite_id')
        if tramite_id:
            tramite_id=int(tramite_id)
            tramite_model = http.request.env['sigedat.tramite']
            datos_tramite = {
                'latitud': latitud,
                'longitud': longitud,
            }
            try:
                record = tramite_model.sudo().browse(tramite_id)
                tramite = record.write(datos_tramite)
                http.request.session['tramite_id'] = tramite_id
                datos = json.dumps({
                    'status': 'OK',
                    'data': tramite_id,
                })
                action_id = request.env.ref('sigedat.tramite_action').id
                menu_id = request.env.ref('sigedat.tramite_menu').id
                return request.redirect('/web#id={}&action={}&model=sigedat.tramite&view_type=form&cids=1&menu_id={}'.format(tramite_id,action_id,menu_id))
                
            except Exception as e:
                return json.dumps({
                    'status': 'ERROR',
                    'data': e,
                })
