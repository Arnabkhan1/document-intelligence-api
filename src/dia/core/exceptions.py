class AppException(Exception):
    """
    Base exception for application-level errors.
    """

    def __init__(
        self,
        message: str,
        code: str = "APPLICATION_ERROR",
        status_code: int = 400,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code

        super().__init__(message)


class DocumentNotFoundError(AppException):
    def __init__(
        self,
        message: str = "The requested document was not found.",
    ):
        super().__init__(
            message=message,
            code="DOCUMENT_NOT_FOUND",
            status_code=404,
        )


class InvalidDocumentError(AppException):
    def __init__(
        self,
        message: str = "The uploaded document is invalid.",
    ):
        super().__init__(
            message=message,
            code="INVALID_DOCUMENT",
            status_code=400,
        )


class DocumentProcessingError(AppException):
    def __init__(
        self,
        message: str = "Document processing failed.",
    ):
        super().__init__(
            message=message,
            code="DOCUMENT_PROCESSING_ERROR",
            status_code=500,
        )
