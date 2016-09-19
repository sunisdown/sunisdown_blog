Closures in Go
=================================================

:date: 2016-09-14
:author: SunisDown
:categories: pl
:tags: closures, go
:comments:


在 Qyuhen_ 老大那边潜水的时候，基本上过一段时间就会看见有人讨论闭包。而随手 ``Google`` 也并没有看到哪些 Blog 说的很清楚，甚至有一些 ``Blog`` 里面的内容都是错的。（当然，也有可能是我理解错了）所以就想自己写一下。

什么是闭包
-----------------------------------

在谈起闭包(Closure)的时候，经常也会说起匿名函数。在 gobyexample_ 里面这两个概念也是放在一起的，很多人搞不清楚闭包与匿名函数有什么关系。这两者确实经常会一起出现，但是并不是一个概念。闭包是闭包，匿名函数是匿名函数。

匿名函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
匿名函数与正常的函数区别不大，只是这个函数没有名字。在 ``Go`` 里面，一个真正的函数里面

.. code-block:: go

   func Foo(message string) { // 声明一个正常的函数
       println(message)
   }

   func main() {
       Foo("hello world!")
   }

里面有函数名，有函数主体。但是匿名函数的类似与下面这样子

.. code-block:: go

   func main() {
      func(message string) { //声明匿名函数并执行
          println(message)
      }("hello world!")
   }

并不需要函数名。

闭包
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  闭包（英语：Closure），又称词法闭包（Lexical Closure）或函数闭包（function closures），是引用了自由变量的函数。这个被引用的自由变量将和这个函数一同存在，即使已经离开了创造它的环境也不例外。
      -- wikipedia

闭包包含两个部分，一个是函数本身，还有是这个函数所引用的环境。 ``Go`` 里闭包的函数必须是匿名函数。

.. code-block:: go

    package main

    func myFunc() func() int{
            foo := 0
            return func() int {
                    foo++
                    return foo
            }
    }

    func main() {
            bar := myFunc()
            value_1 := bar()
            value_2 := bar()

            println(value_1) // 1
            println(value_2) // 2
    }

在上面的例子里面，myFunc 里面的匿名函数可以访问并且更新 myFunc 里面的变量，这个变量的生命周期因为匿名函数的存在而延长。

通过闭包可以比较优雅的实现一些功能。比如斐波那契数列

.. code-block:: go

   package main

   func main() {
     gen := makeFibGen()
     for i := 0; i < 10; i++ {
       println(gen())
     }
   }

   func makeFibGen() func() int {
     f1 := 0
     f2 := 1
     return func() int {
       f2, f1 = (f1 + f2), f2
       return f1
     }
   }



Go 中匿名函数的实现
----------------------------------
前面有提到 ``Go`` 里面匿名函数与普通函数区别不大，但是这不大的区别到底在哪里？在这我们用一个简短的小例子来看一下。

.. code-block:: go

   package main

   func myFunc(message int) {
           println(message)
   }

   func main() {
           f := func(message int) {
                   println(message)
           }
           f(0x100)
           myFunc(0x100)
   }

首先我们将上面的代码编译

.. code-block:: bash

  go build -gcflags "-N -l -m" -o main

生成一个 elf 格式的文件 main。

然后我们通过 go 提供的反汇编工具，反编译我们刚刚生成的 main 文件。

.. code-block:: bash

   $go tool objdump -s "main\.main" ./test
   TEXT main.main(SB) /root/data/example/closures/anonymous_func.go
        anonymous_func.go:7     0x401040        64488b0c25f8ffffff      FS MOVQ FS:0xfffffff8, CX
        anonymous_func.go:7     0x401049        483b6110                CMPQ 0x10(CX), SP
        anonymous_func.go:7     0x40104d        7637                    JBE 0x401086
        anonymous_func.go:7     0x40104f        4883ec10                SUBQ $0x10, SP
        anonymous_func.go:8     0x401053        488d1d16830800          LEAQ 0x88316(IP), BX
        anonymous_func.go:8     0x40105a        48895c2408              MOVQ BX, 0x8(SP)
        anonymous_func.go:11    0x40105f        48c7042400010000        MOVQ $0x100, 0(SP)
        anonymous_func.go:11    0x401067        488b5c2408              MOVQ 0x8(SP), BX
        anonymous_func.go:11    0x40106c        4889da                  MOVQ BX, DX
        anonymous_func.go:11    0x40106f        488b1a                  MOVQ 0(DX), BX
        anonymous_func.go:11    0x401072        ffd3                    CALL BX
        anonymous_func.go:12    0x401074        48c7042400010000        MOVQ $0x100, 0(SP)
        anonymous_func.go:12    0x40107c        e87fffffff              CALL main.myFunc(SB)
        anonymous_func.go:13    0x401081        4883c410                ADDQ $0x10, SP
        anonymous_func.go:13    0x401085        c3                      RET
        anonymous_func.go:7     0x401086        e8b59f0400              CALL runtime.morestack_noctxt(SB)
        anonymous_func.go:7     0x40108b        ebb3                    JMP main.main(SB)
        anonymous_func.go:7     0x40108d        cc                      INT $0x3
        anonymous_func.go:7     0x40108e        cc                      INT $0x3
        anonymous_func.go:7     0x40108f        cc                      INT $0x3

        ...


上面的汇编输出中我们可以看到一共有三次 ``CALL``， 排除调最后那个 ``runtime`` 的 ``CALL`` ，剩下两次分别对应了匿名函数调用以及正常的函数调用。而两次的区别在于正常的函数是 ``CALL  main.myFunc(SB)`` , 匿名函数的调用是 ``CALL BX`` 。这两种不同的调用方式意味着什么？我们可以通过 gdb 来动态的跟踪这段代码来具体分析一下。

.. code-block:: bash

   gdb main
   Reading symbols from test...done.
   (gdb) b main.main
   Breakpoint 1 at 0x401040: file /root/data/example/closures/anonymous_func.go, line 7.
   (gdb) r
   Starting program: /root/data/example/closures/test
   [New LWP 2067]
   [New LWP 2068]
   [New LWP 2069]

   Breakpoint 1, main.main () at /root/data/example/closures/anonymous_func.go:7
   7       func main() {
   (gdb) l
   2
   3       func myFunc(message int) {
   4               println(message)
   5       }
   6
   7       func main() {
   8               f := func(message int) {
   9                       println(message)
   10              }
   11              f(0x100)
   (gdb) i locals
   f = {void (int)} 0xc820039f40
   (gdb) x/1xg 0xc820039f40
   0xc820039f40:   0x000000c820000180

上面在 gdb 里面把断点设置在 ``main.main`` 处，然后通过输出当前的环境变量可以看到变量 f。这时候显示 f 指针指向的内存内容。

.. code-block:: bash

  (gdb) b 11
  Breakpoint 2 at 0x40105f: file /root/data/example/closures/anonymous_func.go, line 11.
  (gdb) c
  Continuing.

  Breakpoint 2, main.main () at /root/data/example/closures/anonymous_func.go:11
  11              f(0x100)
  (gdb) i locals
  f = {void (int)} 0xc820039f40
  (gdb) x/1xg 0xc820039f40
  0xc820039f40:   0x0000000000489370
  (gdb) i symbol 0x0000000000489370
  main.main.func1.f in section .rodata of /root/data/example/closures/test
  (gdb) x/2xg 0x0000000000489370
  0x489370 <main.main.func1.f>:   0x0000000000401090      0x0000000000441fa0
  (gdb) i symbol 0x0000000000401090
  main.main.func1 in section .text of /root/data/example/closures/test


然后在调用匿名函数 ``f`` 的地方再设置一个断点， ``c`` 让程序执行到新的断点。再输出 f 指针指向的内存，发现里面的内容已经改变了，输出符号名可以看到符号是 ``main.main.func1.f``, 这个是编译器提我们生成的符号名，然后具叙看一下这个地址指向的内容，会发现 ``main.main.func1`` ，也就是就是我们的匿名函数。接着跟

.. code-block:: bash

  (gdb) i r
    rax            0xc820000180     859530330496
    rbx            0x489370 4756336
    ...
  (gdb) disassemble
  Dump of assembler code for function main.main:
    0x0000000000401040 <+0>:     mov    %fs:0xfffffffffffffff8,%rcx
    0x0000000000401049 <+9>:     cmp    0x10(%rcx),%rsp
    0x000000000040104d <+13>:    jbe    0x401086 <main.main+70>
    0x000000000040104f <+15>:    sub    $0x10,%rsp
    0x0000000000401053 <+19>:    lea    0x88316(%rip),%rbx        # 0x489370 <main.main.func1.f>
    0x000000000040105a <+26>:    mov    %rbx,0x8(%rsp)
  => 0x000000000040105f <+31>:    movq   $0x100,(%rsp)
    0x0000000000401067 <+39>:    mov    0x8(%rsp),%rbx
    0x000000000040106c <+44>:    mov    %rbx,%rdx
    0x000000000040106f <+47>:    mov    (%rdx),%rbx
    0x0000000000401072 <+50>:    callq  *%rbx
    0x0000000000401074 <+52>:    movq   $0x100,(%rsp)
    0x000000000040107c <+60>:    callq  0x401000 <main.myFunc>
    0x0000000000401081 <+65>:    add    $0x10,%rsp
    0x0000000000401085 <+69>:    retq
    0x0000000000401086 <+70>:    callq  0x44b040 <runtime.morestack_noctxt>
    0x000000000040108b <+75>:    jmp    0x401040 <main.main>
    0x000000000040108d <+77>:    int3
    0x000000000040108e <+78>:    int3
    0x000000000040108f <+79>:    int3
  End of assembler dump.
  (gdb) p $rsp
  $2 = (void *) 0xc820039f38
  (gdb) x/1xg 0xc820039f38
  0xc820039f38:   0x0000000000000000
  (gdb) ni
  0x0000000000401067      11              f(0x100)
  (gdb) x/1xg 0xc820039f38
  0xc820039f38:   0x0000000000000100

输出寄存器里面的值看一下，可以注意到寄存器 ``rbx`` 的内存地址是 ``func1.f`` 的地址。然后反编译可以看到执行到了 +31 这一行，将常量 ``0x100`` 放在 rsp 内指针指向的内存地址。输出 rsp 的内容，然后显示地址指向内存的内容，可以看到是 ``0x0000000000000000``，输入 ``ni`` 执行这一行汇编之后再看，就看到内存里面的内容变成了 ``0x0000000000000100``，也就是我们输入常量。

.. code-block:: bash

  (gdb) ni
  0x000000000040106c      11              f(0x100)
  (gdb) ni
  0x000000000040106f      11              f(0x100)
  (gdb) disassemble
  Dump of assembler code for function main.main:
    0x0000000000401040 <+0>:     mov    %fs:0xfffffffffffffff8,%rcx
    0x0000000000401049 <+9>:     cmp    0x10(%rcx),%rsp
    0x000000000040104d <+13>:    jbe    0x401086 <main.main+70>
    0x000000000040104f <+15>:    sub    $0x10,%rsp
    0x0000000000401053 <+19>:    lea    0x88316(%rip),%rbx        # 0x489370 <main.main.func1.f>
    0x000000000040105a <+26>:    mov    %rbx,0x8(%rsp)
    0x000000000040105f <+31>:    movq   $0x100,(%rsp)
    0x0000000000401067 <+39>:    mov    0x8(%rsp),%rbx
    0x000000000040106c <+44>:    mov    %rbx,%rdx
  => 0x000000000040106f <+47>:    mov    (%rdx),%rbx
    0x0000000000401072 <+50>:    callq  *%rbx
    0x0000000000401074 <+52>:    movq   $0x100,(%rsp)
    0x000000000040107c <+60>:    callq  0x401000 <main.myFunc>
    0x0000000000401081 <+65>:    add    $0x10,%rsp
    0x0000000000401085 <+69>:    retq
    0x0000000000401086 <+70>:    callq  0x44b040 <runtime.morestack_noctxt>
    0x000000000040108b <+75>:    jmp    0x401040 <main.main>
    0x000000000040108d <+77>:    int3
    0x000000000040108e <+78>:    int3
    0x000000000040108f <+79>:    int3
  End of assembler dump.
  (gdb) ni
  0x0000000000401072      11              f(0x100)
  (gdb) p $rbx
  $5 = 4198544
  (gdb) i r
  rax            0xc820000180     859530330496
  rbx            0x401090 4198544
  ...
  (gdb) x/1xg 0x401090
  0x401090 <main.main.func1>:     0xfffff8250c8b4864

接着往下执行到 +47 这一行，可以看到 ``rbx`` 里面的值在这一行会有变化，``ni`` 执行完这一行，输出寄存器的内容看一下，然后显示 ``rbx`` 指向的内存可以看到我们的匿名函数 ``func1``。

现在基本可以理清 ``Go`` 里面匿名函数与正常的函数区别，参数的传递区别不到，只是在调用方面，匿名函数需要通过一个包装对象`func1.f`` 来调用匿名函数，这个过程通过 ``rbx`` 进行二次寻址来完成调用。理论上，匿名函数也会比正常函数性能要差。


Go 中闭包的实现
----------------------------
闭包函数携带着定义这个函数的的环境。

.. code-block:: go

    package main

    func myFunc() func() int{
            foo := 0
            return func() int {
                    foo++
                    return foo
            }
    }

    func main() {
            bar := myFunc()
            value_1 := bar()
            value_2 := bar()

            println(value_1) // 1
            println(value_2) // 2
    }

与分析匿名函数的过程一样，编译然后通过 ``gdb`` 来跟踪。

.. code-block:: bash

   $ go build -gcflags "-N -l -m"  closure_func.go
   # command-line-arguments
   ./closure_func.go:5: func literal escapes to heap
   ./closure_func.go:5: func literal escapes to heap
   ./closure_func.go:4: moved to heap: foo
   ./closure_func.go:6: &foo escapes to heap

   $ gdb closure_func
   (gdb) b main.main
   Breakpoint 1 at 0x4010d0: file /root/data/example/closures/closure_func.go, line 11.
   (gdb) r
   Starting program: /root/data/example/closures/closure_func
   [New LWP 5367]
   [New LWP 5368]
   [New LWP 5370]
   [New LWP 5369]

   Breakpoint 1, main.main () at /root/data/example/closures/closure_func.go:11
   11      func main() {
   (gdb) i locals
   value_2 = 859530428512
   value_1 = 0
   bar = {void (int *)} 0xc820039f40

``gdb`` 在 ``main.main`` 设置断点并输出环境变量可以看到 ``bar``，而且 ``bar`` 是一个指针。

.. code-block:: bash

   (gdb) disassemble
   Dump of assembler code for function main.main:
      0x00000000004010d0 <+0>:     mov    %fs:0xfffffffffffffff8,%rcx
      0x00000000004010d9 <+9>:     cmp    0x10(%rcx),%rsp
      0x00000000004010dd <+13>:    jbe    0x40115c <main.main+140>
      0x00000000004010df <+15>:    sub    $0x20,%rsp
      0x00000000004010e3 <+19>:    callq  0x401000 <main.myFunc>
   => 0x00000000004010e8 <+24>:    mov    (%rsp),%rbx
      0x00000000004010ec <+28>:    mov    %rbx,0x18(%rsp)
      0x00000000004010f1 <+33>:    mov    0x18(%rsp),%rbx
      0x00000000004010f6 <+38>:    mov    %rbx,%rdx
      ...
  (gdb) i r
  rax            0x80000  524288
  rbx            0xc82000a140     859530371392
  ...
  (gdb) x/2xg 0xc82000a140
  0xc82000a140:   0x0000000000401170      0x000000c82000a0b8
  (gdb) x/2xg 0x0000000000401170
  0x401170 <main.myFunc.func1>:   0x085a8b4810ec8348      0x44c74808245c8948

将程序继续向下走到 +24 这一行，然后输出寄存器的信息，能够发现寄存器 ``rbx`` 与之前匿名函数的作用类似，都指向了闭包返回对象。里面封装着我们需要用到的匿名函数。可以看到匿名函数作为返回结果，整个调用过程跟是否形成闭包区别不大。那这个区别在哪里呢？

.. code-block:: bash

  (gdb) disassemble
  Dump of assembler code for function main.main:
    0x00000000004010d0 <+0>:     mov    %fs:0xfffffffffffffff8,%rcx
    0x00000000004010d9 <+9>:     cmp    0x10(%rcx),%rsp
    0x00000000004010dd <+13>:    jbe    0x40115c <main.main+140>
    0x00000000004010df <+15>:    sub    $0x20,%rsp
    0x00000000004010e3 <+19>:    callq  0x401000 <main.myFunc>
    0x00000000004010e8 <+24>:    mov    (%rsp),%rbx
    0x00000000004010ec <+28>:    mov    %rbx,0x18(%rsp)
    0x00000000004010f1 <+33>:    mov    0x18(%rsp),%rbx
    0x00000000004010f6 <+38>:    mov    %rbx,%rdx
  => 0x00000000004010f9 <+41>:    mov    (%rdx),%rbx
    0x00000000004010fc <+44>:    callq  *%rbx
    0x00000000004010fe <+46>:    mov    (%rsp),%rbx
    0x0000000000401102 <+50>:    mov    %rbx,0x10(%rsp)
    ...
  End of assembler dump.
  (gdb) ni
  0x00000000004010fc      13              value_1 := bar()
  (gdb) si
  main.myFunc.func1 (~r0=859530371392) at /root/data/example/closures/closure_func.go:5
  5               return func() int {
  (gdb) disassemble
  Dump of assembler code for function main.myFunc.func1:
  => 0x0000000000401170 <+0>:     sub    $0x10,%rsp
    0x0000000000401174 <+4>:     mov    0x8(%rdx),%rbx
    0x0000000000401178 <+8>:     mov    %rbx,0x8(%rsp)
    0x000000000040117d <+13>:    movq   $0x0,0x18(%rsp)
    0x0000000000401186 <+22>:    mov    0x8(%rsp),%rbx
    0x000000000040118b <+27>:    mov    (%rbx),%rbp
    ...
  End of assembler dump.
  (gdb) i r
  rax            0x80000  524288
  rbx            0x401170 4198768
  rcx            0xc820000180     859530330496
  rdx            0xc82000a140     859530371392
  ...
  (gdb) x/2xg 0xc82000a140
  0xc82000a140:   0x0000000000401170      0x000000c82000a0b8
  (gdb) x/2xg 0x0000000000401170
  0x401170 <main.myFunc.func1>:   0x085a8b4810ec8348      0x44c74808245c8948
  (gdb) x/2xg 0x000000c82000a0b8
  0xc82000a0b8:   0x0000000000000000      0x3d534e4d554c4f43

让程序执行到 +44 行，``si`` 进入到匿名函数内部。在 ``func1`` 内部可以看到从 ``rdx`` 取数据。输出 ``rdx`` 内容，可以看到前面指向匿名函数，而后面则指向另外的内容 ``0x0000000000000000``。

.. code-block:: bash

  (gdb) b 14
  Breakpoint 2 at 0x401107: file /root/data/example/closures/closure_func.go, line 14.
  (gdb) c
  Continuing.

  Breakpoint 2, main.main () at /root/data/example/closures/closure_func.go:14
  14              value_2 := bar()
  14              value_2 := bar()
  (gdb) disassemble
  Dump of assembler code for function main.main:
    0x00000000004010d0 <+0>:     mov    %fs:0xfffffffffffffff8,%rcx
    0x00000000004010d9 <+9>:     cmp    0x10(%rcx),%rsp
    0x00000000004010dd <+13>:    jbe    0x40115c <main.main+140>
    0x00000000004010df <+15>:    sub    $0x20,%rsp
    0x00000000004010e3 <+19>:    callq  0x401000 <main.myFunc>
    0x00000000004010e8 <+24>:    mov    (%rsp),%rbx
    0x00000000004010ec <+28>:    mov    %rbx,0x18(%rsp)
    0x00000000004010f1 <+33>:    mov    0x18(%rsp),%rbx
    0x00000000004010f6 <+38>:    mov    %rbx,%rdx
    0x00000000004010f9 <+41>:    mov    (%rdx),%rbx
    0x00000000004010fc <+44>:    callq  *%rbx
    0x00000000004010fe <+46>:    mov    (%rsp),%rbx
    0x0000000000401102 <+50>:    mov    %rbx,0x10(%rsp)
  => 0x0000000000401107 <+55>:    mov    0x18(%rsp),%rbx
    0x000000000040110c <+60>:    mov    %rbx,%rdx
    0x000000000040110f <+63>:    mov    (%rdx),%rbx
    0x0000000000401112 <+66>:    callq  *%rbx
    0x0000000000401114 <+68>:    mov    (%rsp),%rbx
    ...
  End of assembler dump.
  (gdb) ni 3
  0x0000000000401112      14              value_2 := bar()
  (gdb) disassemble
  Dump of assembler code for function main.main:
    0x00000000004010d0 <+0>:     mov    %fs:0xfffffffffffffff8,%rcx
    0x00000000004010d9 <+9>:     cmp    0x10(%rcx),%rsp
    0x00000000004010dd <+13>:    jbe    0x40115c <main.main+140>
    0x00000000004010df <+15>:    sub    $0x20,%rsp
    0x00000000004010e3 <+19>:    callq  0x401000 <main.myFunc>
    0x00000000004010e8 <+24>:    mov    (%rsp),%rbx
    0x00000000004010ec <+28>:    mov    %rbx,0x18(%rsp)
    0x00000000004010f1 <+33>:    mov    0x18(%rsp),%rbx
    0x00000000004010f6 <+38>:    mov    %rbx,%rdx
    0x00000000004010f9 <+41>:    mov    (%rdx),%rbx
    0x00000000004010fc <+44>:    callq  *%rbx
    0x00000000004010fe <+46>:    mov    (%rsp),%rbx
    0x0000000000401102 <+50>:    mov    %rbx,0x10(%rsp)
    0x0000000000401107 <+55>:    mov    0x18(%rsp),%rbx
    0x000000000040110c <+60>:    mov    %rbx,%rdx
    0x000000000040110f <+63>:    mov    (%rdx),%rbx
  => 0x0000000000401112 <+66>:    callq  *%rbx
    0x0000000000401114 <+68>:    mov    (%rsp),%rbx
    ...
  End of assembler dump.
  (gdb) si
  main.myFunc.func1 (~r0=1) at /root/data/example/closures/closure_func.go:5
  5               return func() int {
  (gdb) disassemble
  Dump of assembler code for function main.myFunc.func1:
  => 0x0000000000401170 <+0>:     sub    $0x10,%rsp
    0x0000000000401174 <+4>:     mov    0x8(%rdx),%rbx
    0x0000000000401178 <+8>:     mov    %rbx,0x8(%rsp)
    0x000000000040117d <+13>:    movq   $0x0,0x18(%rsp)
    0x0000000000401186 <+22>:    mov    0x8(%rsp),%rbx
    0x000000000040118b <+27>:    mov    (%rbx),%rbp
    ...
  End of assembler dump.
  (gdb) i r
  rax            0x80000  524288
  rbx            0x401170 4198768
  rcx            0xc820000180     859530330496
  rdx            0xc82000a140     859530371392
  ...
  (gdb) x/2xg 0xc82000a140
  0xc82000a140:   0x0000000000401170      0x000000c82000a0b8
  (gdb) x/2xg 0x000000c82000a0b8
  0xc82000a0b8:   0x0000000000000001      0x3d534e4d554c4f43
  (gdb) i locals
  &foo = 0xc82000a0b8

设置断点进入到下一次闭包内，输出相同的内容，会发现 ``rdx`` 后半段指向的内容发生了变化。通过 ``i locals`` 查看环境变量，可以看到 foo 的地址是 ``0xc82000a0b8`` ， 跟 ``rdx`` 的后半段内容一样。

由此可以判断，闭包返回的包装对象是一个复合结构，里面包含匿名函数的地址，以及环境变量的地址。

注意事项
----------------------------

1. 匿名函数作为返回对象性能上要比正常的函数性能要差。
2. 闭包可能会导致变量逃逸到堆上来延长变量的生命周期，给 GC 带来压力。
3. 破除迷信，批判性的看任何人的 Blog。

PS: 有些 Blog 写的内容都是错的还自诩对 Go 底层非常了解，这种误人子弟的不要太多。






.. _Qyuhen: https://qyuhen.bearychat.com

.. _gobyexample: https://gobyexample.com/closures
