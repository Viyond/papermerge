import logging

from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from papermerge.core.models import User
from papermerge.core.forms import UserForm

logger = logging.getLogger(__name__)


@login_required
def users_view(request):

    if request.method == 'POST':
        selected_action = request.POST.getlist('_selected_action')
        go_action = request.POST['action']

        if go_action == 'delete_selected':
            User.objects.filter(
                digest__in=selected_action
            ).delete()

    users = User.objects.all()

    return render(
        request,
        'admin/users.html',
        {
            'users': users,
        }
    )


@login_required
def user_view(request):
    """
    When adding a new user, administrator will need to add
    username + password and then he/she will be able to edit further
    details.
    """
    if request.method == 'POST':

        form = UserForm(request.POST)

        if form.is_valid():
            user = form.save()

            return redirect(
                reverse('core:user_change', args=(user.id, ))
            )

    form = UserForm()

    return render(
        request,
        'admin/add_user.html',
        {
            'form': form,
        }
    )


@login_required
def user_change_view(request, id):
    """
    Used to edit existing users
    """
    user = get_object_or_404(User, id=id)
    action_url = reverse('core:user_change', args=(id,))

    form = UserForm(
        request.POST or None, instance=user
    )

    if form.is_valid():
        form.save()
        return redirect('core:users')

    return render(
        request,
        'admin/user.html',
        {
            'form': form,
            'action_url': action_url,
            'title': _('Edit User'),
            'user_id': id
        }
    )


@login_required
def user_change_password_view(request, id):
    """
    This view is used by administrator to change password of ANY user in the
    system. As result, 'current password' won't be asked.
    """
    user = get_object_or_404(User, id=id)
    action_url = reverse('core:user_change_password', args=(id,))

    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            user.set_password(password1)
            user.save()
            messages.success(
                request,
                _("Password was successfully changed.")
            )
            return redirect(
                reverse('core:user_change', args=(id,))
            )

    return render(
        request,
        'admin/user_change_password.html',
        {
            'user': user,
            'action_url': action_url
        }
    )
