import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager

STATE_SYSTEM = (
    ('AC', 'Active'),
    ('PD', 'Pending'),
    ('TOS', 'Inside'),
)


class UserProfileManager(BaseUserManager):

    def create_user(self, email, firstname, lastname,
                    password=None, is_active=False):
        '''
        Creates and saves a User with the given email, firstname,
        lastname and password.
        '''
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
        )
        user.set_password(password)
        user.acceptance = True
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password):
        '''
        Creates and saves a superuser with the given email, date of
        birth and password.
        '''
        user = self.create_user(email, firstname=firstname, lastname=lastname,
                                password=password,)
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser):

    '''
    Models a ToS user that extends of Django AbstractBaseUser
    '''
    # custom fields for User Profile
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    acceptance = models.BooleanField(default=False)

    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)

    objects = UserProfileManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    def get_full_name(self):
        # The user is identified by their email address
        return '%s %s' % (self.firstname, self.lastname)

    def get_short_name(self):
        # The user is identified by their email address
        return self.firstname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Verification(models.Model):

    '''
    Models a verification after signup user

    '''
    user = models.OneToOneField('UserProfile')
    token = models.SlugField()


class Invitation(models.Model):

    '''
    Models an invitation from an existing user to another potential user
    '''
    inviter = models.ForeignKey(
        UserProfile, related_name='invitations')
    email = models.EmailField()
    count = models.PositiveIntegerField(default=1)
    state = models.CharField(max_length=10, choices=STATE_SYSTEM)
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('inviter', 'email', )


class Query(models.Model):

    '''
    Represents the document model in the database, relates to a user, so a user
    can own multiple queries.
    '''
    def rename_file(instance, filename):
        '''
        Rename the file when the user make upload
        '''
        filename = '%s.%s' % (uuid.uuid4(), 'txt')
        return os.path.join('raw', filename)

    user = models.ForeignKey(
        UserProfile, related_name='queries')
    filename = models.TextField(max_length=64)
    raw_data = models.FileField(upload_to=rename_file)
    description = models.TextField()
    tree = models.BinaryField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def ready(self):
        "Is the query ready for deploy?"
        return not self.tree == b''
