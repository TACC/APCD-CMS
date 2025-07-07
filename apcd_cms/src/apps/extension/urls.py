from django.urls import path
from apps.extension.views import ExtensionFormTemplate, ExtensionFormApi, ExtensionListTemplate

app_name = 'extension'
urlpatterns = [
    path('extension-request/', ExtensionFormTemplate.as_view(), name='extension'),
    path('list-extensions/', ExtensionListTemplate.as_view(), name='submitted-extensions'),
    path('extension/api/', ExtensionFormApi.as_view(), name='extension-api'),
]
