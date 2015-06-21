# -*- encoding: utf-8 -*-
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

from openerp.osv import fields, osv

class account_payment_display_credit(osv.osv):
    _name = "account.payment.display.credit"
    _description = "Account Payment Display Credit"

    _columns = {
        'partner_id': fields.integer('partner_id'),
        'account_id': fields.many2one('account.account', 'Account',
                                      required=True, ondelete="cascade",
                                      domain=[('type','<>','view'),
                                              ('type', '<>', 'closed')],
                                      select=2),
        'move_id': fields.integer('move_id'),
        'reconcile_id': fields.char('reconcile_id',size=64),
        'state': fields.selection([('draft','Unbalanced'), ('valid','Balanced')]
            , 'Status', readonly=True),
        'date_maturity': fields.date('Due date', select=True ,
                                     help="This field is used for payable and "
                                          "receivable journal entries. You can "
                                          "put the limit date for the payment "
                                          "of this line."),
        'invoice_date': fields.char('invoice date', size=64),
        'invoice_no': fields.char('invoice no',size=20),
        'reference': fields.char('Reference',size=200),
        'date': fields.date('Effective Date'),
        'ref': fields.char('Reference', size=64),
        'due_date': fields.date('Due date'),
        'debit': fields.float('debit'),
        'credit': fields.float('Credit'),
        'result': fields.float('Balance'),
        'company_id': fields.related('account_id', 'company_id', type='many2one'
            , relation='res.company', string='Company', store=True,
                                     readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency',
                                       help="The optional other currency if it "
                                            "is a multi-currency entry."),
        'blocked':fields.boolean('blocked'),
    }

    _order='date asc'