odoo.define('web_toggle_sidebar.Leftbar', function (require) {
    "use strict";
    var WebClient = require('web.WebClient');

    WebClient.include({
        events: _.extend({}, WebClient.prototype.events, {
            'click .o_sub_menu .o_toggle_icon': '_onToggleClicked',
        }),
        _onToggleClicked: function () {
            this.$el.toggleClass('leftbar_close');
            this.$('.o_toggle_icon i').toggleClass('fa-chevron-left, fa-chevron-right');
        },
    });
});