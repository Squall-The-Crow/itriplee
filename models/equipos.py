# -*- coding: utf-8 -*-

from odoo import models, fields, api

class equipos(models.Model):
    _name = 'itriplee.equipos'
    _rec_name = 'name'
    _description = "Modulo de registro de los equipos de cliente y sus movimientos"

    name = fields.Char('Serie')
    factura = fields.Char('factura')
    venta = fields.Date('Fecha de Venta')
    modelo = fields.Many2one('itriplee.catalogo', 'Modelo')
    capacidad = fields.Char('Capacidad', related='modelo.capacidad', readonly=True)
    marca = fields.Char('Marca', related='modelo.marca.name', readonly=True)
    tipo = fields.Char('Tipo', related='modelo.tipo.name', readonly=True)
    cliente = fields.Many2one('res.partner', 'Cliente')
    vendedor = fields.Many2one('res.users', 'Vendido Por')
    poliza = fields.Many2one('itriplee.polizas', 'Poliza')
    garantia = fields.Many2one('itriplee.garantias', 'Garantia')
    visitas = fields.Many2many ('itriplee.servicio', string='Visitas Realizadas')

class equipos(models.Model):
    _name = 'itriplee.equipos_genericos'
    _rec_name = 'name'
    _description = "Modulo de registro de los equipos de cliente y sus movimientos"
    name = fields.Char('Equipo')
    caracteristicas = fields.Char('Caracteristicas')
    capacidad = fields.Char('Capacidad')

    #Revisar
