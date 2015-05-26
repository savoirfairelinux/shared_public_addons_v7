0# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Excedo Technologies & Solutions Pvt. Ltd.
#    (http://wwww.excedo.in)
#    info@excedo.in
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import datetime
from dateutil.relativedelta import relativedelta

import openerp
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.osv import fields, osv

class r3x_account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'
    #self.cr1=cr


    def _get_period_length_config(self,cr,ids,context=None):
        cr.execute("select module_aged_by_partner_balance from account_config_settings order by id desc")
        data=cr.fetchall()
        if data:
            return data[0][0]
        
    def _get_payment_term(self,cr,ids,context=None):
        cr.execute("select check_payment_option from account_config_settings order by id desc")
        data=cr.fetchall()
        if data:
            return data[0][0]

    _columns={
              'check_payment_option':fields.boolean('Aged by Payment Term'),
              'module_aged_by_partner_balance':fields.integer('Aged By Period Length in Days'),
              }

    _defaults={
               'module_aged_by_partner_balance':_get_period_length_config,
               'check_payment_option':_get_payment_term,  
              }