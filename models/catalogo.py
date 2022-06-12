# -*- coding: utf-8 -*-

from odoo import models, fields, api




class catalogo(models.Model):
    _name = 'itriplee.catalogo'
    _rec_name = 'name'

    name = fields.Char('Modelo', required=True,)
    imagen = fields.Binary()
    precio = fields.Float('Precio')
    capacidad = fields.Char('Capacidad')
    #precio_usd = fields.Float('Precio en DLL')
    tc = fields.Many2one('itriplee.tc', string='Tipo de Cambio')
    selector = fields.Many2one('itriplee.selector', string='Selector')
    #precio_final = fields.Float('Precio en MXN', compute="_dllamxn")
    tipo = fields.Many2one('itriplee.tipo', string='Tipo de Equipo')
    marca = fields.Many2one('itriplee.marca', string='Marca')
    tecnologia = fields.Selection([("monofasico","Monofasico"),("bifasico","Bifasico"),("trifasico","Trifasico"),("ODC","Online Doble Conversión")], 'Tecnologia')
    voltaje_entrada = fields.Char('Voltaje de Entrada')
    voltaje_salida = fields.Char('Voltaje de Salida')
    fases = fields.Char('Fases')
    tiempo_respaldo = fields.Char('Tiempo de Respaldo')
    ancho = fields.Float('Ancho')
    alto = fields.Float('Alto')
    fondo = fields.Float('Fondo')
    peso = fields.Float('Peso')
    volts = fields.Float('Volts')
    amperes = fields.Float('Amperes')
    ficha_tecnica = fields.Char('Ficha Técnica')
    notas = fields.Text('Notas')
    descripcion = fields.Text('Descripcion Corta')
    cotizable = fields.Selection([("USD", "USD"), ("MXN", "MXN")], 'Moneda')
    FT = fields.Char('Ficha Tecnica')
#    seleccion = fields.Selection(string="Ejemplo de seleccion", selection=[("algo"),("algo")])
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
    #@api.depends('tc','precio_usd')
    #def _dllamxn(self):
     #   self.precio_mxn = float(self.tc.tc) * float(self.precio_usd)



class tipo(models.Model):
    _name = 'itriplee.tipo'
    name = fields.Char('Tipo')

class marca(models.Model):
    _name = 'itriplee.marca'
    name = fields.Char('Marca')
    imagen = fields.Binary()
    tipo = fields.Many2one('itriplee.tipo', string='Tipo')

class selector(models.Model):
    _name = 'itriplee.selector'
    name = fields.Char('Modelo')
    imagen = fields.Binary()
    capacidad = fields.Char('Capacidad')
    precio = fields.Float('Precio')
    tc = fields.Many2one('itriplee.tc', string='Tipo de Cambio')
