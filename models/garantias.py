# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class garantias(models.Model):
    _name = 'itriplee.garantias'
    _rec_name = 'folio'

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

    @api.model
    def create(self, vals):
        obj_visita = self.pool.get('itriplee.servicio')
        cliente = self.cliente
        #fecha_compra = self.equipo.venta
        fm = '%Y-%m-%d'
        cantidad_meses = 6
        ind = 0
        folio = self.folio
        now = datetime.now()
        now_str = now.strftime(fm)
        now_int = datetime.strptime(now_str, fm)
        fecha_compra_inicial = datetime.strptime(vals.fecha1, fm)
        vals = {
            'fecha1': self.fecha1
        }
        while ind < cantidad_meses:
            fecha_6_meses = self.fecha1 + relativedelta(months=6)
            if fecha_6_meses >= now_int:
                obj_visita.create(folio,
                    {'cliente': cliente, 'visita': fecha_6_meses}
                )
            ind = ind + 1
            self.fecha1 = fecha_6_meses
        return True
