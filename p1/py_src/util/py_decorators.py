# -*- coding: utf-8-*-

# decorators implementations
"""
register methods as set of properties for class
https://stackoverflow.com/questions/3054372/auto-register-class-methods-using-decorator

example:
---
>>> @entries_register
    class FoodAllocator:
        @registertoentry({"food_list":"flour"})
        def flour_kg(self, n_people):
            return 0.9 * n_people
...
        @registertoentry({"food_list":"apple"})
        def apple_kg(self, n_people):
            return 0.6 * n_people
...
        @registertoentry({"food_list":"steak"})
        def steak_kg(self, n_people):
            return 0.8 * n_people
...
        def all_food_kg(self, n_people):
            return sum([
                self.food_list[food](self, n_people)
                for food in self.food_list
            ])

>>> allocator = FoodAllocator()
>>> allocator.food_list
{'apple': <function __main__.FoodAllocator.apple_kg(self, n_people)>,
 'flour': <function __main__.FoodAllocator.flour_kg(self, n_people)>,
 'steak': <function __main__.FoodAllocator.steak_kg(self, n_people)>}
>>> allocator.food_list["apple"](allocator, 2)
1.2
>>> allocator.all_food_kg(2)
4.6
"""


def entries_register(cls):
    """
    used as class decorator
    """
    registered_entries = set()
    for methodname in dir(cls):
        method = getattr(cls, methodname)
        if hasattr(method, '_entry_dict'):
            for entry_name, methodname_for_entry in method._entry_dict.items():
                if not hasattr(cls, entry_name):
                    setattr(cls, entry_name, {})
                getattr(
                    cls, entry_name).update(
                    {methodname_for_entry: method})
                registered_entries.add(entry_name)
    if not hasattr(cls, '_registered_entries'):
        cls._registered_entries = registered_entries
    else:
        cls._registered_entries = registered_entries.union(
            cls._registered_entries
        )
    return cls


def registertoentry(entry_dict):
    """
    used as method decorator
    """
    def wrapper(func):
        func._entry_dict = entry_dict
        return func
    return wrapper


"""
decorator as object's member

example
---
>>> class SelfDec:
        def __init__(self):
            self.a = 'is a'
            self.b = 'is b'
...
        def dec(self, func):
            print(self.a)
            return func
...
        @selfdecorate('dec')
        def func(self):
            print(self.b)

>>> s = SelfDec()
>>> s.func()
is a
is b
"""


def selfdecorate(decorator_name: str):
    """
    this function allows you to use an object method as decorator
    for another method of this object
    """
    def decorator(func):
        def outer(self, *args, **kwargs):
            @getattr(self, decorator_name)
            def inner(self, *args, **kwargs):
                return func(self, *args, **kwargs)
            return inner(self, *args, **kwargs)
        return outer
    return decorator
