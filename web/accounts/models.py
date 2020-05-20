from datetime import timedelta
from secrets import token_urlsafe

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import now


class FairdyUserManager(models.Manager):
    def create_fairdy_user(self, user):
        fairdy_user = FairdyUser(user=user)
        fairdy_user.is_valid_email = False
        fairdy_user.is_password_expired = False
        return fairdy_user


class FairdyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    block_cycle_limit = models.IntegerField(default=50000000)  # The number of "block cycles" allowed per time unit
    is_valid_email = models.BooleanField()
    is_password_expired = models.BooleanField()
    token = models.CharField(max_length=128)
    token_expiration = models.DateTimeField()

    objects = FairdyUserManager()

    # Helper methods to refer to block cycle limit in millions
    def get_bcl_millions(self):
        if self.block_cycle_limit == -1:
            return -1
        return self.block_cycle_limit / 1000000

    def set_bcl_millions(self, new_limit):
        if new_limit == -1:
            self.block_cycle_limit = -1
        else:
            self.block_cycle_limit = new_limit * 1000000

    # calculates the number of block cycles credits (BCC) the user has remaining.
    # calculated as block cycle credits used over the last month,
    # subtracted from the block_cycle_limit field on the FairdyUser model
    #
    # meant to avoid vandalism or senseless use of server resources
    def get_available_bcc(self):
        a_month_ago = (now() - relativedelta(months=1))
        used_bcc = 0
        user_sims = self.simulation_set.filter(end_time__gte=a_month_ago)
        for sim in user_sims:
            used_bcc += (sim.n_value * sim.num_stripes * sim.num_cycles)
        return self.block_cycle_limit - used_bcc

    # checks to make sure the user has enough block cycle credits remaining
    # to run the web_sim that is passed in
    def can_run_simulation(self, web_sim):
        # Anybody that is 'staff' on the Django User model, or has bcl=-1
        # on their FairdyUser model, is allowed to run any simulation
        if self.user.is_staff or self.block_cycle_limit == -1:
            return True
        # A regular user who has enough block cycle credits left
        elif self.get_available_bcc() > web_sim.get_bcc():
            return True
        else:
            return False

    # the percentage of user's block cycle credits which are currently available
    # expressed as an integer between 0 and 100
    def get_remaining_bcc_percent(self):
        return int((self.get_available_bcc() / self.block_cycle_limit) * 100)

    # Save a new unique token on the user database record, and expiration date
    def set_token(self):
        self.token = token_urlsafe(64)
        self.token_expiration = timezone.now() + timedelta(days=1)
        self.save()

    # Check if is expired
    def token_is_expired(self):
        return timezone.now() > self.token_expiration

    def send_email(self, subject, html):
        text = '\n\nHi {},\n\nHere is the link you requested from fairdy.ux.uis.no ' \
               ':\n\nfairdy.ux.uis.no/accounts/validate/{}\n\n\n' \
            .format(self.user.username, self.token)
        sender = 'FaiRDy@ux.uis.no'
        receivers = [self.user.email]
        send_mail(subject, text, sender, receivers, html_message=html, fail_silently=False)

    def send_reset_email(self):
        self.set_token()
        subject = 'FaiRDy Password Reset'
        html = render_to_string('emails/email_reset.html', {'fairdy_user': self})
        self.send_email(subject, html)

    def send_validation_email(self):
        self.set_token()
        subject = 'FaiRDy Email Confirmation'
        html = render_to_string('emails/email_verify.html', {'fairdy_user': self})
        self.send_email(subject, html)


""" a 'block cycle' is one block for one cycle """
""" for example, 10 stripes of RS(10,10), for 10 cycles: """
""" num_stripes * stripe_size * num_cycles """
""" 10 * 20 * 10 = 2000 'block cycles' required to run simulation above """
""" 'block_cycle_limit' = -1, will indicate unlimited use """
