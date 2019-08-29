from rest_framework import serializers

from mocker.models import Mock


class MockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mock
        fields = '__all__'
        # editable = False  # TODO: make read-only
