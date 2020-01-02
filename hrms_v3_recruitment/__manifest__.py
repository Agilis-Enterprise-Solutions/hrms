# -*- coding: utf-8 -*-
{
    'name': "hrms_v3_recruitment",

    'summary': """
        Part of HRMS V3 Application""",

    'description': """
        This application tackles the recruitment/job requisition side of HR/Recruitment
        Its main components are: Personnel Requisition, Job Posting, Candidate Sourcing, Candidate 
        Assessment, Shortlist and Job Offer, and Induction.
    """,

    'author': "Agilis Enterprise Solutions",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_recruitment','contacts',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/job_posting.xml',
        'data/sequence.xml',
        'views/personnel_requisition.xml',
        'views/skills.xml',
        'views/candidate_sourcing.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
