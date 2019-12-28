// -*- coding: utf-8 -*-
// © 2018 Eestisoft - Hideki Yamamoto
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
// Substantial rework of sunpop.cn 'app_dynamic_list' module to achieve compatibility with odoo 11 and 12

odoo.define('ees_columns_toggles.shcolumns', function (require) {
"use strict";

var core = require('web.core');var ListController = require('web.ListController');
ListController.include({stop_event:function(e){e.stopPropagation();},
	renderButtons:function($node){this._super.apply(this, arguments);
        this.$buttons.find('.oe_select_columns').click(this.proxy('setup_column_toggles'));
        this.$buttons.find('.oe_dropdown_btn').click(this.proxy('apply_column_toggles'));
        this.$buttons.find('.dropdown-menu').click(this.proxy('stop_event'));
    },
	setup_column_toggles:function(fields, grouped){var self=this;var getcb = document.getElementById('showcb');$(getcb).toggle();
		this.visible_columns = _.filter(this.renderer.state.fieldsInfo.list, function (column) {
			var ttext=self.renderer.state.fields[column.name].string||column.name;
            var firstcheck = document.getElementById('cv_'+ttext);
            if(firstcheck == null){var description = document.createTextNode(ttext);
            var checkbox = document.createElement("input");checkbox.id = 'cv_'+ttext;checkbox.type = "checkbox";checkbox.name = "cb";
            if(column.modifiers.column_invisible !== true){checkbox.checked=true;}else{checkbox.checked = false;}
				var li= document.createElement("li");li.appendChild(checkbox);li.appendChild(description);
				getcb.appendChild(li);
            }else{if(column.modifiers.column_invisible !== true){firstcheck.checked = true;}else{firstcheck.checked = false;}}
    }); },
	apply_column_toggles:function(){$("#showcb").hide();this._apply_column_toggles(this.renderer.state.fields, this.grouped);return this.update(this);},
	_apply_column_toggles: function (fields, grouped) {
		var self=this;self.thsvis='';
        this.visible_columns = _.filter(this.renderer.state.fieldsInfo.list, function (column) {
			var text=self.renderer.state.fields[column.name].string;
			var cbid = document.getElementById('cv_'+text);
			if(cbid !== null){var cbid = cbid.checked;
				if(cbid !== false){column.modifiers.invisible=false;column.modifiers.column_invisible=false;}
				else{column.modifiers.invisible=true;column.modifiers.column_invisible=true;}
			}return column.invisible;
		});this.aggregate_columns=_(this.visible_columns).invoke('to_aggregate');
    },	
});
$(document).click(function(){$("#showcb").hide();});});