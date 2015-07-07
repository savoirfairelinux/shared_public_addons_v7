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
import unicodedata
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_aged_trial_balance(osv.osv_memory):
    _inherit="account.aged.trial.balance"

    def _get_hide_period(self, cr,uid, context):
        cr.execute("select check_payment_option from account_config_settings order by id desc")
        data= cr.fetchall()
        #print "Data Here:::",data
        if data:
            data=data[0][0]
        res=False
        if data==True:
            res=data
        #print "At Final Res here............",res
        return res


    def _get_account_config(self, cr,uid, context):
        cr.execute("select check_payment_option from account_config_settings order by id desc")
        data=cr.fetchall()
        if data:
            return data[0][0]

    def _get_period_length(self,cr,uid,context):
        cr.execute("select module_aged_by_partner_balance from account_config_settings order by id desc")
        data=cr.fetchall()
        if data:
            return data[0][0]
        

    _columns={
              'check_account_config':fields.boolean('Verify Account Configuration'),
              'detailed_report':fields.boolean('Detailed Report'),
              'hide_period':fields.boolean('Aged By Payment Terms'),
              'payment_term_id':fields.many2many('account.payment.term','trail_balance_payment_term_rel','trial_id','payment_id',"Payment Terms")
              }

    _defaults={'hide_period':_get_hide_period,
               'check_account_config':_get_account_config,
               'period_length':_get_period_length
               }

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(account_aged_trial_balance, self).pre_print_report(cr, uid, ids, data, context)
        vals = self.read(cr, uid, ids,
                         ['hide_period', 'payment_term_id','detailed_report','check_account_config'],
                         context=context)[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        # we update form with display account value
        data_new = self.pre_print_report(cursor, uid, ids, data, context=context)
        data= super(account_aged_trial_balance, self)._print_report(cursor, uid, ids, data, context=context)
        context = context or {}
        
        # Mentioning Period Names Here............
        def common_report_data_process(data,res):
                payment_obj=self.pool.get('account.payment.term.line')
                payment_name_obj=self.pool.get('account.payment.term')
                if not data_new['form']['payment_term_id']:
                        raise osv.except_osv(_('User Error!'), _('You must select atleast one Payment Term.'))

                if not data['datas']['form']['date_from']:
                        raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

                data['datas']['form'].update({'payment_term_id':data_new['form']['payment_term_id']})

                for var in data_new['form']['payment_term_id']:
                # Return Value From payment term Line Table
                    period_length = 0
                    period_id = payment_obj.search(cursor,uid,[('payment_id','=',var)])
                    period_length=payment_obj.browse(cursor,uid,period_id[0],context).days
                    #Code for Payment Item ids...
                    if period_length == 0:
                        period_length=payment_obj.browse(cursor,uid,period_id[0],context).days2
                        
                    data['datas']['form']['period_length']=period_length

                    partner_obj= self.pool.get('ir.property')
                    res_obj=self.pool.get('res.partner')

                    filter_ids = partner_obj.search(cursor, uid, [('value_reference','=',"account.payment.term,%s"%var),('name','=','property_payment_term')])
                    payment_term_ids = partner_obj.browse(cursor,uid,filter_ids,context)
                   
                    partner_list=[]
                    inner_dt={}
                    res[var]={}
                    if payment_term_ids:
                        payment_partner_list=[]
                        comments={}
                        for partner_id in payment_term_ids:
                            payment_partner_list.append(partner_id)

                            company_id = res_obj.search(cursor,uid,[('id','=',partner_id.res_id.id),('is_company','=',True),('supplier','=',False)])
                            if company_id:
                                partner_list.append(company_id[0])

                        res[var].update({'partner_id':partner_list,'payment_name':payment_name_obj.browse(cursor,uid,var,context).name})

                    # Adding Logic For Date Start & Stop For Multiple Periods
                    start = datetime.strptime(data['datas']['form']['date_from'], "%Y-%m-%d")

                    res[var]['period']={}
                    if data['datas']['form']['direction_selection'] == 'past':
                        for i in range(5)[::-1]:
                            stop = start - relativedelta(days=period_length)
                            res[var]['period'][str(i)] = {
                                'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                                'stop': start.strftime('%Y-%m-%d'),
                                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                            }
                            start = stop - relativedelta(days=1)
                    else:
                        for i in range(5):
                            stop = start + relativedelta(days=period_length)
                            res[var]['period'][str(5-(i+1))] = {
                                'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                                'start': start.strftime('%Y-%m-%d'),
                                'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                            }
                            start = stop + relativedelta(days=1)
            
                    data['datas']['form']['0']['name']=res[var]['period']['0']['name']='Older'
                    data['datas']['form']['1']['name']=res[var]['period']['1']['name']='Period-3'
                    data['datas']['form']['2']['name']=res[var]['period']['2']['name']='Period-2'
                    data['datas']['form']['3']['name']=res[var]['period']['3']['name']='Period-1'
                    data['datas']['form']['4']['name']=res[var]['period']['4']['name']='Current'

                    data['datas']['form']['multi']={}
                    data['datas']['form']['multi'].update(res)
                    if data.get('form',False):
                            data['datas']['ids']=[data['datas']['form'].get('chart_account_id',False)]
                return (data,res)

        if context.get('xls_export'):
            res={}
            # we update form with display account value
            #print "Testing Data Here::::::::::::",data_new['form']['hide_period'] , data_new['form']['detailed_report']
            if data_new['form']['hide_period']==True and data_new['form']['detailed_report']==False:
                data['report_name']='account.new_account_report_aged_partner_balance_xls'
                data['name']="Aged Partner Balance By Period Excel Report"
                data,res=common_report_data_process(data,res)
                
            # Print Report By Payment Term and Detail Report
            elif data_new['form']['hide_period']==True and data_new['form']['detailed_report']==True:
                data['report_name']='account.new_account_report_aged_partner_balance_detail_xls'
                data['name']="Detail Aged Partner Balance By Period Excel Report"
                data,res=common_report_data_process(data,res)
            
            elif data_new['form']['hide_period']==False and data_new['form']['detailed_report']==True:
                print "Hide False and Report True.....new_account_report_aged_partner_balance_detail_xls"
                data['report_name']='account.new_account_report_aged_partner_balance_detail_xls'
                data['name']="Aged Partner Balance Days Report Detail Report"
            else:
                data['report_name']='account.new_account_report_aged_partner_balance_xls'
                data['name']="Aged Partner Balance Excel Report"
        else:
            res = {}
            if data_new['form']['hide_period']==True and data_new['form']['detailed_report']==False:
                data['report_name']='new_aged_trial_balance'
                data['name']="Aged Partner Balance By Period"
                data,res=common_report_data_process(data,res)
                
            # Print Report By Payment Term and Detail Report
            elif data_new['form']['hide_period']==True and data_new['form']['detailed_report']==True:
                data['report_name']='new_aged_trial_balance_detail'
                data['name']="Detail Aged Partner Balance By Period"
                data,res=common_report_data_process(data,res)
                
            elif data_new['form']['hide_period']==False and data_new['form']['detailed_report']==True:
                data['report_name']='aged_trial_report_detailed'
                data['name']="Aged Partner Balance Days Report Detail Report"
            
            else:
                data['report_name']='aged_trial_balance_detail_without_details'
                data['name']="Aged Partner Balance Days Report"
        
        return data
