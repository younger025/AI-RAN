class URANError(Exception):
    pass


class ValidationError(URANError):
    pass


class ModuleLoadError(URANError):
    pass


class RuntimeFallbackTriggered(URANError):
    pass