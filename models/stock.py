# -*- coding: utf-8 -*-

from odoo import models, fields, api


AVAILABLE_STATES = [
    ('disponible', 'Disponible'),
    ('reservado', 'Reservado'),
    ('garantia', 'En Garantia'),
    ('Instalado', 'Instalado'),
    ('vendida', 'Vendida'),
    ]

class stock(models.Model):
    _inherit = 'itriplee.catalogo'

    cantidad = fields.Integer('Cantidad Disponible')
    reservado = fields.Integer('Cantidad Reservada')
    vendidos = fields.Integer('Vendidos')
    garantias = fields.Integer('Instalados en garantia')
    entrega = fields.Integer('Por recibir')
    #programado = fields.Integer('Cantidad', required=True) visualizar el stock entrante
    #atrasado = fields.Integer('Cantidad', required=True) visualizar el stock entrante
    almacen = fields.Many2one('itriplee.almacen', string='Almacen')
    minimo = fields.Integer('Cantidad Minima')
    cb =  fields.Char('Codigo de Barras')
    tecnico = fields.Many2one('res.users', 'Técnico', ondelete='cascade')
    series =  fields.One2many('itriplee.stock.series', 'producto', string='Numeros de Serie')


class series(models.Model):
    _name = 'itriplee.stock.series'
    _rec_name = 'name'

    name = fields.Char('Numero de Serie')
    estado = fields.Selection(AVAILABLE_STATES, 'Estado', default='disponible')
    producto = fields.Many2one('itriplee.catalogo',) #hay que hacerlo automatico
    movimiento = fields.Many2one('itriplee.movimientos',)
    remplazo = fields.Many2one('itriplee.stock.series', 'Remplazado por')
    reparado = fields.Boolean('Reparada', default=False)
    definitivo = fields.Boolean('No genero entrada', default=False)
    documento = fields.Char('No. de documento de entrada')
    tecnico = fields.Many2one('res.users', 'Técnico', ondelete='cascade')
    documento_salida = fields.Char('No. de documento de salida')
    movimiento_entrada = fields.Many2one('itriplee.movimientos', 'Movimiento de entrada')
    movimiento_salida = fields.Many2one('itriplee.movimientos', 'Movimiento de salida')
    #servicio = fields.Many2one()
    #movimientos = fields.Many2many('itriplee.movimientos.linea',
     #                         'movimiento_series_rel',
      #                        'series_id',
       #                       'movimientos_id',
        #                      string='Movimientos de Producto')


    

