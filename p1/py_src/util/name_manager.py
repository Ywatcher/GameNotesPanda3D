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

class NameManager:
    def __init__(self):
        self._used_names: set[str] = set()
        self._counters: dict[str, int] = {}
        self._obj_map: dict[str, object] = {}  # name -> obj

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
        self._used_names.add(name)
        self._obj_map[name] = obj
        return name

    def release_name(self, name: str):
        self._used_names.discard(name)
        self._obj_map.pop(name, None)

    def get_object(self, name: str):
        return self._obj_map.get(name)

    def query_objects(self, pattern: str):
        regex = re.compile(pattern)
        return {name: obj for name, obj in self._obj_map.items() if regex.search(name)}

    @property
    def all_objects(self):
        return dict(self._obj_map)


def managed_name(name_attr="name",transform=None, manager=None):
    if manager is None:
        manager = NameManager()

    def decorator(cls):
        original_init = cls.__init__

        if not hasattr(cls, "_default_basename"):
            @classmethod
            def _default_basename(cls_):
                return cls_.__name__.lower()
            cls._default_basename = _default_basename

        @wraps(original_init)
        def new_init(self, *args, name=None, **kwargs):
            original_init(self, *args, **kwargs)
            # use class name if not specfied
            base_name = name if name is not None else self.__class__._default_basename()
            assigned_name = manager.assign_name(self, base_name, transform)
            setattr(self, name_attr, assigned_name)
            self._name_manager = manager

        cls.__init__ = new_init

        # 实例方法释放名字
        def release(self):
            if hasattr(self, name_attr):
                manager.release_name(getattr(self, name_attr))
        cls.release_name = release

        # 类方法，获取所有名字->对象映射
        @classmethod
        def all_objects(cls_):
            return dict(manager._obj_map)
        cls.all_objects = all_objects

        # 类方法，根据名字查单个对象
        @classmethod
        def get_object(cls_, name: str):
            return manager.get_object(name)
        cls.get_object = get_object

        # 类方法，根据 pattern 查对象
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
