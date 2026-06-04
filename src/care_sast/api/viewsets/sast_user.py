from care.emr.api.viewsets.base import (
    EMRBaseViewSet,
    EMRCreateMixin,
    EMRDestroyMixin,
    EMRListMixin,
    EMRUpdateMixin,
)
from django_filters import rest_framework as filters

from care_sast.api.specs.sast_user import (
    SASTUserCreateSpec,
    SASTUserReadSpec,
    SASTUserUpdateSpec,
)
from care_sast.models.sast_user import SASTUser


class SASTUserFilter(filters.FilterSet):
    hospital = filters.UUIDFilter(field_name="hospital__external_id")
    user = filters.UUIDFilter(field_name="care_user__external_id")
    user_id = filters.CharFilter(field_name="user_id")


class SASTUserViewSet(
    EMRCreateMixin,
    EMRListMixin,
    EMRUpdateMixin,
    EMRDestroyMixin,
    EMRBaseViewSet,
):
    database_model = SASTUser
    pydantic_model = SASTUserCreateSpec
    pydantic_update_model = SASTUserUpdateSpec
    pydantic_read_model = SASTUserReadSpec
    pydantic_retrieve_model = SASTUserReadSpec
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SASTUserFilter

    def get_queryset(self):
        return self.database_model.objects.all().order_by("-modified_date")
