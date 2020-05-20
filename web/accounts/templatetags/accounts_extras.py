from django import template

from accounts.models import FairdyUser

register = template.Library()


@register.filter(name='is_email_verified')
def is_email_validated(user):
    try:
        fairdy_user = FairdyUser.objects.get(user_id=user.id)
        return fairdy_user.is_valid_email
    except FairdyUser.DoesNotExist:
        return False
