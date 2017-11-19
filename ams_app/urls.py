"""django_ams URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from ams_app import views

urlpatterns = [
    url(r'^assignments/$', views.create_assignment, name='add_assignment'),
    url(r'^assignments/(?P<id>[-\w]+)/pass$', views.pre_submission,
        name='pre_submission'),
    url(r'^assignments/(?P<id>[-\w]+)/submission$', views.submit_assignment,
        name='assignment_submission'),
    url(r'^assignments/(?P<id>[-\w]+)/submissions$', views.assignment_submissions,
        name='submissions'),
    url(r'^assignments/(?P<id>[-\w]+)/$', views.assignment_detail,
        name='assignment_detail'),
    url(r'^assignments/(?P<id>[-\w]+)/delete$', views.delete_assignment,
        name='delete_assignment'),
    url(r'^assignments/(?P<id>[-\w]+)/edit$', views.edit_assignment,
        name='edit_assignment'),
    url(r'^submissions/(?P<id>[-\w]+)/delete$', views.delete_submission,
        name='delete_submission'),
    url(r'^submissions/(?P<id>[-\w]+)/edit$', views.edit_submission,
        name='submission_detail'),
    url(r'^dashboard$', views.dashboard, name='dashboard'),
    # django auth urls
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^logout$', views.logout_user, name='logout'),
    url(r'^$', views.sign_up),
]
