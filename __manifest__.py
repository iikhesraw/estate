{
    'name' : 'estate',
    'category' : 'Real Estate/Brokerage',
    'depends' : ['base'],
    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_users_views.xml',
        'data/estate.property.type.csv',
        'reports/estate_property_offer_templates.xml',
        'reports/estate_property_templates.xml',
        'reports/estate_property_reports.xml',
        'reports/res_users_properties_templates.xml',
        'reports/res_users_properties_reports.xml'
    ],
    'license' : 'LGPL-3',
    'installable' : True,
    'application': True
}
