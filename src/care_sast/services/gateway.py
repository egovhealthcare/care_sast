import logging

import requests
from django.utils import timezone

from care_sast.api.specs.sast_submission import SASTSubmissionPayloadSpec
from care_sast.models.sast_submission import (
    SASTSubmission,
    SASTSubmissionStatusChoices,
)
from care_sast.services.specs.gateway import PatientSubmitResponseData
from care_sast.settings import plugin_settings

logger = logging.getLogger(__name__)


class GatewayService:
    def __init__(self):
        self.base_endpoint = plugin_settings.CARE_SAST_GATEWAY_API_BASE_URL.rstrip("/") + "/api/HMIS"

    def _callback_url(self, hosp_code: str, ref_no: str) -> str:
        domain = plugin_settings.BACKEND_DOMAIN
        if not domain.startswith(("http://", "https://")):
            domain = f"https://{domain}"
        return f"{domain.rstrip('/')}/api/care_sast/callback/submission/"

    def _build_payload(self, submission: SASTSubmission) -> dict:
        payload = SASTSubmissionPayloadSpec(**submission.payload).to_gateway_dict()

        hospital = submission.facility.sast_hospitals.first()
        hosp_code = hospital.code

        sast_user = hospital.users.filter(care_user=submission.created_by).first()
        user_id = sast_user.user_id if sast_user else plugin_settings.CARE_SAST_GATEWAY_USER_ID
        password = sast_user.password if sast_user else plugin_settings.CARE_SAST_GATEWAY_PASSWORD

        payload.update(
            {
                "HospCode": hosp_code,
                "Refno": submission.ref_no,
                "TpaCode": submission.tpa_code,
                "Health_scheme": submission.health_scheme,
                "Userid": user_id,
                "Password": password,
                "CallBack_Url": self._callback_url(hosp_code, submission.ref_no),
            }
        )
        return payload

    def patient_submit(self, submission: SASTSubmission) -> SASTSubmission:
        url = f"{self.base_endpoint}/PatienteBasicDetails"
        payload = self._build_payload(submission)

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=plugin_settings.CARE_SAST_GATEWAY_API_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as exc:
            logger.exception("SAST gateway submission failed for %s", submission.ref_no)
            submission.status = SASTSubmissionStatusChoices.FAILED
            submission.errors = [str(exc)]
            submission.save(update_fields=["status", "errors", "modified_date"])
            return submission

        data = response_data.get("Data") or {}
        result = PatientSubmitResponseData(
            success=response_data.get("Success", False),
            errors=response_data.get("Errors", []),
            data=(
                {
                    "message": data.get("message", ""),
                    "hmis_id": data.get("Hmis_ID") or data.get("hmis_id") or "",
                }
                if data
                else None
            ),
        )

        if result.success:
            submission.status = SASTSubmissionStatusChoices.SUBMITTED
            submission.submitted_at = timezone.now()
            submission.errors = []
            if result.data:
                submission.hmis_id = result.data.hmis_id or submission.hmis_id
        else:
            submission.status = SASTSubmissionStatusChoices.FAILED
            submission.errors = result.errors

        submission.save(
            update_fields=[
                "status",
                "submitted_at",
                "errors",
                "hmis_id",
                "modified_date",
            ]
        )
        return submission
