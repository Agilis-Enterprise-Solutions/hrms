# -*- coding: utf-8 -*-
from odoo import http

# class HrmsV3PersonnelRequisition(http.Controller):
#     @http.route('/hrms_v3_personnel_requisition/hrms_v3_personnel_requisition/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hrms_v3_personnel_requisition/hrms_v3_personnel_requisition/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hrms_v3_personnel_requisition.listing', {
#             'root': '/hrms_v3_personnel_requisition/hrms_v3_personnel_requisition',
#             'objects': http.request.env['hrms_v3_personnel_requisition.hrms_v3_personnel_requisition'].search([]),
#         })

#     @http.route('/hrms_v3_personnel_requisition/hrms_v3_personnel_requisition/objects/<model("hrms_v3_personnel_requisition.hrms_v3_personnel_requisition"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hrms_v3_personnel_requisition.object', {
#             'object': obj
#         })