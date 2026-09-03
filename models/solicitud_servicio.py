from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

class solicitud_servicio(models.Model):
    _name = 'itriplee.solicitud_servicio'
    _rec_name = 'folio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Modelo principal para cotizar"

    ###Funcion Fecha automatica######
    def _default_fecha_solicitud(self):
        return fields.Date.context_today(self)

    folio = fields.Char('Modelo', required=True,)
    fecha_solicitud = fields.Date('Fecha', default=_default_fecha_solicitud)
    fecha_servicio = fields.Date('Fecha de Servicio')
    hora_inicio = fields.Float('Hora de inicio')
    hora_fin = fields.Float('Hora de finalizacion')
    es_cliente = fields.Boolean('Cliente dado de alta')
    cliente = fields.Many2one('res.partner', 'Cliente registrado')
    empresa_cliente = fields.Char('Empresa')
    nombre_cliente = fields.Char('Nombre')
    telefono_cliente = fields.Char('Telefono')
    cargo_cliente = fields.Char('Cargo')
    email_cliente = fields.Char('E-mail')
    datos_cliente_completos = fields.Boolean(compute='_compute_datos_cliente_completos')
    mismos_datos_contacto = fields.Boolean('Mismos datos de contacto')
    empresa_servicio = fields.Char('Empresa para el servicio')
    nombre_servicio = fields.Char('Nombre de contacto para el servicio')
    telefono_servicio = fields.Char('Telefono de contacto para el servicio')
    cargo_servicio = fields.Char('Cargo de contacto para el servicio')
    email_servicio = fields.Char('E-mail de contacto para el servicio')
    calle_servicio = fields.Char('Calle')
    numero_exterior_servicio = fields.Char('Numero exterior')
    numero_interior_servicio = fields.Char('Numero interior')
    colonia_servicio = fields.Char('Colonia')
    ciudad_servicio = fields.Char('Ciudad')
    estado_servicio = fields.Char('Estado')
    entre_calles_servicio = fields.Char('Entre calles')
    referencias_servicio = fields.Text('Referencias')
    estado = fields.Selection([('borrador', 'Borrador'),
                                   ('pendiente', 'Pendiente'),
                                   ('aprobada', 'Aprobada'),
                                   ('rechazada', 'Rechazada'),
                                   ('finalizada', 'Finalizada'),
                                   ], string='Estado', default='borrador')
    solicitante = fields.Many2one('res.users', string='Solicitante', default=lambda self: self.env.user)
    autoriza = fields.Many2one('res.users', string='Autoriza')
    firma = fields.Binary('Firma de Autorizacion')
    motivo_rechazo = fields.Text('Motivo de rechazo', readonly=True)

    @api.depends('empresa_cliente', 'nombre_cliente', 'telefono_cliente', 'cargo_cliente', 'email_cliente')
    def _compute_datos_cliente_completos(self):
        for solicitud in self:
            solicitud.datos_cliente_completos = all((
                solicitud.empresa_cliente,
                solicitud.nombre_cliente,
                solicitud.telefono_cliente,
                solicitud.cargo_cliente,
                solicitud.email_cliente,
            ))

    def _valores_contacto_servicio(self):
        return {
            'empresa_servicio': self.empresa_cliente,
            'nombre_servicio': self.nombre_cliente,
            'telefono_servicio': self.telefono_cliente,
            'cargo_servicio': self.cargo_cliente,
            'email_servicio': self.email_cliente,
        }

    @api.onchange('cliente')
    def _onchange_cliente(self):
        if not self.cliente:
            return

        partner = self.cliente
        self.update({
            'empresa_cliente': partner.commercial_company_name or partner.name,
            'nombre_cliente': partner.name,
            'telefono_cliente': partner.phone or partner.mobile,
            'cargo_cliente': partner.function,
            'email_cliente': partner.email,
            'calle_servicio': partner.street,
            'numero_exterior_servicio': partner.street2,
            'ciudad_servicio': partner.city,
            'estado_servicio': partner.state_id.name,
        })
        if self.mismos_datos_contacto:
            self.update(self._valores_contacto_servicio())

    @api.onchange('mismos_datos_contacto')
    def _onchange_mismos_datos_contacto(self):
        if self.mismos_datos_contacto:
            self.update(self._valores_contacto_servicio())

    @api.constrains('hora_inicio', 'hora_fin')
    def _check_horario_servicio(self):
        for solicitud in self:
            if solicitud.hora_fin and solicitud.hora_inicio >= solicitud.hora_fin:
                raise ValidationError(_('La hora de finalizacion debe ser posterior a la hora de inicio.'))

    def _validar_estado(self, estado_actual):
        self.ensure_one()
        if self.estado != estado_actual:
            raise UserError(_('Esta accion no esta disponible en el estado actual de la solicitud.'))

    def _validar_grupo(self, grupo_xml_id):
        if not self.env.user.has_group(grupo_xml_id):
            raise UserError(_('No tiene permisos para realizar esta accion.'))

    def action_mandar_solicitud(self):
        self._validar_grupo('itriplee.cotizaciones_grupo_general')
        self._validar_estado('borrador')
        self.write({'estado': 'pendiente'})

    def action_aprobar(self):
        self._validar_grupo('itriplee.servicios_grupo_gerencia')
        self._validar_estado('pendiente')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Aprobar solicitud'),
            'res_model': 'itriplee.solicitud.servicio.aprobar.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_solicitud_id': self.id},
        }

    def action_rechazar(self):
        self._validar_grupo('itriplee.servicios_grupo_gerencia')
        self._validar_estado('pendiente')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rechazar solicitud'),
            'res_model': 'itriplee.solicitud.servicio.rechazar.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_solicitud_id': self.id},
        }

    def action_finalizar(self):
        self._validar_grupo('itriplee.servicios_grupo_gerencia')
        self._validar_estado('aprobada')
        self.write({'estado': 'finalizada'})

    def write(self, vals):
        if any(solicitud.estado == 'finalizada' for solicitud in self):
            raise UserError(_('No se puede modificar una solicitud finalizada.'))
        return super(solicitud_servicio, self).write(vals)

    @api.model
    def create(self, vals):
        vals['folio'] = self.env['ir.sequence'].next_by_code('solicitud_servicio') or ('New')
        res = super(solicitud_servicio, self).create(vals)
        return res


class SolicitudServicioAprobarWizard(models.TransientModel):
    _name = 'itriplee.solicitud.servicio.aprobar.wizard'
    _description = 'Aprobar solicitud de servicio'

    solicitud_id = fields.Many2one('itriplee.solicitud_servicio', required=True, readonly=True)
    aprobador_id = fields.Many2one('res.users', 'Aprobador', required=True, readonly=True,
                                   default=lambda self: self.env.user)
    firma = fields.Binary('Firma de autorizacion', required=True)

    def action_confirmar(self):
        self.ensure_one()
        self.solicitud_id._validar_grupo('itriplee.servicios_grupo_gerencia')
        self.solicitud_id._validar_estado('pendiente')
        self.solicitud_id.write({
            'autoriza': self.env.user.id,
            'firma': self.firma,
            'estado': 'aprobada',
        })
        return {'type': 'ir.actions.act_window_close'}


class SolicitudServicioRechazarWizard(models.TransientModel):
    _name = 'itriplee.solicitud.servicio.rechazar.wizard'
    _description = 'Rechazar solicitud de servicio'

    solicitud_id = fields.Many2one('itriplee.solicitud_servicio', required=True, readonly=True)
    rechazado_por_id = fields.Many2one('res.users', 'Rechazado por', required=True, readonly=True,
                                       default=lambda self: self.env.user)
    motivo_rechazo = fields.Text('Razon del rechazo', required=True)

    def action_confirmar(self):
        self.ensure_one()
        self.solicitud_id._validar_grupo('itriplee.servicios_grupo_gerencia')
        self.solicitud_id._validar_estado('pendiente')
        self.solicitud_id.write({
            'autoriza': self.env.user.id,
            'motivo_rechazo': self.motivo_rechazo,
            'estado': 'finalizada',
        })
        return {'type': 'ir.actions.act_window_close'}