from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from common.models import District, HouseType, Estate, Agent


class DistrictSerializer(ModelSerializer):

    class Meta:
        model = District
        fields = ('distid', 'name')


class HouseTypeSerializer(ModelSerializer):

    class Meta:
        model = HouseType
        fields = '__all__'


class AgentSerializer(ModelSerializer):

    class Meta:
        model = Agent
        fields = ('agentid', 'name', 'tel', 'servstar', 'certificated')


class EstateSerializer(ModelSerializer):
    district = serializers.SerializerMethodField()
    agents = serializers.SerializerMethodField()

    @staticmethod
    def get_agents(estate):
        results = []
        for agent in estate.agents.all():
            results.append(AgentSerializer(agent).data)
        return results

    @staticmethod
    def get_district(estate):
        return DistrictSerializer(estate.district).data

    class Meta:
        model = Estate
        fields = '__all__'
