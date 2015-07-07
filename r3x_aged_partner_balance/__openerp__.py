# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Excedo Technologies & Solutions (<http:www.excedo.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'Ru3ix Aged Partner Balance',
    'version' : '2.1',
    'author' : 'Excedo Technolgies & Solutions',
    'category' :'Aged partner Balance',
    'website' : 'www.excedo.in',
    'description' : """
                    Module Used to Over Ride Aged Partner Balance View Written By (Camp To Camp) - (account_financial_report_webkit) module
                    Print Button and Export Button Added.
                    Payment Terms Added for Group by Payment Terms.
                    Payment Terms Added for Group By Payment Terms with Detail Transaction Report.
                    Original Aged Partner Balance Functionality Modified Return the Partial Amount.
                    """,
    'depends': [
        "account_financial_report_webkit",
        "account_followup",
        "r3x_res_config"
    ],
    'data': [
        'security/ir.model.access.csv',
        'account_report_aged_partner_balance_view.xml',
        'report/report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
