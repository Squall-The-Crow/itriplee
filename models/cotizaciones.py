# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from datetime import timedelta


class cotizaciones(models.Model):
    _name = 'itriplee.cotizaciones'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
###Funcion Fecha automatica######
    def _default_fecha(self):
        return fields.Date.context_today(self)

    ###Funcion Vigencia automatica######

    def _default_vigencia(self):
        today_str = fields.Date.context_today(self)
        today = fields.Date.from_string(today_str)
        expected = today + timedelta(days=15)
        return fields.Date.to_string(expected)

#####Funcion Sacar el total de los equipos multilinea#####
    @api.depends('multilinea.subtotal')
    def _costo_total(self):
        for order in self:
            total_sin_iva = iva = 0.0
            for line in order.multilinea:
                total_sin_iva += line.subtotal
                iva += total_sin_iva * 0.16
            order.update({
                'subtotal_multilinea': total_sin_iva,
                'iva_multilinea': iva,
                'total_multilinea': total_sin_iva + iva,
            })

    #####Funcion de los botones#####

    @api.multi
    def button_aceptada(self):
        for rec in self:
            rec.write({'estado': 'aceptada'})

    @api.multi
    def button_facturada(self):
        for rec in self:
            rec.write({'estado': 'facturada'})

    @api.multi
    def button_cancelada(self):
        for rec in self:
            rec.write({'estado': 'cancelada'})
########Campos De sistema##############
    name = fields.Char(string='Cotizacion', required=True, readonly=True, index=True,
                       default=lambda self: ('New'))
    estado = fields.Selection([('vigente', 'Vigente'),
                               ('vencida', 'Vencida'),
                               ('cancelada', 'Cancelada'),
                               ('aceptada', 'Aceptada'),
                               ('facturada', 'Facturada'),
                               ], string='Estado', default='vigente')
    fecha = fields.Date('Fecha', default=_default_fecha)
    vendedor = fields.Many2one('res.users', string='Vendedor', default=lambda self: self.env.user)
########Obligatorios, antes de empezar#####
    nuevo = fields.Boolean('Nuevo Cliente', required=True)
    usdomxn = fields.Selection([
        ("USD", "USD"),
        ("MXN", "MXN"),
    ], 'USD o MXN', required=True)
    tipo = fields.Selection([('multilinea', 'Multilinea'),
                               ('catalogo', 'En catalogo'),
                               ('otro', 'Otro'),
                               ], string='Tipo de Cotizacion', default='catalogo', required=True)
    ########Generales, Condicionales#####
    empresa = fields.Char('Empresa') #Falta poner el domain de if empresa
    cliente = fields.Char('Cliente') #Falta Poner el Domain de empresa
    telefono = fields.Char('Telefono')
    tipo_telefono = fields.Selection([
        ("cel","Celular"),
        ("casa","Casa"),
        ("ofi","Oficina")
        ], 'Tipo de Telefono')
    cliente_registrado = fields.Many2one('res.partner', 'Cliente')
    ########Generales#####
    tiempo_entrega = fields.Char('Tiempo de Entrega')
    condiciones_pago = fields.Selection([
        ("cod", "C o D"),
        ("pd", "Previo Deposito"),
        ("8D", "8 Dias"),
        ("15D", "15 Dias"),
        ("30D", "30 Dias"),
        ("60D", "60 Dias"),
        ("45D", "45 Dias"),
        ("90D", "90 Dias"),
        ("5050", "50% anticipo 50% aviso entrega")
    ], 'Condiciones de Pago')
    incluye = fields.Selection([
        ("conexion", "Conexion"),
        ("marcha", "Puesta en Marcha"),
        ("envio", "Envio"),
        ("conexion y marcha", "Conexión y Puesta en Marcha"),
        ("conexion y envio", "Conexión y Envio"),
        ("envio y marcha", "Envio y Puesta en Marcha"),
        ("conexion, envio y marcha", "Conexión, Envio y Puesta en Marcha")
    ], 'Incluye')
    entrega = fields.Text('Condiciones de Entrega', default="La entrega es en Planta Baja Libre de Maniobras")
    notas = fields.Text('Notas',
                        default="La cotización No incluye Instalación Eléctrica, material, así como viáticos para la puesta en marcha fuera de CDMX y área metropolitana.")
    vigencia = fields.Date('Vigencia de Cotizacion', default=_default_vigencia)
    ########Compartidos Cotizaciones#####
    descuento = fields.Integer('Descuento a Aplicar')
    cantidad = fields.Integer('Cantidad')
    precio_final = fields.Float('Precio', dp.get_precision('Precio'), store=True, compute="_operaciones")
    descuento_total = fields.Float('Total del Descuento', dp.get_precision('Precio'), store=True,
                                   compute="_operaciones")
    iva = fields.Float('IVA', dp.get_precision('Precio'), store=True, compute="_operaciones")
    subtotal = fields.Float('Subtotal', dp.get_precision('Precio'), store=True, compute="_operaciones")
    total = fields.Float('Total', dp.get_precision('Precio'), store=True, compute="_operaciones")
    tipo_equipo = fields.Many2one('itriplee.tipo', string='Tipo de Equipo')
    marca = fields.Many2one('itriplee.marca', string='Marca')
    modelo = fields.Many2one('itriplee.catalogo', string='Modelo')
    ########Contenido 2#####
    precio = fields.Float('Precio Unitario', dp.get_precision('Precio'))
    campo_memo = fields.Html('Descripcion')
    ########Contenido 3#####
    multilinea = fields.One2many('itriplee.orden.linea', 'orden_id', string='Equipos', copy=True, auto_join=True) # Falta poner la multilinea
    iva_multilinea = fields.Float('IVA', dp.get_precision('Precio'), store=True, compute="_costo_total")
    subtotal_multilinea = fields.Float('Subtotal', dp.get_precision('Precio'), store=True, compute="_costo_total")
    total_multilinea = fields.Float('Total', dp.get_precision('Precio'), store=True, compute="_costo_total")
    #######Fin de campos, inicia codigo automatizado######
    ######Calculo de totales de contenido 1 y 2#########
    @api.depends('modelo', 'cantidad', 'tipo', 'precio', 'descuento')
    def _operaciones(self):
        res = {}
        if self.tipo == 'catalogo':
            self.precio_final = float(self.modelo.tc.tc) * float(self.modelo.precio)
        elif self.tipo == 'otro':
            self.precio_final = self.precio
        self.descuento_total = (self.descuento / 100) * self.precio_final
        self.subtotal = (self.precio_final - self.descuento_total) * self.cantidad
        self.iva = self.subtotal * 0.16
        self.total = self.subtotal + self.iva
        res = ({
        'precio_final': self.precio_final,
        'descuento_total': self.descuento_total,
        'subtotal': self.subtotal,
        'iva': self.iva,
        'total': self.total,
        })
        return res
#######Automatizacion de nombre consecutivo#########
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cotizaciones') or ('New')
        res = super(cotizaciones, self).create(vals)
        return res



class Linea(models.Model):
    _name = 'itriplee.orden.linea'
    _description = 'Lineas de Cotizacion'
    _order = 'orden_id'

    @api.depends('cantidad', 'descuento', 'product_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            precio = line.product_id.precio * line.product_id.tc.tc
            subtotal = (precio * (1 - (line.descuento or 0.0) / 100.0)) * line.cantidad
            line.update({
                'precio_line': precio,
                'subtotal': subtotal,
            })

    @api.depends('product_id')
    def _compute_descripcion(self):
        """
        Compute the description of the SO line.
        """
        for line in self:
            name = ("Equipo Marca "+ str(line.product_id.marca.name) + " Modelo " + str(line.product_id.name) + " " +
                         str(line.product_id.capacidad) + " " + " Modelo " + " " + str(line.product_id.alto) + " " + str(line.product_id.ancho)
                         + " " + str(line.product_id.fondo))
            line.update({
                'name': name,
            })
    orden_id = fields.Many2one('itriplee.cotizaciones', string='Order Reference', required=True, ondelete='cascade', index=True,
                               copy=False, default=33)
    name = fields.Text(compute='_compute_descripcion', string='Descripcion', required=True, readonly=False, store=True)
    product_id = fields.Many2one('itriplee.catalogo', string='Equipo',
                                 default=0, ondelete='restrict', required=True)
    cantidad = fields.Float(string='Cantidad', digits=dp.get_precision('Precio'), required=True,
                                   default=1.0)
    #precio = fields.Float(string='Precio', required=True, digits=dp.get_precision('Precio'))
    descuento = fields.Float(string='Descuento (%)', digits=dp.get_precision('Precio'), default=0.0)
    subtotal = fields.Float(compute='_compute_amount', digits=dp.get_precision('Precio'), string='Subtotal')
    precio_line = fields.Float(compute='_compute_amount', string='Precio', required=True, readonly=False, digits=dp.get_precision('Precio'))
    sequence = fields.Integer(string='Sequence', default=10)


class tc(models.Model):
    _name = 'itriplee.tc'
    _rec_name = 'name'
    name = fields.Char('Tipo de Cambio')
    tc = fields.Float('Pesos')