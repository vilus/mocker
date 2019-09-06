from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from .models import Mock


@csrf_exempt
def matcher(request):
    mock = Mock.objects.get_by(host=request.get_host(), route=request.path, method=request.method)

    if mock is None:
        raise Http404()

    mock_resp = mock.get_response()

    resp = HttpResponse(content=mock_resp['body'])
    resp.status_code = mock_resp.get('return_code', 200)

    for key, value in mock_resp.get('headers', {}).items():
        resp[key] = value

    return resp
