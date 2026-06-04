from care.emr.models.base import EMRBaseModel
from django.db import models


class SASTUser(EMRBaseModel):
    user_id = models.CharField(max_length=50)
    password = models.CharField(max_length=255)

    care_user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="sast_users",
        db_column="care_user_id",
    )
    hospital = models.ForeignKey(
        "care_sast.SASTHospital", on_delete=models.CASCADE, related_name="users"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hospital", "user_id"],
                condition=models.Q(deleted=False),
                name="unique_sast_user_id_per_hospital",
            ),
            models.UniqueConstraint(
                fields=["hospital", "care_user"],
                condition=models.Q(deleted=False),
                name="unique_sast_user_per_hospital",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} {self.hospital}"
