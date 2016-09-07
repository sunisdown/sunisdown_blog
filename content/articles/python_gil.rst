Python 之 GIL
===========================

:date: 2015-02-03
:author: Sunisdown
:categories: Python
:tags: Python, GIL
:comments:

注: 本篇 Blog 是参照
\ `Python源码剖析 <http://book.douban.com/subject/3117898/>`__\ 过的 Python 源
码,内容算是读书笔记吧,中间还不小心翻错了分支,翻到了3.4版本,不过看起来3.4的 GIL
处理要比2.7的优雅一些.总之,感谢陈孺大神

什么是 GIL
~~~~~~~~~~

GIL(Global Interpreter Lock)
是解释器全局锁,用来互斥线程对于Python虚拟机的使用.

为什么用 GIL
~~~~~~~~~~~~

我们知道 Python
的线程调度是由机器来调度的,在线程执行的时候,我们不能决定线程什么时候挂起.假设线程
A与线程 B 都保存在对象
Obj\_1,而这种情况下有可能会发生一些比较坑的问题:比如 A 在销毁 Obj\_1
的过程中被挂起,而这时候 B 线程开始执行销毁操作,而且正常的将
Obj\_1的销毁,内存被回收.这时候B 被挂起,A 接着被挂起之前的状态执行.然后
Obj\_1已经木有了...类似与这种坑爹的问题,没有 GIL 的情况下会经常发生.

为了避免上述情况发生,我们就需要在解决多线程访问共享资源的互斥.

创建 GIL
~~~~~~~~

要了解在之前的Blog 中,大概的讲过 Python
中的线程调度是由操作系统来调度的.而 GIL
作为多线程操作的产物,要深入了解也必须要从线程\ `Thread <https://github.com/python/cpython/blob/2.7/Modules/threadmodule.c#L850>`__\ 模块入手.

.. code-block:: c


    static PyMethodDef thread_methods[] = {
        {"start_new_thread",        (PyCFunction)thread_PyThread_start_new_thread,
                                METH_VARARGS,
                                start_new_doc},
        {"start_new",               (PyCFunction)thread_PyThread_start_new_thread,
                                METH_VARARGS,
                                start_new_doc},
        {"allocate_lock",           (PyCFunction)thread_PyThread_allocate_lock,
         METH_NOARGS, allocate_doc},
        {"allocate",                (PyCFunction)thread_PyThread_allocate_lock,
         METH_NOARGS, allocate_doc},
        {"exit_thread",             (PyCFunction)thread_PyThread_exit_thread,
         METH_NOARGS, exit_doc},
        {"exit",                    (PyCFunction)thread_PyThread_exit_thread,
         METH_NOARGS, exit_doc},
        {"interrupt_main",          (PyCFunction)thread_PyThread_interrupt_main,
         METH_NOARGS, interrupt_doc},
        {"get_ident",               (PyCFunction)thread_get_ident,
         METH_NOARGS, get_ident_doc},
        {"_count",                  (PyCFunction)thread__count,
         METH_NOARGS, _count_doc},
        {"stack_size",              (PyCFunction)thread_stack_size,
                                METH_VARARGS,
                                stack_size_doc},
        {NULL,                      NULL}           /* sentinel */
    };

从 Thread module我们可以看到Python
给我们提供的多线程机制的接口.非常简单,极其精简,类似于\ ``start_new_thread``\ 跟\ ``start_new``\ 都是同一个接口.

从上面我们找到创建进程的接口,然后跟踪到\ `thread\_PyThread\_start\_new\_thread <https://github.com/python/cpython/blob/2.7/Modules/threadmodule.c#L648>`__\ 里面,官方的\ `注释 <https://github.com/python/cpython/blob/2.7/Modules/threadmodule.c#L687>`__\ 写的也算到位.

.. code-block:: c


    static PyObject *
    thread_PyThread_start_new_thread(PyObject *self, PyObject *fargs)
    {
        PyObject *func, *args, *keyw = NULL;
        struct bootstate *boot;
        long ident;

        if (!PyArg_UnpackTuple(fargs, "start_new_thread", 2, 3,
                               &func, &args, &keyw))
            return NULL;
        if (!PyCallable_Check(func)) {
            PyErr_SetString(PyExc_TypeError,
                            "first arg must be callable");
            return NULL;
        }
        if (!PyTuple_Check(args)) {
            PyErr_SetString(PyExc_TypeError,
                            "2nd arg must be a tuple");
            return NULL;
        }
        if (keyw != NULL && !PyDict_Check(keyw)) {
            PyErr_SetString(PyExc_TypeError,
                            "optional 3rd arg must be a dictionary");
            return NULL;
        }
        boot = PyMem_NEW(struct bootstate, 1);
        if (boot == NULL)
            return PyErr_NoMemory();
        boot->interp = PyThreadState_GET()->interp;
        boot->func = func;
        boot->args = args;
        boot->keyw = keyw;
        boot->tstate = _PyThreadState_Prealloc(boot->interp);
        if (boot->tstate == NULL) {
            PyMem_DEL(boot);
            return PyErr_NoMemory();
        }
        Py_INCREF(func);
        Py_INCREF(args);
        Py_XINCREF(keyw);
        PyEval_InitThreads(); /* Start the interpreter's thread-awareness */
        ident = PyThread_start_new_thread(t_bootstrap, (void*) boot);
        if (ident == -1) {
            PyErr_SetString(ThreadError, "can't start new thread");
            Py_DECREF(func);
            Py_DECREF(args);
            Py_XDECREF(keyw);
            PyThreadState_Clear(boot->tstate);
            PyMem_DEL(boot);
            return NULL;
        }
        return PyInt_FromLong(ident);
    }

``Start the interpreter's thread-awareness``,让解释器开始准备多线程环境,其实就是初始化多线程环境.这里有一些需要注意的地方,Python
在最开始执行的时候,是\ **没有创建多线程的数据结构的**,也没有创建
GIL.这样可以避免一些只需要单线程的程序做多余的线程调度.只有当我们执行\ ``start_new_thread``\ 的时候,才会激活多线程机制,创建
GIL.

我们跟踪\ ``PyEval_InitThreads()``\ 到\ `ceval.c <https://github.com/python/cpython/blob/2.7/Python/ceval.c#L249>`__,可以看到创建
GIL 的代码:

.. code-block:: c

    static PyThread_type_lock interpreter_lock = 0; /* This is the GIL */


    PyEval_InitThreads(void)
    {
        if (interpreter_lock)
            return;
        interpreter_lock = PyThread_allocate_lock();
        PyThread_acquire_lock(interpreter_lock, 1);
        main_thread = PyThread_get_thread_ident();
    }

从上面的代码中我们可以看到,在初始化多线程环境的时候,会检测
``interpreter_lock``
是不是已经创建,如果没有创建,则会用\ ``PyThread_allocate_lock``
创建\ ``interpreter_lock``.

什么是 GIL
~~~~~~~~~~

上面我们跟踪到 GIL 的创建过程,可是 GIL 到底是个什么东西?


从前面的代码中,我们看到是由\ ``PyThread_allocate_lock``\ 来创建GIL
的,而\ ``PyThread_allocate_lock``\ 则是针对各个平台来做的具体实现,这里我们看\ `Posix标准 <https://github.com/python/cpython/blob/2.7/Python/thread_pthread.h#L360>`__\ 的实现:

.. code-block:: c

    PyThread_allocate_lock(void)
    {
        pthread_lock *lock;
        int status, error = 0;

        dprintf(("PyThread_allocate_lock called\n"));
        if (!initialized)
            PyThread_init_thread();

        lock = (pthread_lock *) malloc(sizeof(pthread_lock));
        if (lock) {
            memset((void *)lock, '\0', sizeof(pthread_lock));
            lock->locked = 0;

            status = pthread_mutex_init(&lock->mut,
                                        pthread_mutexattr_default);
            CHECK_STATUS("pthread_mutex_init");

            status = pthread_cond_init(&lock->lock_released,
                                       pthread_condattr_default);
            CHECK_STATUS("pthread_cond_init");

            if (error) {
                free((void *)lock);
                lock = 0;
            }
        }

        dprintf(("PyThread_allocate_lock() -> %p\n", lock));
        return (PyThread_type_lock) lock;
    }

先检测是否已经初始化,如果没有,则进行初始化.中间加上 malloc
机制,最后返回一个\ ``pthread_lock``,这就是我们的 GIL
了,\ `线程互斥的锁 <https://github.com/python/cpython/blob/2.7/Python/thread_pthread.h#L113>`__:


.. code-block:: c

    typedef struct {
        char             locked; /* 0=unlocked, 1=locked */
        /* a <cond, mutex> pair to handle an acquire of a locked lock */
        pthread_cond_t   lock_released;
        pthread_mutex_t  mut;
    } pthread_lock;

什么时候释放 GIL
~~~~~~~~~~~~~~~~

总算回到最初我写这篇 Blog
的动机上面来了,我是在去豆瓣面试的时候被问了这个问题,一时语塞,瞎扯一通之后回来决定要好好看一下代码的...
现在都已经快准备入职豆瓣了,才来动手写 Blog,也算是拖延症晚期吧.

在通过 ``PyThread_allocate_lock`` 创建 GIL
之后,多线程的开始正常的调度,包括\ ``sys.getcheckinterval()``
拿到的\ ``interval``\ (默认为100)的间隔被动放弃 GIL,或者线程阻塞放弃
GIL.总之,\`PyEval\_InitThreads
会通过\ `PyThread\_acquire\_lock <https://github.com/python/cpython/blob/2.7/Python/ceval.c#L254>`__
来获取 GIL.


