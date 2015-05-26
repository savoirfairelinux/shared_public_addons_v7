# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Noviat nv/sa (www.noviat.com). All rights reserved.
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

from __future__ import division

import xlwt
import time
import account_financial_report_webkit
from datetime import datetime
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
#from openerp.addons.account_financial_report_webkit.report.aged_partner_balance import AccountAgedTrialBalanceWebkit
from openerp.addons.r3x_aged_partner_balance.report.account_aged_partner_balance import new_aged_trial_report
from openerp.tools.translate import _

from openerp import pooler
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class open_invoices_xls(report_xls):
    column_sizes = [12,12,20,15,30,30,14,14,14,14,14,14,10]

    def global_initializations(self, wb, _p, xlwt, _xs, objects, data):
        # this procedure will initialise variables and Excel cell styles and return them as global ones
        global ws
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        #-------------------------------------------------------
        global nbr_columns  #number of columns is 11 in case of normal report, 13 in case the option currency is selected and 12 in case of the regroup by currency option is checked
        group_lines = False

        if group_lines:
            nbr_columns = 12
        #Relacing This Line................

        #elif _p.amount_currency(data) and not group_lines:
        elif _p.get_currency(data) and not group_lines:
            nbr_columns = 13
        else:
            nbr_columns = 11
        #-------------------------------------------------------
        global style_font12  #cell style for report title
        style_font12 = xlwt.easyxf(_xs['xls_title'])
        #-------------------------------------------------------
        global style_default
        style_default = xlwt.easyxf(_xs['borders_all'])
        #-------------------------------------------------------
        global style_default_italic
        style_default_italic = xlwt.easyxf(_xs['borders_all'] + _xs['italic'])
        #-------------------------------------------------------
        global style_bold
        style_bold = xlwt.easyxf(_xs['bold'] + _xs['borders_all'])
        #-------------------------------------------------------
        global style_bold_center
        style_bold_center = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['center'])
        #-------------------------------------------------------
        global style_bold_italic
        style_bold_italic = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['italic'])
        #-------------------------------------------------------
        global style_bold_italic_decimal
        style_bold_italic_decimal = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['italic'] + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_bold_blue
        style_bold_blue = xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] )
        #-------------------------------------------------------
        global style_bold_blue_italic_decimal
        style_bold_blue_italic_decimal = xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['italic'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_bold_blue_center #cell style for header titles: 'Chart of accounts' - 'Fiscal year' ...
        style_bold_blue_center= xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['center'])
        #-------------------------------------------------------
        global style_center #cell style for header data: 'Chart of accounts' - 'Fiscal year' ...
        style_center = xlwt.easyxf(_xs['borders_all'] + _xs['wrap'] + _xs['center'])
        #-------------------------------------------------------
        global style_yellow_bold #cell style for columns titles 'Date'- 'Period' - 'Entry'...
        style_yellow_bold = xlwt.easyxf(_xs['bold'] + _xs['fill'] + _xs['borders_all'])
        #-------------------------------------------------------
        global style_yellow_bold_right #cell style for columns titles 'Date'- 'Period' - 'Entry'...
        style_yellow_bold_right = xlwt.easyxf(_xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs['right'])
        #-------------------------------------------------------
        global style_right
        style_right = xlwt.easyxf(_xs['borders_all'] + _xs['right'])
        #-------------------------------------------------------
        global style_right_italic
        style_right_italic = xlwt.easyxf(_xs['borders_all'] + _xs['right'] + _xs['italic'])
        #-------------------------------------------------------
        global style_decimal
        style_decimal = xlwt.easyxf(_xs['borders_all'] + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_decimal_italic
        style_decimal_italic = xlwt.easyxf(_xs['borders_all'] + _xs['right'] + _xs['italic'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_date
        style_date = xlwt.easyxf(_xs['borders_all'] + _xs['left'], num_format_str = report_xls.date_format)
        #-------------------------------------------------------
        global style_date_italic
        style_date_italic = xlwt.easyxf(_xs['borders_all'] + _xs['left'] + _xs['italic'], num_format_str = report_xls.date_format)
        #-------------------------------------------------------
        global style_account_title, style_account_title_right, style_account_title_decimal
        cell_format = _xs['xls_title'] + _xs['bold'] + _xs['fill'] + _xs['borders_all']
        style_account_title = xlwt.easyxf(cell_format)
        style_account_title_right = xlwt.easyxf(cell_format + _xs['right'])
        style_account_title_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_partner_row
        cell_format = _xs['bold']
        style_partner_row = xlwt.easyxf(cell_format)
        #-------------------------------------------------------
        global style_partner_cumul, style_partner_cumul_right, style_partner_cumul_center, style_partner_cumul_decimal
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        style_partner_cumul = xlwt.easyxf(cell_format)
        style_partner_cumul_right = xlwt.easyxf(cell_format + _xs['right'])
        style_partner_cumul_center = xlwt.easyxf(cell_format + _xs['center'])
        style_partner_cumul_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str = report_xls.decimal_format)

    def print_title(self, _p, row_position): # print the first line "OPEN INVOICE REPORT - db name - Currency
        report_name =  ' - '.join([_p.report_name.upper(), _p.company.partner_id.name, _p.company.currency_id.name])
        c_specs = [('report_name', nbr_columns, 0, 'text', report_name), ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_font12)
        return row_position

    def print_empty_row(self, row_position): #send an empty row to the Excel document
        c_sizes = self.column_sizes
        c_specs = [('empty%s'%i, 1, c_sizes[i], 'text', None) for i in range(0,len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, set_column_size=True)
        return row_position


    def print_columns_title(self, _p, data, row_position):  # Fill in a row with the titles of the columns for the invoice lines: Date - Period - Entry -...

        print "Testing the Reportssssss:::",data['form']['hide_period'] , data['form']['detailed_report']
        if data['form']['hide_period'] and not data['form']['detailed_report']:
            print "In the If"
            c_specs = [
            ('partners', 1, 0, 'text', _('Partner'),None,style_yellow_bold),
            ('payment_term',1,0,'text',_('Payment Term'),None,style_yellow_bold),
            ('due', 1, 0, 'text', _('Not Due'),None,style_yellow_bold),
            ('od30', 1, 0, 'text',_('Current'),None,style_yellow_bold),
            ('od60', 1, 0, 'text',_('Period 1'),None,style_yellow_bold),
            ('od90', 1, 0, 'text',_('Period 2'),None,style_yellow_bold),
            ('od120', 1, 0, 'text',_('Period 3'),None,style_yellow_bold),
            ('older', 1, 0, 'text',_('Older'),None,style_yellow_bold),
            ('balance', 1, 0, 'text', _('Total'),None,style_yellow_bold),
            ('coments', 1, 0, 'text', _('Comments'),None,style_yellow_bold),
            ('payment_next_Action_date',1,0,'text',_('Next Action Date'),None,style_yellow_bold),
            ]

        else:            
            c_specs = [
                ('partners', 1, 0, 'text', _('Partner'),None,style_yellow_bold),
                ('payment_term',1,0,'text',_('Payment Term'),None,style_yellow_bold),
                ('due', 1, 0, 'text', _('Not Due'),None,style_yellow_bold),
                ('od30', 1, 0, 'text', _(data['form']['4']['name']),None,style_yellow_bold),
                ('od60', 1, 0, 'text',_(data['form']['3']['name']),None,style_yellow_bold),
                ('od90', 1, 0, 'text',_(data['form']['2']['name']),None,style_yellow_bold),
                ('od120', 1, 0, 'text',_(data['form']['1']['name']),None,style_yellow_bold),
                ('older', 1, 0, 'text', _(data['form']['0']['name']),None,style_yellow_bold),
                ('balance', 1, 0, 'text', _('Total'),None,style_yellow_bold),
                ('coments', 1, 0, 'text', _('Comments'),None,style_yellow_bold),
                ('payment_next_Action_date',1,0,'text',_('Next Action Date'),None,style_yellow_bold),
            ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_yellow_bold)
        return row_position

    def print_lines(self, row_position, account, line,_p, data, line_number): # Fill in rows of invoice line
        # Mako: <div class="act_as_row lines ${line.get('is_from_previous_periods') and 'open_invoice_previous_line' or ''} ${line.get('is_clearance_line') and 'clearance_line' or ''}">
        if line.get('is_from_previous_periods') or line.get('is_clearance_line'):
            style_line_default = style_default_italic
            style_line_right = style_right_italic
            style_line_date = style_date_italic
            style_line_decimal = style_decimal_italic
        else:
            style_line_default = style_default
            style_line_right = style_right
            style_line_date = style_date
            style_line_decimal = style_decimal

        c_specs = [
                       ('partner_name', 1, 0, 'text',line.get('partner_name')or '' ),
                       ('payment_term',1,0,'text',line.get('payment_term')or ' -'),
                       ('due',1,0,'number',line.get('due') or 0.0, None,style_line_decimal),
                       ('od30',1,0,'number',line.get('od30') or 0.0, None,style_line_decimal),
                       ('od60',1,0,'number',line.get('od60') or 0.0, None,style_line_decimal),
                       ('od90',1,0,'number',line.get('od90') or 0.0, None,style_line_decimal),
                       ('od120',1,0,'number',line.get('od120') or 0.0, None,style_line_decimal),
                       ('older',1,0,'number',line.get('older') or 0.0, None,style_line_decimal),
                       ('balance', 1, 0, 'number', line.get('balance') or 0.0, None, style_line_decimal),
                       ('payment_note',1,0,'text',line.get('payment_note')or '  -'),
                       ('payment_next_Action_date',1,0,'text',line.get('payment_next_Action_date')or '  -'),
                    ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, style_line_default)
        return row_position

    def print_ledger_lines(self, row_pos, lines_data, _xs, xlwt, _p, data): # export the invoice AR/AP lines

            row_start_account = row_pos

            row_start_account = row_pos
            res_obj = self.pool.get('ir.property')

            row_pos = self.print_empty_row(row_pos)
            row_pos = self.print_columns_title(_p, data, row_pos)

            line_number=1
            for acc in lines_data:
                line_number = 0
                balance=0
                line={}
                line['balance'] = acc['total']
                line['partner_name'] = acc['name']
                line['payment_term']=acc['payment_term']        #data['form']['payment_info'][p_id]['payment_term']
                line['due']= acc['direction']
                line['od30']= acc[str(4)]
                line['od60']= acc[str(3)]
                line['od90']= acc[str(2)]
                line['od120']= acc[str(1)]
                line['older']= acc[str(0)]
                line['payment_next_Action_date']=acc['next_action']  #data['form']['payment_info'][p_id]['payment_next_Action_date']
                line['payment_note']=acc['comments'] #data['form']['payment_info'][p_id]['payment_note']
                row_pos_start = row_pos
                row_pos = self.print_lines(row_pos, acc, line, _p, data, line_number)
                line_number += 1

            return row_pos

        ########### Printing Multi Select Values .................
    def _get_lines(self,data,form):
        self.total_account = []
        obj_move = self.pool.get('account.move.line')
        ctx = form.get('used_context', {})
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        self.direction_selection = form.get('direction_selection', 'past')
        self.target_move = form.get('target_move', 'all')
        self.date_from = form.get('date_from', time.strftime('%Y-%m-%d'))
        if (form['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (form['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']

        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']

        # Checking Multiple Payment Terms that Any Null customers with payment term Ids

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
        #print "Ids Here The Test::::::::::: Payment Display:::::::::::",ids
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

    def get_lines(self,data,form):
        self.total_account = []
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

        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
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
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,))
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
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'

                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' > %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' < %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (self.date_from,)
            self.cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                        AND (am.state IN %s)
                        AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND ((l.reconcile_id IS NULL)
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

        history_records = []
        for i in range(5):
                args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
                dates_query = '(COALESCE(l.date_maturity,l.date)'
                if form[str(i)]['start'] and form[str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (form[str(i)]['start'], form[str(i)]['stop'])
                elif form[str(i)]['start']:
                    dates_query += ' > %s)'
                    args_list += (form[str(i)]['start'],)
                else:
                    dates_query += ' < %s)'
                    args_list += (form[str(i)]['stop'],)
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

            # Connnect to ir.property table to return the Values for the Payment Term................
            self.cr.execute("select value_reference from ir_property where name='property_payment_term' and res_id='res.partner,%s'    "%partner['id'])
            payment_term_val=self.cr.dictfetchall()
            if payment_term_val:
                payment_term_val=payment_term_val[0]

                self.cr.execute('select name from account_payment_term where id=%s'%payment_term_val['value_reference'].split(',')[-1])
                payment_term = self.cr.dictfetchall()[0]
                values['payment_term']=payment_term['name']
            else:
                values['payment_term']=""
            self.cr.execute('select payment_note,payment_next_action_date from res_partner where id=%s'%partner['id'])
            comments=self.cr.dictfetchall()[0]
            id=partner['id']
            values['id']=id
            values['comments']=comments['payment_note']
            values['next_action']=comments['payment_next_action_date']
            
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



#### Added Functions From Acount Partner Balance................................

    def generate_xls_report(self, _p, _xs, data, objects, wb): # main function
        # Initializations
        _p.update({'report_name':'Aged Partner Balance'})
        self.global_initializations(wb,_p, xlwt, _xs, objects, data)
        row_pos = 0

        row_pos = self.print_title(_p, row_pos)

        ws.set_horz_split_pos(row_pos)

        lines_data=[]

        if data['form']['hide_period']==True:
                lines_data=list(self._get_lines(data,data['form']))
        else:
            lines_data = list(self.get_lines(data,data['form']))

        row_pos = self.print_ledger_lines(row_pos, lines_data , _xs, xlwt, _p, data)
        row_pos += 1

open_invoices_xls('report.account.new_account_report_aged_partner_balance_xls', 
                  'account.account', 
                  parser=new_aged_trial_report)


# Enhancing the Module For New Detail Report...........................

class open_invoices_detail_xls(report_xls):
    column_sizes = [12,12,20,15,30,30,14,14,14,14,14,14,10]

    def global_initializations(self, wb, _p, xlwt, _xs, objects, data):
        # this procedure will initialise variables and Excel cell styles and return them as global ones
        global ws
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        #-------------------------------------------------------
        global nbr_columns  #number of columns is 11 in case of normal report, 13 in case the option currency is selected and 12 in case of the regroup by currency option is checked
        group_lines = False

        if group_lines:
            nbr_columns = 12
        #Relacing This Line................

        #elif _p.amount_currency(data) and not group_lines:
        elif _p.get_currency(data) and not group_lines:
            nbr_columns = 13
        else:
            nbr_columns = 11
        #-------------------------------------------------------
        global style_font12  #cell style for report title
        style_font12 = xlwt.easyxf(_xs['xls_title'])
        #-------------------------------------------------------
        global style_default
        style_default = xlwt.easyxf(_xs['borders_all'])
        #-------------------------------------------------------
        global style_default_italic
        style_default_italic = xlwt.easyxf(_xs['borders_all'] + _xs['italic'])
        #-------------------------------------------------------
        global style_bold
        style_bold = xlwt.easyxf(_xs['bold'] + _xs['borders_all'])
        #-------------------------------------------------------
        global style_bold_center
        style_bold_center = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['center'])
        #-------------------------------------------------------
        global style_bold_italic
        style_bold_italic = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['italic'])
        #-------------------------------------------------------
        global style_bold_italic_decimal
        style_bold_italic_decimal = xlwt.easyxf(_xs['bold'] + _xs['borders_all'] + _xs['italic'] + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_bold_blue
        style_bold_blue = xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] )
        #-------------------------------------------------------
        global style_bold_blue_italic_decimal
        style_bold_blue_italic_decimal = xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['italic'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_bold_blue_center #cell style for header titles: 'Chart of accounts' - 'Fiscal year' ...
        style_bold_blue_center= xlwt.easyxf(_xs['bold'] + _xs['fill_blue'] + _xs['borders_all'] + _xs['center'])
        #-------------------------------------------------------
        global style_center #cell style for header data: 'Chart of accounts' - 'Fiscal year' ...
        style_center = xlwt.easyxf(_xs['borders_all'] + _xs['wrap'] + _xs['center'])
        #-------------------------------------------------------
        global style_yellow_bold #cell style for columns titles 'Date'- 'Period' - 'Entry'...
        style_yellow_bold = xlwt.easyxf(_xs['bold'] + _xs['fill'] + _xs['borders_all'])
        #-------------------------------------------------------
        global style_yellow_bold_right #cell style for columns titles 'Date'- 'Period' - 'Entry'...
        style_yellow_bold_right = xlwt.easyxf(_xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs['right'])
        #-------------------------------------------------------
        global style_right
        style_right = xlwt.easyxf(_xs['borders_all'] + _xs['right'])
        #-------------------------------------------------------
        global style_right_italic
        style_right_italic = xlwt.easyxf(_xs['borders_all'] + _xs['right'] + _xs['italic'])
        #-------------------------------------------------------
        global style_decimal
        style_decimal = xlwt.easyxf(_xs['borders_all'] + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_decimal_italic
        style_decimal_italic = xlwt.easyxf(_xs['borders_all'] + _xs['right'] + _xs['italic'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_date
        style_date = xlwt.easyxf(_xs['borders_all'] + _xs['left'], num_format_str = report_xls.date_format)
        #-------------------------------------------------------
        global style_date_italic
        style_date_italic = xlwt.easyxf(_xs['borders_all'] + _xs['left'] + _xs['italic'], num_format_str = report_xls.date_format)
        #-------------------------------------------------------
        global style_account_title, style_account_title_right, style_account_title_decimal
        cell_format = _xs['xls_title'] + _xs['bold'] + _xs['fill'] + _xs['borders_all']
        style_account_title = xlwt.easyxf(cell_format)
        style_account_title_right = xlwt.easyxf(cell_format + _xs['right'])
        style_account_title_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str = report_xls.decimal_format)
        #-------------------------------------------------------
        global style_partner_row
        cell_format = _xs['bold']
        style_partner_row = xlwt.easyxf(cell_format)
        #-------------------------------------------------------
        global style_partner_cumul, style_partner_cumul_right, style_partner_cumul_center, style_partner_cumul_decimal
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        style_partner_cumul = xlwt.easyxf(cell_format)
        style_partner_cumul_right = xlwt.easyxf(cell_format + _xs['right'])
        style_partner_cumul_center = xlwt.easyxf(cell_format + _xs['center'])
        style_partner_cumul_decimal = xlwt.easyxf(cell_format + _xs['right'], num_format_str = report_xls.decimal_format)

    def print_title(self, _p, row_position): # print the first line "OPEN INVOICE REPORT - db name - Currency
        report_name =  ' - '.join([_p.report_name.upper(), _p.company.partner_id.name, _p.company.currency_id.name])
        c_specs = [('report_name', nbr_columns, 0, 'text', report_name), ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_font12)
        return row_position

    def print_empty_row(self, row_position): #send an empty row to the Excel document
        c_sizes = self.column_sizes
        c_specs = [('empty%s'%i, 1, c_sizes[i], 'text', None) for i in range(0,len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, set_column_size=True)
        return row_position


    def print_columns_title(self, _p, data, row_position):  # Fill in a row with the titles of the columns for the invoice lines: Date - Period - Entry -...

        print "Test the Luck in The Detailed Report Buddy.............."
        if data['form']['hide_period'] and not data['form']['detailed_report']:
            c_specs = [
            ('partners', 1, 0, 'text', _('Partner'),None,style_yellow_bold),
            ('payment_term',1,0,'text',_('Payment Term'),None,style_yellow_bold),
            ('due', 1, 0, 'text', _('Not Due'),None,style_yellow_bold),
            ('od30', 1, 0, 'text',_('Current'),None,style_yellow_bold),
            ('od60', 1, 0, 'text',_('Period 1'),None,style_yellow_bold),
            ('od90', 1, 0, 'text',_('Period 2'),None,style_yellow_bold),
            ('od120', 1, 0, 'text',_('Period 3'),None,style_yellow_bold),
            ('older', 1, 0, 'text',_('Older'),None,style_yellow_bold),
            ('balance', 1, 0, 'text', _('Total'),None,style_yellow_bold),
            ('coments', 1, 0, 'text', _('Comments'),None,style_yellow_bold),
            ('payment_next_Action_date',1,0,'text',_('Next Action Date'),None,style_yellow_bold),
            ]

        elif data['form']['hide_period'] and data['form']['detailed_report']:
            c_specs = [
                ('partners', 1, 0, 'text', _('Partner'),None,style_yellow_bold),
                ('payment_term',1,0,'text',_('Invoice No'),None,style_yellow_bold),
                ('due',1,0,'text',_('Due Date'),None,style_yellow_bold),
                ('od30', 1, 0, 'text', _('Not Due'),None,style_yellow_bold),
                ('od60', 1, 0, 'text', _(data['form']['4']['name']),None,style_yellow_bold),
                ('od90', 1, 0, 'text',_(data['form']['3']['name']),None,style_yellow_bold),
                ('od120', 1, 0, 'text',_(data['form']['2']['name']),None,style_yellow_bold),
                ('older', 1, 0, 'text',_(data['form']['1']['name']),None,style_yellow_bold),
                ('balance', 1, 0, 'text', _(data['form']['0']['name']),None,style_yellow_bold),
                ('coments', 1, 0, 'text', _('Total'),None,style_yellow_bold),
            ]
            
        elif not data['form']['hide_period'] and data['form']['detailed_report']:
            c_specs = [
                ('partners', 1, 0, 'text', _('Partner'),None,style_yellow_bold),
                ('payment_term',1,0,'text',_('Invoice No'),None,style_yellow_bold),
                ('due',1,0,'text',_('Due Date'),None,style_yellow_bold),
                ('od30', 1, 0, 'text', _('Not Due'),None,style_yellow_bold),
                ('od60', 1, 0, 'text', _(data['form']['4']['name']),None,style_yellow_bold),
                ('od90', 1, 0, 'text',_(data['form']['3']['name']),None,style_yellow_bold),
                ('od120', 1, 0, 'text',_(data['form']['2']['name']),None,style_yellow_bold),
                ('older', 1, 0, 'text',_(data['form']['1']['name']),None,style_yellow_bold),
                ('balance', 1, 0, 'text', _(data['form']['0']['name']),None,style_yellow_bold),
                ('coments', 1, 0, 'text', _('Total'),None,style_yellow_bold),
            ]
            
        else:
            c_specs = [
                       ('partners', 1, 0, 'text', _('Partner'),None,style_yellow_bold),
                       ('payment_term',1,0,'text',_('Payment Term'),None,style_yellow_bold),
                       ('due', 1, 0, 'text', _('Not Due'),None,style_yellow_bold),
                       ('od30', 1, 0, 'text',_(data['form']['4']['name']),None,style_yellow_bold),
                       ('od60', 1, 0, 'text',_(data['form']['3']['name']),None,style_yellow_bold),
                       ('od90', 1, 0, 'text',_(data['form']['2']['name']),None,style_yellow_bold),
                       ('od120', 1, 0, 'text',_(data['form']['1']['name']),None,style_yellow_bold),
                       ('older', 1, 0, 'text',_(data['form']['0']['name']),None,style_yellow_bold),
                       ('balance', 1, 0, 'text', _('Total'),None,style_yellow_bold),
                       ('coments', 1, 0, 'text', _('Comments'),None,style_yellow_bold),
                       ('payment_next_Action_date',1,0,'text',_('Next Action Date'),None,style_yellow_bold),
            ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, row_style=style_yellow_bold)
        return row_position


    def print_inlines(self, row_position, account, line,_p, data, line_number): # Fill in rows of invoice line
        # Mako: <div class="act_as_row lines ${line.get('is_from_previous_periods') and 'open_invoice_previous_line' or ''} ${line.get('is_clearance_line') and 'clearance_line' or ''}">
        if line.get('is_from_previous_periods') or line.get('is_clearance_line'):
            style_line_default = style_default_italic
            style_line_right = style_right_italic
            style_line_date = style_date_italic
            style_line_decimal = style_decimal_italic
        else:
            style_line_default = style_default
            style_line_right = style_right
            style_line_date = style_date
            style_line_decimal = style_decimal

        c_specs = [
                       ('partner_name', 1, 0, 'text',line.get('partner_name')or '' ),
                       ('payment_term',1,0,'text',line.get('payment_term')or ' -'),
                       ('date_maturity', 1, 0, 'text',line.get('date_maturity')or '' ),
                       ('due', 1, 0, 'number',line.get('due')or 0.0, None,style_line_decimal ),
                       ('od30',1,0,'number',line.get('od30') or 0.0, None,style_line_decimal),
                       ('od60',1,0,'number',line.get('od60') or 0.0, None,style_line_decimal),
                       ('od90',1,0,'number',line.get('od90') or 0.0, None,style_line_decimal),
                       ('od120',1,0,'number',line.get('od120') or 0.0, None,style_line_decimal),
                       ('older',1,0,'number',line.get('older') or 0.0, None,style_line_decimal),
                       ('balance', 1, 0, 'number', line.get('balance') or 0.0, None, style_line_decimal),
                    ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, style_line_default)
        return row_position


    def print_header(self, row_position, account, _p, data, line_number): # Fill in rows of invoice line
        # Mako: <div class="act_as_row lines ${line.get('is_from_previous_periods') and 'open_invoice_previous_line' or ''} ${line.get('is_clearance_line') and 'clearance_line' or ''}">
        if account.get('is_from_previous_periods') or account.get('is_clearance_line'):
            style_line_default = style_default_italic
            style_line_right = style_right_italic
            style_line_date = style_date_italic
            style_line_decimal = style_decimal_italic
        else:
            style_line_default = style_default
            style_line_right = style_right
            style_line_date = style_date
            style_line_decimal = style_decimal

        c_specs = [
                       ('partner_name', 1, 0, 'text',account.get('name')or '' ),
                       ('payment_term',1,0,'text',''),
                       ('date_maturity',1,0,'text',''),
                       ('due',1,0,'text',''),
                       ('od30',1,0,'text',''),
                       ('od60',1,0,'text',''),
                       ('od90',1,0,'text',''),
                       ('od120',1,0,'text',''),
                       ('older',1,0,'text',''),
                       ('balance', 1, 0, 'text',''),
                    ]
        
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, style_line_default)
        return row_position

    def print_lines(self, row_position, account, line,_p, data, line_number): # Fill in rows of invoice line
        if line.get('is_from_previous_periods') or line.get('is_clearance_line'):
            style_line_default = style_default_italic
            style_line_right = style_right_italic
            style_line_date = style_date_italic
            style_line_decimal = style_decimal_italic
        else:
            style_line_default = style_default
            style_line_right = style_right
            style_line_date = style_date
            style_line_decimal = style_decimal
        
        c_specs = [
                       ('partner_name', 1, 0, 'text',line.get('partner_name')or ''),
                       ('payment_term',1,0,'text',line.get('payment_term')or ' -'),
                       ('date_maturity',1,0,'text',line.get('date_maturity') or '-'),
                       ('due',1,0,'number',line.get('due') or 0.0, None,style_line_decimal),
                       ('od30',1,0,'number',line.get('od30') or 0.0, None,style_line_decimal),
                       ('od60',1,0,'number',line.get('od60') or 0.0, None,style_line_decimal),
                       ('od90',1,0,'number',line.get('od90') or 0.0, None,style_line_decimal),
                       ('od120',1,0,'number',line.get('od120') or 0.0, None,style_line_decimal),
                       ('older',1,0,'number',line.get('older') or 0.0, None,style_line_decimal),
                       ('balance', 1, 0, 'number', line.get('balance') or 0.0, None, style_line_decimal),
                    ]
            
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_position = self.xls_write_row(ws, row_position, row_data, style_line_default)
        return row_position

    def print_ledger_lines(self, row_pos, lines_data, _xs, xlwt, _p, data): # export the invoice AR/AP lines
            import datetime
            import operator
            
            row_start_account = row_pos

            row_start_account = row_pos
            res_obj = self.pool.get('ir.property')

            row_pos = self.print_empty_row(row_pos)
            row_pos = self.print_columns_title(_p, data, row_pos)

            line_number=1
            for acc in lines_data:
                line_number = 0
                balance=0
                row_pos_start = row_pos
                row_pos=self.print_header(row_pos, acc, _p, data, line_number)
                line_number+=1
                
                # Sorting all the Lines by date..................
                inlines=sorted( acc['inlines'], key = operator.itemgetter('invoice_date') )
                
                for detail in inlines:
                    inline={}
                    inline['partner_name']=datetime.datetime.strptime(detail['invoice_date'], '%Y-%m-%d').strftime('%d-%m-%Y')                     
                    inline['payment_term']=detail['invoice_no']
                    if detail['date_maturity']:
                        inline['date_maturity']=datetime.datetime.strptime(detail['date_maturity'], '%Y-%m-%d').strftime('%d-%m-%Y')
                    inline['due']=detail['due']                    
                    inline['od30']= detail[str(4)]
                    inline['od60']= detail[str(3)]
                    inline['od90']= detail[str(2)]
                    inline['od120']= detail[str(1)]
                    inline['older']= detail[str(0)]
                    inline['balance']=detail['result']
                    row_pos_start = row_pos
                    row_pos = self.print_inlines(row_pos, acc, inline, _p, data, line_number)
                    line_number += 1
                line={}
                line['balance'] = acc['total']
                line['partner_name'] = acc['name']
                line['payment_term']=acc['payment_term']        #data['form']['payment_info'][p_id]['payment_term']
                line['due']= acc['direction']
                line['od30']= acc[str(4)]
                line['od60']= acc[str(3)]
                line['od90']= acc[str(2)]
                line['od120']= acc[str(1)]
                line['older']= acc[str(0)]
                row_pos_start = row_pos
                row_pos = self.print_lines(row_pos, acc, line, _p, data, line_number)
                line_number += 1
            return row_pos

        ########### Printing Multi Select Values .................
    def _get_lines(self,data,form):
        self.total_account = []
        obj_move = self.pool.get('account.move.line')
        ctx = form.get('used_context', {})
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        self.direction_selection = form.get('direction_selection', 'past')
        self.target_move = form.get('target_move', 'all')
        self.date_from = form.get('date_from', time.strftime('%Y-%m-%d'))
        if (form['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (form['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']

        res = []
        move_state = ['draft','posted']

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


    def get_lines(self,data,form):
#        print "Getlines Data :::", data
#        print "Get Lines Form :::", form
        self.total_account = []
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

        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
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
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,))
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
            if form[str(i)]['start'] and form[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'

                args_list += (form[str(i)]['start'], form[str(i)]['stop'])
            elif form[str(i)]['start']:
                dates_query += ' > %s)'
                args_list += (form[str(i)]['start'],)
            else:
                dates_query += ' < %s)'
                args_list += (form[str(i)]['stop'],)
            args_list += (self.date_from,)
            self.cr.execute('''SELECT l.partner_id, SUM(l.debit-l.credit)
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                        AND (am.state IN %s)
                        AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND ((l.reconcile_id IS NULL)
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

        history_records = []
        for i in range(5):
                args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
                dates_query = '(COALESCE(l.date_maturity,l.date)'
                if form[str(i)]['start'] and form[str(i)]['stop']:
                    dates_query += ' BETWEEN %s AND %s)'
                    args_list += (form[str(i)]['start'], form[str(i)]['stop'])
                elif form[str(i)]['start']:
                    dates_query += ' > %s)'
                    args_list += (form[str(i)]['start'],)
                else:
                    dates_query += ' < %s)'
                    args_list += (form[str(i)]['stop'],)
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

            # Connnect to ir.property table to return the Values for the Payment Term................
            self.cr.execute("select value_reference from ir_property where name='property_payment_term' and res_id='res.partner,%s'    "%partner['id'])
            payment_term_val=self.cr.dictfetchall()
            if payment_term_val:
                payment_term_val=payment_term_val[0]

                self.cr.execute('select name from account_payment_term where id=%s'%payment_term_val['value_reference'].split(',')[-1])
                payment_term = self.cr.dictfetchall()[0]
                values['payment_term']=payment_term['name']
            else:
                values['payment_term']=""
            self.cr.execute('select payment_note,payment_next_action_date from res_partner where id=%s'%partner['id'])
            comments=self.cr.dictfetchall()[0]
            id=partner['id']
            values['id']=id
            values['comments']=comments['payment_note']
            values['next_action']=comments['payment_next_action_date']
            
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


#### Added Functions From Acount Partner Balance................................

    def generate_xls_report(self, _p, _xs, data, objects, wb): # main function
        # Initializations
        _p.update({'report_name':'Aged Partner Balance'})
        self.global_initializations(wb,_p, xlwt, _xs, objects, data)
        row_pos = 0

        row_pos = self.print_title(_p, row_pos)

        ws.set_horz_split_pos(row_pos)

        lines_data=[]

        if data['form']['hide_period']==True:
                lines_data=list(self._get_lines(data,data['form']))
        else:
            lines_data = list(self.get_lines(data,data['form']))

        row_pos = self.print_ledger_lines(row_pos, lines_data , _xs, xlwt, _p, data)
        row_pos += 1

open_invoices_detail_xls('report.account.new_account_report_aged_partner_balance_detail_xls', 
                         'account.account', 
                         parser=new_aged_trial_report)
