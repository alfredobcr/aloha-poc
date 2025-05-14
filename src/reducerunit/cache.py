"""
Singleton Cache Util
"""

class Singleton(type):
    """
    Singleton type
    """
    _instances = {}
    # we are going to redefine (override) what it means to "call" a class
    # as in ....  x = MyClass(1,2,3)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # we have not every built an instance before.  Build one now.
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            instance = cls._instances[cls]
            # here we are going to call the __init__ and maybe reinitialize.
            if hasattr(cls, '__allow_reinitialization') and \
                cls.__allow_reinitialization:
                # if the class allows reinitialization, then do it
                instance.__init__(*args, **kwargs)  # call the init again
        return instance


class ReducerCache(metaclass=Singleton):

    def __init__(self, value):
        self.value = value

    def set_cache(self, new_value):
        self.value = new_value


class MaxReducerCache(ReducerCache):
    __allow_reinitialization = True


class MinReducerCache(ReducerCache):
    __allow_reinitialization = True


class AvgReducerCache(ReducerCache):
    __allow_reinitialization = True
