from dime_xai.shared.exceptions.dime_base_exception import DIMEBaseException


class InvalidDIMEExplanationFilePath(DIMEBaseException):
    pass


class NotImplementedException(DIMEBaseException):
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


class ModelFingerprintPersistException(DIMEBaseException):
    pass


class DataFingerprintPersistException(DIMEBaseException):
    pass


class DIMEFingerprintPersistException(DIMEBaseException):
    pass


class InvalidIntentSpecifiedException(DIMEBaseException):
    pass


class InvalidMetricSpecifiedException(DIMEBaseException):
    pass


class InvalidIntentRankingException(DIMEBaseException):
    pass


class NLUDataTaggingException(DIMEBaseException):
    pass


class InvalidNLUTagException(DIMEBaseException):
    pass


class EmptyIntentRankingException(DIMEBaseException):
    pass
