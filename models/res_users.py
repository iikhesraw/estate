from odoo import fields, models

class InheritResUsers(models.Model):
    _inherit = 'res.users'


    property_ids = fields.One2many('estate.property','sales_person', domain=['|',('state','=','new'),('state','=','offer received')])
