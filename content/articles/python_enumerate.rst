Python 之 enumerate
=====================================

:date: 2013-06-01
:author: SunisDown
:categories: python
:tags: python, enumerate
:comments:

今天看到enumerate 这个函数,然后Google之,发现limodou大牛写过enumerate了~

enumerate 主要是用再类似的场景:

.. code-block:: bash

    In [20]:for i in xrange(len(a)):
                        print i, a[i]
        ....:
                    0 1
                    1 2
                    2 3
                    3 alkj

使用enumerate可以简化代码为:

.. code-block:: bash

    In [21]: for i, j in enumerate(a):
        ....:     print i, j
        ....:
                    0 1
                    1 2
                    2 3
                    3 alkj

    {i:j for i,j in enumerate('abcdef')}


