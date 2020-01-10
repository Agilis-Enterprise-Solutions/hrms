# coding: utf-8
{
    'name': "hrv3_recruitment",

    'summary': """
        Part of HRMS V3 Application""",

    'description': """
        This application tackles the recruitment/job requisition side of HR/Recruitment
        Its main components are: Personnel Requisition, Job Posting, Candidate Sourcing, Candidate
        Assessment, Shortlist and Job Offer, and Induction.
    """,

    'author': "Agilis Enterprise Solutions",
    'website': "http://www.yourcompany.com",

    'category': 'HR',
    'version': '0.1',

    'depends': [
        'base',
        'contacts',
        'hr',
        'hr_recruitment',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/job_posting.xml',
        'data/sequence.xml',
        'views/personnel_requisition.xml',
        'views/skills.xml',
        'views/candidate_sourcing.xml',
        'views/candidate_assessment.xml',
        'wizard/applicant.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
}
