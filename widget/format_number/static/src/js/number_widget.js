/*
* @Author: D.Jane
* @Email: jane.odoo.sp@gmail.com
*/
odoo.define('format_number.basic_fields', function (require) {
    "use strict";
    var core = require('web.core');

    var basic_fields = require('web.basic_fields');

    basic_fields.InputField.include({
        init: function () {
            this._super.apply(this, arguments);
            this.thousands_sep = core._t.database.parameters.thousands_sep || ',';
            this.decimal_point = core._t.database.parameters.decimal_point || '.';
            this.re = new RegExp("[^" + this.decimal_point + "-\\d]", "g");
        }
    });

    basic_fields.FieldMonetary.include({
        _onInput: function () {
            this._super();
            var self = this;
            $(this.$input).val(function (index, value) {
                var v1 = value.replace(self.re, "").replace(/\B(?=((\d{3})+(?!\d)))/g, self.thousands_sep);
                var v = v1.split(self.decimal_point);
                var re = new RegExp("\\" + self.thousands_sep, "g");
                if (v.length > 1) {
                    v = v[0] + self.decimal_point + v[1].replace(re, '');
                }

                return v
            });
        }
    });

    basic_fields.FieldFloat.include({
        _onInput: function () {
            this._super();
            var self = this;
            if(this.formatType === "float_time"){
                return;
            }
            $(this.$input).val(function (index, value) {
                var v1 = value.replace(self.re, "").replace(/\B(?=((\d{3})+(?!\d)))/g, self.thousands_sep);
                var v = v1.split(self.decimal_point);
                var re = new RegExp("\\" + self.thousands_sep, "g");
                if (v.length > 1) {
                    v = v[0] + self.decimal_point + v[1].replace(re, '');
                }

                return v
            });
        }
    });


});