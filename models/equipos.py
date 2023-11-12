# -*- coding: utf-8 -*-

from odoo import models, fields, api

class equipos(models.Model):
    _name = 'itriplee.equipos'
    _rec_name = 'name'
    _description = "Modulo de registro de los equipos de cliente y sus movimientos"

    name = fields.Char('Serie')
    factura = fields.Char('factura')
    venta = fields.Date('Fecha de Venta')
    catalogo = fields.Boolean('Esta en catalogo?', default=True)
    modelo = fields.Many2one('itriplee.catalogo', 'Modelo')
    modelo_show = fields.Char('Modelo', related='modelo.name', readonly=False, store=True)
    capacidad = fields.Char('Capacidad', related='modelo.capacidad', readonly=False, store=True)
    marca = fields.Char('Marca', related='modelo.marca.name', readonly=False, store=True)
    tipo = fields.Char('Tipo', related='modelo.tipo.name', readonly=False, store=True)
    tecnologia = fields.Selection('Tecnologia', related='modelo.tecnologia', readonly=False, store=True)
    cliente = fields.Many2one('res.partner', 'Cliente')
    vendedor = fields.Many2one('res.users', 'Vendido Por')
    poliza = fields.Many2one('itriplee.polizas', 'Poliza')
    garantia = fields.Many2one('itriplee.garantias', 'Garantia')
    visitas = fields.Many2many ('itriplee.servicio', string='Visitas Realizadas')
    caracteristicas = fields.Text('Caracteristicas')