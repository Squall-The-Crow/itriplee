# -*- coding: utf-8 -*-

from odoo import models, fields, api

AVAILABLE_PRIORITIES = [
    ('1', 'Critico'),
    ('2', 'Alta'),
    ('3', 'Normal'),
    ('4', 'Baja'),
    ('5', 'Informativo'),
]

AVAILABLE_STATES = [

    ('confirmar', 'Confirmar'),
    ('por asignar', 'Por asignar'),
    ('asignado', 'Asignado'),
    ('pendiente', 'Pendiente'),
    ('terminado', 'Terminado'),
    ('cancelado', 'Cancelado'),
    ('firmado', 'Firmado'),
    ('calificado', 'Calificado'),
]


class servicio(models.Model):
    _name = 'itriplee.servicio'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Modulo para agendar y realizar servicios a clientes"

    def button_terminar(self):
        for rec in self:
            rec.write({'estado': 'terminado'})

    name = fields.Char('Consecutivo')
    cliente = fields.Many2one('res.partner', 'Cliente', required=True)
    visita = fields.Datetime('Visita Programada', required=True)
    tipo_visita = fields.Selection([
    	("Ordinaria","Ordinaria"),
    	("Extraordinaria","Extraordinaria")],
    	 'Tipo de Visita')
    ubicacion = fields.Selection([
    	("Local","Local"),
    	("Foraneo","Foraneo")],
    	 'Local o Foraneo')
    prioridad = fields.Selection(AVAILABLE_PRIORITIES, 'Prioridad')
    estado = fields.Selection(AVAILABLE_STATES, 'Status')
    estado_equipo = fields.Selection([
    	("Garantia","Garantia"),
    	("Poliza","Poliza"),
    	("Sin Garantia","Fuera de Garantia"),
    	("Variado","Variado")],
    	 'Estado del Equipo')
    tecnico = fields.Many2one('res.users', 'Tecnico') #
    vendedor = fields.Many2one('res.users', 'Vendedor')# 
    reinsidencia = fields.Boolean('Es reinsidencia?')
    modelo_transicion = fields.Char('Modelo Version anterior')
    garantia_asociada = fields.Many2one('itriplee.garantias', 'Garantias')
    poliza_asociada = fields.Many2one('itriplee.polizas', 'Polizas')
    equipos = fields.Many2many('itriplee.equipos', string='Equipos De Cliente')
    equipos_genericos = fields.One2many('itriplee.equipos_genericos', 'name', 'Equipos Genericos')
    equipos_versionanterior = fields.Text('Equipos Version Anterior')
    observaciones_equipo = fields.Text('Observaciones del equipo')
    razon_cancelacion = fields.Text('Razon de Cancelación')
    falla = fields.Text('Falla Reportada')
    responsable = fields.Selection([
    	("Cliente","Cliente"),
    	("Almacen","Almacen"),
    	("Administracion","Administracion"),
    	("Proveedor","Proveedor"),
    	("Tecnico","Tecnico"),
    	("Otro","Otro")], 
    	'Responsable Actual')
    resultado = fields.Text('Resultado del Reporte')
    comentarios = fields.Text('Comentarios del Técnico')
    firma = fields.Binary('Firma del Cliente')
    firma1 = fields.Binary('Firma del Cliente')
    estado_refacciones = fields.Selection([
    	("disponible","Se pueden solicitar refacciones"),
    	("solicitadas","Refacciones ya solicitadas"),
    	("surtida","Las refacciones fueron surtidas"),
        ("regresadas","Las refacciones fueron regresadas o vendidas")
        ], 'Estado de las refacciones del servicio', default='disponible')
    refacciones = fields.Many2one('itriplee.movimientos', 'Refacciones Solicitadas')
    horario = fields.Selection([
    	("si","Si"),
    	("no","No")],
    	 '¿El tecnico llego en el horario acordado?')
    reparado = fields.Selection([
    	("si","Si"),
    	("no","No")],
    	 '¿El equipo quedo reparado a su entera satisfaccion?') 
    observaciones = fields.Text('Observaciones del cliente')
    calificacion = fields.Selection([
    	("Bueno","Bueno"),
    	("Regular","Regular"),
    	("Malo","Malo"),],
    	 'calificacion')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('servicio') or ('New')
        res = super(servicio, self).create(vals)  
        return res

class servicioRefacciones(models.TransientModel):
    _name = 'itriplee.servicio.refacciones'
    _description = "Modulo que se encarga de solicitar refacciones al almacen"

    def _default_fecha(self):
        return fields.Date.context_today(self)

    refacciones = fields.One2many('itriplee.servicio.refacciones.transient', 'name', string='Refacciones')
    fecha = fields.Date('Fecha', default=_default_fecha)

    def button_wizard(self):
        recs = []
        active_obj = self.env['itriplee.servicio'].browse(self._context.get('active_ids'))        
        for line in self.refacciones:
            recs.append((0, 0, {
            'producto': line.producto.id,
            'estado_refaccion': line.estado_refaccion,
            'cantidad': 1,
            }))
        vals = {
                'servicio': active_obj.id,
                'estado': 'solicitada',
                'tipo': 'apartado',
                'fecha': self.fecha,
                'productos': recs,
                'tecnico': active_obj.tecnico.id,
                }   
        movimiento = self.env['itriplee.movimientos'].create(vals)
        for rec in active_obj:
            rec.estado_refacciones = 'solicitadas'
            rec.refacciones = movimiento
        return movimiento    
    
class servicioFirma(models.TransientModel):
    _name = 'itriplee.servicio.firma'
    _description = "modulo transitorio para firmar los servicios terminados"

    firma = fields.Binary('Firma del Cliente') 

    def button_terminar(self):
        active_obj = self.env['itriplee.servicio'].browse(self._context.get('active_ids'))
        active_obj.estado = 'firmado'
        active_obj.write({'firma' : self.firma})

class servicioCalificacion(models.TransientModel):
    _name = 'itriplee.servicio.calificacion'
    _description = "Modulo transitorio para calificar los servicios realizados"

    horario = fields.Selection([
    	("si","Si"),
    	("no","No")],
    	 '¿El tecnico llego en el horario acordado?')
    reparado = fields.Selection([
    	("si","Si"),
    	("no","No")],
    	 '¿El equipo quedo reparado a su entera satisfaccion?')
    calificacion = fields.Selection([
    	("Bueno","Bueno"),
    	("Regular","Regular"),
    	("Malo","Malo"),],
    	 'calificacion') 
    observaciones = fields.Text('Observaciones del cliente')  

    def button_calificar(self):
        active_obj = self.env['itriplee.servicio'].browse(self._context.get('active_ids'))
        active_obj.estado = 'calificado'
        active_obj.write({
            'horario' : self.horario,
            'reparado' : self.reparado,
            'observaciones' : self.observaciones,
            'calificacion' : self.calificacion,
            })


class ServicioWizard(models.TransientModel):
    _name = 'itriplee.servicio.refacciones.transient'
    _description = "Wizard para solicitar refacciones al almacen"

    name = fields.Many2one('itriplee.servicio.refacciones', ondelete="cascade")
    producto = fields.Many2one('itriplee.catalogo', 'Refaccion', ondelete="cascade")
    estado_refaccion = fields.Selection([
        ("nueva","Nueva"),
        ("reparada","Reparada"),
        ], 'De Preferencia') 
    




# Falta implementar la calificacion
