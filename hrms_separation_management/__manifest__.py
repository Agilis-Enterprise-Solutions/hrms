# coding: utf-8
{
    'name': "HRMS Separation Management",

    'summary': """
        Part of HRMS V3 Application""",

    'description': """
        Separation Management Module allows the employee to manage his exit
    """,

    'author': "John Ardosa, Raymund Martinez, and Ralf Cabarogias - Agilis Enterprise Solutions",
    'website': "http://www.yourcompany.com",

    'category': 'HR',
    'version': '0.1',

    'depends': [
        'base',
        'hr',
        'survey',
        'hrms_employee_exit'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/separation.xml',
        'views/resignation_letter.xml',
        'views/exit_clearance.xml',
        'views/menu_items.xml'

    ],
}
