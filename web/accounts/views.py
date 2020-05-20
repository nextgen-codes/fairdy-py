from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import logout_then_login
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from .forms import FairdyRegistrationForm, DeleteUserForm, ForgotPasswordForm, ChangePasswordForm, ResetPasswordForm, \
    ChangeUsernameForm, ChangeEmailForm, AdminEditUserForm
from .models import FairdyUser


# VALIDATE EMAIL
def validate_email(request, token):
    fairdy_user = get_object_or_404(FairdyUser, token=token)

    # token must not be reused
    if fairdy_user.is_valid_email:
        raise Http404

    # token must not be expired
    if fairdy_user.token_is_expired():
        fairdy_user.send_validation_email()
        messages.error(request, "Sorry! It looks like that link had already expired, "
                                "please check your email for a new one.")
        return redirect('fairdy:index')

    login(request, fairdy_user.user)
    fairdy_user.is_valid_email = True
    fairdy_user.save()
    messages.success(request, "Email successfully validated!")
    return redirect('accounts:profile')


# RESET PASSWORD
# allows user to enter a new password if they have the correct token from their email
def reset_password(request, token):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            fairdy_user = get_object_or_404(FairdyUser, user_id=form.cleaned_data['fairdy_user'])

            # token must not be reused
            if not fairdy_user.is_password_expired:
                raise Http404

            # token must not be expired
            if fairdy_user.token_is_expired():
                fairdy_user.send_validation_email()
                messages.error(request, "Sorry! It looks like that link had already expired, "
                                        "please check your email for a new one.")
                return redirect('fairdy:index')

            pw1 = form.cleaned_data['password1']
            pw2 = form.cleaned_data['password2']
            if token == fairdy_user.token and pw1 == pw2:
                fairdy_user.user.set_password(pw1)
                fairdy_user.user.save()
                fairdy_user.is_password_expired = False
                fairdy_user.save()
                login(request, fairdy_user.user)
                messages.success(request, 'Password successfully changed.')
                return redirect('accounts:profile')

    form = ResetPasswordForm({'user_id': get_object_or_404(FairdyUser, token=token).user_id})
    return render(request, 'password_reset.html', {'form': form})


# FORGOT PASSWORD
# sends password reset email and deactivates user, if the username is found
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            try:
                fairdy_user = FairdyUser.objects.get(user_id=User.objects.get(username=form.cleaned_data["username"]))
                fairdy_user.fairdy_user.set_unusable_password()
                fairdy_user.is_password_expired = True
                messages.success(request, 'Password is reset. Check your email for a link to set a new one.')
                fairdy_user.send_reset_email()
                return redirect('fairdy:index')
            except ObjectDoesNotExist:
                messages.error(request, 'User not found.')
    return render(request, 'password_forgot.html')


# REGISTER
# register a new account, and send a confirmation email
def register(request):
    if request.method == 'POST':
        form = FairdyRegistrationForm(request.POST)
        if form.is_valid():
            username = form.save()
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            fairdy_user = FairdyUser.objects.create_fairdy_user(user)
            fairdy_user.send_validation_email()
            messages.success(request, 'Thank you for registering an account on fairdy.no! '
                                      'Follow the link in your email to complete the process.')
            return redirect('accounts:profile')
    else:
        form = FairdyRegistrationForm()
    return render(request, 'register.html', {'form': form})

# LOG OUT
@login_required
def logout(request):
    messages.success(request, 'Successfully logged out.')
    return logout_then_login(request)


# PROFILE
# return the main profile page for the currently logged in user
@login_required
def profile(request):
    return render(request, 'profile.html')


# CHANGE USERNAME
# allows a logged in user to update their username, as long as the username they want is not already taken
@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data['username']
            try:
                user.save()
                messages.success(request, 'Your username was successfully updated.')
            except IntegrityError:
                messages.error(request, 'That username is not available, please try something else.')
            return redirect('accounts:profile')
    return render(request, 'update.html', {'form': ChangeUsernameForm()})


# CHANGE EMAIL
# allows a logged in user to update their email, it will be necessary to validate the new email
# it is possible for multiple user accounts to have the same email registered and validated
@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            user = request.user
            user.email = form.cleaned_data['email']
            user.save()
            fairdy_user = FairdyUser.objects.get(user_id=user.id)
            fairdy_user.is_valid_email = False
            fairdy_user.send_validation_email()
            messages.success(request, 'Your email address was successfully updated. '
                                      'Follow the link in your email to complete the process.')
            return redirect('accounts:profile')
        messages.error(request, 'There was a problem updating your email address.')
    return render(request, 'update.html', {'form': ChangeEmailForm()})


# CHANGE PASSWORD
# allows a logged in user to update their password, correct current password is required
@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            pw1 = form.cleaned_data['password1']
            pw2 = form.cleaned_data['password2']
            pw_old = form.cleaned_data['password_old']
            user = request.user
            if user.check_password(pw_old) and pw1 == pw2 and pw1 != pw_old:
                user.set_password(pw1)
                user.save()
                alert = 'Your password was successfully changed.'
                messages.add_message(request, messages.SUCCESS, alert)
                return redirect('accounts:profile')
        messages.success(request, 'There was a problem changing your password. Please try again.')
    return render(request, 'password_change.html', {'form': ChangePasswordForm()})


# RESEND VALIDATION EMAIL
@login_required
def resend_validation(request):
    fairdy_user = FairdyUser.objects.get(user_id=request.user.id)
    # Only validate the email address for a user once
    if fairdy_user.is_valid_email:
        raise Http404
    else:
        fairdy_user.send_validation_email()
        messages.success(request, "A new validation link was sent to your email.")
        return redirect('accounts:profile')


# DELETE THE ACCOUNT
# Delete the account of the currently logged in user, if they provide their correct password
@login_required
def delete(request):
    if request.method == 'POST':
        form = DeleteUserForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.user, password=form.cleaned_data.get('password'))
            if user is not None:
                # TODO delete simulations also?
                logout(request)
                user.delete()
                messages.success(request, 'Account deleted successfully.')
            else:
                messages.error(request, 'Error deleting account. Check your password and try again')
            return render(request, 'index.html')

    return render(request, 'delete.html', {'form': DeleteUserForm()})


# USER ACCOUNT ADMINISTRATION
# view index of all user accounts registered in the database
@staff_member_required
def user_index(request):
    user_list = FairdyUser.objects.all().order_by('user__username')
    paginator = Paginator(user_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_index.html', {'page_obj': page_obj})


# EDIT USER ACCOUNT
# edit a user account in the database, only available as post, request comes from user_index page
@staff_member_required
def user_edit(request):
    form = AdminEditUserForm(request.POST)
    if form.is_valid():
        fairdy_user = get_object_or_404(FairdyUser, user_id=form.cleaned_data['user_id'])
        if form.cleaned_data['is_staff']:
            fairdy_user.user.is_staff = True
            fairdy_user.block_cycle_limit = -1
        else:
            fairdy_user.user.is_staff = False
            fairdy_user.set_bcl_millions(form.cleaned_data['block_cycle_limit'])
        fairdy_user.user.save()
        fairdy_user.save()
        messages.success(request, 'Updated user: {}'.format(fairdy_user.user.username))
    else:
        messages.error(request, 'Error updating user.')
    return redirect('accounts:user_index')


# HELP PAGES

def help_create_account(request):
    return render(request, 'help/create_account.html')


def help_manage_account(request):
    return render(request, 'help/manage_account.html')


def help_manage_users(request):
    return render(request, 'help/manage_users.html')
