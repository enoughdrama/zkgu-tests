from rest_framework import serializers
from .models import ZkguPerson, ZkguPersonSync

class ZkguPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZkguPerson
        fields = '__all__'
        read_only_fields = ('created_at', 'last_update')

class ZkguPersonSyncSerializer(serializers.ModelSerializer):
    person = ZkguPersonSerializer(read_only=True)
    
    class Meta:
        model = ZkguPersonSync
        fields = '__all__'