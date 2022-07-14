from dime_xai.shared.exceptions.dime_base_exception import DIMEBaseException


class DIMECoreException(DIMEBaseException):
    pass


class InvalidDIMEExplanationFilePath(DIMECoreException):
    pass


class NotImplementedException(DIMECoreException):
    pass


class DIMEExplanationFileLoadException(DIMECoreException):
    pass


class DIMEExplanationDirectoryException(DIMECoreException):
    pass


class DIMEExplanationFileExistsException(DIMECoreException):
    pass


class DIMEExplanationFilePersistException(DIMECoreException):
    pass


class InvalidDIMEExplanationStructure(DIMECoreException):
    pass


class RasaModelLoadException(DIMECoreException):
    pass


class RESTModelLoadException(DIMECoreException):
    pass


class ModelFingerprintPersistException(DIMECoreException):
    pass


class DataFingerprintPersistException(DIMECoreException):
    pass


class DIMEFingerprintPersistException(DIMECoreException):
    pass


class InvalidIntentSpecifiedException(DIMECoreException):
    pass


class InvalidMetricSpecifiedException(DIMECoreException):
    pass


class InvalidIntentRankingException(DIMECoreException):
    pass


class NLUDataTaggingException(DIMECoreException):
    pass


class InvalidNLUTagException(DIMECoreException):
    pass


class EmptyIntentRankingException(DIMECoreException):
    pass


class DatasetParseException(DIMECoreException):
    pass


class RasaExplainerException(DIMECoreException):
    pass
