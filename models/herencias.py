# -*- coding: utf-8 -*-

from odoo import fields, models, api

class resUsers(models.Model):
    _inherit = "res.users"
    _description = "campo de puesto"

    puesto = fields.Char(string='Puesto')  
    rol = fields.Selection([('vendedor', 'vendedor'),
                            ('tecnico', 'tecnico'),
                            ], string='Rol')  

class resPartner(models.Model):
    _inherit = "res.partner"
    _description = "campos agregados a los clientes"

    cotizaciones = fields.One2many('itriplee.cotizaciones', 'cliente_registrado', string='Cotizaciones', copy=True, auto_join=True)
    equipos = fields.One2many('itriplee.equipos', 'cliente', string='Equipos', copy=True, auto_join=True)
    servicios = fields.One2many('itriplee.servicio', 'cliente', string='Servicios', copy=True, auto_join=True)
    tcliente = fields.Selection([('usuario', 'Usuario'),
                               ('usuario importante', 'Usuario Importante'),
                               ('intermediario', 'Intermediario'),
                               ('rm', 'Representante de Marca'),
                               ], string='Tipo de Cliente', default='usuario')
    sector = fields.Char('Sector')