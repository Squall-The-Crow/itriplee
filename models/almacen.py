# -*- coding: utf-8 -*-

from odoo import models, fields, api

class almacen(models.Model):
    _name = 'itriplee.almacen'
    _rec_name = 'name'

########Campos De sistema##############
    name = fields.Char(string='Nombre de Almacen', required=True)
    ubicacion = fields.Char(string='ubcacion')
    productos = fields.One2many('itriplee.catalogo', 'almacen', string='Productos', copy=True, auto_join=True)