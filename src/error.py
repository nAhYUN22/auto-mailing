from enum import Enum


class CustomErrorType(Enum):
    NOT_RELEASE = "Not release yet"  # 패치가 안떴을 때
    EMPTY_VALUE = "Empty value"  # 특정 값이 비어있을 때
    INVALID_INPUT = "Invalid input provided"  # 유효성 검사에서 에러났을 때
    NETWORK_FAILURE = "Network failure"  # 네트워크 끊어졌을 때
    FILE_NOT_FOUND = "File not found"  # 파일을 찾지 못할 때
    MALICIOUS_FILE = "Malicious File"  # 악성 파일
    UNKNOWN_ERROR = "Unknown error"
    TIMEOUT = "Timeout error"


class CustomError(Exception):
    def __init__(self, error_type: CustomErrorType, message: str):
        self.error_type = error_type
        self.message = message

    def __str__(self):
        return f"[{self.error_type.name}] {self.message}"

    @staticmethod
    def raise_error(error_type: CustomErrorType):
        error_messages = {
            CustomErrorType.NOT_RELEASE: "New patch is not released yet",
            CustomErrorType.EMPTY_VALUE: "The input data is empty value",
            CustomErrorType.INVALID_INPUT: "The provided input data does not match the required format.",
            CustomErrorType.NETWORK_FAILURE: "Could not reach the network.",
            CustomErrorType.FILE_NOT_FOUND: "File Not Found",
            CustomErrorType.MALICIOUS_FILE: "Malicious File",
            CustomErrorType.UNKNOWN_ERROR: "An unknown error has occurred.",
            CustomErrorType.TIMEOUT: "Timeout error",
        }
        raise CustomError(
            error_type, error_messages.get(error_type, "An unknown error has occurred.")
        )
