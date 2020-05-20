from rest_framework import serializers

from fairdy.models import Simulation, PyramidSimulation


class PyramidSimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PyramidSimulation
        fields = ['k_horizontal', 'm_horizontal', 'k_vertical', 'm_vertical']


class SimulationSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    pyramidsimulation = PyramidSimulationSerializer(read_only=True)

    class Meta:
        model = Simulation
        fields = '__all__'

