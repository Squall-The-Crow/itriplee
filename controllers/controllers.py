# -*- coding: utf-8 -*-
from odoo import http

# class Itriplee(http.Controller):
#     @http.route('/itriplee/itriplee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itriplee/itriplee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itriplee.listing', {
#             'root': '/itriplee/itriplee',
#             'objects': http.request.env['itriplee.itriplee'].search([]),
#         })

#     @http.route('/itriplee/itriplee/objects/<model("itriplee.itriplee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itriplee.object', {
#             'object': obj
#         })