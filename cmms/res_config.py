# -*- coding: utf-8 -*-
################################################################################
#
# Computerized maintenance management system (CMMS) module,
# Copyright (C) 
#    2015 - Ait-Mlouk Addi , (http://odoo-services.esy.es/)-- aitmlouk@gmail.com --
#    
# CMMS module is free software: you can redistribute
# it and/or modify it under the terms of the Affero GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# CMMS module is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the Affero GNU
# General Public License for more details.
#
# You should have received a copy of the Affero GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import time
import datetime
from openerp.tools.translate import _
from openerp.osv import fields, osv


class cmms_parameter_mail(osv.osv):

    _name='cmms.parameter.mail'
    _description=u"Paramètre du serveur"
    _columns = {
            'name' : fields.char(u'Type',size=50,required=True),
            'server' : fields.many2one('ir.mail_server',u'Serveur d\'envoi'),
            'mail_from' : fields.char(u'addresse d\'expéditeur',size=100),
            'module' : fields.char(u'Module',size=100),
            'is_param' : fields.boolean(u'Paramètre'),
            }
    
    _defaults = {  
        'is_param': lambda *a: False,
        }
    
    def get_value_by_reference(self,cr,uid,module,reference_param,context={}):
        u"""récupère la valeur du paramètre"""
        if reference_param:
            object_model_data=self.pool.get('ir.model.data')
            if object_model_data:
                param_id = False
                param_model, param_id = object_model_data.get_object_reference(cr, uid, module, reference_param)
                if param_id:
                    object_param=self.browse(cr,uid,param_id)
                    if object_param:
                        return [object_param.server and object_param.server.id or False,object_param.mail_from or object_param.server.smtp_user]
        return []
    
    def create(self, cr, user, vals, context=None):
        u"""méthode de création"""
        flag_travel = vals.get('is_param',False)
        if flag_travel:
            return super(cmms_parameter_mail, self).create(cr, user, vals, context)  
        else:
            raise osv.except_osv(_(u'Création impossible'), _(u'Vous ne pouvez pas créer de paramètres, ils sont définis nativement'))

    def copy(self, cr, uid, id, default=None, context={}):
        u"""méthode de copie"""
        raise osv.except_osv(_(u'Copie impossible'), _(u'Vous ne pouvez pas copier de paramètres, ils sont définis nativement'))

    def unlink(self, cr, uid, ids, context=None):
        u"""méthode de suppression"""
        raise osv.except_osv(_(u'Suppression impossible'), _(u'Vous ne pouvez pas supprimer de paramètres, ils sont définis nativement'))
    
    def send_email(self,cr,uid,data_emails,sender=False,server=False,partner=False,module=False,param=False,auto_commit=False):
        mail_server = False
        mail_from = False
        ids_mail = []
        mail_data_server = self.get_value_by_reference(cr,uid,module,param)
        if mail_data_server:
            mail_server,mail_from = mail_data_server
            
        for mail in data_emails:
            ids_mail.append(self.pool.get('mail.mail').create(cr,uid,{
                                                         'mail_server_id' : mail_server,
                                                         'subject' : mail['subject'],
                                                         'date' : time.strftime('%Y-%m-%d %H:%M:%S'),
                                                         'email_from' : sender or mail_from,
                                                         'email_to' : mail['email_to'],
                                                         'body_html' : mail['body_html'] or False,
                                                         }))
        self.pool.get('mail.mail').send(cr, uid, ids_mail, auto_commit)
        return True
    
cmms_parameter_mail()

class cmms_parameter_option(osv.osv):

    _name='cmms.parameter.option'
    _description=u"Paramètres"
    _columns = {
            'name' : fields.char(u'Type',size=180,required=True,readonly=True),
            'value' : fields.boolean(u'réponse'),
            'is_param' : fields.boolean(u'Paramètre'),
            'module' : fields.char(u'Module',size=100),
            }
    
    _defaults = {  
        'is_param': lambda *a: False,
        }
    
    def get_value_by_reference(self,cr,uid,module,reference_param,context={}):
        u"""récupère la valeur du paramètre"""
        if reference_param:
            object_model_data=self.pool.get('ir.model.data')
            if object_model_data:
                param_id = False
                param_model, param_id = object_model_data.get_object_reference(cr, uid, module, reference_param)
                if param_id:
                    object_param=self.browse(cr,uid,param_id)
                    if object_param:
                        return object_param.value or False
        return False
    
    def create(self, cr, user, vals, context=None):
        u"""méthode de création"""
        flag_travel = vals.get('is_param',False)
        if flag_travel:
            return super(cmms_parameter_option, self).create(cr, user, vals, context)  
        else:
            raise osv.except_osv(_(u'Création impossible'), _(u'Vous ne pouvez pas créer de paramètres, ils sont définis nativement'))

    def copy(self, cr, uid, id, default=None, context={}):
        u"""méthode de copie"""
        raise osv.except_osv(_(u'Copie impossible'), _(u'Vous ne pouvez pas copier de paramètres, ils sont définis nativement'))

    def unlink(self, cr, uid, ids, context=None):
        u"""méthode de suppression"""
        raise osv.except_osv(_(u'Suppression impossible'), _(u'Vous ne pouvez pas supprimer de paramètres, ils sont définis nativement'))
    
cmms_parameter_option()

class cmms_config_settings(osv.osv_memory):
    _name = 'cmms.config.settings'
    _inherit = 'res.config.settings'
    
    def create(self,cr,uid,vals,context={}):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid,'cmms','cmms_event_mail')
        if res and res[1]:
            if 'server_cmms' in vals:
                self.pool.get('cmms.parameter.mail').write(cr,uid,res[1],{'server' : vals['server_cmms']})
        return super(cmms_config_settings,self).create(cr,uid,vals,context)
    
    def _get_server_evaluation(self,cr,uid,context={}):
        res=False
        try:
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid,'cmms','cmms_event_mail')
            if res and res[1]:
                data_read = self.pool.get('cmms.parameter.mail').read(cr,uid,res[1],['server'])
                if data_read:
                    return data_read['server'] and data_read['server'][0] or False
        except:
            pass
        return False
        
    _columns = {
        'server_cmms' : fields.many2one('ir.mail_server',u'CMMS Server'),
    }
    
    _defaults = {  
        'server_cmms' : _get_server_evaluation,
        }
    
cmms_config_settings()

