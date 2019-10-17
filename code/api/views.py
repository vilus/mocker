from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.serializers import MockSerializer
from mocker.models import Lock, Mock, DupError


class MockViewSet(viewsets.ModelViewSet):
    queryset = Mock.objects.all()
    serializer_class = MockSerializer

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, dict):
            return self._create_one(request, *args, **kwargs)
        return self._create_list(request, *args, **kwargs)

    def _create_one(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except DupError as e:
            return Response({'Fail': str(e)}, status=status.HTTP_409_CONFLICT)

    def _create_list(self, request, *_, **__):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                Lock.objects.select_for_update().get_or_create(name='Mocks')  # for avoid livelock
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except DupError as e:
            return Response({'Fail': str(e)}, status=status.HTTP_409_CONFLICT)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_expired = instance.is_expired()
        self.perform_destroy(instance)
        return Response({'is_expired': is_expired}, status=status.HTTP_200_OK)


# TODO: add filtering by expired
