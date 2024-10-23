from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
class PropertyOfferModel(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer Model'
    _sql_constraints = [
        ('check_price','CHECK(price > 0)','An offer price must be strictly positive.'),
    ]
    _order = 'price desc'
    price = fields.Float()
    status = fields.Selection(selection=[('accepted','Accepted'),('refused','Refused')], copy=False)
    partner_id = fields.Many2one('res.partner',required=True)
    property_id = fields.Many2one('estate.property',required=True)
    validity = fields.Integer(default=7, string='Validity (days)')
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline', string='Deadline')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    @api.depends('create_date','validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
            else:
                record.date_deadline = datetime.now() + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            difference = record.date_deadline - datetime.now().date()
            record.validity = difference.days


    def action_mark_as_accepted(self):
        for record in self:
            if record.property_id.state == 'offer accepted':
                raise UserError('You can only accept a single offer for a property!')
            record.property_id.state = 'offer accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer = record.partner_id
            record.status = 'accepted'
        return True

    def action_mark_as_refused(self):
        for record in self:
            if record.status == 'accepted':
                # record.property_id.state = 'offer received'
                record.property_id.buyer = ''
            record.status = 'refused'
        return True


    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])
        property.state = 'offer received'
        offers = property.offer_ids.mapped('price')
        max_price = max(offers,default=0.0)
        if max_price > vals['price'] :
            raise ValidationError('An offer with the price lower than existing offer price cannot be created.')
        return super().create(vals)



