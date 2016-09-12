Python 元类
==========================

:date: 2014-12-29
:author: Sunisdown
:categories: python
:tags: python
:comments:

``Python``\ 中有三个概念比较难懂，分别是：

-  装饰器
-  描述符
-  元类

这三种概念里面，元类又最为难懂，威力最强。

类型，类，对象
~~~~~~~~~~~~~~

神说\ ``万物皆对象``\ ，Python
中一切都是对象，凡是对象必先有类型。类，也是对象的一种。Python
中所有的对象都有一些相同的内容，包含在对象的\ `头部信息 <https://github.com/python/cpython/blob/2.7/Include/object.h#L106>`__\ 中。

.. code-block:: c

    typedef struct _object {
        PyObject_HEAD
    } PyObject;

在
`PyObject <https://github.com/python/cpython/blob/2.7/Include/object.h#L78>`__
的定义中，\ ``ob_refcnt``
是\ ``应用计数``\ ，用来做内存管理垃圾回收有关，这里暂时不细说。有兴趣的可以查看\ `Q.yuhen的
Python 笔记 <https://github.com/qyuhen/book>`__,

.. code-block:: c

    /* PyObject_HEAD defines the initial segment of every PyObject. */
    #define PyObject_HEAD                   \
        _PyObject_HEAD_EXTRA                \
        Py_ssize_t ob_refcnt;               \
        struct _typeobject *ob_type;

``ob_type``\ 则是指向指向具体类型的指针。里面定义各种 Python
的类型。每一个对象都有他的类型。

下面跟我念：Python
中万物皆对象，对象皆有类型，且类型也是一个对象。上面我们说了每一个对象都有一个\ ``类型指针``\ 指向他的类型，我们可以通过类型指针来判断对象的类型。

那么问题来了：我们通过什么来确定一个对象其实是一个类型对象？答案就是
``metaclass``\ ，所有 class 的 class，所有类型的类型。

举个栗子：

.. code-block:: python

    In [1]: class NewData(object):
       ...:     pass
       ...:

    In [2]: newdata = NewData()

    In [3]: NewData.__class__
    Out[3]: type

    In [4]: type(NewData)
    Out[4]: type

    In [5]: newdata.__class__
    Out[5]: __main__.NewData

    In [6]: type(newdata)
    Out[6]: __main__.NewData

    In [7]: type.__class__
    Out[7]: type

    In [8]: type.__base__
    Out[8]: object

    In [9]: NewData.__base__
    Out[9]: object

    In [10]: type(object)
    Out[10]: type

    In [11]: object.__class__
    Out[11]: type

从上面的栗子中我们可以观察到，\ ``NewData``\ 与\ ``type``\ 以及\ ``object``\ 的类型都是
*type*\ ，这 里面的类型 *type* 就是
``metaclass``\ 的一种，现在理一下元类，类型，类，实例之间的关 系：

-  实例的类型是类 newdata.\ **class** == class
-  类的类型是元类 NewData.\ **class** == metaclass #type

**metaclass**
~~~~~~~~~~~~~

Python 中 ``class`` 关键字会
`创建类的对象 <https://github.com/python/cpython/blob/2.7/Python/ceval.c#L4621>`__\ ，
我们观察一下类的创建过程:

.. code-block:: c

        if (PyDict_Check(methods))
            metaclass = PyDict_GetItemString(methods, "__metaclass__");
        if (metaclass != NULL)
            Py_INCREF(metaclass);
        else if (PyTuple_Check(bases) && PyTuple_GET_SIZE(bases) > 0) {
            base = PyTuple_GET_ITEM(bases, 0);
            metaclass = PyObject_GetAttrString(base, "__class__");
            if (metaclass == NULL) {
                PyErr_Clear();
                metaclass = (PyObject *)base->ob_type;
                Py_INCREF(metaclass);
            }
        }

先检测在类的定义中是否指定了\ ``__metaclass__``\ ，如果没有自己定义，则使用\ ``object``\ 的
``__class__``\ 来作为元类，上面演示过\ ``object.__class__``
是\ ``type``\ 。

如何使用元类
~~~~~~~~~~~~

上面一节讲到，如果自己没有定义\ ``__metaclass__``\ 的时候，则会使用默认的元类\ ``type``\ 。
而这一节则会实验如何自己创建一个自定义元类。假设我是一个非常自恋的码农，别人把我
的名字从 Auth
里面抹去这种事儿不能忍，这种情况下也可以蛋疼的用元类（这真的是一个
蛋疼的栗子）：

.. code-block:: python

    class AuthMeta(type):
        def __new__(cls, name, bases, attrs):
            t = type.__new__(cls, name, bases, attrs)
            t.auth = "SunisDown"
            return t

    class Blog(object):
        __metaclass__ = AuthMeta
        pass

    aaa = Blog()

    aaa.auth == 'SunisDown'

如上所示，在后续的代码中，只要将\_\_metaclass\_\_ 指向
``AuthMeta``\ ，后面的类就有了属
性\ ``auth``\ ，嗯，这个蛋疼的作者名字跟代码永远的绑到一起了。

``import this``\ 的作者 Tim Peters
说过描述元类的话，能够非常到位的描述出元类在 Python 中的超然位置:

::

    99%的用户不需要为元类这种黑魔法过渡操心.如果你想搞清楚究竟是否需要用到元类，那么你就不需要它。那些实际用到元类的人都非常 清楚地知道他们需要做什么，而且根本不需要解释为什么要用元类。

在 Django 的
`models <https://github.com/django/django/blob/master/django/db/models/base.py#L60>`__
中，对于元类的使用可以算是一次教科书式的使用。

通过继承\ ``models.Models``\ 里面的元类，我们就可以直接写类似：

.. code-block:: python

    class Blog(models.Model):
        title = models.CharField(max_length=50)
        auth = models.IntegerField()

这种简单方便的
API，用户可以直接使用，而后面负责的逻辑，就隐藏在元类之中。


