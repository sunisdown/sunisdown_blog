Python 装饰器之 functools.wraps
======================================================

:date: 2013-07-08
:author: SunisDown
:categories: python
:tags: python, decorator
:comments:

在看 Bottle 代码中看见 functools.wraps 这种用法。

.. code-block:: python

    def make_default_app_wrapper(name):
        """ Return a callable that relays calls to the current default app. """
        a = getattr(Bottle, name)
        @functools.wraps(getattr(Bottle, name))
        def wrapper(*a, **ka):
            return getattr(app(), name)(*a, **ka)
        return wrapper

之前没有看过，于是查文档了解了一下他的用处 先下定义： **functools.wraps
是 ``装饰器``\ 的\ ``装饰器``**

要明白 functiools.wraps 首先要明白 Python 的 ``Decorator``

Decorator
~~~~~~~~~

在以前的 Blog 中曾经简单写过 Decorator。这次需要讲的更细一些。

``Decorator 通过返回包装对象实现间接调用,以此插入额外逻辑。``\ 是从老大那边偷来的哪里摘抄来的，应该算是言简意赅了。

.. code-block:: python

    @dec2
    @dec1
    def func(arg1, arg2, ...):
        pass

可以还原成

.. code-block:: python

    def func(arg1, arg2, ...):
        pass
    func = dec2(dec1(func))

.. code-block:: python

    @decomaker(argA, argB, ...)
    def func(arg1, arg2, ...):
        pass

可以还原成

.. code-block:: python

    func = decomaker(argA, argB, ...)(func)

.. code-block:: python

    In [1]: def outer(func):
       ...:     def inner():
       ...:         print "before func"
       ...:         ret = func()
       ...:         return ret + 1
       ...:     return inner #返回 inner 函数对象
       ...:

    In [2]: @outer  # 解释器执⾏行 foo = outer(foo)
       ...: def foo():
       ...:     return 1
       ...:

    In [3]: foo
    Out[3]: <function __main__.inner>

    In [4]: foo()
            before func
    Out[4]: 2

这个过程中执行了下面几步

1. 函数 foo 作为 装饰器 outer 的参数被传入
2. 函数 inner 对 func 进行调用，然后装饰器 outer 返回 inner
3. 原来的函数名 foo 关联到
   inner，如上面的\ ``foo <function __main__.inner>`` 所示，调用 foo
   时间上是在调用 inner

装饰器不仅可以用函数返回包装对象，也可以是个类，不过这种方法太尼玛啰嗦，这里就不介绍了，想了解的自己去翻吧。下面我们写一个有点用处的
Decorator。 假想我们有个coordinate类，而且这个类提供了
``x, y``\ 坐标，而我们要对两个coordinate 对象进行计算。代码如下：

.. code-block:: python

    class Coordinate(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y
        def __repr__(self):
            return "Coord: " + str(self.__dict__)

    def add(a, b):
        return Coordinate(a.x + b.x, a.y + b.y)

    def sub(a, b):
        return Coordinate(a.x - b.x, a.y - b.y)

    In [8]: one = Coordinate(100, 200)

    In [9]: two = Coordinate(300, 200)

    In [10]: three = Coordinate(-100, -100)

    In [11]: sub(one, three)
    Out[11]: Coord: {'y': 300, 'x': 200}

    In [12]: add(one, three)
    Out[12]: Coord: {'y': 100, 'x': 0}

    In [13]: sub(one, two)
    Out[13]: Coord: {'y': 0, 'x': -200}

上面例子中的\ ``sub(one, two)``\ 与\ ``three``\ 都有负数，当我们把坐标限制在第一象限时，这两个就不符合我们的要求，用
Decorator 来做一个检测再好不过了

.. code-block:: python

    In [14]: def wrapper(func):
       ....:     def checker(a, b):
       ....:         if a.x < 0 or a.y < 0:
       ....:             a = Coordinate(a.x if a.x > 0 else 0, a.y if a.y > 0 else 0)
       ....:         if b.x < 0 or b.y < 0:
       ....:             b = Coordinate(b.x if b.x > 0 else 0, b.y if b.y > 0 else 0)
       ....:         ret = func(a, b)
       ....:         if ret.x < 0 or ret.y <0:
       ....:             ret = Coordinate(ret.x if ret.x > 0 else 0, ret.y if ret.y > 0 else 0)
       ....:         return ret
       ....:     return checker
       ....:
    In [16]: @wrapper
       ....: def add(a, b):
       ....:     return Coordinate(a.x + b.x, a.y + b.y)
       ....:

    In [17]: @wrapper
       ....: def sub(a, b):
       ....:     return Coordinate(a.x - b.x, a.y + b.y)
       ....:

    In [18]: add(one, three)
    Out[18]: Coord: {'y': 200, 'x': 100}

    In [19]: one
    Out[19]: Coord: {'y': 200, 'x': 100}

    In [20]: sub(one, two)
    Out[20]: Coord: {'y': 400, 'x': 0}

这样，只计算的函数\ ``add``\ 与\ ``sub``\ 前面加一个 Decorator
就可以完成坐标的校验。比在函数内实现要优雅一些。

Decorator 还可以为类增加额外的成员，

.. code-block:: python

    In [21]: def hello(cls):
       ....:     cls.hello = staticmethod(lambda: "HELLO")
       ....:     return cls
       ....:

    In [22]: @hello
       ....: class World(object):pass
       ....:

    In [23]: World.hello
    Out[23]: <function __main__.<lambda>>

    In [24]: World.hello()
    Out[24]: 'HELLO'

functools.wraps
---------------

我们在使用 Decorator 的过程中，难免会损失一些原本的功能信息。直接拿
stackoverflow 里面的栗子

.. code-block:: python

    def logged(func):
        def with_logging(*args, **kwargs):
            print func.__name__ + " was called"
            return func(*args, **kwargs)
        return with_logging

    @logged
    def f(x):
       """does some math"""
       return x + x * x

    def f(x):
        """does some math"""
        return x + x * x
    f = logged(f)

    In [24]: f.__name__
    Out[24]: with_logging

而functools.wraps 则可以将原函数对象的指定属性复制给包装函数对象, 默认有
``__module__``\ 、\ ``__name__``\ 、\ ``__doc__``,或者通过参数选择。代码如下：

.. code-block:: python

    from functools import wraps
    def logged(func):
        @wraps(func)
        def with_logging(*args, **kwargs):
            print func.__name__ + " was called"
            return func(*args, **kwargs)
        return with_logging

    @logged
    def f(x):
       """does some math"""
       return x + x * x

    print f.__name__  # prints 'f'
    print f.__doc__   # prints 'does some math'

