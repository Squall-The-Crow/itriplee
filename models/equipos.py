# -*- coding: utf-8 -*-

from odoo import models, fields, api

class equipos(models.Model):
    _name = 'itriplee.equipos'
    _rec_name = 'name'

    name = fields.Char('Serie')
    factura = fields.Char('factura')
    venta = fields.Date('Fecha de Venta')
    modelo = fields.Many2one('itriplee.catalogo', 'Modelo')
    marca = fields.Char('Marca', related='modelo.marca.name', readonly=True)
    tipo = fields.Char('Tipo', related='modelo.tipo.name', readonly=True)
    cliente = fields.Many2one('res.partner', 'Cliente')
    vendedor = fields.Many2one('res.users', 'Vendido Por')
    poliza = fields.Many2one('itriplee.polizas', 'Poliza')
    garantia = fields.Many2one('itriplee.garantias', 'Garantia')
    visitas = fields.One2many ('itriplee.servicio', 'equipos', 'Visitas Realizadas')

    #Revisar
