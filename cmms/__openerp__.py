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
{
    "name": "CMMS",
    "version": "1.0",
    "depends": ["base", "product", "stock", "account", "mail"],
    "author": "Ait-Mlouk Addi",
    'website': 'http://www.aitmlouk-addi.info/',
    'sequence':1,
    "category": "Specific Modules/CMMS",
    'icon': '/cmms/static/src/img/icon.png',
    'summary' : 'Corrective maintenance, Preventive maintenance, Intervention',
    "description": """
Computerized maintenance management system module allow you to manage 
preventives and corrective maintenance without limit.
All informations is linked to the equipment tree and let you follow 
maintenance operation :
 - Repair.
 - Check up List.
 - ...
With this module you can following all equipment type.

For more information:

 - Gmail: aitmlouk@gmail.com
 - website : http://www.aitmlouk-addi.info/

""",


    "init_xml": [],
    'update_xml': [
        'cmms_view.xml',
        'res_config_view.xml',
        'cmms_dashboard_view.xml', 
        'security/cmms_security.xml',
        'security/ir.model.access.csv',
        'data/cmms_demo.xml',
        'data/cmms_sequence.xml',
        'cmms_menu.xml',
        
        
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
