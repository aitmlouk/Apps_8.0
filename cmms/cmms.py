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
from openerp.osv import fields, osv, orm
import datetime
from dateutil.relativedelta import *
import time


class cmms_line(osv.osv):
    _name = 'cmms.line'
    _description = 'Production line'
    _inherit = ['mail.thread','ir.needaction_mixin']
    _columns = {
        'name': fields.char('Production line', size=64, required=True),
        'code': fields.char('Line reference', size=64),
        'location': fields.char('Location', size=64),
        'sequence': fields.integer('Sequence'),
    }

cmms_line()

class cmms_equipment(osv.osv):
    _name = "cmms.equipment"
    _description = "equipment"
    _inherit = ['mail.thread','ir.needaction_mixin']
    
    def create(self, cr, user, vals, context=None):
        if ('type' not in vals) or (vals.get('type')=='/'):
            vals['type'] = self.pool.get('ir.sequence').get(cr, user, 'cmms.equipment')
        return super(cmms_equipment, self).create(cr, user, vals, context)
    
    def _count_all(self, cr, uid, ids, field_name, arg, context=None):
        Logintervention = self.pool['cmms.intervention']
        Logpm = self.pool['cmms.pm']
        Logcm = self.pool['cmms.cm']
        Logorder = self.pool['cmms.incident']
        return {
            equipment_id: {
                'pm_count': Logpm.search_count(cr, uid, [('equipment_id', '=', equipment_id)], context=context),
                'cm_count': Logcm.search_count(cr, uid, [('equipment_id', '=', equipment_id)], context=context),
                'order_count': Logorder.search_count(cr, uid, [('equipment_id', '=', equipment_id)], context=context),
                'intervention_count': Logintervention.search_count(cr, uid, [('equipment_id', '=', equipment_id)], context=context)
                
            }
            for equipment_id in ids
        }
    
    def return_action_to_open(self, cr, uid, ids, context=None):
        """ This opens the xml view specified in xml_id for the current machine """
        if context is None:
            context = {}
        if context.get('xml_id'):
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'cmms', context['xml_id'], context=context)
            res['context'] = context
            res['context'].update({'default_equipment_id': ids[0]})
            res['domain'] = [('equipment_id','=', ids[0])]
            return res
        return False
    

    _columns = {
        'type': fields.char('Unit of work reference', size=64),
        'name': fields.char('Name', size=64 , required=True),
        'trademark': fields.char('Trademark', size=64),
        'active' : fields.boolean('Active'),
        'local_id': fields.many2one('stock.location', 'Location'),
        'line_id': fields.many2one('cmms.line','Production line', required=True, change_default=True),
        'invoice_id': fields.many2one('account.invoice', 'Purchase invoice'),
        'startingdate': fields.datetime("Starting date"),
        'product_ids': fields.many2many('product.product','product_equipment_rel','product_id','equipment_id','Piece of change'),
        'deadlinegar': fields.datetime("Deadline of guarantee"),
        'description': fields.text('Unit of work reference'),
        'safety': fields.text('Safety instruction'),
        'intervention_id': fields.one2many('cmms.intervention','equipment_id', 'Interventions'),
        'cm_id': fields.one2many('cmms.cm','equipment_id', 'Maintenance Corrective '),
        'pm_id': fields.one2many('cmms.pm','equipment_id', 'Maintenance Preventive'),
        'user_id': fields.many2one('res.users', 'Manager'),
        'photo': fields.binary('Photo'),
        'intervention_count': fields.function(_count_all, type='integer', string='Intervention', multi=True),
        'pm_count': fields.function(_count_all, type='integer', string='Preventive maintenance', multi=True),
        'cm_count': fields.function(_count_all, type='integer', string='Corrective maintenance', multi=True),
        'order_count': fields.function(_count_all, type='integer', string='Work Order', multi=True),
    }
    _defaults = {
        'active' : lambda *a: True,
        'user_id': lambda object,cr,uid,context: uid,
        'type': lambda self, cr, uid, context: '/',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        default = default.copy()
        default['type'] = self.pool.get('ir.sequence').get(cr, uid, 'cmms.equipment')
        return super(cmms_equipment, self).copy(cr, uid, id, default=default, context=context)
    
cmms_equipment()


class cmms_intervention(osv.osv):
    _name = "cmms.intervention"
    _description = "Intervention request"
    _inherit = ['mail.thread','ir.needaction_mixin']

    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'cmms.intervention')
        return super(cmms_intervention, self).create(cr, user, vals, context)
    
    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'done'})
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'cancel'})
    
    def action_draft(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'draft'})

    _columns = {
        'name': fields.char('Intervention reference', size=64),
        'equipment_id': fields.many2one('cmms.equipment', 'Unit of work', required=True),
        'date': fields.datetime('Date'),
        'user_id': fields.many2one('res.users', 'Sender', readonly=True),
        'user2_id': fields.many2one('res.users', 'Recipient'),
        'priority': fields.selection([('normal','Normal'),('low','Low'),('urgent','Urgent'),('other','Other')],'priority', size=32),
        'observation': fields.text('Observation'),
        'motif': fields.text('Motif'),
        'date_inter': fields.datetime('Intervention date'),
        'date_end': fields.datetime('Intervention end date'),
        'type': fields.selection([('check','Check'),('repair','Repair'),('revision','Revision'),('other','Other')],'Intervention type', size=32),
        'state_machine': fields.selection([('start','En Marche'),('stop','En Arret')],'Etat de machine', size=32),
        'state' : fields.selection([('draft',u'En cours'),('done',u'Validé'),('cancel',u'Annulé')],u'Statut',required=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'type': lambda * a:'repair',
        'priority': lambda * a:'normal',
        'user_id': lambda object,cr,uid,context: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': lambda self, cr, uid, context: '/',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        if default is None:
            default = {}
            default = default.copy()
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cmms.intervention')
        return super(cmms_intervention, self).copy(cr, uid, id, default=default, context=context)
    
    """email"""
    def action_broadcast(self,cr,uid,ids,context={}):
        data_email = []
        text_inter = u"""<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: rgb(255, 255, 255); ">
                <p>Bonjour %s, </p>
                <p>Nous vous informons que vous êtes attribué a l'intervention %s de l'émetteur  %s.</p>
                <br/>
                <p></p>
                <p>-----------------------------</p>
                <p>Référence intervention  : %s </p>
                <p>Type d'intervention : %s </p>
                <p>Machine : %s </p>
                <p>Date du debut : %s </p>
                <p>Date de fin d'intervention : %s </p>
                <p>Priorité  : %s </p>
                <p>Etat de machine  : %s </p>
                <p>Motif d'intervention  : %s </p>
                <p>------------------------------</p>
                <p> Service du Gmao</p>
                </div>
                """
        for object_inter in self.browse(cr,uid,ids):
            if not object_inter.user2_id.login:
                raise osv.except_osv(u'Email non spécifiée', u'Veuillez indiquer l\'email de Destinataire')
            if object_inter.user2_id.login:
                    text_inter = text_inter %(
                                                       object_inter.user2_id.name,
                                                       object_inter.name,object_inter.user_id.name,
                                                       object_inter.name,
                                                       object_inter.type,
                                                       object_inter.equipment_id.name,
                                                       object_inter.date_inter,
                                                       object_inter.date_end,
                                                       object_inter.priority,
                                                       object_inter.state_machine,
                                                       object_inter.motif,
                                                      
                                                       )
                    data_email.append(
                                {
                                'subject' : "Service du Gmao %s" %object_inter.name,
                                'email_to' : object_inter.user2_id.name,
                                'subtype' : 'html',
                                'body_text' : False,
                                'body_html' : text_inter,
                                }
                            )
                                   
        self.pool.get('cmms.parameter.mail').send_email(cr,uid,data_email,module='cmms',param='cmms_event_mail')      
        
"""fin"""


cmms_intervention()

AVAILABLE_PRIORITIES = [
    ('3','Normal'),
    ('2','Low'),
    ('1','High')
]

class cmms_request_link(osv.osv):
    _name = 'cmms.request.link'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'object': fields.char('Object', size=64, required=True),
        'priority': fields.integer('Priority'),
    }
    _defaults = {
        'priority': lambda *a: 5,
    }
    _order = 'priority'

cmms_request_link()

class cmms_incident(osv.osv):
    _name = "cmms.incident"
    _description = "Incident" 
    _inherit = ['mail.thread','ir.needaction_mixin']
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'cmms.incident')
        return super(cmms_incident, self).create(cr, user, vals, context)

    def _links_get(self, cr, uid, context={}):
        obj = self.pool.get('cmms.request.link')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['object', 'name'], context)
        return [(r['object'], r['name']) for r in res]
    
    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'done'})
    
    def action_cancel(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'cancel'})
    
    def action_draft(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'draft'})

    _columns = {
        'name':fields.char('Work order reference',size=64),
        'state' : fields.selection([('draft',u'En cours'),('done',u'Validé'),('cancel',u'Annulé')],u'Statut',required=True),
        'priority': fields.selection(AVAILABLE_PRIORITIES, 'Priority'),
        'user_id': fields.many2one('res.users', 'Manager', readonly=True),
        'date': fields.datetime('Work order date'),
        'active' : fields.boolean('Active?'),
        'ref' : fields.reference('Work order source', selection=_links_get, size=128),
        'equipment_id': fields.many2one('cmms.equipment', 'Unit of work', required=True),
        'archiving3_ids': fields.one2many('cmms.archiving3', 'incident_id', 'follow-up history'),
    }
    _defaults = {
        'active': lambda * a:True,
        'name': lambda self, cr, uid, context: '/',
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'priority': lambda *a: AVAILABLE_PRIORITIES[2][0],
        'user_id': lambda object,cr,uid,context: uid,
        'state': lambda * a:'draft',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not context:
            context = {}
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cmms.incident')
        return super(cmms_incident, self).copy(cr, uid, id, default=default, context=context)

cmms_incident()

class cmms_archiving3(osv.osv):
    _name = "cmms.archiving3"
    _description = "Incident follow-up history"
    _columns = {
        'name': fields.char('Objet', size=32, required=True),
        'date': fields.datetime('Date'),
        'description': fields.text('Description'),
        'incident_id': fields.many2one('cmms.incident', 'Incident',required=True),
        'user_id': fields.many2one('res.users', 'Manager', readonly=True),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda object,cr,uid,context: uid,
    }

cmms_archiving3()


class cmms_pm(osv.osv):
    _name = "cmms.pm"
    _description = "Preventive Maintenance System"
    _inherit = ['mail.thread','ir.needaction_mixin']
    
    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context):
        res = self.name_get(cr, uid, ids, context)
        return dict(res)
    
    def _days_next_due(self, cr, uid, ids, prop, unknow_none, context):
        if ids:
            reads = self.browse(cr, uid, ids, context)
            res = []
            for record in reads:
                if (record.meter == "days"):
                    interval = datetime.timedelta(days=record.days_interval)
                    last_done = record.days_last_done
                    last_done = datetime.datetime.fromtimestamp(time.mktime(time.strptime(last_done, "%Y-%m-%d")))
                    next_due = last_done + interval
                    res.append((record.id, next_due.strftime("%Y-%m-%d")))
                else:
                    res.append((record.id, False))
            return dict(res)
    
    def _days_due(self, cr, uid, ids, prop, unknow_none, context):
        if ids:
            reads = self.browse(cr, uid, ids, context)
            res = []
            for record in reads:
                if (record.meter == "days"):
                    interval = datetime.timedelta(days=record.days_interval)
                    last_done = record.days_last_done
                    last_done = datetime.datetime.fromtimestamp(time.mktime(time.strptime(last_done, "%Y-%m-%d")))
                    next_due = last_done + interval
                    NOW = datetime.datetime.now()
                    due_days = next_due - NOW
                    res.append((record.id, due_days.days))
                else:
                    res.append((record.id, False))
            return dict(res)

    def _get_state(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        if ids:
            reads = self.browse(cr, uid, ids, context)
            for record in reads:    
                if record.meter == u'days':
                    if record.days_left <= 0:
                        res[record.id] = u'Dépassé'
                    elif record.days_left <= record.days_warn_period:
                        res[record.id] = u'Approché'
                    else:
                        res[record.id] = u'OK'
            return res

    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'cmms.pm')
        return super(cmms_pm, self).create(cr, user, vals, context)
    
    _columns = {
        'name':fields.char('Ref PM',size=20, required=True),
        'equipment_id': fields.many2one('cmms.equipment', 'Unit of work', required=True),
        'meter':fields.selection([ ('days', 'Days')], 'Unit of measure'),
        'recurrent':fields.boolean('Recurrent ?', help="Mark this option if PM is periodic"),
        'days_interval':fields.integer('Interval'),
        'days_last_done':fields.date('Begun the',required=True),
        'days_next_due':fields.function(_days_next_due, method=True, type="date", string='Next date'),
        'days_warn_period':fields.integer('Warning date'),
        'user_id': fields.many2one('res.users', 'Chef'),
        'days_left':fields.function(_days_due, method=True, type="integer", string='Staying days'),
        'state':fields.function(_get_state, method=True, type="char", string='Status')
    }
    _defaults = {
        'meter': lambda * a: 'days',
        'recurrent': lambda * a: True,
        'days_last_done': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': lambda self, cr, uid, context: '/',
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
            default = default.copy()
            default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cmms.pm')
        return super(cmms_pm, self).copy(cr, uid, id, default=default, context=context)
cmms_pm()

class cmms_archiving2(osv.osv):
    _name = "cmms.archiving2"
    _description = "PM follow-up history"
    _columns = {
        'name': fields.char('effect', size=32, required=True),
        'date': fields.datetime('Date'),
        'description': fields.text('Description'),
        'pm_id': fields.many2one('cmms.pm', 'Archiving',required=True),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

cmms_archiving2()

CHOICE = [
    ('yes','Yes'),
    ('no','No'),
]

class cmms_checklist(osv.osv):
    _name="cmms.checklist"
    _description= "checklist"
    _columns={
        'name': fields.char("Title",size=128, required=True),
        'description': fields.text('Description'), 
        'questions_ids': fields.one2many("cmms.question","checklist_id","Questions",),
        'equipment_id': fields.many2one('cmms.equipment', 'Equipment'),
        }
cmms_checklist()

class cmms_question(osv.osv):
    _name = "cmms.question"
    _description = "Question"
    _columns = {
        'name': fields.char("Question",size=128, required=True),
        'checklist_id': fields.many2one('cmms.checklist', 'Checklist', required=True), 
    }
cmms_question()

class cmms_checklist_history(osv.osv):
    _name="cmms.checklist.history"
    _description= "Checklist History"
    _inherit = ['mail.thread','ir.needaction_mixin']
    
    def onchange_checklist_id(self, cr, uid, ids, id, context={}):
        liste = self.pool.get('cmms.question').search(cr, uid, [('checklist_id', '=', id)])
        enrs = self.pool.get('cmms.question').name_get(cr, uid, liste)
        res = []
        for id, name in enrs:
            obj = {'name': name}
            res.append(obj)
        return {'value':{'answers_ids': res}}
    
    def create(self, cr, uid, vals, context=None):
        for i, obj in enumerate(vals['answers_ids']):
            vals['answers_ids'][i] = [0,0,vals['answers_ids'][i][2]]
        return osv.osv.create(self, cr, uid, vals, context=context)
    
    def action_done(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'done'})
    
    def action_confirmed(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'confirmed'})
    
    def action_draft(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state' : 'draft'})
    
    _columns={
        'name': fields.char("Checklist name",size=128, required=True),
        'checklist_id': fields.many2one('cmms.checklist', 'Checklist'), 
        'answers_ids': fields.one2many("cmms.answer.history","checklist_history_id","Responses"),
        'date_planned': fields.datetime("Planned date"), 
        'date_end': fields.datetime("End date"), 
        'equipment_id': fields.many2one('cmms.equipment', 'Unit of work'),
        'user_id': fields.many2one('res.users', 'Manager'),
        'state': fields.selection([('draft', 'Brouillon'), ('confirmed', 'Confirmé'),('done', 'Validé')], "Status"),
        }
    _defaults = {
        'state' : lambda *a: 'draft',
        'user_id': lambda object,cr,uid,context: uid,
    }
    
cmms_checklist_history()

class cmms_question_history(osv.osv):
    _name="cmms.answer.history"
    _description= "Answers"
    _columns={    
        'name': fields.char("Question",size=128, required=True),
        'checklist_history_id': fields.many2one('cmms.checklist.history', 'Checklist'),
        'answer': fields.selection(CHOICE, "response"),
        'detail': fields.char("Detail",size=128),
    }
    
cmms_question_history()

class cmms_failure(osv.osv):
    _name = "cmms.failure"
    _description = "failure cause"
    _columns = {
        'name': fields.char('Type of failure', size=32, required=True),
        'code': fields.char('Code', size=32),
        'description': fields.text('failure description'),
    }

cmms_failure()

class cmms_cm(osv.osv):
    _name = "cmms.cm"
    _description = "Corrective Maintenance System"
    _inherit = ['mail.thread','ir.needaction_mixin']

    _columns = {
        'name': fields.char('CM reference',size=20),
        'equipment_id': fields.many2one('cmms.equipment', 'Unit of work', required=True),
        'failure_id': fields.many2one('cmms.failure', 'Failure?'),
        'date': fields.datetime('Date'),
        'note': fields.text('Notes'),
        'user_id': fields.many2one('res.users', 'Chef'),
        'diagnosistab_ids': fields.one2many('cmms.diagnosistab', 'cm_id', 'Diagnosis Table'),
    }
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda object,cr,uid,context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        #netsvc.Logger().notifyChannel("[HNM]["+__name__+"][create]", netsvc.LOG_DEBUG,"vals:%s" % (vals,))
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cmms.cm')
        return super(cmms_cm, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'cmms.cm')
        return super(cmms_cm, self).copy(cr, uid, id, default=default, context=context)

cmms_cm()

class cmms_diagnosistab(osv.osv):
    _name = "cmms.diagnosistab"
    _description = "Diagnosis List"
    _columns = {
        'name': fields.char('Failure causes', size=32, required=True),
        'solution': fields.text('Solution'),
        'cm_id': fields.many2one('cmms.cm', 'Corrective Maintenance'),
    }

cmms_diagnosistab()

class cmms_archiving(osv.osv):
    _name = "cmms.archiving"
    _description = "CM follow-up History"
    _columns = {
        'name': fields.char('effect', size=32, required=True),
        'date': fields.datetime('Date'),
        'description': fields.text('Description'),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

cmms_archiving()

