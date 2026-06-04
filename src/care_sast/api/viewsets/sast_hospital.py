from care.emr.api.viewsets.base import (
    EMRBaseViewSet,
    EMRCreateMixin,
    EMRRetrieveMixin,
    EMRUpdateMixin,
)
from care.utils.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters import rest_framework as filters

from care_sast.api.specs.sast_hospital import (
    SASTHospitalCreateSpec,
    SASTHospitalReadSpec,
    SASTHospitalUpdateSpec,
)
from care_sast.models.sast_hospital import SASTHospital


class SASTHospitalFilter(filters.FilterSet):
    code = filters.CharFilter(field_name="code")
    facility = filters.UUIDFilter(field_name="facility__external_id")


class SASTHospitalViewSet(
    EMRCreateMixin,
    EMRRetrieveMixin,
    EMRUpdateMixin,
    EMRBaseViewSet,
):
    database_model = SASTHospital
    pydantic_model = SASTHospitalCreateSpec
    pydantic_update_model = SASTHospitalUpdateSpec
    pydantic_read_model = SASTHospitalReadSpec
    pydantic_retrieve_model = SASTHospitalReadSpec
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SASTHospitalFilter

    def get_queryset(self):
        return self.database_model.objects.all().order_by("-modified_date")

    def get_object(self):
        # Allow lookup by the SAST hospital's external_id or its facility's external_id
        lookup = self.kwargs[self.lookup_field]
        return get_object_or_404(
            self.get_queryset(),
            Q(external_id=lookup) | Q(facility__external_id=lookup),
        )
