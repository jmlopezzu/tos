import pickle
import uuid

from django.contrib import auth
from django.contrib.auth import get_user_model

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy

from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

from .models import Query
from .models import Invitation
from .models import Verification

from .forms import AuthenticationForm
from .forms import ContactForm
from .forms import SignUpForm
from .forms import InvitationForm
from .forms import QueryForm
from .forms import UpdateUserForm

from .tasks import contact_email
from .tasks import verification_email

from .mixins import LoginRequiredMixin
from .mixins import JSONResponseMixin
from .mixins import CSVResponseMixin

from .utils import default_redirect


class LandingView(TemplateView):

    '''
    A simple TemplateView for render landing page
    '''
    template_name = 'tos_web/landing.html'

    def dispatch(self, *args, **kwargs):
        '''
        Function override that redirect if
        user is authenticated
        '''

        if self.request.user.is_authenticated():
            return redirect(reverse('home'))
        return super().dispatch(*args, **kwargs)


class AboutView(TemplateView):

    '''
    A simple TemplateView for render about page
    '''
    template_name = 'tos_web/about.html'


class HomeView(LoginRequiredMixin, TemplateView):

    '''
    A simple TemplateView with LoginRequiredMixin
    for render home page if user is authenticated
    '''

    template_name = 'tos_web/home.html'


class QueryList(LoginRequiredMixin, ListView):

    '''
    View for list queries of user authenticated
    '''
    template_name = 'tos_web/query_list.html'
    model = Query

    def get_queryset(self):
        '''
        Queryset modified for get queries of a user
        '''
        self.user = self.request.user
        return self.model.objects.filter(user=self.user)


class QueryDelete(LoginRequiredMixin, DeleteView):

    '''
    View for response details of specified query trough pk
    '''
    model = Query
    success_url = reverse_lazy('queries')

    def get_queryset(self):
        '''
        Queryset modified for load queries of user
        '''
        user = self.request.user
        return self.model.objects.filter(user=user)


class QueryDetail(LoginRequiredMixin, JSONResponseMixin, DetailView):

    '''
    View for response details of specified query trough pk
    '''
    template_name = 'tos_web/query_detail.html'
    model = Query

    def get_queryset(self):
        '''
        Queryset modified for load queries of user
        '''
        user = self.request.user
        return self.model.objects.filter(user=user)

    def render_to_response(self, context):
        '''
        Function override for deliver result according
        to the type of request
        '''
        result = self.build_struct_tree(context)
        if self.request.is_ajax():
            return self.render_to_json_response(result)
        return super().render_to_response(context)

    def build_struct_tree(self, context):
        '''
        Function for build and deliver a dictionary with
        nodes collection since tree field of query deserialized

        Args:
            context (dict): Context with object query

        Returns:
            A dict with the nodes extracted and status

        '''

        query = context['object']

        if not query.ready():
            return {'status': 'not ready'}

        tree = pickle.loads(query.tree)
        roots = tree.root()
        trunks = tree.trunk()
        leaves = tree.leave(count=60)

        nodes = []

        for ri, root in zip(reversed(range(len(roots))), roots):
            nodes.append({
                'indice': root.index,
                'label': root['label'],
                'group': 'root',
                'id': 0,
                'degree': root.degree(),
                'ri': ri,
            })

        for ri, trunk in zip(reversed(range(len(trunks))), trunks):
            nodes.append({
                'indice': trunk.index,
                'label': trunk['label'],
                'group': 'trunk',
                'id': 1,
                'degree': trunk.degree(),
                'ri': ri,
            })

        for ri, leave in zip(reversed(range(len(leaves))), leaves):
            nodes.append({
                'indice': leave.index,
                'label': leave['label'],
                'group': 'leaf',
                'id': 2,
                'degree': leave.degree(),
                'ri': ri,
            })

        return {'nodes': nodes, 'status': 'success'}


class QueryExport(CSVResponseMixin, QueryDetail):

    def render_to_response(self, context):
        data = self.build_struct_tree(context)
        return self.render_to_csv(data, context)


class QueryCreate(LoginRequiredMixin, CreateView):

    '''
    Create view for make a query, validate through
    QueryForm.
    '''

    form_class = QueryForm
    template_name = 'tos_web/query_form.html'
    success_url = reverse_lazy('queries')
    model = Query

    def form_valid(self, form):
        # Override form valid for assign the user
        form.instance.user = self.request.user
        return super().form_valid(form)


class LogInView(FormView):

    '''
    View for authenticate a user on ToS
    '''
    form_class = AuthenticationForm
    template_name = 'tos_web/users/login.html'
    success_url = reverse_lazy('home')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Override function get for redirect if a user is authenticated
        if self.request.user.is_authenticated():
            return redirect(reverse('home'))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = auth.authenticate(email=form.cleaned_data.get('email'),
                                 password=form.cleaned_data.get('password'))
        auth.login(self.request, user)
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):

    model = get_user_model()
    form_class = UpdateUserForm
    template_name = 'tos_web/users/update.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        '''
        Queryset modified for get update user authenticated
        '''
        user = self.request.user
        return get_user_model().objects.filter(email=user.email)


class ProfileView(LoginRequiredMixin, DetailView):

    model = get_user_model()
    template_name = 'tos_web/users/profile.html'

    def get_queryset(self):
        '''
        Queryset modified for get update user authenticated
        '''
        user = self.request.user
        return get_user_model().objects.filter(email=user.email)


class LogOutView(TemplateResponseMixin, View):

    '''
    A small view for assure that logout of a user.
    '''

    template_name = 'tos_web/users/logout.html'
    redirect_field_name = 'next'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect(self.get_redirect_url())
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            auth.logout(self.request)
        return redirect(self.get_redirect_url())

    def get_context_data(self, **kwargs):
        context = kwargs
        rfn = self.get_redirect_field_name()
        context.update({
            'redirect_field_name': rfn,
            'redirect_field_valie': self.request.REQUEST.get(rfn),
        })
        return context

    def get_redirect_field_name(self):
        return self.redirect_field_name

    def get_redirect_url(self, falback_url=None, **kwargs):
        if falback_url is None:
            falback_url = reverse('landing')
        kwargs.setdefault(
            "redirect_field_name", self.get_redirect_field_name())
        return default_redirect(self.request, falback_url, **kwargs)


class SignUpView(CreateView):

    '''
    Create a user on ToS if the email user have a
    invitation associated.
    '''

    model = get_user_model()
    form_class = SignUpForm
    template_name = 'tos_web/users/signup.html'
    success_url = reverse_lazy('verify')

    def get(self, *args, **kwargs):
        # The user is authenticated ?
        if self.request.user.is_authenticated():
            return redirect(reverse_lazy('home'))
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        # Override form_valid for create a verification and send email
        response = super().form_valid(form)
        verification = Verification.objects.create(
            user=self.object,
            token="%s" % uuid.uuid4())
        verification_email.delay(form.cleaned_data.get('email'),
                                 form.cleaned_data.get('firstname'),
                                 verification.token)
        return response


class ContactView(FormView):

    '''
    Form for users contact us
    '''
    form_class = ContactForm
    success_url = reverse_lazy('landing')
    template_name = 'tos_web/contact.html'

    def form_valid(self, form):
        # Override form_valid for send email contact
        contact_email.delay(form.cleaned_data.get('email'),
                            form.cleaned_data.get('name'),
                            form.cleaned_data.get('message'))
        return super().form_valid(form)


class InvitationCreateView(LoginRequiredMixin, CreateView):

    '''
    View for invite a potential user since user authenticated
    '''
    form_class = InvitationForm
    model = Invitation
    template_name = 'tos_web/users/invitation.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Override form_valid for associate the user authenticated
        form.instance.inviter = self.request.user
        return super().form_valid(form)


class VerifyView(TemplateView):

    '''
    Render the verify page after a user signup
    '''
    template_name = 'tos_web/users/verify.html'


class VerifyTokenView(RedirectView):

    '''
    View resolve the link sent for verify user account
    '''
    permanent = False
    url = reverse_lazy('login')

    def get_redirect_url(self, *args, **kwargs):
        # Override get_redirect_url for validate token receive
        token = kwargs['token']
        try:
            verification = Verification.objects.get(token=token)
            verification.user.is_active = True
            verification.user.save()
        except Verification.DoesNotExist:
            pass
        return super().get_redirect_url(*args, **kwargs)
