# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class polizas(models.Model):
    _name = 'itriplee.polizas'
    _rec_name = 'folio'
    _inherit = ['itriplee.servicio']
    _description = "Modulo de polizas"

    folio = fields.Integer('Folio', required=True)
    cliente = fields.Many2one('res.partner', 'Cliente', required=True)
    fecha_contratacion = fields.Date('Fecha de Contratación', required=True)
    tipo_poliza = fields.Selection([("con refacciones","Con Refacciones"),("sin refacciones","Sin Refacciones")], 'Tipo de Poliza', required=True)
    horario = fields.Selection([("24 / 7","24 / 7"),("Horario de Oficina","Horario de Oficina")], 'Horario Contratado', required=True)
    tiempo = fields.Selection([("1 año","1 año"),("2 años","2 años"),("3 años","3 años")], 'Duración de la Poliza', required=True)
    tiempo_int = fields.Integer("años de contratación")
    visitas_int = fields.Integer("Visitas contratadas por año")
    visitas_contratadas = fields.Selection([("1","1"),("2","2"),("3","3")], 'Visitas anuales contratadas', required=True)
    ubicacion = fields.Selection([("Local","Local"),("Forane+o","Foraneo")], 'Local o Foraneo')
    visitas = fields.One2many('itriplee.servicio', 'poliza_asociada', 'Visitas')
    equipos = fields.One2many('itriplee.equipos', 'name', 'Equipos')
    observaciones = fields.Text('Observaciones')

    @api.multi
    def create_visita(self):
        cantidad = 0
        dias = 0
        intervalo = 0

        cantidad = self.tiempo_int * self.visitas_int
        dias = cantidad * 365
        intervalo = dias / cantidad

        for visita in self:
            fecha_visita = visita.fecha_contratacion + timedelta(days=intervalo)
            
            while cantidad > 0:
                visita_programada = {
                    'visita': fecha_visita,
                    'cliente': self.cliente.id,
                    'poliza_asociada': self.id,
                    'equipos':[(4, self.equipos.id)]
                }
                self.env['itriplee.servicio'].create(visita_programada)
                cantidad -= 1



    #Falta funcion para al momento de guardar se creen las visitas correspondientes
    #falta factura related