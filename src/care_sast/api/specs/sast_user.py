from datetime import datetime

from care.emr.resources.base import EMRResource
from care.users.models import User
from django.shortcuts import get_object_or_404
from pydantic import UUID4, field_validator, model_validator
from rest_framework.exceptions import ValidationError

from care_sast.models.sast_hospital import SASTHospital
from care_sast.models.sast_user import SASTUser


class SASTUserBaseSpec(EMRResource):
    __model__ = SASTUser
    __exclude__ = ["hospital", "user"]

    id: UUID4 | None = None


class SASTUserCreateSpec(SASTUserBaseSpec):
    hospital: UUID4
    user: UUID4
    user_id: str
    password: str

    @field_validator("hospital")
    @classmethod
    def validate_hospital(cls, value):
        if not SASTHospital.objects.filter(external_id=value).exists():
            raise ValidationError("Hospital not found")
        return value

    @field_validator("user")
    @classmethod
    def validate_user(cls, value):
        if not User.objects.filter(external_id=value).exists():
            raise ValidationError("User not found")
        return value

    @model_validator(mode="after")
    def validate_unique_constraints(self):
        hospital = SASTHospital.objects.filter(external_id=self.hospital).first()
        if not hospital:
            return self
        if SASTUser.objects.filter(hospital=hospital, user_id=self.user_id).exists():
            raise ValidationError(
                "A user with this user_id already exists for the hospital"
            )
        if SASTUser.objects.filter(
            hospital=hospital, care_user__external_id=self.user
        ).exists():
            raise ValidationError(
                "A SAST user already exists for this user in the hospital"
            )
        return self

    def perform_extra_deserialization(self, is_update, obj):
        obj.hospital = get_object_or_404(SASTHospital, external_id=self.hospital)
        obj.care_user = get_object_or_404(User, external_id=self.user)


class SASTUserUpdateSpec(SASTUserBaseSpec):
    user_id: str
    password: str

    @model_validator(mode="after")
    def validate_unique_user_id(self, info):
        instance = info.context.get("object") if info.context else None
        if instance:
            qs = SASTUser.objects.filter(
                hospital=instance.hospital, user_id=self.user_id
            ).exclude(id=instance.id)
            if qs.exists():
                raise ValidationError(
                    "A user with this user_id already exists for the hospital"
                )
        return self


class SASTUserReadSpec(SASTUserBaseSpec):
    user_id: str
    hospital: UUID4
    user: UUID4
    created_date: datetime | None = None
    modified_date: datetime | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["id"] = obj.external_id
        mapping["hospital"] = obj.hospital.external_id
        mapping["user"] = obj.care_user.external_id
