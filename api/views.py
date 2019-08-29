from rest_framework import viewsets, status
from rest_framework.response import Response

from api.serializers import MockSerializer
from mocker.models import Mock, DupError


class MockViewSet(viewsets.ModelViewSet):
    queryset = Mock.objects.all()
    serializer_class = MockSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except DupError as e:
            return Response({"Fail": str(e)}, status=status.HTTP_409_CONFLICT)


# TODO: add filtering by expired
