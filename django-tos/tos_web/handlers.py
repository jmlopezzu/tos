from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Verification
from .models import Query

from .tasks import verification_email
from .tasks import build_tree


@receiver(post_save, sender=Verification)
def invitation_email_handler(sender, instance, created, raw, *args, **kwargs):
    '''
    This signal is execute for send email verification after signup
    user in ToS
    '''
    if created and not raw:
        # Send the verification email through celery task
        verification_email.delay(instance.user.email,
                                 instance.user.firstname,
                                 instance.token)


@receiver(post_save, sender=Query)
def throw_task_to_build_tree(sender, created, instance, *args, **kwargs):
    '''
    This signal is execute for begin job to building tree after
    that a user make upload file
    '''
    if created:
        # Call task for build tree on Celery queue
        build_tree.apply_async((instance.pk, ), countdown=5)
