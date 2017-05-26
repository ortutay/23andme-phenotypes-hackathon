# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

from my_app.lib.ttam_api.ttam_api.django.views import OauthCallbackView
from .my_app import views as my_app_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', my_app_views.Index.as_view(), name='index'),
    url(r'^results$', my_app_views.Results.as_view(), name='results'),
    url(r'^_status/$', my_app_views.status, name='status'),
    url(r'^_auth_status/$', my_app_views.AuthenticatedStatus.as_view(), name='auth_status'),
    url(r'^receive_code/$', OauthCallbackView.as_view(), name='oauth_callback'),
    url(r'^logout/$', my_app_views.LogoutView.as_view(), name='logout'),
    url(r'^home/$', RedirectView.as_view(url='/'), name='home'),
    url(r'^fitbit-handler/$', my_app_views.FitbitHandlerView.as_view(), name='fitbit-handler'),
    url(r'^facebook-handler/$', my_app_views.FacebookHandlerView.as_view(), name='facebook-handler'),
    url(r'^withings-handler/$', my_app_views.FitbitHandlerView.as_view(), name='withings-handler'),
    url(r'^ihealth-handler/$', my_app_views.FitbitHandlerView.as_view(), name='ihealth-handler'),
    url(r'^ihealth-removal/$', my_app_views.FitbitHandlerView.as_view(), name='ihealth-removal'),
    url(r'^ihealth-pubsub/$', my_app_views.FitbitHandlerView.as_view(), name='ihealth-pubsub'),
    url(r'^omran-handler/$', my_app_views.FitbitHandlerView.as_view(), name='omran-handler'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
