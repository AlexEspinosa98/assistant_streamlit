from langchain_core.pydantic_v1 import BaseModel, Field


class ResponseModel(BaseModel):
    """Information about a person."""

    response: str = Field(..., description= "Response from the model")


class InformationModel(BaseModel):
    """Information about a person."""

    identificacion: str = Field(..., description="Identification number of the person")
    nombre: str = Field(..., description="Full name of the person")
    telefono: str = Field(..., description="Phone number of the person")
    correo: str = Field(..., description="Email address of the person")
    is_new: bool = Field(..., description="Indicates if the person is new or already registered")
    is_complete: bool = Field(..., description="Indicates if the information provided is complete")
    response : str = Field(..., description="Response message to continue the interaction")

    class Config:
        schema_extra = {
            "example": {
                "identificacion": "1234567890",
                "nombre": "Juan Pérez",
                "telefono": "3001234567",
                "correo": "juan.perez@example.com"
            }
        }


class IntentUser(BaseModel):
    """Intent for user interaction."""

    greeting: bool  = Field(..., description="Indicates if the user is greeting or being polite")
    ask_for_info: bool = Field(..., description="Indicates if the user is asking for information about the service or product")
    data_personal: bool = Field(..., description="Indicates if the user is providing personal data")
