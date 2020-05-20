from fairdy.models import Simulation

"""this file makes a list of all installed codes, which are defined in models.py of the fairdy app, """
"""available in every html template"""


def get_installed_codes(request):
    return {
        'installed_codes': Simulation.Codes
    }
