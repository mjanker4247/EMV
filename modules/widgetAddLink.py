#!/usr/bin/env python 
# coding: utf8 
from gluon.html import *
from gluon.http import *
from gluon.validators import *
from gluon.sqlhtml import *
# request, response, session, cache, T, db(s) 
# must be passed and cannot be imported!

class OPTIONS_WITH_ADD_LINK:
#####################################################################################
## http://www.web2pyslices.com/slice/show/1338/options-with-add-link
#####################################################################################
    def __init__(self,**parameters):
         self.parameters=parameters
    def __del__(self): pass
    def __call__(self,field,value):
        """
        example::
            db.main.product.widget = OPTIONS_WITH_ADD_LINK(T=T, r=request, c="product")

        When the form is rendered it shows a dropbox and a "add" link
        """        

        # Create a SELECT object
        select = OptionsWidget.widget(field,value)

        # Get the parameters
        request = self.parameters["r"] 
        a = request.application
        c = self.parameters["c"]
        T = self.parameters["T"]
        f = self.parameters["f"] or None #new paremeter either None or the name of the field to use           

        requires = select.attributes["requires"]

        # If is not the "IS_IN_DB" validator then can be that the line below fails 
        # because the requires can't have "ks" object        
        try:
            # Get the field name from the foreign table from validator IS_IN_DB
            if f is None:
                field_name = requires.ks[0]
            else:
                field_name = f #use the one we specified (because there was no "ks" object)
        except AttributeError:
            return select
        else:
            # Get the id from the SELECT object that allows adding an option
            select_id = select.attributes.get('_id', None)

            id = "%(tablename)s_%(fieldname)s" % {"tablename":field._tablename,
                "fieldname":field.name}
            popup_id = "popup_%s" % id
            width = 700

            # Build the URL responsible for opening a popup window in the same screen
            url= URL(r=request, c=c, f="create_popup",
                vars=dict(title_name=field.name,field_name=field_name, 
                        select_id=select_id))


            # Create the script that add the "Add" link after the SELECT object
            add_link = A(T("Add"), 
                                    _id="add_%s" % id,
                                    _name="add_%s" % id,
                                    _href="#",
                                    _onclick=("openAjaxPopup('%(name)s',%(width)d,'%(url)s')"\
                                        % {"id": id, "name":popup_id, "width":width, "url":url}),
                                    _title="Add")

            return DIV(select, " ", add_link)

def create_popup(request, table):
    """
    Create a popup with a form to register a new record
    """

    select_id = request.vars.select_id
    form_name = "form_%(name)s" % {"name":select_id}
    field_name = request.vars.field_name

    url_ajax = URL(r=request,f='validate_popup', 
        vars=dict(form_name=form_name, select_id=select_id, field_name=field_name))

    # Build the script responsible for submiting the form via ajax
    script_submit = SCRIPT("""jQuery('#%(form)s').submit(function(){ 
        jQuery.ajax({
                 type: "POST",
                 url: "%(url_ajax)s",
                 data: jQuery("#%(form)s").serialize(),
                 success: function(msg){jQuery('#message').html(msg);} });
        return false;
        });""" %  {"form":form_name, "url_ajax":url_ajax}  )

    form = SQLFORM(table, _enctype=None, _id=form_name,_action=None, _method=None)
    return dict(form=form,script_submit=script_submit,message=DIV(_id="message")) 

def validate_popup(request, table):
    """
    Validate the data from popup 
    """

    select_id = request.vars.select_id or None
    field_name = request.vars.field_name or None
    field_value = request.vars["%s" % field_name]

    form = SQLFORM(table)

    if form.accepts(request.vars,formname=None):
        script = "$.closePopupLayer();"
        if select_id:
            script_add_option = """$("#%s").append("<option value='%s'>%s</option>");""" \
                % (select_id, form.vars.id, field_value)
            script_select_option = """$("#%s").val("%s");""" % (select_id, field_value)
        return SCRIPT(script,script_add_option,script_select_option)
    elif form.errors:
        return DIV(TABLE(*[TR("%s %s" % (k,v)) for k, v in form.errors.items()]))