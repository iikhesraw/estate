from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
class PropertyModel(models.Model):
    _name = 'estate.property'
    _description = 'Property Model.'
    _sql_constraints = [
        ('check_expected_price','CHECK(expected_price > 0)','A property expected price must be strictly positive.'),
        ('check_selling_price','CHECK(selling_price >= 0)','A property selling price must be positive.'),
    ]
    _order = 'id desc'
    _check_company_auto = True
    name = fields.Char(required=True,string='Title')
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=fields.Date.today() + relativedelta(months=3),string='Available From')
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=[('north','North'),('south','South'),('east','East'),('west','West')])
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='Status',
        default='new',
        selection=[('new','New'),('offer received','Offer Received'),('offer accepted','Offer Accepted'),('sold','Sold'),('canceled','Canceled')])
    property_type_id = fields.Many2one('estate.property.type')
    sales_person = fields.Many2one('res.users', string="Salesman", default=lambda self: self.env.user)
    buyer = fields.Many2one('res.partner', copy=False)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer','property_id')
    total_area = fields.Float(compute='_compute_total_area')
    best_offer = fields.Float(compute='_compute_best_offer')
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area


    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped('price'),default=0)

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''


    def action_mark_as_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError('A canceled property cannot be sold.')
            record.state = 'sold'
        return True


    def action_mark_as_canceled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('A sold property cannot be canceled.')
            record.state = 'canceled'
        return True


    @api.constrains('selling_price')
    def check_selling_price(self):
        for record in self:
            # if float_compare(record.selling_price, (record.expected_price * 0.9),0.0) :
            if record.selling_price > 0 and record.selling_price < 0.9 * record.expected_price:
                raise ValidationError('An offer selling price cannot be less than 90% of the property expected price.')


    @api.ondelete(at_uninstall=False)
    def validate_delete(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError('Properties with state other than New or Canceled cannot be deleted.')