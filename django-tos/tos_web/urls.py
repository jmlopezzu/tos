from django.conf.urls import patterns, url

# New views

from .views import AboutView
from .views import HomeView
from .views import LandingView

from .views import QueryList
from .views import QueryCreate
from .views import QueryDetail
from .views import QueryExport
from .views import QueryDelete

from .views import LogInView
from .views import LogOutView
from .views import SignUpView
from .views import VerifyView
from .views import VerifyTokenView
from .views import InvitationCreateView
from .views import ContactView
# from .views import ProfileUpdateView
# from .views import ProfileView


NEW_URLS = patterns(
    '',

    # Load anding redirect to home for users
    url(r'^$', LandingView.as_view(),
        name='landing'),

    # About page with the article reference and stuff
    url(r'^about$', AboutView.as_view(),
        name='about'),

    # Load home login for unauthenticated users
    url(r'^home$', HomeView.as_view(),
        name='home'),

    # List the bibfiles uploaded
    url(r'^queries$', QueryList.as_view(),
        name='queries'),

    # Deploy an individual query if is_ajax, return json
    url(r'^queries/(?P<pk>\d+)$', QueryDetail.as_view(),
        name='queries-detail'),
    # Export tree to CSV file
    url(r'^queries/(?P<pk>\d+)/export$', QueryExport.as_view(),
        name='queries-export'),
    # Disable (Delete) Queries
    url(r'^queries/(?P<pk>\d+)/delete$', QueryDelete.as_view(),
        name='queries-delete'),
    # Form for upload
    url(r'^queries/create$', QueryCreate.as_view(),
        name='queries-create'),

    # Do the account (harlem) shake
    url(r'^invitations$', InvitationCreateView.as_view(), name='invitations'),
    url(r'^login$', LogInView.as_view(), name='login'),
    url(r'^logout$', LogOutView.as_view(), name='logout'),
    url(r'^signup$', SignUpView.as_view(), name='signup'),
    # Renders a screen that encourages the user to verify its email
    url(r'^verify$', VerifyView.as_view(), name='verify'),
    # Handles the form verification and activates the user, then redirects to
    # login
    url(r'^verify/(?P<token>[-_\w]+)$', VerifyTokenView.as_view(),
        name='verify-token'),
    url(r'^contact$', ContactView.as_view(), name='contact'),
    # url(r'^profile/(?P<pk>\d+)/details$', ProfileView.as_view(),
    #    name='profile'),
    # url(r'^profile/(?P<pk>\d+)/update$', ProfileUpdateView.as_view(),
    #   name='profile-update'),
)

urlpatterns = NEW_URLS
