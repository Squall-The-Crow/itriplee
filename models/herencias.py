# -*- coding: utf-8 -*-

from odoo import fields, models, api

class resUsers(models.Model):
    _inherit = "res.users"
    puesto = fields.Char(string='Puesto')

resUsers()

class resPartner(models.Model):
    _inherit = "res.partner"

    cotizaciones = fields.One2many('itriplee.cotizaciones', 'name', string='Cotizaciones', copy=True, auto_join=True)
    tcliente = fields.Selection([('usuario', 'Usuario'),
                               ('usuario importante', 'Usuario Importante'),
                               ('intermediario', 'Intermediario'),
                               ('rm', 'Representante de Marca'),
                               ], string='Tipo de Cliente', default='usuario')
    sector = fields.Char('Sector')