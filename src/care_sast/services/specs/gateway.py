from pydantic import BaseModel, ConfigDict, Field


class PatientSubmitSuccessData(BaseModel):
    message: str
    hmis_id: str


class PatientSubmitResponseData(BaseModel):
    success: bool
    errors: list[str]
    data: PatientSubmitSuccessData | None


class CallbackRequestData(BaseModel):
    """
    Inbound payload posted by the gateway to
    ``<callback endpoint>/<HospCode>/<RefNo>`` once a submission is processed.
    """

    model_config = ConfigDict(populate_by_name=True)

    hmis_id: str = Field(validation_alias="Hmis_ID")
    ab_ark_id: str = Field(validation_alias="AbArkId")
    hosp_code: str = Field(validation_alias="HospCode")
    patient_name: str = Field(validation_alias="PatientName")
    age: int = Field(validation_alias="Age")
    age_time: str = Field(validation_alias="AGETIME")
    dob: str = Field(validation_alias="DOB")
    gender: str | None = Field(default=None, validation_alias="Gender")
