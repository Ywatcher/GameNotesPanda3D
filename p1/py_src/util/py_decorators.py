# -*- coding: utf-8-*-

# decorators implementatio
"""
register methods as set of properties for class
https://stackoverflow.com/questions/3054372/auto-register-class-methods-using-decorator


"""


def entries_register(cls):
    registered_entries = set()
    for methodname in dir(cls):
        method = getattr(cls, methodname)
        if hasattr(method, '_entry_dict'):
            for entry_name, method_name_for_entry in method._entry_dict.items():
                if not hasattr(cls, entry_name):
                    setattr(cls, entry_name, {})
                getattr(
                    cls, entry_name).update(
                    {entry_name: method_name_for_entry})
                registered_entries.add(entry_name)
    if not hasattr(cls, '_registered_entries'):
        cls._registered_entries = registered_entries
    else:
        cls._registered_entries = cls._registered_entries.union(
                                                                registered_entries)
    return cls
    # cls._propdict.update(
    #     {cls.__name__ + '.' + methodname: method._prop})


def registertoentry(entry_dict):
    def wrapper(func):
        func._entry_dict = entry_dict
        return func
    return wrapper


"""
decorator as object's member
"""


def selfdecorate(decorator_name: str):
    def decorator(func):
        def outer(self, *args, **kwargs):
            @getattr(self, decorator_name)
            def inner(self, *args, **kwargs):
                return func(self, *args, **kwargs)
            return inner(self, *args, **kwargs)
        return outer
    return decorator
