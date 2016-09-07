================================
 Mininet Walkthrough
================================

:date: 2014-10-16
:author: SunisDown
:categories: none
:tags: sdn, mininet
:comments:

译者注： 这篇 Blog 是在学习 SDN 过程中翻译的Mininet
官方的文档。文档主要是介绍了 Mininet
的简单用法。会分成几个部分放出来，\ `原文 <http://mininet.org/walkthrough/#test-connectivity-between-hosts>`__\ 。下面是正文

Part 1: Everyday Mininet Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

首先是是命令语法

-  ``$`` 这个符号代表现在处于 Linux 的shell 交互下，需要使用的是 Linux
   命令
-  ``mininet>`` 这个符号表示现在处于 Mininet 交互下，需要使用的是
   Mininet 的命令
-  ``＃`` 这个符号表示的是现在处于 Linux 的 root 权限下。

以上相应的状态下下属于对应的命令，就能够得到正常的输出。需要注意的是\ ``mininet>``\ 的情况比较特殊，需要使用
minient 的命令来进行交互。

Display Startup Options
^^^^^^^^^^^^^^^^^^^^^^^

我们首先来启动 Mininet。

键入以下命令来显示Mininet的帮助信息:

.. code-block:: bash

    $ sudo mn -h

    Usage: mn [options]
    (type mn -h for details)

    The mn utility creates Mininet network from the command line. It can create
    parametrized topologies, invoke the Mininet CLI, and run tests.

    Options:
      -h, --help            show this help message and exit
      --switch=SWITCH       ivs|ovsk|ovsl|user[,param=value...]
      --host=HOST           cfs|proc|rt[,param=value...]
      --controller=CONTROLLER
                            none|nox|ovsc|ref|remote[,param=value...]
      --link=LINK           default|tc[,param=value...]
      --topo=TOPO           linear|minimal|reversed|single|tree[,param=value...]
      -c, --clean           clean and exit
      --custom=CUSTOM       read custom topo and node params from .pyfile
      --test=TEST           cli|build|pingall|pingpair|iperf|all|iperfudp|none
      -x, --xterms          spawn xterms for each node
      -i IPBASE, --ipbase=IPBASE
                            base IP address for hosts
      --mac                 automatically set host MACs
      --arp                 set all-pairs ARP entries
      -v VERBOSITY, --verbosity=VERBOSITY
                            info|warning|critical|error|debug|output
      --innamespace         sw and ctrl in namespace?
      --listenport=LISTENPORT
                            base port for passive switch listening
      --nolistenport        don't use passive listening port
      --pre=PRE             CLI script to run before tests
      --post=POST           CLI script to run after tests
      --pin                 pin hosts to CPU cores (requires --host cfs or --host
                            rt)
      --version

如上所示，输出了 mn 的帮助信息。

Start Wireshark
^^^^^^^^^^^^^^^

为了使用 Wireshark 来查看 OpenFlow 的控制信息，我们先打开 Wireshark
并让他在后台运行。

.. code-block:: bash

    $ sudo wireshark &

在 Wireshark 的过滤选项中，输入\ ``of``\ ，然后选择 Apply。

In Wireshark, click Capture, then Interfaces, then select Start on the
loopback interface (``lo``).

现在窗口上暂时应该没有任何 OpenFlow 的数据包。

::

    注：在Mininet VM镜像中Wireshark是默认已经安装的。如果你的系统中没有Wireshark的和OpenFlow，您可以使用Mininet的install.sh脚本，按以下步骤安装：

.. code-block:: bash

    $ cd ~
    $ git clone https://github.com/mininet/mininet＃如果它尚不存在
    $ mininet/util/install.sh -w

如果已经安装了 Wireshark，但是运行不了（e.g.
你得到一个类似\ ``$DISPLAY not set``\ 之类的错误信息，可以参考
FAQ，：https://github.com/mininet/mininet/wiki/FAQ#wiki-X11-forwarding）

设置好 X11就可以正常运行 GUI 程序，并且使用 xterm
之类的终端仿真器了，后面的演示中可以用到。

Interact with Hosts and Switches
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start a minimal topology and enter the CLI:

.. code-block:: bash

    $ sudo mn

默认的最小拓扑结构包含有两台主机（h1，h2），还有一个 OpenFlow
的交换机，一个 OpenFlow
的控制器四台设备。这种拓扑接口也可以使用\ ``--topo=minimal``\ 来指定。当然我们也可以使用其他的拓扑结构，具体信息可以看
``--topo``\ 的信息。

现在四个实体（h1，h2，c0，s1）都在运行着。c0作为控制器，是可以放在虚拟机外部的。

如果没有具体的测试作为参数传递时，我们可以使用 Mininet 交互。

在Wireshark的窗口中，你会看到内核交换机连接到控制器。

显示Mininet CLI命令：

.. code-block:: bash

    mininet> help

    Documented commands (type help <topic>):
    ========================================
    EOF    exit   intfs     link   noecho       pingpair      py    source  xterm
    dpctl  gterm  iperf     net    pingall      pingpairfull  quit  time
    dump   help   iperfudp  nodes  pingallfull  px            sh    x

    You may also send a command to a node using:
      <node> command {args}
    For example:
      mininet> h1 ifconfig

    The interpreter automatically substitutes IP addresses
    for node names when a node is the first arg, so commands
    like
      mininet> h2 ping h3
    should work.

    Some character-oriented interactive commands require
    noecho:
      mininet> noecho h2 vi foo.py
    However, starting up an xterm/gterm is generally better:
      mininet> xterm h2

显示节点：

::

    mininet> nodes
    available nodes are:
    c0 h1 h2 s1

显示网络链接：

::

    mininet> net
    h1 h1-eth0:s1-eth1
    h2 h2-eth0:s1-eth2
    s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0
    c0

输出所有节点的信息：

::

    mininet> dump
    <Host h1: h1-eth0:10.0.0.1 pid=3278>
    <Host h2: h2-eth0:10.0.0.2 pid=3279>
    <OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=3282>
    <OVSController c0: 127.0.0.1:6633 pid=3268>

从上面的输出中，你可以看到有一台交换机和两台主机。

在 Mininet 的CLI
中第一个字符串是设备名，那后面的命令就在该设备上执行。例如我们想在h1设备上执行\ ``ifconfig``\ 则输入如下命令：

.. code-block:: bash

    mininet> h1 ifconfig -a
    h1-eth0   Link encap:Ethernet  HWaddr 3e:94:43:b1:ad:48
              inet addr:10.0.0.1  Bcast:10.255.255.255  Mask:255.0.0.0
              inet6 addr: fe80::3c94:43ff:feb1:ad48/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:22 errors:0 dropped:0 overruns:0 frame:0
              TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:1764 (1.7 KB)  TX bytes:648 (648.0 B)

    lo        Link encap:Local Loopback
              inet addr:127.0.0.1  Mask:255.0.0.0
              inet6 addr: ::1/128 Scope:Host
              UP LOOPBACK RUNNING  MTU:65536  Metric:1
              RX packets:0 errors:0 dropped:0 overruns:0 frame:0
              TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

上面的输出中，可以看见 ``h1-eth0`` 跟 ``lo``\ 两个接口，需要注意的是，在
Linux 系统的 shell 中运行\ ``ifconfig``\ 是看不到h1-eth0。

与\ ``h1-eth0``\ 相反的是，\ ``switch`` 默认是跑在 root
的网络namespace上面，所以在\ ``switch``\ 上执行命令与在 Linux 下的 shell
中是一样的。

.. code-block:: bash

    mininet> s1 ifconfig-a
    eth0      Link encap:Ethernet  HWaddr 08:00:27:98:dc:aa
              inet addr:10.0.2.15  Bcast:10.0.2.255  Mask:255.255.255.0
              inet6 addr: fe80::a00:27ff:fe98:dcaa/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:46716 errors:0 dropped:0 overruns:0 frame:0
              TX packets:40265 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:10804203 (10.8 MB)  TX bytes:40122199 (40.1 MB)

    lo        Link encap:Local Loopback
              inet addr:127.0.0.1  Mask:255.0.0.0
              inet6 addr: ::1/128 Scope:Host
              UP LOOPBACK RUNNING  MTU:65536  Metric:1
              RX packets:43654 errors:0 dropped:0 overruns:0 frame:0
              TX packets:43654 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:37264504 (37.2 MB)  TX bytes:37264504 (37.2 MB)

    lxcbr0    Link encap:Ethernet  HWaddr fe:5e:f0:f7:a6:f3
              inet addr:10.0.3.1  Bcast:10.0.3.255  Mask:255.255.255.0
              inet6 addr: fe80::a8c4:b5ff:fea6:2809/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:52 errors:0 dropped:0 overruns:0 frame:0
              TX packets:20 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:4759 (4.7 KB)  TX bytes:2952 (2.9 KB)

    ovs-system Link encap:Ethernet  HWaddr 3e:79:59:3d:d9:bb
              BROADCAST MULTICAST  MTU:1500  Metric:1
              RX packets:0 errors:0 dropped:0 overruns:0 frame:0
              TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

    s1        Link encap:Ethernet  HWaddr 6e:8c:5d:91:d5:44
              inet6 addr: fe80::fc47:8aff:fe6a:4155/64 Scope:Link
              UP BROADCAST RUNNING  MTU:1500  Metric:1
              RX packets:13 errors:0 dropped:0 overruns:0 frame:0
              TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:1026 (1.0 KB)  TX bytes:648 (648.0 B)

    s1-eth1   Link encap:Ethernet  HWaddr 5e:a2:f7:86:f3:b1
              inet6 addr: fe80::5ca2:f7ff:fe86:f3b1/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:8 errors:0 dropped:0 overruns:0 frame:0
              TX packets:22 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:648 (648.0 B)  TX bytes:1764 (1.7 KB)

    s1-eth2   Link encap:Ethernet  HWaddr b2:c6:37:e0:d9:61
              inet6 addr: fe80::b0c6:37ff:fee0:d961/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:8 errors:0 dropped:0 overruns:0 frame:0
              TX packets:21 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:648 (648.0 B)  TX bytes:1674 (1.6 KB)

    veth14524J Link encap:Ethernet  HWaddr fe:ca:13:f5:dd:b4
              inet6 addr: fe80::fcca:13ff:fef5:ddb4/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:8 errors:0 dropped:0 overruns:0 frame:0
              TX packets:40 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:648 (648.0 B)  TX bytes:4190 (4.1 KB)

    veth2K19CE Link encap:Ethernet  HWaddr fe:f1:f7:e8:49:45
              inet6 addr: fe80::fcf1:f7ff:fee8:4945/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:8 errors:0 dropped:0 overruns:0 frame:0
              TX packets:42 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:648 (648.0 B)  TX bytes:4370 (4.3 KB)

    veth9WSHRK Link encap:Ethernet  HWaddr fe:87:1d:33:f6:41
              inet6 addr: fe80::fc87:1dff:fe33:f641/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:8 errors:0 dropped:0 overruns:0 frame:0
              TX packets:43 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:648 (648.0 B)  TX bytes:4460 (4.4 KB)

    vethH2K7R5 Link encap:Ethernet  HWaddr fe:5e:f0:f7:a6:f3
              inet6 addr: fe80::fc5e:f0ff:fef7:a6f3/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:14 errors:0 dropped:0 overruns:0 frame:0
              TX packets:48 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:1776 (1.7 KB)  TX bytes:5030 (5.0 KB)

    vethO99MI2 Link encap:Ethernet  HWaddr fe:cf:ee:97:fb:7f
              inet6 addr: fe80::fccf:eeff:fe97:fb7f/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:14 errors:0 dropped:0 overruns:0 frame:0
              TX packets:51 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:1767 (1.7 KB)  TX bytes:5294 (5.2 KB)

上面的输出中包含交换机的虚拟网卡 s1，以及主机的 eth0。

为了区别显示host
主机的网络是隔离的，我们可以通过\ ``arp``\ 与\ ``route``\ 命令来做演示，分别在
s1与h1上面演示如下：

.. code-block:: bash

    mininet> s1 arp
    Address                  HWtype  HWaddress           Flags Mask            Iface
    localhost                ether   00:16:3e:54:9c:03   C                     lxcbr0
    localhost                ether   52:54:00:12:35:02   C                     eth0
    localhost                ether   52:54:00:12:35:03   C                     eth0
    localhost                ether   00:16:3e:51:24:a7   C                     lxcbr0
    mininet> s1 route
    Kernel IP routing table
    Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
    default         localhost       0.0.0.0         UG    0      0        0 eth0
    10.0.2.0        *               255.255.255.0   U     0      0        0 eth0
    10.0.3.0        *               255.255.255.0   U     0      0        0 lxcbr0
    172.17.0.0      *               255.255.0.0     U     0      0        0 docker0
    mininet> h1 arp
    mininet> h1 route
    Kernel IP routing table
    Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
    10.0.0.0        *               255.0.0.0       U     0      0        0 h1-eth0

这样可以做到将每一个主机，交换机，以及控制器都放到他自己的标准的 network
namespace
中，但是这种做法并没有什么特别的优势，除非你想复制一个非常复杂的网络。Mininet
不支持这种做法，你可以通过\ ``--innamespace``\ 参数来查看更多的信息。
``译者注：感觉有点像 LXC 或者说想最近比较火的 Docker``

*注意*:只有网络是虚拟出来的，每一个主机里面的进程使用的都是同一套目录，可以看到相同的进程集合，我们打印不同主机下面的进程列表看看：

.. code-block:: bash

    mininet> h1 ps -a
      PID TTY          TIME CMD
     3899 pts/3    00:00:00 tmux
     4000 pts/23   00:00:00 sudo
     4001 pts/23   00:00:51 wireshark
     4030 pts/23   00:00:00 dbus-launch
     4530 pts/23   00:00:43 dumpcap
     4541 pts/22   00:00:00 sudo
     4542 pts/22   00:00:00 mn
    mininet> h2 ps -a
      PID TTY          TIME CMD
     3899 pts/3    00:00:00 tmux
     4000 pts/23   00:00:00 sudo
     4001 pts/23   00:00:52 wireshark
     4030 pts/23   00:00:00 dbus-launch
     4530 pts/23   00:00:43 dumpcap
     4541 pts/22   00:00:00 sudo
     4542 pts/22   00:00:00 mn
    mininet> s1 ps -a
      PID TTY          TIME CMD
     3899 pts/3    00:00:00 tmux
     4000 pts/23   00:00:00 sudo
     4001 pts/23   00:00:54 wireshark
     4030 pts/23   00:00:00 dbus-launch
     4530 pts/23   00:00:46 dumpcap
     4541 pts/22   00:00:00 sudo
     4542 pts/22   00:00:00 mn

如上所示， h1，h2，s1三个进程列表是完全相同的。

其实完全可以做到各个主机完全独立，就想 LXC 那样，但是目前 Mininet
并没有这么做。在 Mininet 中所有的进程都放在 root 下面，这样你可以在
Linux的 shell
中直接用\ ``kill``\ 或者\ ``ps``\ 这些命令查看或者杀死进程。

Test connectivity between hosts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

现在，验证您可以h1 ping 通 h2:

.. code-block:: bash

    mininet> h1 ping h2 -c 1
    PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
    64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=8.57 ms

    --- 10.0.0.2 ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 8.576/8.576/8.576/0.000 ms

mininet中的命令语法如上所示。\ ``host1 command  host2``\ 。

在 Wireshark 中可以看到 OpenFlow 的控制流量，可以看到h1 ARPs h2的
mac，并将一个 ``packet_in``\ 发送到
``c0``,然后\ ``c0``\ 发送\ ``packet_out``\ 消息流广播到交换机（在本例中，唯一的其他数据端口）。第二个主机接受到的ARP请求，并发送一个广播答复。此回复进到控制器，该控制器将其发送到\ ``h1``\ 并且
pushes down a flow entry。

现在第一主机知道的第二个IP地址，并且可以通过ICMP ping
来回显请求。这个请求，连同其从第二主机对应的应答，both go the controller
and result in a flow entry pushed down (along with the actual packets
getting sent out).

重复前一条命令：

.. code-block:: bash

    mininet> h1 ping -c 1 h2

这次 ping 的时间将比第一次低的多， A flow entry covering ICMP ping
traffic was previously installed in the switch, so no control traffic
was generated, and the packets immediately pass through the switch.

使用\ ``pingall``\ 命令可以让每一个节点直接都产生上面的效果。

.. code-block:: bash

    mininet> pingall

Run a simple web server and client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

我们不单可以在主机上面运行\ ``ping``\ 命令，每一条
Linux下的命令或者程序都可以在 Mininet 中运行：

接下来，尝试开始于h1启动一个简单的HTTP服务器上，然后从h2发出请求，最后关闭Web服务器：

.. code-block:: bash

    mininet> h1 python -m SimpleHTTPServer 80 &
    mininet> h2 wget h1
    --2014-09-15 08:10:11--  http://10.0.0.1/
    Connecting to 10.0.0.1:80... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 2647 (2.6K) [text/html]
    Saving to: ‘index.html’

         0K ..                                                    100% 71.7M=0s

    2014-09-15 08:10:11 (71.7 MB/s) - ‘index.html’ saved [2647/2647]
    mininet> h1 kill %python

退出mininet交互命令：

.. code-block:: bash

    mininet>exit

cleanup
^^^^^^^

如果Mininet出于某种原因崩溃，可以用下面命令来清理：

.. code-block:: bash

    sudo mn -c

Part 2: 高级选项Advanced Startup Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

回归测试Run a Regression Test
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Mininet 可以用于直接运行回归测试，不一定要切换到他的 CLI 下面。

运行回归测试：

.. code-block:: bash

    $ sudo mn --test pingpair

这条命令会创建一个小的拓扑结构，然后启动 OpenFLow 的控制器，然后跑 ping
测试，最后再把拓扑结构跟控制器关掉。

另一种有用的试验是iperf的（给它约10秒来完成）：
还有一直常用的测试是\ ``iperf``\ (完成这个测试大概需要10s 钟):

.. code-block:: bash

    $ sudo mn --test iperf

此命令创建的相同Mininet，并在其中一台 host 上面跑 iperf server,
然后在另外一台 host 上面运行iperf client 然后解析取得带宽情况。
####更改拓扑结构大小和类型 Changing Topology Size and Type

--------------

Mininet 默认的拓扑结构是由两台 host
以及一台交换机组成的，你可以用\ ``--topo``\ 参数来更改拓扑结构。
假设你要在一个交换机与三台 host 之间做 ping 探测验证（verify all-pairs
ping connectivity）。：

运行回归测试：

.. code-block:: bash

    $ sudo mn --test pingall --topo single,3

另一个例子中，使用线性拓扑（其中每个交换机配有一个主机，并且所有的交换机连接在一起）：

.. code-block:: bash

    $ sudo mn --test pingall --topo linear,4

课哟用参数来控制拓扑结构是 Mininet 中最有用的功能之一，非常强大。

链路变化 Link variations
^^^^^^^^^^^^^^^^^^^^^^^^


Mininet2.0允许你设置连接参数，甚至可以通过命令行实现自动化设置：

.. code-block:: bash

    $ sudo mn --link tc,bw=10,delay=10ms
     mininet> iperf
     ...
     mininet> h1 ping -c10 h2

上面的设置每两个节点之间的延迟是10ms，因为 ICMP
请求传过了两条链路（一次是到大交换机，一次到达主机），往返时间（RRT）就应该是40ms。
你还可以使用
`PythonAPI <https://github.com/mininet/mininet/wiki/Introduction-to-Mininet>`__
来做更多的事儿,不过现在我们先继续往下演练。

调整输出信息Adjustable Verbosity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Mininet默认输出信息的级别是 ``Info``\ ，\ ``Info``\ 级别会输出
Mininet的详细信息。 我们也可以通过
``-v``\ 参数来设置输出\ ``DEBUG``\ 信息。

.. code-block:: bash

    $ sudo mn -v debug
    ...
    mininet> exit

这样会打印出更多额外的细节。现在尝试一下\ ``output``\ 参数，这样可以在
CLI 中打印更少的信息。

.. code-block:: bash

    $ sudo mn -v output
    mininet> exit

除了上面的几个级别，还有其他的级别可以使用，比如\ ``warning``\ 等

Custom Topologies自定义拓扑结构
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


在\ ``custom/topo-2sw-2host.py``\ 中是一个例子可以拿来参考，我们可以看到通过
PythonAPI 我们可以很简单的来定义拓扑结构。
这个例子直接连接两台交换机，每个交换机带有一台主机。

.. code-block:: python

    """Custom topology example

    Two directly connected switches plus a host for each switch:

       host --- switch --- switch --- host

    Adding the 'topos' dict with a key/value pair to generate our newly defined
    topology enables one to pass in '--topo=mytopo' from the command line.
    """

    from mininet.topo import Topo

    class MyTopo( Topo ):
        "Simple topology example."

        def __init__( self ):
            "Create custom topo."

            # Initialize topology
            Topo.__init__( self )

            # Add hosts and switches
            leftHost = self.addHost( 'h1' )
            rightHost = self.addHost( 'h2' )
            leftSwitch = self.addSwitch( 's3' )
            rightSwitch = self.addSwitch( 's4' )

            # Add links
            self.addLink( leftHost, leftSwitch )
            self.addLink( leftSwitch, rightSwitch )
            self.addLink( rightSwitch, rightHost )


    topos = { 'mytopo': ( lambda: MyTopo() ) }

我们提供一个自定义的mininet 文件，就可以创建新的拓扑结构、交换机类型。
我们在命令行里面测试一下：

.. code-block:: bash

    $ sudo mn --custom ~/mininet/custom/topo-2sw-2host.py --topo mytopo --test pingall
    *** Creating network
    *** Adding controller
    *** Adding hosts:
    h1 h2
    *** Adding switches:
    s3 s4
    *** Adding links:
    (h1, s3) (h2, s4) (s3, s4)
    *** Configuring hosts
    h1 h2
    *** Starting controller
    *** Starting 2 switches
    s3 s4
    *** Ping: testing ping reachability
    h1 -> h2
    h2 -> h1
    *** Results: 0% dropped (2/2 received)
    *** Stopping 2 switches
    s3 ..s4 ..
    *** Stopping 2 hosts
    h1 h2
    *** Stopping 1 controllers
    c0
    *** Done
    completed in 1.220 seconds

ID= MAC
^^^^^^^


默认情况下，host 的 mac 地址是随机分配的。这会导致每次 mininet
创建的时候，MAC地址都会改变，这会给调试带来一些困难

``--mac``\ 参数可以解决上面的问题，栗子如下：

之前：

.. code-block:: bash

    $ sudo mn

    mininet> h1 ifconfig
    h1-eth0   Link encap:Ethernet  HWaddr c2:d9:4a:37:25:17
              inet addr:10.0.0.1  Bcast:10.255.255.255  Mask:255.0.0.0
              inet6 addr: fe80::c0d9:4aff:fe37:2517/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:17 errors:0 dropped:0 overruns:0 frame:0
              TX packets:7 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:1398 (1.3 KB)  TX bytes:578 (578.0 B)

    lo        Link encap:Local Loopback
              inet addr:127.0.0.1  Mask:255.0.0.0
              inet6 addr: ::1/128 Scope:Host
              UP LOOPBACK RUNNING  MTU:65536  Metric:1
              RX packets:0 errors:0 dropped:0 overruns:0 frame:0
              TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

使用\ ``--mac``\ 参数：

::

    $ sudo mn --mac

    mininet> h1 ifconfig
    h1-eth0   Link encap:Ethernet  HWaddr 00:00:00:00:00:01
              inet addr:10.0.0.1  Bcast:10.255.255.255  Mask:255.0.0.0
              inet6 addr: fe80::200:ff:fe00:1/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:17 errors:0 dropped:0 overruns:0 frame:0
              TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:1414 (1.4 KB)  TX bytes:676 (676.0 B)

    lo        Link encap:Local Loopback
              inet addr:127.0.0.1  Mask:255.0.0.0
              inet6 addr: ::1/128 Scope:Host
              UP LOOPBACK RUNNING  MTU:65536  Metric:1
              RX packets:0 errors:0 dropped:0 overruns:0 frame:0
              TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

n contrast, the MACs for switch data ports reported by Linux will remain
random. This is because you can ‘assign’ a MAC to a data port using
OpenFlow, as noted in the FAQ. This is a somewhat subtle point which you
can probably ignore for now.

XTerm Display xterm屏显
^^^^^^^^^^^^^^^^^^^^^^^


为了方便更复杂的调试工作，可以使用 mininet 的 xterms

可以通过\ ``x``\ 选项来给每一个 host 与交换机启动一个\ ``xterm``\ 。

.. code-block:: bash

    $ sudo mn -x

后一秒钟，在xterm终端会弹出，并且具有自动设置窗口的名称(\ ``h1``,\ ``h2``...)。

或者，您也可以用下面的方式打开更多的xterm。

默认情况下，仅仅 host 需要一个但大户的
namespace，而交换机的窗口则不用(与政策的终端类似) but can be a
convenient place to run and leave up switch debug commands, such as flow
counter dumps.

在你想看到交互命令的时候，xterm
很有用，但是如果你仅仅想看到输出信息，那你可能想停掉 xterm

例如： 在\ ``switch: s1 (root)``\ 的 xterm下面运行:

.. code-block:: bash

    # dpctl dump-flows tcp:127.0.0.1:6634

因为交换机中没有数据流量，所以不会有信息输出。 To use ``dpctl`` with
other switches, start up mininet in verbose mode and look at the passive
listening ports for the switches when they’re created.

现在，在\ ``host: h1``\ 的xterm中运行：

.. code-block:: bash

    # ping 10.0.0.2

回到\ ``s1``\ 的 xterm中查看:

.. code-block:: bash

    # dpctl dump-flows tcp:127.0.0.1:6634

现在就可以看见数据流了。 另外我们可以直接用\ ``dpctl``\ 命令直接调用
Mininet CLI 里面的命令，而不需要启动任何\ ``xterm``\ 或者指定交换机的IP
跟端口。 我们看已通过\ ``ifconfig``\ 命令来判断xterm
是否在\ ``root``\ 的名字空间下，如果所有的网卡都显示出来（包含\ ``eth0``)，那他就是在\ ``root``\ 下。

从 mininet 的 CLI中退出：

.. code-block:: bash

    mininet>exit

这样 mininet 的 CLI就自动关闭了。

Other Switch Types 其他类型的交换机
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

我们可以使用不同的交换机类型。例如：运行 user-space 交换机：

::

    $ sudo mn --switch user --test iperf

值得注意的是这种交换机下，带宽相比于前面的内核态交换机要小的多。 如果做
ping
探测，也会有更高的延迟，这是因为现在的数据包需要从内核态转换到用户空间，消耗了更多的资源。

另一方面，用户空间的交换机会有一些新功能，如果交换机的性能不是关键问题是的时候。
在 Mininet 虚拟机中预装了另外一个交换机类型是
``Open vSwitch(OVS)``\ ，在\ ``iperf``\ 测试中，带宽会比内核态交换机更大。

.. code-block:: bash

    $ sudo mn --switch ovsk --test iperf

Mininet Benchmark
^^^^^^^^^^^^^^^^^

To record the time to set up and tear down a topology, use test ‘none’:

.. code-block:: bash

    $ sudo mn --test none

Everything in its own Namespace (user switch only)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

默认情况下，主机都放在自己的命名空间，
而交换机和控制器的\ ``root``\ 命名空间。
我们可以通过\ ``--innamespace``\ 参数来把交换机放在自己的名字空间中。

.. code-block:: bash

    $ sudo mn --innamespace --switch user

Instead of using loopback, the switches will talk to the controller
through a separately bridged control connection.
就其本身而言，这个选项是没有多大用处的，但它确实提供了如何分离不同交换机的例子。

请注意，此选项不会（截至12年11月19日）与Open vSwitch的工作。

需要注意的是这个选项在\ ``Open vSwitch``\ 中是没法使用的（截至12年11月19日是没法使用）

.. code-block:: bash

    mininet>exit

Part 3: Mininet Command-Line Interface (CLI) Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

第3部分：Mininet命令行界面（CLI）命令

Display Options
^^^^^^^^^^^^^^^

我们可以通过启动一个最小拓扑结构，然后让他一直运行，来来查看 mininet 的
CLI 的选项列表：

.. code-block:: bash

    $ sudo mn

显示选项：

.. code-block:: bash

    mininet>help

Python Interpreter
^^^^^^^^^^^^^^^^^^

如果在 Mininet CLI中的命令的第一个字符串是\ ``py``\ ，那这个条命令会用
Python 来执行。 这对于扩展 Mininet，探测 mininet的内部工作机智都有帮助。
每个主机，交换机和控制器都有一个与之关联的对象。

在Mininet命令行下运行：

.. code-block:: bash

    mininet> py 'hello ' + 'world'

打印 locals:

.. code-block:: bash

    mininet> py locals()
    {'h2': <Host h2: h2-eth0:10.0.0.2 pid=5166> , 'net': <mininet.net.Mininet object at 0x7f7c47668ad0>, 'h1': <Host h1: h1-eth0:10.0.0.1 pid=5165> , 'c0': <OVSController c0: 127.0.0.1:6633 pid=5157> , 's1': <OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=5169> }

还可以通过 dir()函数来查看节点的方法和属性：

.. code-block:: bash

    mininet> py dir(s1)
    ['IP', 'MAC', 'TCReapply', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'addIntf', 'attach', 'checkSetup', 'cleanup', 'cmd', 'cmdPrint', 'config', 'configDefault', 'connected', 'connectionsTo', 'controlIntf', 'controllerUUIDs', 'datapath', 'defaultDpid', 'defaultIntf', 'deleteIntfs', 'detach', 'dpctl', 'dpid', 'dpidLen', 'execed', 'failMode', 'fdToNode', 'inNamespace', 'inToNode', 'intf', 'intfIsUp', 'intfList', 'intfNames', 'intfs', 'isSetup', 'lastCmd', 'lastPid', 'linkTo', 'listenPort', 'monitor', 'name', 'nameToIntf', 'newPort', 'opts', 'outToNode', 'params', 'pexec', 'pid', 'pollOut', 'popen', 'portBase', 'ports', 'read', 'readbuf', 'readline', 'sendCmd', 'sendInt', 'setARP', 'setDefaultRoute', 'setHostRoute', 'setIP', 'setMAC', 'setParam', 'setup', 'shell', 'start', 'startShell', 'stdin', 'stdout', 'stop', 'terminate', 'waitOutput', 'waitReadable', 'waiting', 'write']

您可以通过使用help()函数读取在线文档，查看节点上可用的方法：

.. code-block:: bash

    mininet> py help(h1) #(按`q`退出文档)

You can also evaluate methods of variables:

.. code-block:: python

    mininet> py h1.IP
    <bound method Host.IP of <Host h1: h1-eth0:10.0.0.1 pid=5165> >
    mininet> py h1.IP()
    10.0.0.1

Link Up/Down
^^^^^^^^^^^^

断开/联通链路，对于提供容错能力的测试非常有用。

比如端口\ ``h1``\ 与\ ``s1``\ 之间的连接：

.. code-block:: bash

    mininet> link s1 h1 down

你应该可以看到一个OpenFlow产生了一个的端口状态变化通知。

重新连接\ ``h1`` ``s1``:

.. code-block:: bash

    mininet>link s1 h1 up

XTerm Display
^^^^^^^^^^^^^

要显示\ ``h1`` 与 ``h2``\ 的 xterm:

.. code-block:: bash

    mininet> xterm h1 h2

Part 4: Python API Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~

在\ `Mininet源代码 <https://github.com/mininet/mininet/tree/master/examples>`__
中的示例目录包括如何使用Mininet的Python的API，
还有一些可能有用的代码并没有放到主代码库中。

SSH daemon per host
^^^^^^^^^^^^^^^^^^^

这个栗子对于要在每台设备上启用 ssh 服务可能很有帮助。

.. code-block:: bash

    $ sudo ~/mininet/examples/sshd.py

在另外一个终端上，就可以ssh到任何主机并运行交互式命令：

.. code-block:: bash

    $ ssh 10.0.0.1
    $ ping 10.0.0.2
    ...
    $ exit

退出mininet：

.. code-block:: bash

    exit

你会想重新看看那这些栗子可以看\ `Introduction to
Mininet <https://github.com/mininet/mininet/wiki/Introduction-to-Mininet>`__
，里面介绍了 Python API。

Part 5: Walkthrough Complete!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

恭喜！你已经完成了Mininet演练。之后可以随意尝试新的​​拓扑结构和控制器或查看源代码。

Next Steps to mastering Mininet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

阅读 `OpenFlow
的教程 <https://github.com/mininet/openflow-tutorial/wiki>`__

虽然你可以得到合理的利用Mininet的CLI，但是如果你掌握了 Python
API，Mininet会变得更加有用和强大的。 所以去看 `Mininet
的文档 <https://github.com/mininet/mininet/wiki/Introduction-to-Mininet>`__

后面会解释如何远程控制 mininet（e.g. one running outside Mininet’s
control）。

Appendix: Supplementary Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

这些都不是必需的，但你会发现它们非常有用。

Using a Remote Controller
^^^^^^^^^^^^^^^^^^^^^^^^^

*注意：这一步是不是默认演练的一部分;如果你在mininet
之外运行一个控制器，这个附录将有些帮助。 在 OpenFLow
的教程中介绍了可以使用\ ``controller --remote``\ 参数来启动一个交换机，然后你可以用SDN
控制器比如\ ``POX``, ``NOX``, ``Beacon`` 或者
``Floodlight``\ 之类的来控制这个交换机。*

当您启动Mininet网络，每个交换机可以连接到控制器，无论这个控制器在哪里。

如果你本地装有开发工具或者控制器，又或者你想在不同的物理机上面运行控制器，这种设置会非常方便。

如果你想尝试一下这个，只需要加上 ip 或者port 就可以：

.. code-block:: bash

    $ sudo mn --controller=remote,ip=[controller IP],port=[controller listening port]

例如，要运行POX的交换机，你可以这样做

.. code-block:: bash

    $ cd ~/pox
    $ ./pox.py forwarding.l2_learning

在另一个窗口，启动Mininet连接到“远程”控制器（这实际上是在本地运行，但Mininet的控制范围之外）：

.. code-block:: bash

    $ sudo mn --controller=remote,ip=127.0.0.1,port=6633

*注意，这些其实都是默认的IP地址和端口值。*

如果你制造一些流量（如h1 ping h2），
你应该能够观察到窗口显示该交换机连接，而且输出了一些流量数据。

mininet虚拟机中已经预装了一些OpenFlow的控制器，你可以很轻松的就把这些东西搞起来。

NOX Classic
^^^^^^^^^^^

使用 mininet 的默认\ ``util/install.sh -a``\ 并不会安装 NOX。
如果你想安装它，执行\ ``sudo ~/mininet/util/install.sh -x``

需要注意的是NOX Classic已被弃用，可能不会在将来得到支持。

早 NOX 中运行\ ``pyswitch``\ 来做一个回归测试，
首先确认\ ``NOX_CORE_DIR``\ 已经在环境变量中设置好。

首先验证NOX正在运行：

.. code-block:: bash

    $ cd $NOX_CORE_DIR
    $ ./nox_core -v -i ptcp:

Ctrl-C来杀死 NOX 进程，然后运行与NOX 的 ``pyswitch``\ 测试：

::

    $ cd
    $ sudo -E mn --controller=nox,pyswitch --test pingpair

注意，\ ``--controller``\ 选项具有方便的语法来向控制器类型指定选项
（在这种情况下，nox 运行 pyswitch。）

几秒钟之后，而NOX加载完成并且交换机之间相互连接，随后\ ``ping``\ 。

注意，此时，\ ``mn``\ 应该由\ ``sudo -E``\ 来调用，以保持NOX\_CORE\_DIR环境变量。
如果你是通过\ ``--controller remote``\ 来远程启用的
nox，那就不需要加\ ``-E``\ 参数了。
或者，你可以改变的\ ``/etc/sudoers``\ 文件，把

::

    Defaults        env_reset

修改成

::

    Defaults        !env_reset

使运行sudo的时候的环境变量的设置不会改变。

