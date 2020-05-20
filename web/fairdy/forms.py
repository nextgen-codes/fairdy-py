from django import forms

from fairdy.models import Simulation, PyramidSimulation


class BootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self:
            if isinstance(self, PyramidSimulationForm):
                field.field.widget.attrs.update({'class': 'form-control gpc-field'})
            else:
                field.field.widget.attrs.update({'class': 'form-control'})


class SimulationForm(forms.ModelForm):

    class Meta:
        model = Simulation
        fields = ['code_type', 'k_value', 'm_value', 'n_value',
                  'num_stripes', 'num_cycles', 'p_error',
                  'storage_location_mode', 'num_storage_locations', 'lazy_heal_threshold']


class PyramidSimulationForm(forms.ModelForm):

    class Meta:
        model = PyramidSimulation
        fields = ['num_repair_cycles', 'k_horizontal', 'm_horizontal',
                  'k_vertical', 'm_vertical', 'lazy_heal_threshold_ver']
