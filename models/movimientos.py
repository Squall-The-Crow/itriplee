# -*- coding: utf-8 -*-

from odoo import models, fields, api

class movimientos(models.Model):
    _name = 'itriplee.movimientos'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_fecha(self):
        return fields.Date.context_today(self)
    
    name = fields.Char(string='ID de Movimiento', readonly=True, index=True,
                       default=lambda self: ('New'))
    estado = fields.Selection([
        ("1","1"),
        ("2","Programada"),
        ("solicitada","Solicitada"),
        ("recibida","Recibida"),
        ("atrasada","Atrasada"),
        ("cancelada","Cancelada"),
        ("surtida","Surtida"),
        ("retornada","Refacciones retornadas"),
        ("entregadas","Refacciones entregadas"),
        ], 'Estado del movimiento', default='1')
    tipo = fields.Selection([
        ("entrada","Entrada"),
        ("salida","Salida"),
        ("apartado","Apartado"),
        ("stock","Cantidad Inicial")
        ], 'Tipo de Movimiento')
    tsalida = fields.Selection([
        ("venta","Venta"),
        ("consigna","Consigna"),
        ], 'Tipo de Salida')
    documento = fields.Char('Documento de entrada')
    cantidad = fields.Integer('Cantidad', default=1)
    documento_salida = fields.Char('Factura')
    fecha = fields.Date('Fecha', default=_default_fecha)
    productos = fields.One2many('itriplee.movimientos.linea', 'movimiento_id', string='Cantidades', ondelete='cascade')
    series = fields.One2many('itriplee.movimientos.series', 'name', string='Series')
    servicio = fields.Many2one('itriplee.servicio', 'Servicio', ondelete='cascade')
    movimiento = fields.Many2one('itriplee.movimientos', 'Proviene de', ondelete='cascade')
    comentarios = fields.Text('comentarios')
    tecnico = fields.Many2one('res.users', 'Técnico', ondelete='cascade')
    salidas = fields.One2many('itriplee.movimientos.linea', 'movimiento_id', string='Salida por venta', ondelete='cascade')
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('movimientos') or ('New')
        res = super(movimientos, self).create(vals)  
        return res

    @api.multi
    def button_vender(self):
        self.estado = 'entregadas'
        for line in self.salidas:
            salida = line.productod.cantidad - 1
            venta = line.productod.vendidos + 1
            line.productod.update({
            'cantidad': salida,
            'vendidos': venta
            })
            line.seriesdisponibles.update({
            'movimiento_salida': self.id,
            'estado': 'vendida',
            'documento_salida':self.documento_salida
            })

    @api.multi
    def button_consigna(self):
        self.estado = 'entregadas'
        for line in self.salidas:
            salida = line.seriesdisponibles.producto.cantidad - 1
            reserva = line.seriesdisponibles.producto.reservado + 1
            line.productod.update({
            'cantidad': salida,
            'reservado': reserva,
            })
            line.seriesdisponibles.update({
            'movimiento_salida': self.id,
            'estado': 'reservado',
            'documento_salida':self.documento_salida,
            'tecnico':self.tecnico.id
            })

    @api.multi
    def button_retornar(self):
        pass
##Codigo Boton Recibir
class SeriesWizardRecibir(models.TransientModel):
    _name = 'itriplee.series.wizard.recibir'

    @api.model    
    def default_get(self, fields):        
        rec = super(SeriesWizardRecibir, self).default_get(fields)
        product_line = []
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids')) 
        for producto in active_obj.productos:
            product_line.append((0, 0, {
            'movimiento_id': producto.movimiento_id.id,
            'cantidad': producto.cantidad,
            'cantidad_recibida': producto.cantidad_recibida,
            'cantidad_faltante': producto.cantidad_faltante,
            'producto': producto.producto.id,
            'series': [],
            }))
            rec['productos'] = product_line        
        return rec

    productos = fields.One2many('itriplee.movimientos.linea.transient', 'producto_recibir', string='Cantidades', ondelete='cascade')

    @api.multi
    def button_wizard_recibir(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))        
        for rec in active_obj:
            rec.estado = 'recibida'
        for a in active_obj.productos:
            for line in self.productos:
                if line.producto == a.producto:
                    recibidos = 0          
                    for record in line.series:                
                        recibidos += 1
                        vals = {
                            'name': record.name,
                            'estado': 'disponible',
                            'producto': line.producto.id,
                            'documento': active_obj.documento,
                            'movimiento_entrada': line.movimiento_id.id,
                        }
                        self.env['itriplee.stock.series'].create(vals)
                        a.write({'series': [
                            (0, 0, {'name': record.name}),
                        ]})  
                    cantidadr = recibidos + line.cantidad_recibida
                    cantidadf = line.cantidad - cantidadr
                    total = line.producto.cantidad + recibidos
                    line.producto.update({
                            'cantidad': total
                            }) 
                    a.update({
                            'cantidad_recibida': cantidadr,
                            'cantidad_faltante': cantidadf,
                            })
                
    ##Finaliza Codigo Boton Recibir

    ##Comienza Codigo de Prueba

    class SeriesWizardVenta(models.TransientModel):
        _name = 'itriplee.series.wizard.venta'

        @api.model    
        def default_get(self, fields):        
            rec = super(SeriesWizardVenta, self).default_get(fields)
            product_line = []
            active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids')) 
            for producto in active_obj.productos:
                product_line.append((0, 0, {
                'movimiento_id': producto.movimiento_id.id,
                'cantidad': producto.cantidad,
                'producto': producto.producto.id,
                'series': [],
                }))
                rec['productos'] = product_line        
            return rec

        productos = fields.One2many('itriplee.movimientos.linea.transient', 'producto_venta', string='Cantidades', ondelete='cascade')

    ##Comienza Codigo de Prueba
    



class SeriesWizard(models.TransientModel):
    _name = 'itriplee.series.wizard'

    def _default_fecha(self):
        return fields.Date.context_today(self)

    @api.model    
    def default_get(self, fields):        
        rec = super(SeriesWizard, self).default_get(fields)
        product_line = []
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids')) 
        self.write({'estado' : active_obj.estado})
        for producto in active_obj.productos:
            product_line.append((0, 0, {
            'movimiento_id': producto.movimiento_id.id,
            'cantidad': producto.cantidad,
            'producto': producto.producto.id,
            'series': [],
            'seriesdisponibles': producto.seriesdisponibles.id,
            }))
            rec['productos'] = product_line        
        return rec

    productos = fields.One2many('itriplee.movimientos.linea.transient', 'productow', string='Cantidades', ondelete='cascade')
    estado = fields.Selection([
        ("programada","Programada"),
        ("solicitada","Solicitada"),
        ("recibida","Recibida"),
        ("atrasada","Atrasada"),
        ("cancelada","Cancelada"),
        ("retornada","Refacciones retornadas"),
        ("surtida","Surtida"),
        ("entregadas","Entregadas"),
        ], 'Estado del movimiento', default='programada')
    fecha = fields.Date('Fecha', default=_default_fecha)
    salientes = fields.One2many('itriplee.movimientos.linea.transient', 'productow', string='Equipos por Salir', ondelete='cascade', domain=[('regresar','=',False)])

    @api.model    
    def default_get(self, fields):        
        rec = super(SeriesWizard, self).default_get(fields)
        product_line = []
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids')) 
        self.write({'estado' : active_obj.estado})
        for producto in active_obj.productos:
            product_line.append((0, 0, {
            'movimiento_id': producto.movimiento_id.id,
            'cantidad': producto.cantidad,
            'producto': producto.producto.id,
            'series': [],
            'seriesdisponibles': producto.seriesdisponibles.id,
            }))
            rec['productos'] = product_line        
        return rec
        
    @api.multi
    def button_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        for rec in active_obj:
            rec.estado = 'recibida'
        for line in self.productos:
            total = line.producto.cantidad + line.cantidad
            line.producto.update({
                'cantidad': total
            })         
            for record in line.series:                
                vals = {
                    'name': record.name,
                    'estado': 'disponible',
                    'producto': line.producto.id,
                    'documento': active_obj.documento,
                    'movimiento_entrada': line.movimiento_id.id
                }
                self.env['itriplee.stock.series'].create(vals)
               # if line.producto.id == line.producto.id:   #Colocar bien el filtro                 
                #    active_obj.productos.write({'series': [
                 #       (0, 0, {'name': record.name}),
                  #  ]})

    @api.multi
    def button_surtir_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        for rec in active_obj:
            rec.estado = 'surtida'
            rec.servicio.estado_refacciones = 'surtida'
        for line in self.productos:
            disponible = line.producto.cantidad - line.cantidad
            reservado = line.producto.reservado + line.cantidad
            serie = line.producto
            line.producto.update({
                'cantidad': disponible,
                'reservado': reservado,
            })
            line.seriesdisponibles.update({
                'estado': 'reservado',
            })
            for prod in active_obj.productos:
                if serie == prod.producto:
                    prod.update(
                    {'seriesdisponibles': line.seriesdisponibles})
            

    @api.multi
    def button_retornar1_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        regresadas = []
        self.estado = 'retornada'        
        for rec in active_obj:
            rec.servicio.estado_refacciones = 'regresadas'
        for line in self.productos:
            if line.regresar == True:
                disponible = line.producto.cantidad + line.cantidad
                reservado = line.producto.reservado - line.cantidad
                line.producto.update({
                    'cantidad': disponible,
                    'reservado': reservado,
                })
                line.seriesdisponibles.update({
                    'estado': 'disponible',
                }) 
                regresadas.append((0, 0, {
                    'producto': line.producto.id,
                    'cantidad': 1,
                    'seriesdisponibles': line.seriesdisponibles.id
                    }))
                vals = {
                'estado': 'recibida',
                'tipo': 'entrada',
                'fecha': self.fecha,
                'productos': regresadas,
                } 
                rec.env['itriplee.movimientos'].create(vals)
            else:
                pass
            return {"type": "set_scrollTop"}
            
    def button_retornar2_wizard(self):
        active_obj = self.env['itriplee.movimientos'].browse(self._context.get('active_ids'))
        salidas = []
        entradas = []
        for line in self.salientes:
            salida = line.producto.reservado - line.cantidad
            line.producto.update({
                'reservado': salida
                }) 
            if line.tipo_salida == 'garantia':
                garantia = line.producto.garantias + line.cantidad
                line.producto.update({
                'garantias': garantia
                })
                line.seriesdisponibles.update({
                'estado': 'Instalado',
                'movimiento_salida': active_obj.id
                }) 
            elif line.tipo_salida == 'venta':
                venta = line.producto.vendidos + line.cantidad
                line.producto.update({
                'vendidos': venta
                }) 
                line.seriesdisponibles.update({
                'estado': 'vendida',
                'movimiento_salida': active_obj.id,
                'documento_salida': line.factura
                })# Aqui acaban los movimientos directo al inventario del producto
            else:
                pass
            salidas.append((0, 0, {
                    'producto': line.producto.id,
                    'cantidad': 1,
                    'seriesdisponibles': line.seriesdisponibles.id
                    }))
            vals = {
                'estado': 'entregadas',
                'tipo': 'salida',
                'fecha': self.fecha,
                'movimiento': active_obj.id,
                'productos': salidas,
                } 
            self.env['itriplee.movimientos'].create(vals)# Aqui acaba la creación de los movimientos de salida
            if line.serie_nueva != False and line.tipo_salida == 'garantia':
                for reg in self.salientes:
                    total2 = line.producto.reservado + line.cantidad
                    line.producto.update({
                    'reservado': total2
                    })
                    vals2 = {
                    'name': reg.serie_nueva,
                    'reparado': True,
                    'estado': 'garantia',
                    'producto': line.producto.id,
                    'documento': active_obj.servicio.name,
                    'movimiento_entrada': line.movimiento_id.id,
                    }
                nuevo = self.env['itriplee.stock.series'].create(vals2)                    
                entradas.append((0, 0, {
                    'producto': line.producto.id,
                    'cantidad': 1,
                    'seriesdisponibles': nuevo.id
                    }))
                vals3 = {
                    'estado': 'solicitada',
                    'tipo': 'entrada',
                    'fecha': self.fecha,
                    'movimiento': active_obj.id,
                    'productos': entradas,
                    }
                self.env['itriplee.movimientos'].create(vals3)
                line.seriesdisponibles.update({
                'remplazo': nuevo.id
                })
                return nuevo
            elif line.serie_nueva == False and line.tipo_salida == 'garantia':
                line.seriesdisponibles.update({
                'definitivo': True
                })
                active_obj.write({
                    'comentarios' : 'no se trajo pieza de remplazo por equipo de garantia'
                    })


            



class lineasWizard(models.TransientModel):
    _name = 'itriplee.movimientos.linea.transient'

    productow = fields.Many2one('itriplee.series.wizard', string='Movimiento')
    salientes = fields.Many2one('itriplee.series.wizard', string='Productos por Salir')
    cantidad = fields.Integer('Cantidad')
    cantidad_recibida = fields.Integer('Cantidad Recibida')
    cantidad_faltante = fields.Integer('Cantidad Faltante')
    producto = fields.Many2one('itriplee.catalogo')
    producto_recibir = fields.Many2one('itriplee.series.wizard.recibir', string='Movimiento')
    producto_venta = fields.Many2one('itriplee.series.wizard.venta', string='Movimiento')
    movimiento_id = fields.Many2one('itriplee.movimientos', string='Movimiento')
    series = fields.One2many('itriplee.movimientos.series.transient', 'movimiento', string='Series')
    seriesdisponibles = fields.Many2one('itriplee.stock.series', string='Series')
    regresar = fields.Boolean('Regresar al almacen', default=False)
    tipo_salida = fields.Selection([
                    ("venta","Venta"),
                    ("garantia","Garantia"),
                    ], 'Tipo de Salida')
    serie_nueva = fields.Char('Serie de remplazo')
    factura = fields.Char('Factura de Salida')

class lineas_movimientos(models.Model):
    _name = 'itriplee.movimientos.linea'
    _rec_name = 'movimiento_id'

    movimiento_id = fields.Many2one('itriplee.movimientos', string='Movimiento')
    cantidad = fields.Integer('Cantidad')
    cantidad_recibida = fields.Integer('Cantidad Recibida')
    cantidad_faltante = fields.Integer('Cantidad Faltante')
    producto = fields.Many2one('itriplee.catalogo')
    series = fields.One2many('itriplee.movimientos.series', 'movimiento', string='name', ondelete='cascade')
    seriesdisponibles = fields.Many2one('itriplee.stock.series', string='Series')
    estado_refaccion = fields.Selection([
                    ("nueva","Nueva"),
                    ("reparada","Reparada"),
                    ], 'De Preferencia')
    productod = fields.Many2one('itriplee.catalogo', related='seriesdisponibles.producto', store=True,
        string="Producto")
    tecnico = fields.Many2one('res.users', 'Técnico', ondelete='cascade')
        

class lineas_movimientos_series(models.Model):
    _name = 'itriplee.movimientos.series'

    name = fields.Char('Serie', ondelete='cascade')
    movimiento = fields.Many2one('itriplee.movimientos.linea', ondelete='cascade')

class seriesWizard(models.TransientModel):
    _name = 'itriplee.movimientos.series.transient'

    name = fields.Char('Serie', ondelete='cascade')
    movimiento = fields.Many2one('itriplee.movimientos.linea.transient', ondelete='cascade')