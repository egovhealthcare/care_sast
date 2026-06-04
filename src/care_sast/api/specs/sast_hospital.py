from datetime import datetime

from care.emr.resources.base import EMRResource
from care.facility.models import Facility
from django.shortcuts import get_object_or_404
from pydantic import UUID4, field_validator, model_validator
from rest_framework.exceptions import ValidationError

from care_sast.models.sast_hospital import SASTHospital


class SASTHospitalBaseSpec(EMRResource):
    __model__ = SASTHospital
    __exclude__ = ["facility"]

    id: UUID4 | None = None


class SASTHospitalCreateSpec(SASTHospitalBaseSpec):
    code: str
    facility: UUID4

    @field_validator("code")
    @classmethod
    def validate_code(cls, value):
        if SASTHospital.objects.filter(code=value).exists():
            raise ValidationError("A hospital with this code already exists")
        return value

    @field_validator("facility")
    @classmethod
    def validate_facility(cls, value):
        if not Facility.objects.filter(external_id=value).exists():
            raise ValidationError("Facility not found")
        if SASTHospital.objects.filter(facility__external_id=value).exists():
            raise ValidationError("A hospital is already mapped to this facility")
        return value

    def perform_extra_deserialization(self, is_update, obj):
        obj.facility = get_object_or_404(Facility, external_id=self.facility)


class SASTHospitalUpdateSpec(SASTHospitalBaseSpec):
    code: str

    @model_validator(mode="after")
    def validate_code(self, info):
        instance = info.context.get("object") if info.context else None
        qs = SASTHospital.objects.filter(code=self.code)
        if instance:
            qs = qs.exclude(id=instance.id)
        if qs.exists():
            raise ValidationError("A hospital with this code already exists")
        return self


class SASTHospitalReadSpec(SASTHospitalBaseSpec):
    code: str
    facility: UUID4
    created_date: datetime | None = None
    modified_date: datetime | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["id"] = obj.external_id
        mapping["facility"] = obj.facility.external_id
