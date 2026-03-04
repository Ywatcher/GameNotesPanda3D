"""
manage names of certain class of objects,
so that they have legal identifier 

# example
def add_camera_prefix(name: str) -> str:
    return f"view_{name}"

@managed_name(transform=add_camera_prefix)
class RenderView:
    def __init__(self, data):
        self.data = data

r1 = RenderView("data1")
r2 = RenderView("data2")
r3 = RenderView("data3", name="main")

print(RenderView.all_objects())  
# {'view_renderview': <RenderView object>, 'view_renderview_1': <RenderView object>, 'view_main': <RenderView object>}

print(RenderView.get_object("view_renderview_1"))  # 返回 r2

print(RenderView.query_objects("view"))  
# {'view': <r1>, 'view_1': <r2>}



"""

import re
from functools import wraps
import weakref

class NameManager:
    @property
    def _used_names(self) -> set:
        return set(self._obj_map.keys())

    def __init__(self, tag=None):
        self.tag = tag
        self._counters: dict[str, int] = {}
        # delete unused objects autmatically
        self._obj_map: dict[str, object]  = weakref.WeakValueDictionary()

    def __repr__(self):
        return f"NameManager[{self.tag}]"

    def generate_name(self, base_name: str="", transform: callable = None) -> str:
        if base_name is None:
            base_name = ""
        candidate = base_name
        if transform:
            candidate = transform(candidate)
        if len(candidate) == 0:
            candidate = str(id(candidate))[:4]
        if candidate not in self._used_names:
            return candidate

        if candidate not in self._counters:
            self._counters[candidate] = 1

        while True:
            new_name = f"{candidate}_{self._counters[candidate]}"
            self._counters[candidate] += 1
            if new_name not in self._used_names:
                return new_name

    def assign_name(self, obj, base_name: str, transform: callable = None) -> str:
        name = self.generate_name(base_name, transform)
        self._obj_map[name] = obj
        return name

    def release_name(self, name: str):
        self._obj_map.pop(name, None)

    def get_object(self, name: str):
        return self._obj_map.get(name)

    def query_objects(self, pattern: str):
        regex = re.compile(pattern)
        return {name: obj for name, obj in self._obj_map.items() if regex.search(name)}

    @property
    def all_objects(self):
        return dict(self._obj_map)


def managed_name(name_attr="name",transform=None, manager=None, name_param="name"):
    """
    name_attr: the object attribute name for naming 
    transform: the transform applied for name
    manager: naming manager instance 
    name_param: the parameter name at __init__ for naming
    """
    if manager is None:
        manager = NameManager()

    def decorator(cls):
        original_init = cls.__init__
        if manager.tag is None:
            manager.tag = cls.__name__
        cls._name_manager = manager

        if not hasattr(cls, "_default_basename"):
            @classmethod
            def _default_basename(cls_):
                return cls_.__name__.lower()
            cls._default_basename = _default_basename

        @wraps(original_init)
        def new_init(self, *args,  **kwargs):
            input_name = kwargs.pop(name_param, None)
            original_init(self, *args, **kwargs)
            # use class name if not specfied
            if not hasattr(self, name_attr):
                base_name = input_name if input_name is not None else self.__class__._default_basename()
                assigned_name = manager.assign_name(self, base_name, transform)
                setattr(self, name_attr, assigned_name)
                self._name_manager = manager

        cls.__init__ = new_init

        # release a name (when an object is not used any more)
        def release(self):
            if hasattr(self, name_attr):
                manager.release_name(getattr(self, name_attr))
        cls.release_name = release

        # get all names for the class and map to their objects 
        @classmethod
        def all_objects(cls_):
            return dict(manager._obj_map)
        cls.all_objects = all_objects

        # get single object by its name 
        @classmethod
        def get_object(cls_, name: str):
            return manager.get_object(name)
        cls.get_object = get_object

        # query a list of objects with name pattern
        @classmethod
        def query_objects(cls_, pattern: str):
            return manager.query_objects(pattern)
        cls.query_objects = query_objects

        cls._name_manager = manager

        return cls

    return decorator


if __name__ == "__main__":
    def add_camera_prefix(name: str) -> str:
        return f"view_{name}"

    @managed_name(transform=add_camera_prefix)
    class RenderView:
        def __init__(self, data):
            self.data = data

    class SubClass(RenderView):
        pass

    r1 = RenderView("data1")
    r2 = RenderView("data2")
    r3 = RenderView("data3", name="main")
    r4 = SubClass("data4")
    class SpecialView(RenderView):

        @classmethod
        def _default_basename(cls):
            return "special"

    r5 = SpecialView("data4")

    print(RenderView.all_objects())  
# {'view': <RenderView object>, 'view_1': <RenderView object>, 'main': <RenderView object>}

    print(RenderView.get_object("view_renderview_1"))  # 返回 r2

    print(RenderView.query_objects("renderview"))  
    print(SpecialView._name_manager)
    print("now delete")
    del r1 
    print(RenderView.all_objects())
