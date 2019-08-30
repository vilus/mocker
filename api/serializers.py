from rest_framework import serializers

from mocker.models import Mock


class MockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mock
        fields = '__all__'
        extra_kwargs = {
            'route': {'required': True},
            'method': {'required': True},
            'responses': {'required': True},
        }
