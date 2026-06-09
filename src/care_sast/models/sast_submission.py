from care.emr.models.base import EMRBaseModel
from django.db import models


class SASTSubmissionStatusChoices(models.TextChoices):
    PENDING = "pending"      # Waiting for submission to the gateway
    SUBMITTED = "submitted"  # Submitted to the gateway with success
    FAILED = "failed"        # Error while submitting to the gateway
    COMPLETED = "completed"  # Callback received from the gateway


class SASTSubmission(EMRBaseModel):
    facility = models.ForeignKey("facility.Facility", on_delete=models.CASCADE)
    patient = models.ForeignKey("emr.Patient", on_delete=models.CASCADE)
    encounter = models.ForeignKey("emr.Encounter", on_delete=models.CASCADE)

    tpa_code = models.CharField(max_length=255, null=False, blank=False)
    health_scheme = models.CharField(max_length=255, null=False, blank=False)
    payload = models.JSONField(null=False, blank=False)

    hmis_id = models.CharField(max_length=255, null=True, blank=True)
    ab_ark_id = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        choices=SASTSubmissionStatusChoices.choices,
        default=SASTSubmissionStatusChoices.PENDING,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    gateway_payload = models.JSONField(null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    callback_response = models.JSONField(null=True, blank=True)

    @property
    def ref_no(self) -> str:
        return self.external_id.hex

    @property
    def errors(self) -> list:
        if not self.gateway_response:
            return []
        return self.gateway_response.get("Errors", [])
