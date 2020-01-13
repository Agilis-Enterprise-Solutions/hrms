# coding: utf-8
from odoo import models, fields, api
from logging import getLogger


def log(**to_output):
    for key, value in to_output.items():
        getLogger().info("\n\n\n{0}: {1}\n\n".format(key, value))


class Employee(models.Model):
    _inherit = 'hr.employee'

    mobile_phone = fields.Char(compute="_auto_populate_work_info")
    work_email = fields.Char(compute="_auto_populate_work_info")
    work_location = fields.Char(compute="_auto_populate_work_info")
    work_phone = fields.Char(compute="_auto_populate_work_info")

    passport_validity_date = fields.Date()
    place_of_passport_issuance = fields.Char()

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
