from django import forms

from fairdy.models import Simulation, PyramidSimulation


class SimulationForm(forms.ModelForm):
    class Meta:
        model = Simulation
        fields = ['code_type', 'k_value', 'm_value', 'n_value',
                  'num_stripes', 'num_cycles', 'p_error',
                  'storage_location_mode', 'num_storage_locations', 'lazy_heal_threshold']

    def clean(self):
        cleaned_data = super().clean()
        m_val = cleaned_data.get("m_value")
        k_val = cleaned_data.get("k_value")
        n_val = cleaned_data.get("n_value")
        if n_val != k_val + m_val:
            raise forms.ValidationError(
                "Check stripe configuration, the sum of redundancy and data "
                "blocks does not equal the total number of blocks."
            )


class PyramidSimulationForm(forms.ModelForm):
    class Meta:
        model = PyramidSimulation
        fields = ['num_repair_cycles', 'k_horizontal', 'm_horizontal',
                  'k_vertical', 'm_vertical', 'lazy_heal_threshold_ver']
