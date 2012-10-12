'''
Created on Oct 12, 2012

@author: johnfoo
'''

from django import http
from django.template import (Context, RequestContext,
                             loader, TemplateDoesNotExist)
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: Full
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    http.HttpResponseServerError(t.render(RequestContext(request)))