python之 unicode\_literals
==============================================

:date: 2013-06-03
:author: SunisDown
:categories: python
:tags: python, unicode, str
:comments:

在邮件列表中看见有人在讨论github上面的内容,然后看见一阁大牛说"看见别人的python代码没有from
\_\_future\_\_ import unicode\_literals就想fork改掉…"

之前代码中确实没有加这个,嗯,受教啦

::

        from __future__ import unicode_literals

是python2.6
之后新增加的新特性,可以使得所有的字符串文本成为Unicode字符串.

::

        In [4]: from __future__ import unicode_literals

        In [5]: a = '你好'

        In [6]: a
        Out[6]: u'\u4f60\u597d'


