Learning Rust with LLDB
=================================================

:date: 2019-01-14
:author: SunisDown
:categories: pl
:tags: rust
:comments:


为什么要学习 `Rust` 呢？因为 Go 自带的 GC 还不够强，同时 goroutine 的调度机制又导致 go 对 CPU 也没办法用的很充分。当需要写对 CPU 性能要求比较高的系统，就需要换一门新语言。同时因为不想写 Cpp，Rust 有媲美 Cpp 的性能，相对 Cpp 来讲更好维护的代码。学习一下没有毛病。


Hello Hex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
通常学习一门新语言都是用 `Hello World` 来开始，但是因为字符串类型相比与int或者是 hex 要复杂的多，我们这里用 `Hex` 来替代 `Hello world` 。在之前我已经装好了 rust 的各种环境，包含 cargo 之类的包管理，在这里我用 cargo 创建一个新的项目。


.. code-block:: shell

                cargo new helloHex
                cd helloHex


然后将如下内容编辑到 `src/main.rs` 里面，              

.. code-block:: rust

    fn main() {
      let x = 0x100;
      println!("{}", x);
    }

编辑完这个文件之后，我们再编译他，通常情况下为了方便调试，我们都会在编译的时候禁止编译器对程序进行优化，在 C/Go 中需要加一些参数来完成这项工作， `cargo` 这个工具省略了这个步骤，直接会生成一个 debug 版本，我们可以直接拿来调试。编译命令如下：

.. code-block:: shell

   cargo build
   lldb target/debug/helloHex


现在我们已经进入到了 lldb 的调试界面中，然后我们可以设置断点，查看堆栈信息等。我们先做一些简单的操作来熟悉一下 lldb。 在指令后面我加上了注释，说明了每一条命令的作用。

.. code-block:: shell

              $  lldb target/debug/helloHex
              (lldb) target create "target/debug/helloHex"
              Current executable set to 'target/debug/helloHex' (x86_64).
              (lldb) b helloHex::main  // 这条指令是对 helloHex 好个程序的 main 函数打一个断点
              Breakpoint 1: where = helloHex`helloHex::main::hc8d39b80069dcddb + 18 at main.rs:2, address = 0x00000001000011d2
              (lldb) r // run 开始执行 helloHex 程序
              Process 84414 launched: '/Users/chaotang.sun/rust_project/rustlearing/lldb/helloHex/target/debug/helloHex' (x86_64)
              Process 84414 stopped
              * thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
                  frame #0: 0x00000001000011d2 helloHex`helloHex::main::hc8d39b80069dcddb at main.rs:2
                1    fn main() {
              -> 2        let x = 0x100;
                3        println!("{}", x);
                4    }
              Target 0: (helloHex) stopped.
              (lldb) s // step 执行下一步机器指令
              Process 84414 stopped
              * thread #1, queue = 'com.apple.main-thread', stop reason = step in
                  frame #0: 0x00000001000011d9 helloHex`helloHex::main::hc8d39b80069dcddb at main.rs:3
                1    fn main() {
                2        let x = 0x100;
              -> 3        println!("{}", x);
                4    }
              Target 0: (helloHex) stopped.
              (lldb) frame v // 查看当前栈的变量
              (int) x = 256
              (lldb) p x // 打印变量 x 的值
              (int) $0 = 256
              (lldb)
              (int) $1 = 256


Variables & Const
~~~~~~~~~~~~~~~~~~
Rust 的变量相对 C 来说有一些特殊，有可变的变量跟不可变的变量。（这有点绕，不可变的变量还可以称之为变量嘛？ 他们有什么区别，除了在语法上的之外，我也很好奇对于CPU来说，处理这两种不同的变量有什么区别。
在这里我创建两段不同的程序，一段是用 `mutable` 的变量，一段是用 `immutable` 的变量，然后反编译看一下这俩到底有什么区别。

.. code-block:: rust

   $ cargo new var_immut
   fn main() {
    let x = 0x100;
    println!("The value of x is: {}", x);

    let x = x + 0x100;
    println!("The value of x is: {}", x);
  }


.. code-block:: rust

   $ cargo new var_mut
   fn main() {
    let mut x = 0x100;
    println!("The value of x is: {}", x);

    x = x + 0x100;
    println!("The value of x is: {}", x);
  }
  
然后我们进入到 lldb 之中反编译这两段程序。

.. code-block:: shell

   lldb target/debug/var_mut
   lldb target/debug/var_immut

这两端程序反编译之后的结果机器相似，这里就只放其中一个截取的片段来展示：

.. code-block:: shell

   (lldb) b var_mut::main
    Breakpoint 1: where = var_mut`var_mut::main::hbe57c58c6c7f6d8b + 18 at main.rs:2, address = 0x00000001000012a2
    (lldb) r
    Process 88038 launched: '/Users/chaotang.sun/rust_project/rustlearing/lldb/var_mut/target/debug/var_mut' (x86_64)
    Process 88038 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
        frame #0: 0x00000001000012a2 var_mut`var_mut::main::hbe57c58c6c7f6d8b at main.rs:2
      1    fn main() {
    -> 2        let mut x = 0x100;
      3        println!("The value of x is: {}", x);
      4        x = x + 0x100;
      5        println!("The value of x is: {}", x);
      6    }
    Target 0: (var_mut) stopped.
    (lldb) disassemble
    var_mut`var_mut::main::hbe57c58c6c7f6d8b:
        0x100001290 <+0>:   pushq  %rbp
        0x100001291 <+1>:   movq   %rsp, %rbp
        0x100001294 <+4>:   subq   $0xf0, %rsp
        0x10000129b <+11>:  leaq   0x4150e(%rip), %rsi       ; core::fmt::num::_$LT$impl$u20$core..fmt..Display$u20$for$u20$i32$GT$::fmt::h04ca12b7570d3d05 at num.rs:201
    ->  0x1000012a2 <+18>:  movl   $0x100, -0xa4(%rbp)       ; imm = 0x100
        0x1000012ac <+28>:  leaq   -0xa4(%rbp), %rax

        .....

        0x100001328 <+152>: movq   $0x1, (%rsp)
        0x100001330 <+160>: callq  0x100001100               ; core::fmt::Arguments::new_v1_formatted::h1a26f71ed7a6be2c at mod.rs:363
        0x100001335 <+165>: leaq   -0xa0(%rbp), %rdi
        0x10000133c <+172>: callq  0x10000a010               ; std::io::stdio::_print::h85f0ba007302c9c0 at stdio.rs:708
        0x100001341 <+177>: movl   -0xa4(%rbp), %eax
        0x100001347 <+183>: addl   $0x100, %eax              ; imm = 0x100

        ......

        0x100001400 <+368>: addq   $0xf0, %rsp
        0x100001407 <+375>: popq   %rbp
        0x100001408 <+376>: retq
        0x100001409 <+377>: leaq   0x53f40(%rip), %rdi
        0x100001410 <+384>: callq  0x100047bf0               ; core::panicking::panic::h3941d6082b26bb8e at panicking.rs:44
        0x100001415 <+389>: nopw   %cs:(%rax,%rax)
        0x10000141f <+399>: nop


这里先不关注这个函数栈内的数据转换，只关注两个程序里面不同的变量有什么异同，所以直接跳到变量初始化与赋值的地方，看一下有什么异同。 下面的 gdb 调试分为左右两列，左边为 mutable， 右边 为 immutable 的变量。在不同的阶段我们查看 x 变量的地址，可以看到 mutable 的变量 x 地址是不变的，后面的赋值都是基于栈上某一个固定地址进行值的修改。而 immutable 的 x 地址是会变化的，每一次初始化，都会在栈内重新分配一个新的地址。

.. code-block:: shell


    (lldb) r                                                                                                               │(lldb) r
    Process 89402 launched: '/Users/chaotang.sun/rust_project/rustlearing/lldb/var_mut/target/debug/var_mut' (x86_64)      │Process 89331 launched: '/Users/chaotang.sun/rust_project/rustlearing/lldb/var_immut/target/debug/var_immut' (x86_64)
    Process 89402 stopped                                                                                                  │Process 89331 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1                                             │* thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
        frame #0: 0x00000001000012a2 var_mut`var_mut::main::hbe57c58c6c7f6d8b at main.rs:2                                 │    frame #0: 0x0000000100001242 var_immut`var_immut::main::hab4d3d25ce94e8b3 at main.rs:2
       1    fn main() {                                                                                                    │   1    fn main() {
    -> 2        let mut x = 0x100;                                                                                         │-> 2        let x = 0x100;
       3        println!("The value of x is: {}", x);                                                                      │   3        println!("The value of x is: {}", x);
       4        x = x + 0x100;                                                                                             │   4        let x = x + 0x100;
       5        println!("The value of x is: {}", x);                                                                      │   5        println!("The value of x is: {}", x);
       6    }                                                                                                              │   6    }
    Target 0: (var_mut) stopped.                                                                                           │Target 0: (var_immut) stopped.
    (lldb) frame v                                                                                                         │(lldb) frame v
    (lldb) s                                                                                                               │(lldb) s
    Process 89402 stopped                                                                                                  │Process 89331 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = step in                                                    │* thread #1, queue = 'com.apple.main-thread', stop reason = step in
        frame #0: 0x00000001000012ac var_mut`var_mut::main::hbe57c58c6c7f6d8b at main.rs:3                                 │    frame #0: 0x000000010000124c var_immut`var_immut::main::hab4d3d25ce94e8b3 at main.rs:3
       1    fn main() {                                                                                                    │   1    fn main() {
       2        let mut x = 0x100;                                                                                         │   2        let x = 0x100;
    -> 3        println!("The value of x is: {}", x);                                                                      │-> 3        println!("The value of x is: {}", x);
       4        x = x + 0x100;                                                                                             │   4        let x = x + 0x100;
       5        println!("The value of x is: {}", x);                                                                      │   5        println!("The value of x is: {}", x);
       6    }                                                                                                              │   6    }
    Target 0: (var_mut) stopped.                                                                                           │Target 0: (var_immut) stopped.
    (lldb) frame v                                                                                                         │(lldb) frame v
    (int) x = 256                                                                                                          │(int) x = 256
    (lldb)                                                                                                                 │(lldb)
    (int) x = 256                                                                                                          │(int) x = 256
    (lldb) p &x                                                                                                            │(lldb) p &x
    (int *) $0 = 0x00007ffeefbff17c                                                                                        │(int *) $0 = 0x00007ffeefbff164
    (lldb) x/xw 0x00007ffeefbff17c                                                                                         │(lldb) x/xw 0x00007ffeefbff164
    0x7ffeefbff17c: 0x00000100                                                                                             │0x7ffeefbff164: 0x00000100
    (lldb) n                                                                                                               │(lldb) n
    The value of x is: 256                                                                                                 │The value of x is: 256
    Process 89443 stopped                                                                                                  │Process 89452 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = step over                                                  │* thread #1, queue = 'com.apple.main-thread', stop reason = step over
        frame #0: 0x0000000100001341 var_mut`var_mut::main::hbe57c58c6c7f6d8b at main.rs:4                                 │    frame #0: 0x00000001000012e1 var_immut`var_immut::main::hab4d3d25ce94e8b3 at main.rs:4
       1    fn main() {                                                                                                    │   1    fn main() {
       2        let mut x = 0x100;                                                                                         │   2        let x = 0x100;
       3        println!("The value of x is: {}", x);                                                                      │   3        println!("The value of x is: {}", x);
    -> 4        x = x + 0x100;                                                                                             │-> 4        let x = x + 0x100;
       5        println!("The value of x is: {}", x);                                                                      │   5        println!("The value of x is: {}", x);
       6    }                                                                                                              │   6    }
    Target 0: (var_mut) stopped.                                                                                           │Target 0: (var_immut) stopped.
    (lldb) n                                                                                                               │(lldb) n
    Process 89443 stopped                                                                                                  │Process 89452 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = step over                                                  │* thread #1, queue = 'com.apple.main-thread', stop reason = step over
        frame #0: 0x0000000100001371 var_mut`var_mut::main::hbe57c58c6c7f6d8b at main.rs:5                                 │    frame #0: 0x000000010000130e var_immut`var_immut::main::hab4d3d25ce94e8b3 at main.rs:5
       2        let mut x = 0x100;                                                                                         │   2        let x = 0x100;
       3        println!("The value of x is: {}", x);                                                                      │   3        println!("The value of x is: {}", x);
       4        x = x + 0x100;                                                                                             │   4        let x = x + 0x100;
    -> 5        println!("The value of x is: {}", x);                                                                      │-> 5        println!("The value of x is: {}", x);
       6    }                                                                                                              │   6    }
    Target 0: (var_mut) stopped.                                                                                           │Target 0: (var_immut) stopped.
    (lldb) frame v                                                                                                         │(lldb) frame v
    (int) x = 512                                                                                                          │(int) x = 256
    (lldb) p &x                                                                                                            │(int) x = 512
    (int *) $1 = 0x00007ffeefbff17c                                                                                        │(lldb) p &x
    (lldb)                                                                                                                 │(int *) $1 = 0x00007ffeefbff1bc
    (lldb) x/xw 0x00007ffeefbff17c                                                                                         │(lldb) x/xw 0x00007ffeefbff1bc
    0x7ffeefbff17c: 0x00000200                                                                                             │0x7ffeefbff1bc: 0x00000200
