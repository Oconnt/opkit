import inspect
import pkgutil
import importlib


def get_package_modules(package):
    if isinstance(package, str):
        package = importlib.import_module(package)

    modules = []
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if is_pkg:
            modules.extend(get_package_modules('.'.join([package.__name__, name])))
        else:
            full_name = '.'.join([package.__name__, name])
            mod = importlib.import_module(full_name)
            modules.append(mod)

    return modules


def get_subclasses(cls, modules):
    subclasses = []

    for mod in modules:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, cls) and obj is not cls:
                subclasses.append(obj)

    subclasses = list(dict.fromkeys(subclasses))
    return subclasses


def get_method_params(cls, method_name):
    method = getattr(cls, method_name)
    params = inspect.signature(method).parameters

    return params
