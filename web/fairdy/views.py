import base64
import csv
from io import BytesIO

import fairdypy
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Max
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from matplotlib import pyplot

from accounts.models import FairdyUser
from fairdy.forms import SimulationForm, PyramidSimulationForm
from fairdy.models import Simulation, Cycle
from web import settings


def index(request, code_type=None):
    # If code type parameter is not None (meaning show sims for all codes)
    # Check it is a valid installed code, and set the request's code_type
    if code_type is not None:
        installed_codes = [item.name for item in Simulation.Codes]
        code_type = code_type.upper()
        if code_type not in installed_codes:
            raise Http404()
        else:
            # get sim list from database filtered by the valid code
            request.code_type = Simulation.Codes[code_type]
            sim_list = Simulation.objects.filter(code_type=request.code_type)
    else:
        sim_list = Simulation.objects.all()
        # filter the sim list from database by username if present in the query string
        if 'username' in request.GET:
            fairdy_user = FairdyUser.objects.get(user__username=request.GET['username'])
            sim_list = sim_list.filter(fairdy_user=fairdy_user)

    # Django paginator initialization
    paginator = Paginator(sim_list.order_by('-id'), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html', {'page_obj': page_obj})


def about(request):
    return render(request, 'about.html')


def about_simulation(request):
    return render(request, 'help/templates/about_simulation.html')


# Helper method to instantiate the different codes in the fairdy module
# If new codes are added to web app, this function must be updated,
# together with Simulation.Codes and Simulation.__str__
def run_module_simulation(web_sim):
    # STANDARD CODES
    standard_codes = [Simulation.Codes.REED_SOLOMON, Simulation.Codes.REPLICATION]
    if web_sim.code_type in standard_codes:
        module_sim = fairdypy.Reed_solomon(
            word_blocks=web_sim.k_value,
            extra_blocks=web_sim.m_value,
            num_of_stripes=web_sim.num_stripes,
            lazy_heal_threshold=web_sim.lazy_heal_threshold,
            storage_fault_mode=web_sim.storage_location_mode,
            num_of_storage=web_sim.num_storage_locations if web_sim.storage_location_mode else None,
        )

    # GENERALIZED PYRAMID
    elif web_sim.code_type == Simulation.Codes.GENERALIZED_PYRAMID:
        module_sim = fairdypy.Generalized_pyramid_code(
            gpc_definition=(web_sim.n_value, web_sim.k_value),
            horizontal_rs=(web_sim.pyramidsimulation.k_horizontal, web_sim.pyramidsimulation.m_horizontal),
            vertical_rs=(web_sim.pyramidsimulation.k_vertical, web_sim.pyramidsimulation.m_vertical),
            num_of_stripes=web_sim.num_stripes,
            lazy_heal_threshold_hor=web_sim.lazy_heal_threshold,
            lazy_heal_threshold_vert=web_sim.pyramidsimulation.lazy_heal_threshold_ver,
            storage_fault_mode=web_sim.storage_location_mode,
            num_of_storage=web_sim.num_storage_locations if web_sim.storage_location_mode else None,
        )
    # RUN SIMULATION
    module_sim.loop_simulation(
        loops=web_sim.num_cycles,
        p_error=web_sim.p_error,
    )
    return module_sim


# helper method to redirect if accounts app is enabled, and the user is not logged in
def is_valid_user(request):
    if settings.USE_ACCOUNTS_APP:
        if request.user.is_anonymous:
            messages.error(request, 'You must log in before running simulations.')
            return False
        else:
            fairdy_user = FairdyUser.objects.get(user_id=request.user.id)
            if settings.REQUIRE_EMAIL_VERIFICATION and not fairdy_user.is_valid_email:
                messages.error(request, 'You must validate your email before running simulations.')
                return False
    return True


def user_has_enough_bcc(fairdy_user, web_sim):
    # if the accounts app is turned off, ignore null fairdy_user
    if not fairdy_user:
        if not settings.USE_ACCOUNTS_APP:
            return True
        else:
            return False
    # Check user has enough block cycle credits available to run this simulation
    elif settings.USE_ACCOUNTS_APP and settings.ENFORCE_BLOCK_CYCLE_LIMIT and fairdy_user.can_run_simulation(web_sim):
        return True
    else:
        return False


def initialize_gp(web_sim, gpc_form):
    if gpc_form.is_valid():
        web_sim.save()
        gpc_sim = gpc_form.save(commit=False)
        gpc_sim.simulation = web_sim
        gpc_sim.save()
        return True
    else:
        return False


def run_simulation(request):
    if not is_valid_user(request):
        return redirect('fairdy:index')

    if request.method == 'POST':
        sim_form = SimulationForm(request.POST)
        gpc_form = PyramidSimulationForm(request.POST)
        fairdy_user = FairdyUser.objects.get(user_id=request.user.id)

        if sim_form.is_valid():
            web_sim = sim_form.save(commit=False)

            # check the user has enough credits to run the sim, or is exempt
            if not user_has_enough_bcc(fairdy_user, web_sim):
                messages.error(request, 'You do not have enough block cycle credits to run this simulation, '
                                        'ask the administrator to raise your limit.')
                return redirect('fairdy:index')
            web_sim.fairdy_user = fairdy_user
            web_sim.start_time = timezone.now()

            # deal with extra fields required by pyramid codes
            if web_sim.code_type == Simulation.Codes.GENERALIZED_PYRAMID and not initialize_gp(web_sim, gpc_form):
                messages.error(request, gpc_form.non_field_errors())
                return render(request, 'form.html', {'base_form': sim_form, 'gpc_form': gpc_form})

            # try running simulation
            try:
                module_sim = run_module_simulation(web_sim)
                if len(module_sim.baf_history) is 0:
                    messages.error(request, 'There was a problem running the simulation')
                    return render(request, 'form.html', {'base_form': sim_form, 'gpc_form': gpc_form})
                web_sim.save()
                cycles = (Cycle(
                        simulation=web_sim,
                        block_availability_factor=module_sim.baf_history[cycle],
                        num_faulted_blocks=module_sim.blocks_failed_history[cycle],
                        num_repaired_blocks=module_sim.blocks_healed_history[cycle]
                    ) for cycle in range(len(module_sim.baf_history))
                )
                Cycle.objects.bulk_create(cycles)
                web_sim.end_time = timezone.now()
                web_sim.save()
                return redirect(web_sim)

            except ValueError as error:
                if web_sim:
                    web_sim.delete()
                messages.error(request, error)

    else:    # = request.method is NOT POST
        sim_form = SimulationForm()
        # prefill the code-type on the form if the user clicked from a specific code page
        if 'code_type' in request.GET:
            sim_form.initial = {'code_type': request.GET['code_type']}
        gpc_form = PyramidSimulationForm()
    return render(request, 'form.html', {'sim_form': sim_form, 'gpc_form': gpc_form})


def get_csv(request):
    if 'id' not in request.GET:
        raise Http404()
    ids = request.GET.getlist('id')

    sim_fields = ['id', 'code_type', 'n_value', 'k_value', 'm_value', 'num_stripes', 'num_cycles', 'p_error',
                  'lazy_heal_threshold', 'storage_location_mode', 'num_storage_locations']
    gpc_fields = ['k_horizontal', 'm_horizontal', 'k_vertical', 'm_vertical', 'lazy_heal_threshold_ver',
                  'num_repair_cycles']
    sims = Simulation.objects.filter(pk__in=ids).order_by('-id')
    # set maximum number of cycles to the highest that any of the selected sims have
    max_cycle_count = sims.aggregate(Max('num_cycles'))['num_cycles__max'] + 1

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="FaiRDy.csv"'
    writer = csv.writer(response)
    cycle_fields = list('cycle {}'.format(i) for i in range(max_cycle_count))
    writer.writerow(sim_fields + gpc_fields + cycle_fields)
    for sim in sims:
        writer.writerow(
            list(getattr(sim, field) for field in sim_fields) +
            list(getattr(sim.pyramidsimulation, field) if hasattr(sim, 'pyramidsimulation') else '' for field in gpc_fields) +
            list(getattr(cycle, 'block_availability_factor') for cycle in sim.cycle_set.all())
        )
        writer.writerow(
            ['faulted_blocks'] +
            list('' for i in range(len(sim_fields + gpc_fields)-1)) +
            list(getattr(cycle, 'num_faulted_blocks') for cycle in sim.cycle_set.all())
        )
        writer.writerow(
            ['healed_blocks'] +
            list('' for i in range(len(sim_fields + gpc_fields)-1)) +
            list(getattr(cycle, 'num_repaired_blocks') for cycle in sim.cycle_set.all())
        )

    return response


def visualize(request):
    if 'id' not in request.GET:
        raise Http404()
    ids = request.GET.getlist('id')
    sims = Simulation.objects.filter(pk__in=ids).order_by('-id')
    for sim in sims:
        sim.view_count += 1
        sim.save()

    data = {'sims': sims}
    # get the highest num_cycles any of the sims have and add
    # an additional one to compensate for cycle 0 with baf 1
    max_cycle_count = sims.aggregate(Max('num_cycles'))['num_cycles__max'] + 1
    labels = []
    for sim in sims:
        y = sim.cycle_set.values_list('block_availability_factor', flat=True)
        # if simulation goes to 0 before completing all cycles,
        # it is necessary to add 0 baf measurements to the list so the graph is complete
        if len(y) < max_cycle_count:
            y = list(y) + ([None] * (max_cycle_count - len(y)))
        x = range(max_cycle_count)
        pyplot.plot(x, y)
        labels.append('{}, sim{}'.format(str(sim), sim.id))
    pyplot.legend(labels)
    pyplot.xlim(0, max_cycle_count - 1)
    pyplot.ylim(0, 1.1)
    pyplot.xlabel('time (in cycles)')
    pyplot.ylabel('Block Availability Factor')
    pyplot.title('Block Availability Factor vs. time')
    buf = BytesIO()
    pyplot.savefig(buf, format='png', dpi=150)
    pyplot.close()
    data['graph'] = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')

    return render(request, 'visualize.html', data)


# HELP PAGES

def help_getting_started(request):
    return render(request, 'help/getting_started.html')


def help_run_simulation(request):
    return render(request, 'help/run_simulation.html')


def help_compare_download(request):
    return render(request, 'help/compare_download.html')
