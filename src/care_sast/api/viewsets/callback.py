import logging

from care.emr.api.viewsets.base import EMRBaseViewSet
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from care_sast.models.sast_submission import (
    SASTSubmission,
    SASTSubmissionStatusChoices,
)
from care_sast.services.specs.gateway import CallbackRequestData

logger = logging.getLogger(__name__)


class CallbackViewSet(EMRBaseViewSet):
    authentication_classes = []
    permission_classes = []

    @extend_schema(request=CallbackRequestData, responses={200: None})
    @action(
        detail=False,
        methods=["POST"],
        url_path=r"submission/(?P<hosp_code>[^/.]+)/(?P<ref_no>[^/.]+)",
    )
    def handle(self, request, hosp_code=None, ref_no=None, *args, **kwargs):
        submission = SASTSubmission.objects.filter(external_id=ref_no).first()
        if submission is None:
            return Response(
                {
                    "success": False,
                    "errors": [f"No submission found for ref no {ref_no}"],
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        body = CallbackRequestData.model_validate(request.data)

        submission.hmis_id = body.hmis_id
        submission.ab_ark_id = body.ab_ark_id
        submission.callback_response = body.model_dump(mode="json")
        submission.status = SASTSubmissionStatusChoices.COMPLETED
        submission.completed_at = timezone.now()
        submission.save(
            update_fields=[
                "hmis_id",
                "ab_ark_id",
                "callback_response",
                "status",
                "completed_at",
                "modified_date",
            ]
        )

        return Response(
            {
                "success": True,
                "errors": [],
                "data": {
                    "message": "Record saved successfully.",
                    "Hmis_ID": submission.hmis_id,
                },
            },
            status=status.HTTP_200_OK,
        )
