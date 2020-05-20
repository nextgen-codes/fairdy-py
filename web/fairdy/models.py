import base64
from io import BytesIO

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from matplotlib import pyplot

from accounts.models import FairdyUser


class Simulation(models.Model):
    # Erasure Codes which are currently installed on FaiRDy web framework
    class Codes(models.TextChoices):
        REPLICATION = 'REP'
        REED_SOLOMON = 'RS'
        GENERALIZED_PYRAMID = 'GP'

    # Storage fault modes available from fairdypy module
    class StorageLocationModes(models.TextChoices):
        RANDOM = 'random'
        EQUAL_SHUFFLE = 'equal_shuffle'
        HASH_BLOCK_INDEX = 'hash_block_index'

    # FIELDS FOR SIMULATION MODEL
    code_type = models.CharField(
        'Erasure Code',
        max_length=10,
        choices=Codes.choices
    )
    k_value = models.PositiveIntegerField(
        '(k) data blocks per stripe',
        validators=[MinValueValidator(1)]
    )
    m_value = models.PositiveIntegerField(
        '(m) redundancy blocks per stripe',
        validators=[MinValueValidator(1)]
    )
    n_value = models.PositiveIntegerField(
        '(n) total blocks per stripe',
        validators=[MinValueValidator(1)]
    )
    num_stripes = models.PositiveIntegerField(
        'stripes per simulation',
        validators=[MinValueValidator(1)]
    )
    num_cycles = models.PositiveIntegerField(
        'number of cycles',
        validators=[MinValueValidator(1)]
    )
    p_error = models.FloatField(
        '(p_error) probability of block failure',
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    storage_location_mode = models.CharField(
        max_length=50,
        choices=StorageLocationModes.choices,
        blank=True,
        null=True
    )
    num_storage_locations = models.PositiveIntegerField(
        'Number of storage locations',
        validators=[MinValueValidator(1)]
    )
    lazy_heal_threshold = models.PositiveIntegerField(
        default=1,  # '1' for for eager heal, for GPC sims this field holds the horiz. threshold, vert. is on GPC model
        validators=[MinValueValidator(1)]
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    fairdy_user = models.ForeignKey(
        FairdyUser,
        on_delete=models.SET_NULL,
        null=True
    )
    view_count = models.PositiveIntegerField(default=0, blank=True)

    # returns the URL for the sim's visualize page
    def get_absolute_url(self):
        return '/fairdy/visualize/?id={}'.format(self.id)

    # defines a short string with the sim's parameters
    # for example RS(16,16) or (32,8)-GPC H:{4,6} V:{2,3}
    def __str__(self):
        if self.code_type == self.Codes.REED_SOLOMON:
            return 'RS({},{}), p_error={}'.format(self.k_value, self.m_value, self.p_error)
        elif self.code_type == self.Codes.GENERALIZED_PYRAMID:
            return '({},{})-GPC H:{{{},{}}} V:{{{},{}}}, p_error={}'.format(
                self.n_value,
                self.k_value,
                self.pyramidsimulation.k_horizontal,
                self.pyramidsimulation.m_horizontal,
                self.pyramidsimulation.k_vertical,
                self.pyramidsimulation.m_vertical,
                self.p_error
            )
        elif self.code_type == self.Codes.REPLICATION:
            return 'REP {} copies, p_error={}'.format(self.m_value, self.p_error)
        else:
            self.__str__()

    # returns the number of blocks in the system
    def num_blocks_in_system(self):
        return self.n_value * self.num_stripes

    # returns the number of block cycle credits required for this simulation
    def get_bcc(self):
        return self.num_blocks_in_system() * self.num_cycles

    def get_thumbnail(self):
        max_cycle_count = self.cycle_set.count()
        y = self.cycle_set.values_list('block_availability_factor', flat=True)
        x = range(0, max_cycle_count)
        pyplot.plot(x, y, linewidth=7)
        pyplot.xlim(0, max_cycle_count - 1)
        pyplot.ylim(0, 1.1)
        buf = BytesIO()
        pyplot.savefig(buf, format='png', dpi=20)
        pyplot.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')


class Cycle(models.Model):
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE)
    block_availability_factor = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    num_faulted_blocks = models.PositiveIntegerField(null=True)
    num_repaired_blocks = models.PositiveIntegerField(null=True)


class PyramidSimulation(models.Model):
    simulation = models.OneToOneField(Simulation, on_delete=models.CASCADE)
    num_repair_cycles = models.IntegerField(
        'repair steps per cycle',
        choices=[(1, 1), (2, 2), (3, 3)],
        default=2
    )
    k_horizontal = models.PositiveIntegerField(
        '(k_1) data blocks in horizontal direction',
    )
    m_horizontal = models.PositiveIntegerField(
        '(m_1) redundancy blocks in horizontal direction',
    )
    k_vertical = models.PositiveIntegerField(
        '(k_2) data blocks in vertical direction',
    )
    m_vertical = models.PositiveIntegerField(
        '(m_2) redundancy blocks in vertical direction',
    )
    lazy_heal_threshold_ver = models.PositiveIntegerField(
        default=1,  # default '1' for for eager heal
        validators=[MinValueValidator(1)]
    )
