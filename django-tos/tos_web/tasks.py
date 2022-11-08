import hashlib
import os
import pickle

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from celery import shared_task
from pusher import Pusher

from tos.graph.tree_of_science import TreeOfScience
from tos.interpreters import IsiInterpreter

from .models import Query


@shared_task
def invitation_email(email):
    '''
    Task as function with decorator @shared_task for send
    a invitation for potential user.

    Args:
        email (str): A string with email guest user

    Returns:
        This task doesn't return a result, but can control its execution.
    '''

    subject = "Tree of Science Invitation"
    url = '%s/signup' % (settings.BASE_URL, )
    img = '%s/static/img/ToS.png' % (settings.BASE_URL, )
    context = {'url': url, 'img': img}
    html_content = render_to_string('tos_web/users/invitation_email.html',
                                    context)
    text_content = strip_tags(html_content)
    message = EmailMultiAlternatives(
        subject, text_content,
        settings.EMAIL_HOST_USER, [email, ])
    message.attach_alternative(html_content, "text/html")
    message.send()


@shared_task
def contact_email(email, name, message):
    '''
    Task as function with decorator @shared_task for send the
    content of contact form to our email.

    Args:
        email (str): A string with email of user interested
        message (str): A string with message of user interested
        name str: A string with firstname user interested

    Returns:
        This task doesn't return a result, but can control its execution.
    '''

    subject = "Tree of Science Contact"
    img = '%s/static/img/ToS.png' % (settings.BASE_URL, )
    context = {'name': name, 'message': message, 'email': email, 'img': img}
    html_content = render_to_string('tos_web/users/contact_email.html',
                                    context)
    text_content = strip_tags(html_content)
    message = EmailMultiAlternatives(subject, text_content,
                                     settings.EMAIL_HOST_USER,
                                     [settings.EMAIL_HOST_USER, ])
    message.attach_alternative(html_content, "text/html")
    message.send()


@shared_task
def verification_email(email, firstname, token):
    '''
    Task as function with decorator @shared_task for send email
    verification after signup a user.

    Args:
        email (str): A string with email of user lastest signup
        firstname (str): A string with firstname user
        token (Slug): A value for validate the record

    Returns:
        This task doesn't return a result, but can control its execution.
    '''

    subject = "Tree of Science Verify Account"
    url = settings.BASE_URL
    img = '%s/static/img/ToS.png' % (settings.BASE_URL, )
    context = {
        'firstname': firstname,
        'verify_url': '%s/verify/%s' % (url, token, ),
        'img': img
    }
    html_content = render_to_string(
        'tos_web/users/verification_email.html',
        context)
    text_content = strip_tags(html_content)
    message = EmailMultiAlternatives(subject, text_content,
                                     settings.EMAIL_HOST_USER,
                                     [email, ])
    message.attach_alternative(html_content, "text/html")
    message.send()


@shared_task(bind=True)
def build_tree(self, pk):
    '''
    Task as function with decorator @shared_task for build a tree
    with TreeOfScience lib, serialize and save result in database.

    Args:
        pk (str): A string with primary key of query

    Returns:
        This task doesn't return a result, but can control its execution.
    '''

    query = Query.objects.get(pk=pk)
    path = os.path.join(settings.MEDIA_ROOT,
                        query.raw_data.path)
    handle = open(path, 'r')
    tree = TreeOfScience(IsiInterpreter(), {'data': handle.read()})
    query.tree = pickle.dumps(tree)
    query.save()

    code = hashlib.sha1(query.user.email.encode('utf-8')).hexdigest()
    channel = "queries-%s" % (code, )

    pusher = Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET)
    url = '%s/queries/%s' % (settings.BASE_URL, pk, )
    pusher.trigger(channel, 'tree-created', {'pk': pk, 'url': url})
