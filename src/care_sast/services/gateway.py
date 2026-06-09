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

    def _redact_payload(self, payload: dict) -> dict:
        redacted = dict(payload)
        if redacted.get("Password"):
            redacted["Password"] = "***"
        return redacted

    def patient_submit(self, submission: SASTSubmission) -> SASTSubmission:
        url = f"{self.base_endpoint}/PatienteBasicDetails"
        payload = self._build_payload(submission)
        submission.gateway_payload = self._redact_payload(payload)

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=plugin_settings.CARE_SAST_GATEWAY_API_TIMEOUT,
            )
        except requests.RequestException as exc:
            exc_response = exc.response
            status_code = exc_response.status_code if exc_response is not None else None
            response_text = exc_response.text if exc_response is not None else None
            logger.exception(
                "SAST gateway submission failed for %s (HTTP %s): %s",
                submission.ref_no,
                status_code,
                response_text,
            )
            submission.status = SASTSubmissionStatusChoices.FAILED
            submission.gateway_response = {
                "Success": False,
                "Errors": [str(exc)],
                "Data": None,
                "StatusCode": status_code,
                "RawResponse": response_text,
            }
            submission.save(
                update_fields=["status", "gateway_payload", "gateway_response", "modified_date"]
            )
            return submission

        try:
            response_data = response.json()
        except ValueError:
            logger.exception(
                "SAST gateway returned a non-JSON response for %s (HTTP %s): %s",
                submission.ref_no,
                response.status_code,
                response.text,
            )
            submission.status = SASTSubmissionStatusChoices.FAILED
            submission.gateway_response = {
                "Success": False,
                "Errors": [f"Unexpected gateway response (HTTP {response.status_code})"],
                "Data": None,
                "StatusCode": response.status_code,
                "RawResponse": response.text,
            }
            submission.save(
                update_fields=["status", "gateway_payload", "gateway_response", "modified_date"]
            )
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

        submission.gateway_response = response_data
        if result.success:
            submission.status = SASTSubmissionStatusChoices.SUBMITTED
            submission.submitted_at = timezone.now()
            if result.data:
                submission.hmis_id = result.data.hmis_id or submission.hmis_id
        else:
            submission.status = SASTSubmissionStatusChoices.FAILED

        submission.save(
            update_fields=[
                "status",
                "submitted_at",
                "gateway_payload",
                "gateway_response",
                "hmis_id",
                "modified_date",
            ]
        )
        return submission
