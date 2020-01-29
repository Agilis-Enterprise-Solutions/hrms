# -*- coding: utf-8 -*-
{
    'name': "hrv3_compliance",

    'summary': """
        This module focuses on Infraction Management and Workplace Accidents""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/suspension.xml',
        'views/infraction.xml',
        'views/policy.xml',
        'views/offense.xml',
        'views/violation.xml',
        'views/menu_views.xml',
        'views/action_history.xml',
        
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    'auto_install': False,
}