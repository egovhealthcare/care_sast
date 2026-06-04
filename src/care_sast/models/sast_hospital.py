from care.emr.models.base import EMRBaseModel
from django.db import models


class SASTHospital(EMRBaseModel):
    code = models.CharField(max_length=50)
    facility = models.ForeignKey(
        "facility.Facility", on_delete=models.CASCADE, related_name="sast_hospitals"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(deleted=False),
                name="unique_sast_hospital_code",
            ),
            models.UniqueConstraint(
                fields=["facility"],
                condition=models.Q(deleted=False),
                name="unique_sast_hospital_per_facility",
            ),
        ]

    def __str__(self):
        return f"{self.code} {self.facility}"
