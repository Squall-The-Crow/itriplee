# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class garantias(models.Model):
    _name = 'itriplee.garantias'
    _rec_name = 'folio'
    _description = "Modulo de garantias"

    folio = fields.Integer('Folio')
    cliente = fields.Many2one('res.partner', 'Cliente', required=True)
    equipo = fields.Many2one('itriplee.equipos', 'Equipo', required=True)
    serie = fields.Char('Numero de Serie', related='equipo.name', readonly=True)
    factura = fields.Char('Numero de Factura', related='equipo.factura', readonly=True)
    modelo = fields.Char('Modelo', related='equipo.modelo.name', readonly=True)
    marca = fields.Char('Marca', related='equipo.marca', readonly=True)
    tipo = fields.Char('Tipo', related='equipo.tipo', readonly=True)
    fecha_de_venta = fields.Date('Fecha de Venta', related='equipo.venta', readonly=True)
    fecha1 = fields.Date('Fecha de Venta1')
    visitas = fields.One2many('itriplee.servicio', 'garantia_asociada', 'Visitas')
    observaciones = fields.Text('Observaciones')
    valoracion = fields.Text('Valoración para Poliza')

    def generar_visitas_programadas(self):
        for garantia in self:
            fecha_compra = datetime.strptime(garantia.fecha_de_venta, '%Y-%m-%d').date()
            fecha_actual = datetime.now().date()
            fecha_limite = fecha_compra + timedelta(days=1095)  # 3 años desde la compra
            while fecha_compra <= fecha_limite and fecha_compra <= fecha_actual:
                visita_programada = {
                    'visita': fecha_compra,
                    'cliente': garantia.cliente.id,
                    'garantia_asociada': garantia.id,
                    'equipos': [(6, 0, [garantia.equipo.id])]
                }
                self.env['itriplee.servicio'].create(visita_programada)
                fecha_compra += timedelta(days=180)  # 6 meses