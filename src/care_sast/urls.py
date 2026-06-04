from django.conf import settings
from django.shortcuts import HttpResponse
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from care_sast.api.viewsets.callback import CallbackViewSet
from care_sast.api.viewsets.sast_hospital import SASTHospitalViewSet
from care_sast.api.viewsets.sast_submission import SASTSubmissionViewSet
from care_sast.api.viewsets.sast_user import SASTUserViewSet


def healthy(request):
    return HttpResponse("OK")


router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("submission", SASTSubmissionViewSet, basename="care_sast-submission")
router.register("hospital", SASTHospitalViewSet, basename="care_sast-hospital")
router.register("user", SASTUserViewSet, basename="care_sast-user")

callback_router = (
    DefaultRouter(trailing_slash=False)
    if settings.DEBUG
    else SimpleRouter(trailing_slash=False)
)
callback_router.register("callback", CallbackViewSet, basename="care_sast-callback")

urlpatterns = [
    path("health", healthy),
    *router.urls,
    *callback_router.urls,
]
