Unix/Linux终端下代理快速设置
==================================================


:date: 2014-10-22
:author: SunisDown
:categories: mac
:tags: linux, unix, proxy
:comments:


最近开始从 Vim 往 Emacs，这是一个痛苦的过程，不过好在有
evil-mode，让这个迁移的过程不至于夭折。别问我为什么要背叛 Vim 。

像我这种 Emacs 新手难免会需要下载插件，而下载插件就需要FUCK GFW。笨笨用

.. code-block:: bash

    http_proxy=http://host:port emacs -nw

这种方法来启动 emacs，简直要哭晕在地上。 

设置方法
--------------
所以在配置文件中加了下面的代码，方便在终端下控制当前环境变量下FUCK GFW：

.. code-block:: bash

    function proxy_on() {
        export no_proxy="localhost,127.0.0.1,localaddress,.localdomain.com"
        export http_proxy="http://host:port"
        export https_proxy=$http_proxy
        echo "Proxy environment variable set."

    }

    function proxy_off(){
        unset http_proxy
        unset https_proxy
        echo -e "Proxy environment variable removed."
    }

将上面代码加到你的\ ``.bashrc``\ 中，然后执行

.. code-block:: bash

    source ~/.bashrc

zsh 用户请将上面命令中的\ ``.bashrc``\ 替换成\ ``.zshrc``，然后在终端下就可以快
速设置代理的启动与关闭了：

.. code-block:: bash

    #启动代理
    $ proxy_on
    Proxy environment variable set.

    #关闭代理
    $ proxy_off
    Proxy environment variable removed.


友情提示
-------------------------
.. code-block:: bash

    友情提示，请将 http://host:port 替换成自己的代理地址

