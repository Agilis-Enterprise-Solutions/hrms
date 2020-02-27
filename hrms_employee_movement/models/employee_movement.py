from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class HRMSEmployeeMovement(models.Model):
    _name = "hr.employee.movement"
    _description = "Employee Management"
    _inherit = ["mail.thread", "mail.activity.mixin", "resource.mixin"]


    name = fields.Many2one('hr.employee', "Employee Name", required=True)
    department_id = fields.Many2one('hr.department', "Department",
                                    related="name.department_id")
    job_id = fields.Many2one('hr.job', "Job Position", related="name.job_id")
    movement_type = fields.Selection([
        ('promition', 'Promotion'),
        ('demotion', 'Demotion'),
        ('lateral', 'Lateral Transfer')
        ], string="Movement Type", required=True)
    movement_date = fields.Date("Movement Date",  required=True)
    start_date = fields.Date("Start Date",  required=True)
    end_date = fields.Date("End Date",  required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('for_reviewing', 'Waiting to be Review'),
        ('review', 'Reviewed'),
        ('approve', 'Approve'),
    ], string="Status", default="draft", readonly=True, copy=False)

    date_submitted = fields.Date("Date Submitted")
    submitted_by = fields.Many2one('res.users', 'Submitted By')
    date_review = fields.Date("Date Reviewed")
    review_by = fields.Many2one('res.users', 'Reviewed By')
    date_approved = fields.Date("Date Approved")
    approved_by = fields.Many2one('res.users', 'Approved By')

    movement_line_ids = fields.One2many('hr.employee.movement_lines','movement_id')

    @api.multi
    def submit(self):
        for rec in self:
            rec.date_submitted = date.today()
            user_id = self.env['res.users'].browse(self._context.get('uid'))
            rec.submitted_by = user_id.id

        return self.write({'state': 'for_reviewing'})

    @api.multi
    def confirm(self):
        for rec in self:
            rec.date_review = date.today()
            user_id = self.env['res.users'].browse(self._context.get('uid'))
            rec.review_by = user_id.id

        return self.write({'state': 'review'})

    @api.multi
    def approve(self):
        for rec in self:
            for i in rec.movement_line_ids:
                if i.attribute == 'position':
                    rec.name.job_id = i.new_position.id
                if i.attribute == 'department':
                    rec.name.department_id = i.new_department.id
                # if i.attribute == 'contract':
                #     contract = self.env['hr.contract'].search([
                #         ('employee_id','=',rec.name.id)])[0]
                #     contract.write({
                #         'date_end': date.today(),
                #         'state': 'close'
                #     })
                #     contract_false = self.env['hr.contract'].search([
                #         ('id','=',i.new_contract.id),
                #         ('active','=',False)])
                #     contract_false.write({
                #         'state': 'open',
                #         'active': True
                #     })

        #     rec.date_approved = date.today()
        #     user_id = self.env['res.users'].browse(self._context.get('uid'))
        #     rec.approved_by = user_id.id
        #
        # return self.write({'state': 'approve'})

class HRMSEmployeeMovementLines(models.Model):
    _name = "hr.employee.movement_lines"
    _description = "Employee Management Lines"

    movement_id = fields.Many2one('hr.employee.movement')
    attribute = fields.Selection([
        ('position', 'Position'),
        ('department', 'Department'),
        ('contract', 'Contract')
        ], string="Attribute", required=True)
    current = fields.Char("Current", compute="_get_attribute_current", store=True)
    new_position = fields.Many2one('hr.job', "New Position")
    new_department = fields.Many2one('hr.department', "New Department")
    new_contract = fields.Many2one('hr.contract', "New Contract")


    @api.depends('attribute')
    def _get_attribute_current(self):
        for rec in self:
            if rec.attribute and rec.attribute == "position" and rec.movement_id.name:
                rec.current = rec.movement_id.name.job_id.name
            if rec.attribute and rec.attribute == "department" and rec.movement_id.name:
                rec.current = rec.movement_id.name.department_id.name
            if rec.attribute and rec.attribute == "contract" and rec.movement_id.name:
                contract = self.env['hr.contract'].search([
                    ('employee_id','=',rec.movement_id.name.id),
                    ('active','=',True)])
                rec.current = contract.name
