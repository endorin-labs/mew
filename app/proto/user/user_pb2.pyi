"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import google.protobuf.descriptor
import google.protobuf.message
import typing

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class SignUpRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    EMAIL_FIELD_NUMBER: builtins.int
    USERNAME_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    DEPARTMENT_FIELD_NUMBER: builtins.int
    PASSWORD_FIELD_NUMBER: builtins.int
    email: builtins.str
    username: builtins.str
    name: builtins.str
    department: builtins.str
    password: builtins.str
    def __init__(
        self,
        *,
        email: builtins.str = ...,
        username: builtins.str = ...,
        name: builtins.str = ...,
        department: builtins.str = ...,
        password: builtins.str = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing.Literal[
            "department",
            b"department",
            "email",
            b"email",
            "name",
            b"name",
            "password",
            b"password",
            "username",
            b"username",
        ],
    ) -> None: ...

global___SignUpRequest = SignUpRequest

@typing.final
class EditProfileRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    USER_ID_FIELD_NUMBER: builtins.int
    EMAIL_FIELD_NUMBER: builtins.int
    USERNAME_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    DEPARTMENT_FIELD_NUMBER: builtins.int
    user_id: builtins.int
    email: builtins.str
    username: builtins.str
    name: builtins.str
    department: builtins.str
    def __init__(
        self,
        *,
        user_id: builtins.int = ...,
        email: builtins.str = ...,
        username: builtins.str = ...,
        name: builtins.str = ...,
        department: builtins.str = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing.Literal[
            "department",
            b"department",
            "email",
            b"email",
            "name",
            b"name",
            "user_id",
            b"user_id",
            "username",
            b"username",
        ],
    ) -> None: ...

global___EditProfileRequest = EditProfileRequest

@typing.final
class LoginRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    USERNAME_FIELD_NUMBER: builtins.int
    PASSWORD_FIELD_NUMBER: builtins.int
    username: builtins.str
    password: builtins.str
    def __init__(
        self,
        *,
        username: builtins.str = ...,
        password: builtins.str = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing.Literal["password", b"password", "username", b"username"],
    ) -> None: ...

global___LoginRequest = LoginRequest

@typing.final
class UserResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    ID_FIELD_NUMBER: builtins.int
    EMAIL_FIELD_NUMBER: builtins.int
    USERNAME_FIELD_NUMBER: builtins.int
    NAME_FIELD_NUMBER: builtins.int
    DEPARTMENT_FIELD_NUMBER: builtins.int
    id: builtins.int
    email: builtins.str
    username: builtins.str
    name: builtins.str
    department: builtins.str
    def __init__(
        self,
        *,
        id: builtins.int = ...,
        email: builtins.str = ...,
        username: builtins.str = ...,
        name: builtins.str = ...,
        department: builtins.str = ...,
    ) -> None: ...
    def ClearField(
        self,
        field_name: typing.Literal[
            "department",
            b"department",
            "email",
            b"email",
            "id",
            b"id",
            "name",
            b"name",
            "username",
            b"username",
        ],
    ) -> None: ...

global___UserResponse = UserResponse

@typing.final
class LoginResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TOKEN_FIELD_NUMBER: builtins.int
    USER_FIELD_NUMBER: builtins.int
    token: builtins.str
    @property
    def user(self) -> global___UserResponse: ...
    def __init__(
        self,
        *,
        token: builtins.str = ...,
        user: global___UserResponse | None = ...,
    ) -> None: ...
    def HasField(
        self, field_name: typing.Literal["user", b"user"]
    ) -> builtins.bool: ...
    def ClearField(
        self, field_name: typing.Literal["token", b"token", "user", b"user"]
    ) -> None: ...

global___LoginResponse = LoginResponse
