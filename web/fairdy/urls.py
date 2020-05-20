from django.urls import path

from .views import *

app_name = 'fairdy'

urlpatterns = [
    path('', index, name='index'),
    path('index/', index, name='index'),
    path('visualize/', visualize, name='visualize'),
    path('run/', run_simulation, name='run_simulation'),
    path('csv/', get_csv, name='get_csv'),
    path('about_simulation/', about_simulation, name='about_simulation'),
    path('help/getting_started/', help_getting_started, name='help_getting_started'),
    path('help/run_simulation/', help_run_simulation, name='help_run_simulation'),
    path('help/compare_download/', help_compare_download, name='help_compare_download'),
    # should be last since it will check any string (after /fairdy/) to see if it is an installed code
    path('<str:code_type>/', index, name='codes'),
]
