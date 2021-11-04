import importlib


def import_name(file_path, name):
    spec = importlib.util.spec_from_file_location("", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, name)
