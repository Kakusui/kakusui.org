## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from pydantic import BaseModel, EmailStr, Field

from kairyou_runtime import MAX_REPLACEMENTS_JSON_BYTES, MAX_TEXT_LENGTH

MAX_LLM_TEXT_LENGTH = 100_000
MAX_LLM_INSTRUCTIONS_LENGTH = 5_000
MAX_LLM_TYPE_LENGTH = 32
MAX_API_KEY_LENGTH = 4_096
MAX_MODEL_NAME_LENGTH = 256
MAX_TURNSTILE_TOKEN_LENGTH = 4_096

class LoginModel(BaseModel):
    email:EmailStr = Field(max_length=320)
    verification_code:str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class LoginToken(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    email:str

class SendVerificationEmailRequest(BaseModel):
    email:EmailStr = Field(max_length=320)
    clientID:str = Field(min_length=1, max_length=128)
    turnstile_token:str | None = Field(default=None, max_length=MAX_TURNSTILE_TOKEN_LENGTH)

class VerifyEmailCodeRequest(BaseModel):
    email:EmailStr = Field(max_length=320)
    code:str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class VerifyTurnstileRequest(BaseModel):
    token:str = Field(min_length=1, max_length=MAX_TURNSTILE_TOKEN_LENGTH)

class RegisterForEmailAlert(BaseModel):
    email:EmailStr = Field(max_length=320)

class KairyouRequest(BaseModel):
    textToPreprocess:str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)
    replacementsJson:str = Field(min_length=2, max_length=MAX_REPLACEMENTS_JSON_BYTES)
    turnstile_token:str | None = Field(default=None, max_length=MAX_TURNSTILE_TOKEN_LENGTH)

class EasyTLRequest(BaseModel):
    textToTranslate:str = Field(max_length=MAX_LLM_TEXT_LENGTH)
    translationInstructions:str = Field(max_length=MAX_LLM_INSTRUCTIONS_LENGTH)
    llmType:str = Field(min_length=1, max_length=MAX_LLM_TYPE_LENGTH)
    userAPIKey:str = Field(max_length=MAX_API_KEY_LENGTH)
    model:str = Field(min_length=1, max_length=MAX_MODEL_NAME_LENGTH)
    using_credits:bool
    turnstile_token:str | None = Field(default=None, max_length=MAX_TURNSTILE_TOKEN_LENGTH)

class ElucidateRequest(BaseModel):
    textToEvaluate:str = Field(max_length=MAX_LLM_TEXT_LENGTH)
    evaluationInstructions:str = Field(max_length=MAX_LLM_INSTRUCTIONS_LENGTH)
    llmType:str = Field(min_length=1, max_length=MAX_LLM_TYPE_LENGTH)
    userAPIKey:str = Field(max_length=MAX_API_KEY_LENGTH)
    model:str = Field(min_length=1, max_length=MAX_MODEL_NAME_LENGTH)
    turnstile_token:str | None = Field(default=None, max_length=MAX_TURNSTILE_TOKEN_LENGTH)

class EmailRequest(BaseModel):
    subject:str = Field(min_length=1, max_length=256)
    body:str = Field(min_length=1, max_length=100_000)

class FeedbackEmailRequest(BaseModel):
    email:EmailStr
    text:str = Field(min_length=1, max_length=50_000)
    turnstile_token:str | None = Field(default=None, max_length=MAX_TURNSTILE_TOKEN_LENGTH)

class TokenCostRequest(BaseModel):
    text_to_translate:str = Field(max_length=MAX_LLM_TEXT_LENGTH)
    translation_instructions:str = Field(max_length=MAX_LLM_INSTRUCTIONS_LENGTH)
    model:str = Field(min_length=1, max_length=MAX_MODEL_NAME_LENGTH)

class GoogleLoginRequest(BaseModel):
    token:str = Field(min_length=1, max_length=16_384)

class LanguageDetectionRequest(BaseModel):
    text:str = Field(max_length=MAX_LLM_TEXT_LENGTH)
    llmType:str = Field(min_length=1, max_length=MAX_LLM_TYPE_LENGTH)
    userAPIKey:str = Field(max_length=MAX_API_KEY_LENGTH)
    model:str = Field(min_length=1, max_length=MAX_MODEL_NAME_LENGTH)
    using_credits:bool
    turnstile_token:str | None = Field(default=None, max_length=MAX_TURNSTILE_TOKEN_LENGTH)

class StripeCheckoutRequest(BaseModel):
    is_home_page:bool = True
