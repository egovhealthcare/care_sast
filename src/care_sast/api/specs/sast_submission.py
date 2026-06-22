from datetime import date, datetime

from care.emr.models.encounter import Encounter
from care.emr.models.patient import Patient
from care.emr.resources.base import EMRResource
from care.facility.models import Facility
from django.shortcuts import get_object_or_404
from pydantic import UUID4, BaseModel, Field, field_validator
from rest_framework.exceptions import ValidationError

from care_sast.models.sast_hospital import SASTHospital
from care_sast.models.sast_submission import SASTSubmission


class SASTSubmissionPayloadSpec(BaseModel):
    """
    Mirror of the SAST gateway ``PatienteBasicDetails`` request body.

    Field names are snake_case for the CARE API; ``serialization_alias`` carries
    the PascalCase key the gateway expects. ``model_dump(by_alias=True)`` (via
    :meth:`to_gateway_dict`) produces the gateway-ready payload.
    """

    patient_name: str = Field(serialization_alias="PatientName")
    age: int = Field(serialization_alias="Age")
    age_time: str = Field(serialization_alias="AGETIME")
    dob: date = Field(serialization_alias="DOB")
    gender: str = Field(serialization_alias="Gender")
    family_head_name: str = Field(serialization_alias="FamilyHeadName")
    payer_zone: str = Field(serialization_alias="PayerZone")
    family_type: str = Field(serialization_alias="FamilyType")
    family_card_type: str = Field(serialization_alias="FamilyCardType")
    family_card_no: str = Field(serialization_alias="FamilyCardNo")
    caste: str = Field(serialization_alias="Caste")
    relation_with_head: str = Field(serialization_alias="RelationwithHead")
    card_issue_date: date | None = Field(default=None, serialization_alias="CardIssueDate")
    date_reporting_nwh: date = Field(serialization_alias="Datereporting_nwh")
    marital_status: str = Field(serialization_alias="MaritalStatus")
    is_child: bool | None = Field(default=None, serialization_alias="Is_child")
    mobile: str = Field(serialization_alias="Mobile")
    email: str | None = Field(default=None, serialization_alias="Email")
    prt_pa_id: str = Field(serialization_alias="PRTpaId")
    patient_ip_no: str = Field(serialization_alias="Patientipno")
    address: str = Field(serialization_alias="Address")
    patient_village: str = Field(serialization_alias="PatientVillage")
    patient_taluk: str = Field(serialization_alias="PatientTaluk")
    patient_district: str = Field(serialization_alias="PatientDistrict")
    patient_state: str = Field(serialization_alias="PatientState")
    patient_country: str = Field(serialization_alias="PatientCountry")
    pincode: str = Field(serialization_alias="Pincode")
    insurance_code: str | None = Field(default=None, serialization_alias="Insurance_Code")
    scheme_id: str | None = Field(default=None, serialization_alias="Schemeid")
    referral_type: str = Field(serialization_alias="ReferalType")
    date_of_referral: date | None = Field(default=None, serialization_alias="Date_of_Referral")
    referral_id: str | None = Field(default=None, serialization_alias="ReferalId")
    referral_remarks: str | None = Field(default=None, serialization_alias="Referrer_Remarks")
    upload_file1: str = Field(serialization_alias="UploadFile1")  # base64 encoded file
    upload_file2: str = Field(serialization_alias="UploadFile2")  # base64 encoded file
    upload_file1_remarks: str | None = Field(default=None, serialization_alias="UploadFile1_remarks")
    upload_file2_remarks: str | None = Field(default=None, serialization_alias="UploadFile2_remarks")
    upload_file1_filetype: str = Field(serialization_alias="UploadFile1_Filetype")
    upload_file2_filetype: str = Field(serialization_alias="UploadFile2_Filetype")
    smart_card_verified_by: str | None = Field(default=None, serialization_alias="SmartCardVerifiedBy")
    department: str | None = Field(default=None, serialization_alias="Department")
    designation: str | None = Field(default=None, serialization_alias="Designation")
    uid_number: str | None = Field(default=None, serialization_alias="UID_number")
    kgid: str | None = Field(default=None, serialization_alias="KGID")
    photo: str = Field(serialization_alias="Photo")  # base64 encoded photo
    family_head_dob: date | None = Field(default=None, serialization_alias="FamilyHeadDob")
    national_identity_type: str | None = Field(default=None, serialization_alias="National_Identity_type")
    national_identity_no: str | None = Field(default=None, serialization_alias="National_Identity_no")
    doa: date = Field(serialization_alias="DOA")
    accident_victim: str | None = Field(default=None, serialization_alias="AccidentVictim")
    is_aadhaar_verified: str | None = Field(default=None, serialization_alias="IsAadharVerified")
    mode_of_verify: str | None = Field(default=None, serialization_alias="ModeofVerify")
    acid_victim: str | None = Field(default=None, serialization_alias="AcidVictim")
    abha_id: str | None = Field(default=None, serialization_alias="Abha_id")
    abha_address: str | None = Field(default=None, serialization_alias="Abha_address")
    ip_op: str | None = Field(default=None, serialization_alias="IP_OP")
    ben_fetch_card_type: str | None = Field(default=None, serialization_alias="Ben_Fetch_Card_type")
    ors_id: str | None = Field(default=None, serialization_alias="ORS_id")
    ors_ref_from_hosp: str | None = Field(default=None, serialization_alias="ORS_Ref_from_hosp")
    district_code: str = Field(serialization_alias="District_Code")
    district_name: str = Field(serialization_alias="District_name")
    taluk_code: str = Field(serialization_alias="Taluk_Code")
    taluk_name: str = Field(serialization_alias="Taluk_Name")
    is_dengue: str | None = Field(default=None, serialization_alias="IsDengue")
    nhm_id: str | None = Field(default=None, serialization_alias="NHM_ID")
    scan_type: str | None = Field(default=None, serialization_alias="ScanType")
    kfd: str | None = Field(default=None, serialization_alias="KFD")
    kutumba_family_id: str | None = Field(default=None, serialization_alias="Kutumba_familyid")
    mobile_verified_flag: str | None = Field(default=None, serialization_alias="MobileVerifiedFlag")
    kutumba_caste_e: str | None = Field(default=None, serialization_alias="Kutumba_caste_E")
    parent_name: str | None = Field(default=None, serialization_alias="Parent_Name")
    parent_age: int | None = Field(default=None, serialization_alias="Parent_Age")
    parent_dob: date | None = Field(default=None, serialization_alias="Parent_DOB")
    parent_gender: str | None = Field(default=None, serialization_alias="Parent_Gender")
    parent_age_time: str | None = Field(default=None, serialization_alias="Parent_Age_time")
    vrn: str | None = Field(default=None, serialization_alias="VRN")
    masked_aadhaar: str | None = Field(default=None, serialization_alias="Masked_Aadhar")

    # Gateway expects dates as dd/MM/yyyy; these alias keys get reformatted on dump.
    _GATEWAY_DATE_ALIASES = (
        "DOB",
        "CardIssueDate",
        "Datereporting_nwh",
        "Date_of_Referral",
        "FamilyHeadDob",
        "DOA",
        "Parent_DOB",
    )

    def to_gateway_dict(self) -> dict:
        data = self.model_dump(by_alias=True, mode="json", exclude_none=True)
        for key in self._GATEWAY_DATE_ALIASES:
            if data.get(key):
                data[key] = datetime.strptime(data[key], "%Y-%m-%d").strftime("%d/%m/%Y")  # noqa: DTZ007
        return data


class SASTSubmissionBaseSpec(EMRResource):
    __model__ = SASTSubmission
    __exclude__ = ["facility", "patient", "encounter"]

    id: UUID4 | None = None


class SASTSubmissionCreateSpec(SASTSubmissionBaseSpec):
    facility: UUID4
    patient: UUID4
    encounter: UUID4
    tpa_code: str
    health_scheme: str
    payload: SASTSubmissionPayloadSpec

    @field_validator("facility")
    @classmethod
    def validate_facility(cls, value):
        if not Facility.objects.filter(external_id=value).exists():
            raise ValidationError("Facility not found")
        if not SASTHospital.objects.filter(facility__external_id=value).exists():
            raise ValidationError("Facility is not mapped to a SAST hospital")
        return value

    @field_validator("patient")
    @classmethod
    def validate_patient(cls, value):
        if not Patient.objects.filter(external_id=value).exists():
            raise ValidationError("Patient not found")
        return value

    @field_validator("encounter")
    @classmethod
    def validate_encounter(cls, value):
        if not Encounter.objects.filter(external_id=value).exists():
            raise ValidationError("Encounter not found")
        return value

    def perform_extra_deserialization(self, is_update, obj):
        obj.facility = get_object_or_404(Facility, external_id=self.facility)
        obj.patient = get_object_or_404(Patient, external_id=self.patient)
        obj.encounter = get_object_or_404(Encounter, external_id=self.encounter)


class SASTSubmissionListSpec(SASTSubmissionBaseSpec):
    facility: UUID4
    patient: UUID4
    encounter: UUID4
    tpa_code: str
    health_scheme: str
    status: str
    hmis_id: str | None = None
    ab_ark_id: str | None = None
    submitted_at: datetime | None = None
    completed_at: datetime | None = None
    created_date: datetime | None = None
    modified_date: datetime | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["id"] = obj.external_id
        mapping["facility"] = obj.facility.external_id
        mapping["patient"] = obj.patient.external_id
        mapping["encounter"] = obj.encounter.external_id


class SASTSubmissionRetrieveSpec(SASTSubmissionListSpec):
    payload: dict | None = None
    gateway_payload: dict | None = None
    gateway_response: dict | None = None
    callback_response: dict | None = None
    errors: list | None = None
