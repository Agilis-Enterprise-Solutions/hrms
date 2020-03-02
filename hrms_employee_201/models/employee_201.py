# coding: utf-8
from odoo import models, fields, api
from datetime import date
from logging import getLogger


def log(**to_output):
    getLogger().info("\n\n\n{0}\n\n".format(to_output))


class HealthCondition(models.Model):
    _name = 'health.condition'

    employee_id = fields.Many2one('hr.employee')

    health_condition = fields.Char()
    doctor_name = fields.Char('Name of the Doctor')
    address = fields.Char()
    medications = fields.Char()
    medical_documents = fields.Binary()
    date = fields.Date()
    fit_to_work = fields.Boolean()


class WorkHistory(models.Model):
    _name = 'hr.work.history'

    employee_id = fields.Many2one('hr.employee', ondelete="cascade")
    job_id = fields.Many2one('hr.job', "Position")
    company_name = fields.Char("Company Name", required=True)
    address = fields.Char("Address", required=True)
    line_of_business = fields.Char("Line of Business")
    date_started = fields.Date()
    date_exited = fields.Date()
    years_of_service = fields.Char('Year(s) of Service',
                                   compute="_get_years_of_service")

    statutory_requirements = fields.Float(string="SSS, GSIS, PHIC, HDMF & union Dues", store=True)
    nontax_other_benefits = fields.Float(string="Other Benefits & 13th Mo. Pay", store=True)
    deminimis = fields.Float(string="Nontaxable DeMinimis Benefits", store=True)
    holiday = fields.Float(string="Holiday Pay", store=True)
    overtime = fields.Float(string="Overtime Pay", store=True)
    night_diff = fields.Float(string="Night Shift Differential", store=True)
    hazard = fields.Float(string="Hazard Pay", store=True)
    nontax_salaries_other_comp = fields.Float(string="Salaries & Others Comp", store=True)
    total_nontax = fields.Float("Total", store=True, compute="_get_total_nontaxable")

    night_diff = fields.Float(string="Taxable Basic Salary", store=True)
    tax_other_benefits = fields.Float(string="Other Benefits & 13th Mo. Pay", store=True)
    tax_salaries_other_comp = fields.Float(string="Salaries & Others Comp", store=True)
    total_tax = fields.Float("Total", store=True, compute="_get_total_taxable")

    premium_paid = fields.Float(string="Premium Paid on Health & other Hops. Insurance", store=True)
    exempt_amount = fields.Float(string="Exemption Amount", store=True)
    tax_withheld = fields.Float(string="Tax Withheld", store=True)

    gross = fields.Float(string="Gross Compensation Income", store=True)
    net_tax = fields.Float(string="Net Taxable Income", store=True)
    tax_due = fields.Float(string="Tax Due", store=True)
    amount_withheld = fields.Float(string="Amount Withheld and paid for in December", store=True)
    over_withheld = fields.Float(string="Over Withheld Tax refunded to Employees", store=True)
    tax_withheld_adjusted = fields.Float(string="Amt. of Tax Withheld as Adjusted", store=True)
    substitute_filing = fields.Selection([
        ('yes', 'YES'),
        ('no', 'No')
    ], string="Substitute filing")

    @api.depends('statutory_requirements','nontax_other_benefits',
                 'deminimis','holiday','overtime','night_diff','hazard',
                 'nontax_salaries_other_comp','total_nontax')
    def _get_total_nontaxable(self):
        for rec in self:
            rec.total_nontax = (rec.statutory_requirements
                                + rec.nontax_other_benefits
                                + rec.deminimis
                                + rec.holiday
                                + rec.overtime
                                + rec.night_diff
                                + rec.hazard
                                + rec.nontax_salaries_other_comp
                                + rec.total_nontax)

    @api.depends('night_diff','tax_other_benefits',
                 'tax_salaries_other_comp')
    def _get_total_taxable(self):
        for rec in self:
            rec.total_tax =(rec.night_diff
                            + rec.tax_other_benefits
                            + rec.tax_salaries_other_comp)

    @api.depends('date_started','date_exited')
    def _get_years_of_service(self):
        for rec in self:
            if rec.date_started:
                years_services = str(int((date.today()
                                          - rec.date_started).days
                                         / 365)) + " Year(s)"
                month = int((date.today()
                             - rec.date_started).days * 0.0328767)
                if month > 12:
                    month_services = str(month % 12) + " Month(s)"
                else:
                    month_services = str(month) + " Month(s)"
                rec.years_of_service = years_services + " , " + month_services


class Employee(models.Model):
    _inherit = 'hr.employee'

    """======================WORK INFORMATION======================"""
    mobile_phone = fields.Char(compute="_auto_populate_work_info")
    work_email = fields.Char(compute="_auto_populate_work_info")
    work_location = fields.Char(compute="_auto_populate_work_info")
    work_phone = fields.Char(compute="_auto_populate_work_info")

    """======================PRIVATE INFORMATION======================"""
    passport_validity_date = fields.Date()
    place_of_passport_issuance = fields.Char()

    marital = fields.Selection([
        ('single', 'Single'),
        ('Single Mother', 'Single Mother'),
        ('Single Father', 'Single Father'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed')
    ])

    age = fields.Integer(compute="_compute_age_years")

    """======================PRE-EMPLOYMENT INFORMATION======================"""
    sss_checkbox = fields.Boolean('SSS')
    hdmf_checkbox = fields.Boolean()
    philhealth_checkbox = fields.Boolean()
    gsis_checkbox = fields.Boolean()
    tin_checkbox = fields.Boolean()
    medical_transaction_number_checkbox = fields.Boolean()

    nbi_checkbox = fields.Boolean()
    police_checkbox = fields.Boolean()
    barangay_checkbox = fields.Boolean()

    birth_checkbox = fields.Boolean()
    tor_checkbox = fields.Boolean()
    diploma_checkbox = fields.Boolean()

    sss = fields.Integer('SSS')
    hdmf = fields.Integer('HDMF')
    philhealth = fields.Integer('PhilHealth', default=None)
    gsis = fields.Integer('GSIS')
    tin = fields.Integer('TIN')
    medical_transaction_number = fields.Char()

    nbi_clearance = fields.Char('NBI')
    nbi_expiration = fields.Date()
    nbi_issued_at = fields.Char()
    nbi_date_issued = fields.Date()
    nbi_clearance_photo = fields.Binary()

    police_clearance = fields.Char('Police Clearance')
    police_expiration = fields.Date()
    police_issued_at = fields.Char()
    police_date_issued = fields.Date()
    police_clearance_photo = fields.Binary()

    barangay_clearance = fields.Char('Barangay Clearance')
    barangay_expiration = fields.Date()
    barangay_issued_at = fields.Char()
    barangay_date_issued = fields.Date()
    barangay_clearance_photo = fields.Binary()

    birth_certificate = fields.Binary()
    transcript_of_records = fields.Binary()
    diploma = fields.Binary()

    """======================SKILLS AND TRAINING======================"""
    skill_ids = fields.One2many('hrmsv3.skills', 'employee_id',
                                string="Skills")

    """======================HEALTH INFORMATION======================"""
    fit_to_work = fields.Boolean()

    height = fields.Float()
    height_uom = fields.Selection([
        ('mm', 'mm'),
        ('cm', 'cm'),
        ('inch', 'inch'),
        ('ft', 'ft')
    ])

    weight = fields.Float()
    weight_uom = fields.Selection([
        ('lbs', 'lbs'),
        ('kg', 'kg')
    ])

    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ])
    drug_test = fields.Selection([
        ('Positive', 'Positive'),
        ('Negative', 'Negative')
    ])

    health_card_provider = fields.Char()
    id_number = fields.Char(string='ID Number')
    cap_limit = fields.Float()
    credit_usage = fields.Float()

    hmo_validity_date = fields.Date(string='HMO Validity Date')
    hmo_validity_date_end = fields.Date()
    for_renewal = fields.Boolean()
    renewal_date = fields.Date()

    health_condition_ids = fields.One2many('health.condition', 'employee_id')

    """======================EMPLOYEE MOVEMENT======================"""
    contract_history_ids = fields.One2many(
        'hr.contract', 'employee_id',
        string="Contract History",
        compute='_compute_contract_history_record'
    )

    @api.depends('children')
    def _compute_contract_history_record(self):
        record = self.env['hr.contract'].search([('employee_id', '=', self.id)])
        self.update({
            'contract_history_ids': [(6, 0, record.ids)],
        })

    """========================WORK HISTORY========================"""
    work_history_ids = fields.One2many(
        'hr.work.history', 'employee_id',
        string="Work History"
    )

    """======================PRIVATE INFORMATION FUNCTIONS==================="""
    @api.depends('birthday')
    def _compute_age_years(self):
        today = date.today()
        for rec in self:
            if rec.birthday:
                rec.age = (today.year - rec.birthday.year
                           - ((today.month, today.day) < (rec.birthday.month,
                                                          rec.birthday.day)))

    """======================WORK INFORMATION FUNCTIONS======================"""
    @api.depends('address_id')
    def _auto_populate_work_info(self):
        for rec in self:
            if rec.address_id:
                rec.mobile_phone = rec.address_id.mobile or ""
                rec.work_email = rec.address_id.email or ""
                rec.work_location = ((rec.address_id.street
                                      or "")
                                     + ", " + (rec.address_id.street2
                                               or "")
                                     + ", " + (rec.address_id.city
                                               or "")
                                     + ", " + (rec.address_id.state_id.name
                                               or "")
                                     + ", " + (rec.address_id.zip
                                               or "")
                                     + ", " + (rec.address_id.country_id.name
                                               or ""))
                rec.work_phone = rec.address_id.phone or ""
