from django.urls import path
from apps.exception.views import ExceptionFormTemplate, ExceptionFormApi, ExceptionListTemplate


app_name = 'exception'
urlpatterns = [
    path('exception/', ExceptionFormTemplate.as_view(), name='exception'),
    path('list-exceptions/', ExceptionListTemplate.as_view(), name='submitted-exceptions'),
    path('exception/api/', ExceptionFormApi.as_view(), name='exception-api'),
]
