from pyramid.view import view_config


@view_config(route_name='home',
			 request_method='GET',
			 renderer='templates/home.pt')
def home(request):
    return {
		'errors': [],
		'not_auth_warn': False,
		'success_slo': False,
		'paint_logout': False,
	}

@view_config(route_name='home',
	         match_param='action=login',
	         request_method='GET',
	         renderer='templates/home.pt')
def login(request):
	return {
		'errors': [],
		'not_auth_warn': False,
		'success_slo': False,
		'paint_logout': False,
	}


@view_config(route_name='home',
	         match_param='action=metadata',
	         request_method='GET',
	         renderer='templates/metadata.pt')
def login(request):
	return  {}