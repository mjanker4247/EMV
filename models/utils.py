def url(f,args=[]): 
	return URL(r=request,f=f,args=args)

def button(text,action,args=[]):
    return SPAN('[',A(text,_href=URL(r=request,f=action,args=args)),']')

def link_instrument(instrument):
    return A(instrument.name,_href=url('view_instrument',instrument.id))

def link_measurement_place(measurement_place):
    return A(measurement_place.name,_href=url('view_measurement_place',measurement_place.id))
