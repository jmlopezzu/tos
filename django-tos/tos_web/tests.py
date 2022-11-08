import json
import os

from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.urlresolvers import reverse

from django.test import TestCase

from .models import Invitation
from .models import Query
from .models import Verification


class TosWebTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model()

    def assertCalled(self, mock):
        self.assertTrue(mock.called)

    def assertCalledOnce(self, mock):
        self.assertTrue(mock.called)
        self.assertEqual(1, mock.call_count)

    def createUser(self, email=None, password=None,
                   firstname=None, lastname=None):
        email = email or 'aksfdjlaskdf@lkjasdlfkj.kasdjf'
        password = password or 'sakdfjaslkdjflks'
        firstname = firstname or 'John'
        lastname = lastname or 'Doe'
        user = self.user.objects.create_user(
            email, firstname, lastname, password=password)
        return user

    def loginUser(self, user=None, password=None):
        if user is None:
            user = self.createUser()
        success = self.client.login(
            email=user.email, password=password or 'sakdfjaslkdjflks')
        self.assertTrue(success)
        return user

    def visit(self, viewname, ajax=False, **kwargs):
        args = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'} if ajax else {}
        return self.client.get(reverse(viewname, **kwargs), **args)


class IndexViewTest(TosWebTestCase):

    def test_index_shows_landing_page(self):
        response = self.visit('landing')
        self.assertTemplateUsed(response, 'tos_web/landing.html')
        self.assertTemplateNotUsed(response, 'home.html')

    def test_landing_redirects_home_for_loged_users(self):
        self.loginUser()
        response = self.visit('landing')
        self.assertRedirects(response, reverse('home'))


class AboutViewTest(TosWebTestCase):

    def test_there_is_an_about_page(self):
        response = self.visit('about')
        self.assertTemplateNotUsed(response, 'home.html')


class HomeViewTest(TosWebTestCase):

    def test_home_page_doesnt_show_for_logged_out_users(self):
        response = self.visit('home')
        self.assertRedirects(response, reverse('login') + '?next=/home')

    def test_home_page_shows_for_loged_users(self):
        self.loginUser()
        response = self.visit('home')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tos_web/home.html')


class QueryResourceTest(TosWebTestCase):

    def setUp(self):
        super().setUp()
        someone = self.createUser(email='some@example.com', firstname='One')
        self.filename = os.path.join(settings.BASE_DIR,
                                     os.path.pardir,
                                     'tos_web/data/isi.txt')
        self.query = Query.objects.create(
            user=someone,
            filename='asldfkasl.txt',
            raw_data=File(open(self.filename)),
        )
        self.query.save()

    def test_query_list_is_not_accesible_for_unauthenticated_users(self):
        response = self.visit('queries')
        self.assertRedirects(response, reverse('login') + '?next=/queries')

    def test_query_list_is_accesible_for_authenticated_users(self):
        self.loginUser()
        response = self.visit('queries')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tos_web/query_list.html')

    def test_query_detail_is_not_accesible_for_unauthenticated_users(self):
        response = self.visit('queries-detail', kwargs={'pk': self.query.pk})
        self.assertRedirects(response, reverse('login') + '?next=/queries/1')

    def test_query_detail_is_accesible_for_authenticated_users(self):
        john = self.loginUser()
        john_query = Query.objects.create(
            user=john,
            filename='asldfkasl.txt',
            raw_data=File(open(self.filename)),
        )
        response = self.visit('queries-detail', kwargs={'pk': john_query.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tos_web/query_detail.html')

    def test_query_create_is_not_accesible_for_unauthenticated_users(self):
        response = self.visit('queries-create')
        self.assertRedirects(response,
                             reverse('login') + '?next=/queries/create')

    def test_query_create_is_accesible_for_authenticated_users(self):
        self.loginUser()
        response = self.visit('queries-create')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tos_web/query_form.html')

    def test_query_list_only_uses_its_user_queries(self):
        john = self.loginUser()
        jane = self.createUser(email='jane@example.com', firstname='Jane')
        self.assertNotEqual(john, jane)
        john_query = Query.objects.create(
            user=john,
            filename='asldfkasl.txt',
            raw_data=File(open(self.filename)),
        )
        john_query.save()
        jane_query = Query.objects.create(
            user=jane,
            filename='asldfkasl.txt',
            raw_data=File(open(self.filename)),
        )
        jane_query.save()
        response = self.visit('queries')
        self.assertIn(john_query, response.context['object_list'])
        self.assertNotIn(jane_query, response.context['object_list'])

    def test_query_detail_only_shows_users_queries(self):
        john = self.loginUser()
        jane = self.createUser(email='jane@example.com', firstname='Jane')
        self.assertNotEqual(john, jane)
        john_query = Query.objects.create(
            user=john,
            filename='asldfkasl.txt',
            raw_data=File(open(self.filename)),
        )
        john_query.save()
        jane_query = Query.objects.create(
            user=jane,
            filename='asldfkasl.txt',
            raw_data=File(open(self.filename)),
        )
        jane_query.save()
        response = self.visit('queries-detail', kwargs={'pk': jane_query.pk})
        self.assertEqual(404, response.status_code)
        response = self.visit('queries-detail', kwargs={'pk': john_query.pk})
        self.assertEqual(200, response.status_code)

    def test_query_create_creates_queries(self):
        self.loginUser()
        old_count = Query.objects.count()
        with open(self.filename, 'rb') as handle:
            response = self.client.post(reverse('queries-create'), {
                'description': 'alsdkfjalskdjf',
                'raw_data': handle,
            })
        self.assertRedirects(response, reverse('queries'))
        self.assertEqual(old_count + 1, Query.objects.count())

    @patch('tos_web.tasks.build_tree.apply_async')
    def test_query_create_disipates_build_tree_task(self, mock):
        self.loginUser()
        with open(self.filename, 'rb') as handle:
            self.client.post(reverse('queries-create'), {
                'description': 'alsdkfjalskdjf',
                'raw_data': handle,
            })
            query = Query.objects.latest(field_name='pk')
            self.assertCalledOnce(mock)
            mock.assert_called_with((query.pk, ), countdown=5)

    def test_queries_receive_a_proper_tree_at_some_point(self):
        user = self.loginUser()
        with open(self.filename, 'rb') as handle:
            self.client.post(reverse('queries-create'), {
                'description': 'alsdkfjalskdjf',
                'raw_data': handle,
            })
        query = Query.objects.get(user=user)
        self.assertNotEqual(b'', query.tree)

    def test_deliver_json_response_for_request_ajax(self):
        john = self.loginUser()
        with open(self.filename, 'rb') as handle:
            self.client.post(reverse('queries-create'), {
                'description': 'alsdkfjalskdjf',
                'raw_data': handle,
            })
        john_query = Query.objects.get(user=john)
        response = self.visit('queries-detail', ajax=True,
                              kwargs={'pk': john_query.pk})
        self.assertEqual(200, response.status_code)
        data = json.loads(str(response.content, encoding='utf8'))
        self.assertIn('nodes', data)
        self.assertEqual('success', data.get('status', None))

    def test_query_deliver_not_ready_on_ajax(self):
        john = self.loginUser()
        john_query = Query.objects.create(
            user=john,
            filename='asldfkasl.txt',
            raw_data=File(open(self.filename)),
        )
        john_query.save()
        response = self.visit('queries-detail', ajax=True,
                              kwargs={'pk': john_query.pk})
        self.assertEqual(200, response.status_code)
        self.assertFalse(john_query.ready())
        data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual('not ready', data.get('status', None))


class AuthSystemTest(TosWebTestCase):

    def setUp(self):
        super().setUp()
        self.invited = 'john@example.com'
        self.invitee = self.createUser(email='jane@example.com',
                                       firstname='Jane')
        Invitation.objects.create(inviter=self.invitee, email=self.invited)

    def test_there_is_a_login_page(self):
        response = self.visit('login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tos_web/users/login.html')

    def test_login_page_redirects_home_for_authenticated_users(self):
        self.loginUser()
        response = self.visit('login')
        self.assertRedirects(response, reverse('home'))

    def test_login_page_logs_in_user(self):
        credentials = {'email': 'jhon@example.com', 'password': 'secret'}
        self.createUser(**credentials)
        response = self.client.post(reverse('login'), credentials)
        self.assertRedirects(response, reverse('home'))

    def test_logout_page_logs_out_users(self):
        self.loginUser()
        response = self.client.post(reverse('logout'))
        response = self.visit('home')
        self.assertRedirects(response, reverse('login') + '?next=/home')

    def test_sign_up_view_shows_form_for_unauthenticated_users(self):
        response = self.visit('signup')
        self.assertTemplateUsed(response, 'tos_web/users/signup.html')

    def test_sign_up_redirects_home_for_authenticated_users(self):
        self.loginUser()
        response = self.visit('signup')
        self.assertRedirects(response, reverse('home'))

    def test_does_not_sign_up_people_without_an_invitation(self):
        response = self.client.post(reverse('signup'), {
            'email': 'petter@doe.com',
            'firstname': 'John',
            'lastname': 'Doe',
            'new_password': 'Amo a mi mamá',
            'confirmation': 'Amo a mi mamá', })
        self.assertEqual(1, len(response.context['form'].errors))

    def test_sign_up_signs_invited_people_up(self):
        response = self.client.post(reverse('signup'), {
            'email': self.invited,
            'firstname': 'John',
            'lastname': 'Doe',
            'new_password': 'Amo a mi mamá',
            'confirmation': 'Amo a mi mamá', })
        user = self.user.objects.get(email=self.invited)
        self.assertTrue(user is not None)
        self.assertRedirects(response, reverse('verify'))

    def test_sign_up_signs_invited_people_and_user_is_not_active(self):
        self.client.post(reverse('signup'), {
            'email': self.invited,
            'firstname': 'John',
            'lastname': 'Doe',
            'new_password': 'Amo a mi mamá',
            'confirmation': 'Amo a mi mamá', })
        user = self.user.objects.get(email=self.invited)
        self.assertFalse(user.is_active)

    def test_sign_up_creates_a_verification_object_for_the_user(self):
        self.client.post(reverse('signup'), {
            'email': self.invited,
            'firstname': 'John',
            'lastname': 'Doe',
            'new_password': 'Amo a mi mamá',
            'confirmation': 'Amo a mi mamá', })
        user = self.user.objects.get(email=self.invited)
        verification = Verification.objects.get(user=user)
        self.assertTrue(verification is not None)

    def test_verify_verifies_a_recently_created_user(self):
        self.client.post(reverse('signup'), {
            'email': self.invited,
            'firstname': 'John',
            'lastname': 'Doe',
            'new_password': 'Amo a mi mamá',
            'confirmation': 'Amo a mi mamá', })
        user = self.user.objects.get(email=self.invited)
        verification = Verification.objects.get(user=user)
        response = self.visit('verify-token',
                              kwargs={'token': verification.token})
        # Get the user from db again
        user = self.user.objects.get(email=self.invited)
        self.assertTrue(user.is_active)
        self.assertRedirects(response, reverse('login'))

    def test_a_verifycation_email_is_sent_when_the_user_is_created(self):
        with patch('tos_web.tasks.verification_email.delay') as mock:
            self.client.post(reverse('signup'), {
                'email': self.invited,
                'firstname': 'John',
                'lastname': 'Doe',
                'new_password': 'Amo a mi mamá',
                'confirmation': 'Amo a mi mamá', })
            self.assertTrue(mock.called)

    def test_verified_users_can_log_in(self):
        self.client.post(reverse('signup'), {
            'email': self.invited,
            'firstname': 'John',
            'lastname': 'Doe',
            'new_password': 'Amo a mi mamá',
            'confirmation': 'Amo a mi mamá', })
        user = self.user.objects.get(email=self.invited)
        verification = Verification.objects.get(user=user)
        self.visit('verify-token',
                   kwargs={'token': verification.token})
        self.loginUser(user, 'Amo a mi mamá')


class InvitationMechanicsTest(TosWebTestCase):

    def test_an_email_is_scheduled_when_a_new_invitation_is_created(self):
        self.loginUser()
        with patch('tos_web.tasks.invitation_email.delay') as mock:
            self.client.post(reverse('invitations'), {'email': 'jane@doe.com'})
            mock.assert_called_with('jane@doe.com')

    def test_an_email_is_scheduled_just_once_for_inviter_invitee_pair(self):
        self.loginUser()
        with patch('tos_web.tasks.invitation_email.delay') as mock:
            self.client.post(reverse('invitations'), {'email': 'jane@doe.com'})
            self.client.post(reverse('invitations'), {'email': 'jane@doe.com'})
            mock.assert_called_once_with('jane@doe.com')

    def test_invitation_counter_increases_for_inviter_invitee_pairs(self):
        user = self.loginUser()
        with patch('tos_web.tasks.invitation_email.delay'):
            self.client.post(reverse('invitations'), {'email': 'jane@doe.com'})
            self.client.post(reverse('invitations'), {'email': 'jane@doe.com'})
            invitation = Invitation.objects.get(inviter=user,
                                                email='jane@doe.com')
            self.assertEqual(2, invitation.count)

    def test_invitations_can_be_created_by_different_users(self):
        self.loginUser()
        with patch('tos_web.tasks.invitation_email.delay') as mock:
            self.client.post(reverse('invitations'), {'email': 'jane@doe.com'})
            self.client.logout()
            jack = self.createUser(firstname='Jack', email='jack@doe.com')
            self.loginUser(jack)
            self.client.post(reverse('invitations'), {'email': 'jane@doe.com'})
            self.assertEqual(2, mock.call_count)


class ContactMechanicsTest(TosWebTestCase):

    def test_contact_an_email_is_send_when_a_person_completing_form(self):
        with patch('tos_web.tasks.contact_email.delay') as mock:
            self.client.post(reverse('contact'), {
                'name': 'MaryJane',
                'email': 'maryj@lol.com',
                'message': 'Hi Guys, I want use ToS pls pls', })
            mock.assert_called_once_with('maryj@lol.com', 'MaryJane',
                                         'Hi Guys, I want use ToS pls pls')

    def test_contact_an_email_is_send_several_times(self):
        with patch('tos_web.tasks.contact_email.delay') as mock:
            for i in range(100):
                self.client.post(reverse('contact'), {
                    'name': 'MaryJane',
                    'email': 'maryj@lol.com',
                    'message': 'Hi Guys, I want use ToS pls pls', })
            self.assertEqual(100, mock.call_count)
