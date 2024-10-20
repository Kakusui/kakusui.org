## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from pydantic import BaseModel, EmailStr

class LoginModel(BaseModel):
    email:str
    verification_code:str

class LoginToken(BaseModel):
    access_token:str
    token_type:str
    refresh_token:str

class TokenData(BaseModel):
    email:str

class SendVerificationEmailRequest(BaseModel):
    email:str
    clientID:str

class VerifyEmailCodeRequest(BaseModel):
    email:str
    code:str

class RegisterForEmailAlert(BaseModel):
    email:str

class KairyouRequest(BaseModel):
    textToPreprocess:str
    replacementsJson:str

class EasyTLRequest(BaseModel):
    textToTranslate:str
    translationInstructions:str
    llmType:str
    userAPIKey:str
    model:str
    using_credits:bool

class ElucidateRequest(BaseModel):
    textToEvaluate:str
    evaluationInstructions:str
    llmType:str
    userAPIKey:str
    model:str

class VerifyTurnstileRequest(BaseModel):
    token:str

class EmailRequest(BaseModel):
    subject:str
    body:str

class FeedbackEmailRequest(BaseModel):
    email:EmailStr
    text:str

class TokenCostRequest(BaseModel):
    text_to_translate:str
    translation_instructions:str
    model:str

class GoogleLoginRequest(BaseModel):
    token:str