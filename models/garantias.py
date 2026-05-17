# -*- coding: utf-8 -*-
from odoo import models, fields
from dateutil.relativedelta import relativedelta

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
        fecha_actual = fields.Date.context_today(self)

        for garantia in self:
            if not garantia.fecha_de_venta:
                continue

            # Genera 6 visitas: una cada 6 meses durante 3 años.
            fecha_visita = garantia.fecha_de_venta
            for numero_visita in range(1, 7):
                fecha_visita = fecha_visita + relativedelta(months=6)

                # Solo registra visitas pendientes a partir de la fecha actual.
                if fecha_visita <= fecha_actual:
                    continue

                visita_existente = self.env['itriplee.servicio'].search([
                    ('garantia_asociada', '=', garantia.id),
                    ('visita', '=', fecha_visita),
                ], limit=1)

                if visita_existente:
                    continue

                visita_programada = {
                    'visita': fecha_visita,
                    'numero_visita': numero_visita,
                    'cliente': garantia.cliente.id,
                    'garantia_asociada': garantia.id,
                    'tipo_visita': 'Ordinaria',
                    'estado_equipo': 'Garantia',
                    'prioridad': '3',
                    'equipos': [(6, 0, [garantia.equipo.id])]
                }
                self.env['itriplee.servicio'].create(visita_programada)