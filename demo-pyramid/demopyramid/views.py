from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'demo-pyramid'}


@view_config(route_name='home',
	         match_param='action=login',
	         request_method='GET',
	         renderer='templates/login.pt')
def login(request):
	return  {}