# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class polizas(models.Model):
    _name = 'itriplee.polizas'
    _rec_name = 'folio'
    _description = "Modulo de polizas"

    name = fields.Integer('ID de poliza', required=True)
    folio = fields.Integer('Folio', required=True)
    cliente = fields.Many2one('res.partner', 'Cliente', required=True)
    fecha_contratacion = fields.Date('Fecha de Contratación', required=True)
    tipo_poliza = fields.Selection([("con refacciones","Con Refacciones"),("sin refacciones","Sin Refacciones")], 'Tipo de Poliza', required=True)
    horario = fields.Selection([("24 / 7","24 / 7"),("Horario de Oficina","Horario de Oficina")], 'Horario Contratado', required=True)
    tiempo = fields.Selection([("1 año","1 año"),("2 años","2 años"),("3 años","3 años")], 'Duración de la Poliza')
    tiempo_int = fields.Integer("años de contratación")
    visitas_int = fields.Integer("Visitas contratadas por año")
    visitas_contratadas = fields.Selection([("1","1"),("2","2"),("3","3")], 'Visitas anuales contratadas')
    ubicacion = fields.Selection([("Local","Local"),("Foraneo","Foraneo")], 'Local o Foraneo')
    visitas = fields.One2many('itriplee.servicio', 'poliza_asociada', 'Visitas')
    equipos = fields.One2many('itriplee.equipos', 'poliza', 'Equipos')
    observaciones = fields.Text('Observaciones')

    def create_visita(self):
        cantidad = self.tiempo_int * self.visitas_int
        intervalo = 365 / self.visitas_int      
        for i in range(cantidad):
            fecha_visita = self.fecha_contratacion + timedelta(days=intervalo * i)
            equipos_relacionados = [(4, equipo.id, 0) for equipo in self.equipos]
            visita_programada = {
                'tipo_visita': 'Ordinaria',
                'estado_equipo': 'Poliza',
                'prioridad': '1',
                'visita': fecha_visita,
                'cliente': self.cliente.id,
                'poliza_asociada': self.id,
                'equipos': equipos_relacionados
            }
            self.env['itriplee.servicio'].create(visita_programada)
