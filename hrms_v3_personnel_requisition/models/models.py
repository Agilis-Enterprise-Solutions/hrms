# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class hrms_v3_personnel_requisition(models.Model):
#     _name = 'hrms_v3_personnel_requisition.hrms_v3_personnel_requisition'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100