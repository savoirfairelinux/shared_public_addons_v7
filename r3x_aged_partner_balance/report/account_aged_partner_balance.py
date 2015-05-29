# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
import re
import unicodedata
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from openerp.osv import fields, osv

class new_aged_trial_report(report_sxw.rml_parse,common_report_header):

    def __init__(self, cr, uid, name, context):
        super(new_aged_trial_report, self).__init__(cr, uid, name, context=context)

        self.total_account = []
        self.localcontext.update({
            'time': time,
            'get_period_length': self._get_period_length,
            'get_result_selection':self._get_result_selection,
            'get_lines': self._get_lines,
            'get_total': self._get_total,
            'get_direction': self._get_direction,
            'get_for_period': self._get_for_period,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'get_partners':self._get_partners,
            'get_account': self._get_account,
            'get_fiscalyear': self._get_fiscalyear,
            'get_target_move': self._get_target_move,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        ctx = data['form'].get('used_context', {})
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        self.direction_selection = data['form'].get('direction_selection', 'past')
        self.target_move = data['form'].get('target_move', 'all')
        self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        if (data['form']['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (data['form']['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']
        return super(new_aged_trial_report, self).set_context(objects, data, ids, report_type=report_type)

    def _get_period_length(self,form):
        if len(form['payment_term_id']) >  1:
            return '--'
        else:
            return form['period_length']


    def _get_result_selection(self,form):
        if form['result_selection']== 'customer':
            return 'Receivable Accounts'
        elif form['result_selection'] == 'supplier':
            return 'Payable Accounts'
        else:
            return 'Receivable and Payable Accounts'

    ## ................. Adding Lines Logic Here ...................
    
    def _get_lines(self, form):
        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        # Making Single List of Partners in the Report
        # Checking whether the Ids Have Elements to Print or Not............
        # It Elements Existed for the Key ,then that key will be considered otherwise that key will be removed from the list for removing interuption
        
        if len(form['payment_term_id']) > 1:    
            for val in form['multi'].keys():
                if 'partner_id' in form['multi'][val].keys():
                    partners_list=form['multi'][val]['partner_id']            

                    self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                        res_partner.name AS name \
                        FROM res_partner,account_move_line AS l, account_account, account_move am\
                        WHERE (l.account_id=account_account.id) \
                        AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND account_account.active\
                        AND ((reconcile_id IS NULL)\
                        OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND (l.partner_id=res_partner.id)\
                        AND (l.date <= %s)\
                        AND ' + self.query + ' \
                        AND (res_partner.id IN %s)\
                        ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,tuple(partners_list)))

                    partners = self.cr.dictfetchall()
                    if partners:
                        pass
                    else:
                        del form['multi'][val]
                else:
                    del form['multi'][val]
        
        for val in form['multi'].keys():
            if 'partner_id' in form['multi'][val].keys():
                partners_list=form['multi'][val]['partner_id']
            else:
                return []
            payment_name=form['multi'][val]['payment_name']
            # Added New customized Sql Query............

            self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                    FROM res_partner,account_move_line AS l, account_account, account_move am\
                    WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                    OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                    AND (res_partner.id IN %s)\
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,tuple(partners_list)))

            partners = self.cr.dictfetchall()
            ## mise a 0 du total
            for i in range(7):
                self.total_account.append(0)
            #
            # Build a string like (1,2,3) for easy use in SQL query
            partner_ids = [x['id'] for x in partners]

            if not partner_ids:
                    return []

            # This dictionary will store the debit-credit for all partners, using partner_id as key.
            totals = {}

            #self.query=""
            self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND ((l.reconcile_id IS NULL)\
                    OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND ' + self.query + '\
                    AND account_account.active\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
            
            t = self.cr.fetchall()
            for i in t:
                totals[i[0]] = i[1]
            
            # This dictionary will store the future or past of all partners
            future_past = {}
            if self.direction_selection == 'future':
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
                t = self.cr.fetchall()
                for i in t:
                    future_past[i[0]] = i[1]
            elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
                t = self.cr.fetchall()
                for i in t:
                    future_past[i[0]] = i[1]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
            history = []
            for i in range(5):
                args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
                dates_query = '(COALESCE(l.date_maturity,l.date)'

                # Relaced form variable with form['multi'][val]
                if form['multi'][val]['period'][str(i)]['start'] and form['multi'][val]['period'][str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'], form['multi'][val]['period'][str(i)]['stop'])
                elif form['multi'][val]['period'][str(i)]['start']:
                    dates_query += ' > %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'],)
                else:
                    dates_query += ' < %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['stop'],)
                args_list += (self.date_from,)
                self.cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                        FROM account_move_line AS l, account_account, account_move am
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                            AND (am.state IN %s)
                            AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id''', args_list)
                t = self.cr.fetchall()
                d = {}
                for i in t:
                    d[i[0]] = i[1]
                history.append(d)

            # Trying to retrieve the Fields Here Omkar...........................
            
            # Use one query per period and store results in history (a list variable)
            # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
            history_records = []
            for i in range(5):
                args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
                dates_query = '(COALESCE(l.date_maturity,l.date)'

                # Relaced form variable with form['multi'][val]
                if form['multi'][val]['period'][str(i)]['start'] and form['multi'][val]['period'][str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'], form['multi'][val]['period'][str(i)]['stop'])
                elif form['multi'][val]['period'][str(i)]['start']:
                    dates_query += ' > %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'],)
                else:
                    dates_query += ' < %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['stop'],)
                args_list += (self.date_from,)
                self.cr.execute('''SELECT l.partner_id, l.id,l.move_id,l.debit,l.credit
                        FROM account_move_line AS l, account_account, account_move am
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                            AND (am.state IN %s)
                            AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)''', args_list)
                t = self.cr.dictfetchall()
                for data in t:
                    data.update({'period':i})
                history_records.append(t)

            for partner in partners:
                values = {}
            ## If choise selection is in the future
                if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                    before = False
                    if future_past.has_key(partner['id']):
                        before = [ future_past[partner['id']] ]
                        self.total_account[6] = self.total_account[6] + (before and before[0] or 0.0)
                        values['direction'] = before and before[0] or 0.0
                elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                    after = False
                    if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                        after = [ future_past[partner['id']] ]

                    self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
                    values['direction'] = after and after[0] or 0.0

                for i in range(5):
                    during = False
                    if history[i].has_key(partner['id']):
                        during = [ history[i][partner['id']] ]
                # Ajout du compteur
                    self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
                    values[str(i)] = during and during[0] or 0.0
                total = False
                if totals.has_key( partner['id'] ):
                    total = [ totals[partner['id']] ]
                values['total'] = total and total[0] or 0.0
            ## Add for total
                self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
                values['name'] = partner['name']
                id=partner['id']
                values['payment_term']=payment_name
                self.cr.execute('select payment_note,payment_next_action_date from res_partner where id=%s'%partner['id'])
                comments=self.cr.dictfetchall()[0]
                values['id']=id
                values['comments']=comments['payment_note']
                values['next_action']=comments['payment_next_action_date']

                # Reading and Re assigning the Totals for all the Periods
                current_records=[]
                for record in history_records:
                    for rec in record:
                        if rec['partner_id']==partner['id']:
                            current_records.append(rec)

                reorder_values=self._display_screen(values['id'],form,current_records)
                t_dict={'0':0.0,'1':0.0,'2':0.0,'3':0.0,'4':0.0,'due':0.0}

                for data in reorder_values:
                        t_dict.update({'0':t_dict['0']+data['0'],'1':t_dict['1']+data['1'],'2':t_dict['2']+data['2'],'3':t_dict['3']+data['3'],'4':t_dict['4']+data['4'],'due':t_dict['due']+data['due']})
                
                values['inlines']=reorder_values
                
                values.update({'0':t_dict['0'],'1':t_dict['1'],'2':t_dict['2'],'3':t_dict['3'],'4':t_dict['4'],'direction':t_dict['due']})
                res.append(values)

            total = 0.0
            totals = {}
        
            for r in res:
                total += float(r['total'] or 0.0)
                for i in range(5)+['direction']:
                    totals.setdefault(str(i), 0.0)
                    totals[str(i)] += float(r[str(i)] or 0.0)
        return res


    def _display_screen(self,ids,form,detailed):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False
        cr=self.cr
        uid=self.uid
        #context=self.context
        ids=[ids]

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')
        payment_display=self.pool.get('account.payment.display.credit')

        # Unlink all the records from the Customer Statement Table and Re write the Records once again...
        payment_ids = payment_display.search(cr,uid,[('partner_id','=',ids[0])])
        if payment_ids:
            payment_display.unlink(cr,uid,payment_ids)

        
        #set default values
        default = {
            'value': {'line_dr_ids': [] ,'line_cr_ids': []},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        partner = partner_pool.browse(cr, uid, ids[0], context=None)
        currency_id = partner.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'

        ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner.id)])

        #invoice_id = context.get('invoice_id', False)
        company_currency = partner.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=None)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        #voucher line creation
        for line in account_move_lines:
            price=0
            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual))
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            
            rs = {
                'ref':line.ref,
                'date':line.date,
                'blocked':line.blocked,
                'company_id':line.company_id.id,                  
                'invoice_date': line.date_created,
                'reference': line.name,
                'partner_id':partner.id,
                'state':line.state,
                'reconcile_id':False, 
                'invoice_no':line.move_id.name,
                'move_id':line.move_id,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(price), amount_unreconciled) or 0.0,
                'date':line.date,
                'date_maturity':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            price -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)
        Fields=[]
        
        for data in default['value'].keys():
            for value in default['value'][data]:
                if value['type']=='cr':
                    debit=value['amount_original']
                    credit=debit-value['amount_unreconciled']
                    
                else:
                    # Here Customer Refunds , or Customer Excess Amount is Recorded..
                    credit=value['amount_original']
                    debit=credit-value['amount_unreconciled']
                value.update({'debit':debit,'credit':credit,'result':debit-credit})
                move_line_id=value['move_line_id']
                for ele in ['amount_unreconciled','move_line_id','type','amount_original','amount']:
                    value.pop(ele)

                payment_display.create(cr, uid,value)

                #Writing the Fields to Table........
                value.update({'1':0.0,'2':0.0,'3':0.0,'4':0.0,'0':0.0,'due':0.0,'move_line_id':move_line_id})
                Fields.append(value)  
                
        if detailed:
            for line in Fields:
                period=self.check_line(line['move_line_id'],detailed)
                if period in range(5):
                        line.update({str(period):line['result']})
                if period=='due':
                    line.update({'due':line['result']})
        else:
            for line in Fields:
                    line.update({'due':line['result']})

        return Fields        

    def check_line(self,move_line,detailed):
        res='due'
        for line in detailed:
            if move_line == line['id']:
                res=line['period']
        return res
    
    def _get_total(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_direction(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_for_period(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_partners(self,data):
        # TODO: deprecated, to remove in trunk
        if data['form']['result_selection'] == 'customer':
            return self._translate('Receivable Accounts')
        elif data['form']['result_selection'] == 'supplier':
            return self._translate('Payable Accounts')
        elif data['form']['result_selection'] == 'customer_supplier':
            return self._translate('Receivable and Payable Accounts')
        return ''

report_sxw.report_sxw('report.r3x_aged_partner_balance.new_aged_trial_balance', 'res.partner',
        'addons/r3x_aged_partner_balance/report/new_account_aged_partner_balance.rml',
        parser=new_aged_trial_report, 
        header="internal landscape")


class new_aged_trial_report_detail(report_sxw.rml_parse,common_report_header):

    def __init__(self, cr, uid, name, context):
        super(new_aged_trial_report_detail, self).__init__(cr, uid, name, context=context)

        self.total_account = []
        self.localcontext.update({
            'time': time,
            'get_period_length': self._get_period_length,
            'get_result_selection':self._get_result_selection,
            'get_lines': self._get_lines,
            'get_total': self._get_total,
            'get_direction': self._get_direction,
            'get_for_period': self._get_for_period,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'get_partners':self._get_partners,
            'get_account': self._get_account,
            'get_fiscalyear': self._get_fiscalyear,
            'get_target_move': self._get_target_move,
            'get_detail_lines':self._display_screen,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        ctx = data['form'].get('used_context', {})
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        self.direction_selection = data['form'].get('direction_selection', 'past')
        self.target_move = data['form'].get('target_move', 'all')
        self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        if (data['form']['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (data['form']['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']
        return super(new_aged_trial_report_detail, self).set_context(objects, data, ids, report_type=report_type)

    def _get_period_length(self,form):
        if len(form['payment_term_id']) >  1:
            return '--'
        else:
            return form['period_length']


    def _get_result_selection(self,form):
        if form['result_selection']== 'customer':
            return 'Receivable Accounts'
        elif form['result_selection'] == 'supplier':
            return 'Payable Accounts'
        else:
            return 'Receivable and Payable Accounts'

    def _get_lines(self, form):
        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        # Making Single List of Partners in the Report
        # Checking whether the Ids Have Elements to Print or Not............
        # It Elements Existed for the Key ,then that key will be considered otherwise that key will be removed from the list for removing interuption
        
        if len(form['payment_term_id']) > 1:    
            for val in form['multi'].keys():
                if 'partner_id' in form['multi'][val].keys():
                    partners_list=form['multi'][val]['partner_id']            

                    self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                        res_partner.name AS name \
                        FROM res_partner,account_move_line AS l, account_account, account_move am\
                        WHERE (l.account_id=account_account.id) \
                        AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND account_account.active\
                        AND ((reconcile_id IS NULL)\
                        OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND (l.partner_id=res_partner.id)\
                        AND (l.date <= %s)\
                        AND ' + self.query + ' \
                        AND (res_partner.id IN %s)\
                        ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,tuple(partners_list)))

                    partners = self.cr.dictfetchall()
                    if partners:
                        pass
                    else:
                        del form['multi'][val]
                else:
                    del form['multi'][val]
        
        for val in form['multi'].keys():
            if 'partner_id' in form['multi'][val].keys():
                partners_list=form['multi'][val]['partner_id']
            else:
                return []
            payment_name=form['multi'][val]['payment_name']
            # Added New customized Sql Query............

            self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name \
                    FROM res_partner,account_move_line AS l, account_account, account_move am\
                    WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                    OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                    AND (res_partner.id IN %s)\
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,tuple(partners_list)))

            partners = self.cr.dictfetchall()
            ## mise a 0 du total
            for i in range(7):
                self.total_account.append(0)
            #
            # Build a string like (1,2,3) for easy use in SQL query
            partner_ids = [x['id'] for x in partners]

            if not partner_ids:
                    return []

            # This dictionary will store the debit-credit for all partners, using partner_id as key.
            totals = {}

            #self.query=""
            self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND (l.partner_id IN %s)\
                    AND ((l.reconcile_id IS NULL)\
                    OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                    AND ' + self.query + '\
                    AND account_account.active\
                    AND (l.date <= %s)\
                    GROUP BY l.partner_id ', (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids), self.date_from, self.date_from,))
            
            t = self.cr.fetchall()
            for i in t:
                totals[i[0]] = i[1]
            
            # This dictionary will store the future or past of all partners
            future_past = {}
            if self.direction_selection == 'future':
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                        FROM account_move_line AS l, account_account, account_move am \
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
                t = self.cr.fetchall()
                for i in t:
                    future_past[i[0]] = i[1]
            elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
                self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) \
                    FROM account_move_line AS l, account_account, account_move am \
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
                t = self.cr.fetchall()
                for i in t:
                    future_past[i[0]] = i[1]

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
            history = []
            for i in range(5):
                args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
                dates_query = '(COALESCE(l.date_maturity,l.date)'

                # Relaced form variable with form['multi'][val]
                if form['multi'][val]['period'][str(i)]['start'] and form['multi'][val]['period'][str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'], form['multi'][val]['period'][str(i)]['stop'])
                elif form['multi'][val]['period'][str(i)]['start']:
                    dates_query += ' > %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'],)
                else:
                    dates_query += ' < %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['stop'],)
                args_list += (self.date_from,)
                self.cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                        FROM account_move_line AS l, account_account, account_move am
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                            AND (am.state IN %s)
                            AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id''', args_list)
                t = self.cr.fetchall()
                d = {}
                for i in t:
                    d[i[0]] = i[1]
                history.append(d)

            # Trying to retrieve the Fields Here Omkar...........................
            
            # Use one query per period and store results in history (a list variable)
            # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
            history_records = []
            for i in range(5):
                args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
                dates_query = '(COALESCE(l.date_maturity,l.date)'

                # Relaced form variable with form['multi'][val]
                if form['multi'][val]['period'][str(i)]['start'] and form['multi'][val]['period'][str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'], form['multi'][val]['period'][str(i)]['stop'])
                elif form['multi'][val]['period'][str(i)]['start']:
                    dates_query += ' > %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['start'],)
                else:
                    dates_query += ' < %s)'
                    args_list += (form['multi'][val]['period'][str(i)]['stop'],)
                args_list += (self.date_from,)
                self.cr.execute('''SELECT l.partner_id, l.id,l.move_id,l.debit,l.credit
                        FROM account_move_line AS l, account_account, account_move am
                        WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                            AND (am.state IN %s)
                            AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s )))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)''', args_list)
                t = self.cr.dictfetchall()
                for data in t:
                    data.update({'period':i})
                history_records.append(t)

            for partner in partners:
                values = {}
            ## If choise selection is in the future
                if self.direction_selection == 'future':
                # Query here is replaced by one query which gets the all the partners their 'before' value
                    before = False
                    if future_past.has_key(partner['id']):
                        before = [ future_past[partner['id']] ]
                        self.total_account[6] = self.total_account[6] + (before and before[0] or 0.0)
                        values['direction'] = before and before[0] or 0.0
                elif self.direction_selection == 'past': # Changed this so people could in the future create new direction_selections
                # Query here is replaced by one query which gets the all the partners their 'after' value
                    after = False
                    if future_past.has_key(partner['id']): # Making sure this partner actually was found by the query
                        after = [ future_past[partner['id']] ]

                    self.total_account[6] = self.total_account[6] + (after and after[0] or 0.0)
                    values['direction'] = after and after[0] or 0.0

                for i in range(5):
                    during = False
                    if history[i].has_key(partner['id']):
                        during = [ history[i][partner['id']] ]
                # Ajout du compteur
                    self.total_account[(i)] = self.total_account[(i)] + (during and during[0] or 0)
                    values[str(i)] = during and during[0] or 0.0
                total = False
                if totals.has_key( partner['id'] ):
                    total = [ totals[partner['id']] ]
                values['total'] = total and total[0] or 0.0
            
            ## Add for total
                self.total_account[(i+1)] = self.total_account[(i+1)] + (total and total[0] or 0.0)
                values['name'] = partner['name']
                id=partner['id']
                values['payment_term']=payment_name
                self.cr.execute('select payment_note,payment_next_action_date from res_partner where id=%s'%partner['id'])
                comments=self.cr.dictfetchall()[0]
                values['id']=id
                values['comments']=comments['payment_note']
                values['next_action']=comments['payment_next_action_date']

                # Reading and Re assigning the Totals for all the Periods
                current_records=[]
                for record in history_records:
                    for rec in record:
                        if rec['partner_id']==partner['id']:
                            current_records.append(rec)

                import operator
                
                inlines=self._display_screen(values['id'],form,current_records)
                reorder_values=sorted(inlines, key = operator.itemgetter('invoice_date'))
                t_dict={'0':0.0,'1':0.0,'2':0.0,'3':0.0,'4':0.0,'due':0.0}
                
                for data in reorder_values:
                        t_dict.update({'0':t_dict['0']+data['0'],'1':t_dict['1']+data['1'],'2':t_dict['2']+data['2'],'3':t_dict['3']+data['3'],'4':t_dict['4']+data['4'],'due':t_dict['due']+data['due']})
                
                values['inlines']=reorder_values
                values.update({'0':t_dict['0'],'1':t_dict['1'],'2':t_dict['2'],'3':t_dict['3'],'4':t_dict['4'],'direction':t_dict['due']})
                res.append(values)
            
            total = 0.0
            totals = {}
        
            for r in res:
                total += float(r['total'] or 0.0)
                for i in range(5)+['direction']:
                    totals.setdefault(str(i), 0.0)
                    totals[str(i)] += float(r[str(i)] or 0.0)
        return res


    def _display_screen(self,ids,form,detailed):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False
        cr=self.cr
        uid=self.uid
        #context=self.context
        ids=[ids]

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')
        payment_display=self.pool.get('account.payment.display.credit')

        # Unlink all the records from the Customer Statement Table and Re write the Records once again...
        payment_ids = payment_display.search(cr,uid,[('partner_id','=',ids[0])])
        if payment_ids:
            payment_display.unlink(cr,uid,payment_ids)

        
        #set default values
        default = {
            'value': {'line_dr_ids': [] ,'line_cr_ids': []},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        partner = partner_pool.browse(cr, uid, ids[0], context=None)
        currency_id = partner.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'

        ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner.id)])

        #invoice_id = context.get('invoice_id', False)
        company_currency = partner.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=None)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        #voucher line creation
        for line in account_move_lines:
            price=0
            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual))
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            
            rs = {
                'ref':line.ref,
                'date':line.date,
                'blocked':line.blocked,
                'company_id':line.company_id.id,                  
                'invoice_date': line.date_created,
                'reference': line.name,
                'partner_id':partner.id,
                'state':line.state,
                'reconcile_id':False, 
                'invoice_no':line.move_id.name,
                'move_id':line.move_id,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(price), amount_unreconciled) or 0.0,
                'date':line.date,
                'date_maturity':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            price -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)
        Fields=[]
        
        for data in default['value'].keys():
            for value in default['value'][data]:
                if value['type']=='cr':
                    debit=value['amount_original']
                    credit=debit-value['amount_unreconciled']
                    
                else:
                    # Here Customer Refunds , or Customer Excess Amount is Recorded..
                    credit=value['amount_original']
                    debit=credit-value['amount_unreconciled']
                value.update({'debit':debit,'credit':credit,'result':debit-credit})
                move_line_id=value['move_line_id']
                for ele in ['amount_unreconciled','move_line_id','type','amount_original','amount']:
                    value.pop(ele)

                payment_display.create(cr, uid,value)

                #Writing the Fields to Table........
                value.update({'1':0.0,'2':0.0,'3':0.0,'4':0.0,'0':0.0,'due':0.0,'move_line_id':move_line_id})
                Fields.append(value)  
        
        if detailed:
            for line in Fields:
                period=self.check_line(line['move_line_id'],detailed)
                if period in range(5):
                        line.update({str(period):line['result']})
                if period=='due':
                    line.update({'due':line['result']})
        else:
            for line in Fields:
                    line.update({'due':line['result']})
        return Fields        

    def check_line(self,move_line,detailed):
        res='due'
        for line in detailed:
            if move_line == line['id']:
                res=line['period']
        return res
        
    def _get_total(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_direction(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_for_period(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_partners(self,data):
        # TODO: deprecated, to remove in trunk
        if data['form']['result_selection'] == 'customer':
            return self._translate('Receivable Accounts')
        elif data['form']['result_selection'] == 'supplier':
            return self._translate('Payable Accounts')
        elif data['form']['result_selection'] == 'customer_supplier':
            return self._translate('Receivable and Payable Accounts')
        return ''

report_sxw.report_sxw('report.r3x_aged_partner_balance.new_aged_trial_balance_detail', 
                      'res.partner',
                      'addons/r3x_aged_partner_balance/report/new_account_aged_partner_balance_detail.rml'
                      ,parser=new_aged_trial_report_detail, 
                      header="internal landscape")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
