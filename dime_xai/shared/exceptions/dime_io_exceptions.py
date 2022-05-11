from dime_xai.shared.exceptions.dime_base_exception import DIMEBaseException


class DIMEIOException(DIMEBaseException):
    pass


class InvalidInitDirException(DIMEIOException):
    pass


class DIMEProjectExistsException(DIMEIOException):
    pass


class YAMLFormatException(DIMEIOException):
    pass


class NLUFileNotFoundException(DIMEIOException):
    pass


class EmptyNLUDatasetException(DIMEIOException):
    pass


class DIMEConfigException(DIMEBaseException):
    pass


class ConfigFileNotFoundException(DIMEIOException):
    pass


class InvalidMainKeyException(DIMEConfigException):
    pass


class InvalidSubKeyException(DIMEConfigException):
    pass


class InvalidDataTypeException(DIMEConfigException):
    pass


class InvalidInterfaceException(DIMEConfigException):
    pass


class InvalidConfigValueException(DIMEConfigException):
    pass


class InvalidConfigPropertyException(DIMEConfigException):
    pass


class MissingConfigPropertyException(DIMEConfigException):
    pass


class InvalidURLSpecifiedException(DIMEConfigException):
    pass


class InvalidPathSpecifiedException(DIMEIOException):
    pass


class ModelNotFoundException(DIMEIOException):
    pass


class ModelLoadException(DIMEIOException):
    pass
