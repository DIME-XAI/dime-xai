from dime_xai.shared.exceptions.dime_base_exception import DIMEBaseException


class InvalidDIMEExplanationFilePath(DIMEBaseException):
    pass


class DIMEExplanationFileLoadException(DIMEBaseException):
    pass


class DIMEExplanationDirectoryException(DIMEBaseException):
    pass


class DIMEExplanationFileExistsException(DIMEBaseException):
    pass


class DIMEExplanationFilePersistException(DIMEBaseException):
    pass


class InvalidDIMEExplanationStructure(DIMEBaseException):
    pass


class RESTModelLoadException(DIMEBaseException):
    pass
