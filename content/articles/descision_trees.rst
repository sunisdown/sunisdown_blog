如何利用决策树来决定去不去年会
==============================

:date: 2014-11-06
:author: SunisDown
:categories: algo
:tags:
:comments:


又到一年年会时,吸引大家去年会的,要么是冲奖品去,要么是为了看表演的妹子,作为一个好青年我排除掉看妹子的选项,仅用奖品来做价值来决定\ **到底年会值不值得去!!!**

如果我们去年会的话,有可能得到一个
iMac,如果我们不去,那我们可能什么都得不到.但是
如果去年会,我们需要花路费,假设我们需要坐一次公交￥1,然后再坐一次地铁￥3,现在帝都公交地
铁都涨价了,出门的成本也增加了T
T.有的小伙伴可能会开车,这样路费比公共交通更贵.反正我没有车,一天的来回路费按￥8计算.

通过上面的简单计算,如果我们去年会,则肯定需要支出￥8的成本,但是有可能会收获一台价
值￥8000的 iMac,看起来不错,即使没有抽到
iMac,其他的奖品也还是不错的~但是前提是你 人品要好.这是一个概率事件.

+-----------------+------------------+------------------+----------------+
|抽奖顺序         | 奖品级别         | 价值￥           | 人数           |
+=================+==================+==================+================+
| 1               | 4等              | 200              | 40             |
+-----------------+------------------+------------------+----------------+
| 2               | 3等              | 300              | 30             |
+-----------------+------------------+------------------+----------------+
| 3               | 2等              | 400              | 20             |
+-----------------+------------------+------------------+----------------+
| 4               | 1等              | 800              | 10             |
+-----------------+------------------+------------------+----------------+
| 5               | 特等             | 8000             | 1              |
+-----------------+------------------+------------------+----------------+
| 5               | 特别幸运         | 8000             | 1              |
+-----------------+------------------+------------------+----------------+

当你对于一件事犹豫不决不知道该不该做的时候,决策树是帮你的好工具,下面我们利用决策树来帮助我们做一下决策.

首先我们开始画一个决策树: 去或者不去,

.. figure:: images/dt1.png
   :alt: 图片1

   图片1

如果我们去了,开始了抽奖环节,估计大家都跟我一样,在开始的时候祈祷:不要不要不要抽
我,因为四等奖太小了.四等奖价值￥200,有40个四等奖,全公司有1200人,这样我们可以得出
抽中4等奖的概率为40/1200,然后￥200减去我们的成本￥8,预计收益为￥192.

::

     200-8
    =192

决策树如下:

.. figure:: images/dt2.png
   :alt: 图2

   图2

如果没有抽中4等奖,后面还有机会竞争3等奖,由于前面有小伙伴得到了4等奖,所以我们获得3等奖的概率会增加,因为抽奖的时候会排除他们,重新计算,

::

     300 - 8
    = 292

得到如下决策树:

.. figure:: images/dt3.png
   :alt: 图3

   图3

根据上面的计算方法,我们可以得到完整的决策树:

.. figure:: images/dt4.png
   :alt: 图4

   图4

当然,通常情况下为了尽兴,或者老板心情好,决定给一个特别将,嗯,再加一个特别奖:

.. figure:: images/dt5.png
   :alt: 图5

   图5

上面的图中,我已经在决策树中分析了各种可能以及概率,下面我们要从末端反推决策树,确认每个分支的价值,然后做出判断:
特别奖的分支我们可以做出如下判断:

::

     1/1099*7992 + (1098/1099)*(-8)
    =-0.72

然后根据上面的计算简化决策树:

.. figure:: images/dt6.png
   :alt: 图6

   图6

根据上面的简化方法一直计算,最终得到最简化的树:

.. figure:: images/dt7.png
   :alt: 图7

   图7

嗯,通过最终的简化图,我们可以看到,如果去年会,我们会有￥32.85
的收益,对我们是有好处的.So,还是去吧~

当然,如果是周末开年会的话,计算的时候就需要再加上时间成本,小伙伴们自己来算吧:)



