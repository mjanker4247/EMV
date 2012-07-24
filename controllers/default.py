# coding: utf8

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

error_page=URL('error')

if not session.recent_measurement_places: session.recent_measurement_places=[]
if not session.recent_instruments: session.recent_instruments=[]

response.menu=[
  ['Measurement Places',False,url('list_measurement_places')],
  ['Instruments',False,url('list_instruments')],
]

def add(mylist,item):
    if not item.id in [x[0] for x in mylist]:
        return mylist[:9]+[(item.id,item.name)]
    else:
        return mylist

def index():
    return dict()

@auth.requires_login()
def list_measurement_places():
    form=crud.create(db.measurement_place)
    measurement_places=db(db.measurement_place.id>0).select(orderby=db.measurement_place.name)
    return dict(measurement_places=measurement_places,form=form)

@auth.requires_login()
def view_measurement_place():
    measurement_place_id=request.args(0)
    measurement_place=db.measurement_place[measurement_place_id] or redirect(error_page)
    session.recent_measurement_places = add(session.recent_measurement_places,measurement_place)
    return dict(measurement_place=measurement_place)

@auth.requires_login()
def edit_measurement_place():
    measurement_place_id=request.args(0)
    measurement_place=db.measurement_place[measurement_place_id]  or redirect(error_page)
    session.recent_measurement_places = add(session.recent_measurement_places,measurement_place)
    form=crud.update(db.measurement_place,measurement_place,next=url('list_measurement_places'))
    return dict(form=form)

@auth.requires_login()
def list_instruments():
    form=crud.create(db.instrument)
    instruments=db(db.instrument.id>0).select(orderby=db.instrument.name)
    return dict(instruments=instruments,form=form)

@auth.requires_login()
def view_instrument():
    instrument_id=request.args(0)
    instrument=db.instrument[instrument_id] or redirect(error_page)
    session.recent_instruments = add(session.recent_instruments,instrument)
    return dict(instrument=instrument)
	
@auth.requires_login()
def edit_instrument():
    instrument_id=request.args(0)
    instrument=db.instrument[instrument_id] or redirect(error_page)
    session.recent_instruments = add(session.recent_instruments,instrument)
    db.instrument.measurement_place.writable=False
    db.instrument.measurement_place.readable=False
    form=crud.update(db.instrument,instrument,next=url('view_instrument',instrument_id))
    return dict(form=form)


@auth.requires_login()
def list_docs():
    instrument_id=request.args(0)
    instrument=db.instrument[instrument_id] or redirect(error_page)
    session.recent_instruments = add(session.recent_instruments,instrument)
    db.document.instrument.default=instrument.id
    db.document.instrument.writable=False
    db.document.instrument.readable=False
    form=crud.create(db.document)
    docs=db(db.document.instrument==instrument.id).select(orderby=db.document.name)
    return dict(instrument=instrument,docs=docs,form=form)

@auth.requires_login()
def list_logs():
    instrument_id=request.args(0)
    instrument=db.instrument[instrument_id] or redirect(error_page)
    session.recent_instruments = add(session.recent_instruments,instrument)
    db.log.instrument.default=instrument.id
    db.log.instrument.writable=False
    db.log.instrument.readable=False
    form=crud.create(db.log)
    logs=db(db.log.instrument==instrument.id).select(orderby=~db.log.created_on)
    return dict(instrument=instrument,logs=logs,form=form)


@auth.requires_login()
def edit_task():
    task_id=request.args(0)
    task=db.task[task_id] or redirect(error_page)
    instrument=db.instrument[task.instrument]
    db.task.instrument.writable=db.task.instrument.readable=False
    form=crud.update(db.task,task,next='view_task/[id]')
    return dict(form=form, instrument=instrument)

@auth.requires_login()
def view_task():
    task_id=request.args(0)
    task=db.task[task_id] or redirect(error_page)
    instrument=db.instrument[task.instrument]
    db.task.instrument.writable=db.task.instrument.readable=False
    form=crud.read(db.task,task)
    return dict(form=form, instrument=instrument, task=task)

@auth.requires_login()
def list_tasks():
    instrument_id=request.args(0)
    instrument=db.instrument[instrument_id]
    if instrument_id:
       tasks=db(db.task.instrument==instrument_id)\
               (db.task.created_by==auth.user.id)\
               (db.task.start_time>=request.now).select()
    else:
       tasks=db(db.task.created_by==auth.user.id)\
               (db.task.start_time<=request.now).select()
    db.task.instrument.default=instrument_id
    db.task.instrument.writable=db.task.instrument.readable=False
    form=crud.create(db.task,next='view_task/[id]')
    return dict(tasks=tasks,instrument=instrument,form=form)

@auth.requires_login()
def calendar():
    instrument_id=request.args(0)
    instrument=db.instrument[instrument_id]
    if instrument_id:
       tasks=db(db.task.instrument==instrument_id)\
               (db.task.created_by==auth.user.id)\
               (db.task.start_time>=request.now).select()
    else:
       tasks=db(db.task.created_by==auth.user.id)\
               (db.task.start_time>=request.now).select()
    return dict(tasks=tasks,instrument=instrument)

@auth.requires(auth.user and auth.user.email=='mdipierro@cs.depaul.edu')
def reset():
    for table in db.tables:
        if table=='auth_user':
            db(db[table].email!='mdipierro@cs.depaul.edu').delete()
        else:
            db(db[table].id>0).delete()
    session.flash='done!'
    redirect('index')

def error():
    return dict(message="something is wrong")

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
