import re

from django.contrib.auth import authenticate

from django import forms

from .models import UserProfile, Query, Invitation
from .tasks import invitation_email


class AuthenticationForm(forms.Form):

    '''
    Form to authenticate an user.
    '''

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        user = authenticate(
            username=cleaned_data.get('email'),
            password=cleaned_data.get('password'))
        if user is None:
            raise forms.ValidationError('The email or password are wrong',
                                        code='invalid')
        if not user.is_active:
            raise forms.ValidationError('Please activate your account',
                                        code='inactive')
        return cleaned_data


class SignUpForm(forms.ModelForm):

    '''
    A form for creating new users. Includes all the required fields, plus a
    repeated password.
    '''

    new_password = forms.CharField(label='Password',
                                   widget=forms.PasswordInput)
    confirmation = forms.CharField(label='Password confirmation',
                                   widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        exclude = ('password', )
        fields = ('email', 'firstname', 'lastname')

    def clean_new_password(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('new_password')
        password2 = self.cleaned_data.get('confirmation')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match')
        return password2

    def clean(self):
        cleaned_data = super().clean()
        invitations = Invitation.objects.filter(
            email=cleaned_data.get('email'))
        if not invitations.exists():
            raise forms.ValidationError(
                'Sorry, you don\'t have an invitation',
                code='invalid')
        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['confirmation'])
        if commit:
            user.save()
        return user


class UpdateUserForm(forms.ModelForm):

    '''
    A form for update a user profile
    '''
    class Meta:
        model = UserProfile
        exclude = ('password', )
        fields = ('firstname', 'lastname', )


class QueryForm(forms.ModelForm):

    '''
    A form for a query user, raw_data and description are mandatory
    fields on template form
    '''

    class Meta:
        model = Query
        exclude = ['user', ]
        fields = ['raw_data', 'description', ]

    def clean_raw_data(self):
        raw_data = self.cleaned_data.get('raw_data')
        content = raw_data.read().decode()
        has_cr = re.search(r'^CR', content, re.MULTILINE) is not None
        has_er = re.search(r'^ER$', content), re.MULTILINE is not None
        if not has_cr or not has_er:
            raise forms.ValidationError(
                'Your file does not include cited references, make sure you '
                'download the references in the right format.',
                code='bad-file'
            )
        return raw_data


class InvitationForm(forms.ModelForm):

    '''
    Represent a form for invitations that users can send
    '''

    class Meta:
        model = Invitation
        exclude = ['inviter', ]
        fields = ['email', ]

    def save(self, commit=True, *args, **kwargs):
        '''
        Function override for control the send invitations for email
        and diffusion record
        '''
        invitation = super().save(commit=False, *args, **kwargs)
        email = invitation.email
        inviter = invitation.inviter
        new_invite = not Invitation.objects.filter(email=email).exists()
        try:
            invitation = Invitation.objects.get(email=email, inviter=inviter)
            invitation.count += 1
        except Invitation.DoesNotExist:
            invitation_email.delay(email)
            invitation = Invitation(
                inviter=inviter,
                email=email,
                state='TOS')

        if new_invite:
            invitation.state = 'PD'
        if commit:
            invitation.save()

        return invitation


class ContactForm(forms.Form):

    '''
    Form for users contact us
    '''
    email = forms.EmailField()
    name = forms.CharField(max_length=32)
    message = forms.CharField(widget=forms.Textarea)
