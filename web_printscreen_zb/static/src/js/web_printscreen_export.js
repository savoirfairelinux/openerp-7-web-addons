odoo.define('web_printscreen_export', function (require) {
"use strict";

var core = require('web.core');
var ListView = require('web.ListView');
var ViewManager = require('web.ViewManager');
var formats = require('web.formats');
var Model = require('web.DataModel');

var QWeb = core.qweb;
var _t = core._t;

ListView.include({
    render_pager: function ($node) {
        var self = this;
        var res = this._super.apply(this, arguments);

        if (!this.$printscreen) {
            this.$printscreen = $(QWeb.render("ListView.ExportLinks", {'widget': self}));
            this.$printscreen.appendTo($node);
            this.$printscreen.find('.oe_list_button_import_excel').click(function(event) {
                event.preventDefault();
                self.export_to_excel("excel");
            });
            this.$printscreen.find('.oe_list_button_import_pdf').click(function(event) {
                event.preventDefault();
                self.export_to_excel("pdf");
            });
        }

        return res;
    },

    export_to_excel: function(export_type) {
        var self = this
        var export_type = export_type
        var view = this.getParent()
        // Find Header Element
        var header_eles = self.$el.find('.o_list_view > thead > tr')
        var header_name_list = []
        var selector_index = null;
        $.each(header_eles,function(){
            var $header_ele = $(this)
            var header_td_elements = $header_ele.find('th')
            var i = 0;
            $.each(header_td_elements, function(){
                var $header_td = $(this)
                if($header_td.hasClass('o_list_record_selector')){
                    selector_index = i;
                }
                else{
                    var text = $header_td.text().trim() || ""
                    var data_id = $header_td.attr('data-id')
                    if (text && !data_id){
                        data_id = 'group_name'
                    }
                    header_name_list.push({'header_name': text.trim(), 'header_data_id': data_id})
                }
                i++;
            });
        });
        
        //Find Data Element
        var data_eles = self.$el.find('.o_list_view > tbody > tr')
        var export_data = []
        $.each(data_eles,function(){
            var data = []
            var $data_ele = $(this)
            var is_analysis = false;
            if ($data_ele.text().trim()){
                //Find group name
                var group_th_eles = $data_ele.find('.o_group_name')
                $.each(group_th_eles,function(){
                    var $group_th_ele = $(this)
                    var text = $group_th_ele.text()
                    var is_analysis = true
                    data.push({'data': text, 'bold': true, 'is_group': true})
                });
                var data_td_eles = $data_ele.find('td')
                var i = 0;
                $.each(data_td_eles, function(){
                    if(i === selector_index){
                        i += 1;
                        return;
                    }
                    i += 1;

                    var $data_td_ele = $(this)
                    var text = $data_td_ele.text().trim() || ""
                    if ($data_td_ele && $data_td_ele[0].classList.contains('o_list_number') && !$data_td_ele[0].classList.contains('oe_list_field_float_time')){
                        text = text.split('').filter(function(char){
                            return char === ',' || char === '.' || parseInt(char) || parseInt(char) === 0;
                        }).join('');
                        text = formats.parse_value(text, {type: "float"})
                        data.push({'data': text || "", 'number': true})
                    }
                    else{
                        data.push({'data': text})
                    }
                });
                export_data.push(data)
            }
        });
        
        //Find Footer Element
        var footer_eles = self.$el.find('.o_list_view > tfoot> tr')
        $.each(footer_eles,function(){
            var data = []
            var $footer_ele = $(this)
            var footer_td_eles = $footer_ele.find('td')
            var i = 0;
            $.each(footer_td_eles,function(){
                if(i === selector_index){
                    i += 1;
                    return;
                }
                i += 1;
                var $footer_td_ele = $(this)
                var text = $footer_td_ele.text().trim() || ""
                if ($footer_td_ele && $footer_td_ele[0].classList.contains('o_list_number')){
                    text = formats.parse_value(text, { type:"float" })
                    data.push({'data': text || "", 'bold': true, 'number': true})
                }
                else{
                    data.push({'data': text, 'bold': true})
                }
            });
            export_data.push(data)
        });
        
        //Export to excel
        if (export_type === 'excel'){
             view.session.get_file({
                 url: '/web/export/zb_excel_export',
                 data: {data: JSON.stringify({
                        model : view.model,
                        headers : header_name_list,
                        rows : export_data,
                 })},
                 complete: $.unblockUI
             });
         }
         else{
            new Model("res.users").get_func("get_printscreen_report_context")(this.session.uid).then(function(res) {
                view.session.get_file({
                     url: '/web/export/zb_pdf_export',
                     data: {data: JSON.stringify({
                            uid: view.session.uid,
                            model : view.model,
                            headers : header_name_list,
                            rows : export_data,
                            company_name: res['company_name'],
                            company_logo: res['company_logo'],
                            current_date: res['current_date'],
                     })},
                     complete: $.unblockUI
                });
            });
         }
    },
});

ViewManager.include({
    switch_mode: function(view_type, no_store, view_options) {
        var export_div = this.$el.find('.oe_web_printscreen');
        if (view_type != 'list' /** && view_type != 'tree' */ ) {
            export_div.css("display", "none")
        } else {
            export_div.css("display", "")
        }

        return this._super.apply(this, arguments);
    },
});

});
