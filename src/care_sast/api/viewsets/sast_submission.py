from care.emr.api.viewsets.base import (
    EMRBaseViewSet,
    EMRCreateMixin,
    EMRListMixin,
    EMRRetrieveMixin,
)
from django_filters import rest_framework as filters

from care_sast.api.specs.sast_submission import (
    SASTSubmissionCreateSpec,
    SASTSubmissionListSpec,
    SASTSubmissionRetrieveSpec,
)
from care_sast.models.sast_submission import SASTSubmission
from care_sast.services.gateway import GatewayService


class SASTSubmissionFilter(filters.FilterSet):
    facility = filters.UUIDFilter(field_name="facility__external_id")
    patient = filters.UUIDFilter(field_name="patient__external_id")
    encounter = filters.UUIDFilter(field_name="encounter__external_id")
    status = filters.CharFilter(field_name="status")


class SASTSubmissionViewSet(
    EMRCreateMixin,
    EMRListMixin,
    EMRRetrieveMixin,
    EMRBaseViewSet,
):
    database_model = SASTSubmission
    pydantic_model = SASTSubmissionCreateSpec
    pydantic_read_model = SASTSubmissionListSpec
    pydantic_retrieve_model = SASTSubmissionRetrieveSpec
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SASTSubmissionFilter

    def get_queryset(self):
        return self.database_model.objects.all().order_by("-modified_date")

    def perform_create(self, instance):
        super().perform_create(instance)
        GatewayService().patient_submit(instance)
