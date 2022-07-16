from dime_xai.shared.exceptions.dime_base_exception import DIMEBaseException


class DIMEServerException(DIMEBaseException):
    pass


class DIMEServerNotFoundException(DIMEServerException):
    pass


class ProcessTerminationException(DIMEServerException):
    pass


class InvalidProcessIDException(DIMEServerException):
    pass


class ProcessQueueException(DIMEServerException):
    pass


class ProcessQueuePushException(DIMEServerException):
    pass


class ProcessQueueUpdateException(DIMEServerException):
    pass


class ProcessQueuePullException(DIMEServerException):
    pass


class ProcessAlreadyExistsException(DIMEServerException):
    pass


class ProcessNotExistsException(DIMEServerException):
    pass


class MetadataRetrievalException(DIMEServerException):
    pass


class InvalidRequestIDException(DIMEServerException):
    pass


class ServerCacheException(DIMEServerException):
    pass


class ServerCachePushException(DIMEServerException):
    pass


class ServerCachePullException(DIMEServerException):
    pass


class ModelNotFoundException(DIMEServerException):
    pass


class ExplanationNotFoundException(DIMEServerException):
    pass


class InvalidExplanationSpecifiedException(DIMEServerException):
    pass


class InvalidServerConfigsException(DIMEServerException):
    pass


class ServerConfigsPersistException(DIMEServerException):
    pass


class InvalidConfigurationTypeSpecifiedException(DIMEServerException):
    pass


class CustomConfigsNotFoundException(DIMEServerException):
    pass
