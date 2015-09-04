from pyramid.view import view_config
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError
from urlparse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


def init_saml_auth(req, request):
    saml_path = request.registry.settings.get('saml_path')
    auth = OneLogin_Saml2_Auth(req, custom_base_path=saml_path)
    return auth


def prepare_pyramid_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    url_data = urlparse(request.url)
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': url_data.port,
        'script_name': request.path,
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }


@view_config(route_name='home',
             renderer='templates/home.pt')
def home(request):
    req = prepare_pyramid_request(request)
    auth = init_saml_auth(req, request)
    errors = []
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    if 'sso' in request.params:
        raise HTTPFound(auth.login())
    elif 'sso2' in request.params:
        raise HTTPFound(auth.login(request.route_url(route_name='attrs')))
    elif 'slo' in request.params:
        name_id = None
        session_index = None
        if 'samlNameId' in request.session:
            name_id = request.session['samlNameId']
        if 'samlSessionIndex' in request.session:
            session_index = request.session['samlSessionIndex']

        headers = forget(request)
        raise HTTPFound(auth.logout(name_id=name_id, session_index=session_index), headers=headers)

    elif 'acs' in request.params:
        auth.process_response()
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            request.session['samlUserdata'] = auth.get_attributes()
            request.session['samlNameId'] = auth.get_nameid()
            request.session['samlSessionIndex'] = auth.get_session_index()
            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if 'RelayState' in request.POST and self_url != request.POST['RelayState']:
                raise HTTPFound(auth.redirect_to(request.POST['RelayState']))

    elif 'sls' in request.params:
        dscb = lambda: request.session.clear()
        url = auth.process_slo(delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            headers = forget(request)
            if url is not None:
                raise HTTPFound(url, headers=headers)
            else:
                request.response.headerlist.extend(headers)
                success_slo = True

    if 'samlUserdata' in request.session:
        paint_logout = True
        headers = remember(request, request.session['samlUserdata']['mail'][0])
        request.response.headerlist.extend(headers)

        if len(request.session['samlUserdata']) > 0:
            attributes = request.session['samlUserdata'].items()

    return {
        'errors': errors,
        'not_auth_warn': not_auth_warn,
        'success_slo': success_slo,
        'attributes': attributes,
        'paint_logout': paint_logout
    }


@view_config(route_name='attrs',
             renderer='templates/attrs.pt')
def attrs(request):
    paint_logout = False
    attributes = False

    if 'samlUserdata' in request.session:
        paint_logout = True
        if len(request.session['samlUserdata']) > 0:
            attributes = request.session['samlUserdata'].items()

    return {
        'paint_logout': paint_logout,
        'attributes': attributes
    }


@view_config(route_name='metadata',
             renderer='string')
def metadata_view(request):
    req = prepare_pyramid_request(request)
    auth = init_saml_auth(req, request)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if errors:
        raise HTTPInternalServerError(detail=errors.join(', '))

    request.response.content_type = 'text/xml'
    return metadata

