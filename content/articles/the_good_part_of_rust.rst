The Good Part of Rust
=================================================

:date: 2019-03-06
:author: SunisDown
:categories: pl
:tags: rust
:comments:

Rust 语言中最有趣的两个特性分别是 ownership 和 borrowing，通过这两个特性，Rust 实现了他所谓的最安全的变成语言。

Ownership
~~~~~~~~~~

1. Each value in Rust has a variable that’s called its owner.
2. There can only be one owner at a time.
3. When the owner goes out of scope, the value will be dropped.

Rust 的 ownership 往前可以追溯到 Wadler 开发的一个函数式编程语言，这个语言也跟 Rust 一样，没有 gc，但是也不需要手动管理内存。Wadler 主要是通过程序运行时，不断的复制数据做到这一点。在论文中可以这么实现，但是现实世界中做工程的时候，这种复制带来的性能损耗是无法接受的。Rust 的 ownership 简单来理解有点类似，但是 Rust 不是频繁的拷贝数据，而是复用内存里面的对象。
在 Rust 中，每个值都有他自己的 owner，传递或者返回某一个值，就意味着从原本的 owner 把值给了新的 owner。
我们通过下面的例子来看一下


.. code-block:: rust

    fn make_str() {
        let mut s = String::from("hello"); // 字符串被创建，owner 是 s，s属于 make_str 这个作用域。
        s.push_str(", world!"); // s 是 owner
        s.push_str("你好，世界!"); // s 是 owner
        println!("{}", s); // s 是 owner
        // 作用域到此结束， s 被销毁。
    }
    fn main() {
        make_str();
    }

这个例子中，我们创建另一个字符串，然后向他push了一些元素进去。 make_str 这个作用域中，s 一直是有效的，在这个作用域中，可以对s的值做任何操作。但是在 make_str 结束的时候，s 被自动回收。

当我们要把一个值作为返回值，或者传递给其他变量的时候，则是另外一种状态。这里为了方便调试，不在使用 String 类型，而是用 Vec<i32> 类型。

.. code-block:: rust

    fn make_vec() -> Vec<i32>{
        let mut s = Vec::new(); // Vec 创建，owner 是 s，s属于 make_vec 这个作用域。
        s.push(0x100); //
        s.push(0x200); //
        s.push(0x300); // vec 扩容，在堆上申请新的地址， s.buf 指向新的地址。
        s // 把 s 的值，传递给调用这个函数的作用域中。
    }

    fn print_vec(s_parameter: Vec<i32>) {
        // 参数 s_parameter 是属于 print_str 的一部分，也存活于这个 print_str 作用域内。
        // s_parameter.buf 的地址与 make_vec 里面 s.buf 的地址相同，s_parameter 与 s 属于不同的栈空间。
        for i in s_parameter.iter() {
            println!("{}", i)
        }
        // 在 print_str 结束的时候，s_parameter 被回收。
    }

    fn main() {
        let s_new = make_vec(); // s_new 从 make_str 中把值拿过来，s_new 作为新的 owner 存在与 main 函数中。
        print_vec(s_new); // s_new 把值传递给 print_str
    }

在 make_vec 结束之前， s 被作为返回值被返回，这样在函数结束的时候，这个值并不会被销毁掉。main 函数作为调用者接管了那个返回值。
另一方面，print_vec 函数把 s_new 作为参数拿了过来，这个 Vec<i32> 对象又被从 main 函数传递给了 print_vec 函数，而 print_vec 再也没有传递这个值给别的地方，所以在 print_vec 结束的时候，顺手把这个值回收掉。

一旦把某一个值的 ownership 交给别人之后，原先的 owner 就再也无法被使用。举个例子：

.. code-block:: rust

    fn make_vec() -> Vec<i32>{
        let mut s = Vec::new(); // Vec 创建，owner 是 s，s属于 make_vec 这个作用域。
        s.push(0x100); //
        s.push(0x200); //
        s.push(0x300); // vec 扩容，在堆上申请新的地址， s.buf 指向新的地址。
        s // 把 s 的值，传递给调用这个函数的作用域中。
    }

    fn print_vec(s_parameter: Vec<i32>) {
        // 参数 s_parameter 是属于 print_str 的一部分，也存活于这个 print_str 作用域内。
        // s_parameter.buf 的地址与 make_vec 里面 s.buf 的地址相同，s_parameter 与 s 属于不同的栈空间。
        for i in s_parameter.iter() {
            println!("{}", i)
        }
        // 在 print_str 结束的时候，s_parameter 被回收。
    }

    fn main() {
        let s_new = make_vec(); // s_new 从 make_str 中把值拿过来，s_new 作为新的 owner 存在与 main 函数中。
        print_vec(s_new); // s_new 把值传递给 print_str
        let s_second = s_new; // 在编译的时候会报错， value used here after move，
        print_vec(s_second);
    }

上面这段代码在编译的时候会直接报错，

.. code-block:: shell

   error[E0382]: use of moved value: `s_new`

编译器说 s_new 已经被移走了，这个值的 owner 已经不在是 s_new。在这个例子中， 我们创建的 vector 已经被回收了。



Borrowing
~~~~~~~~~~

前面的 ownership 里面，每个值都在同一时间都只有一个 owner。Rust 还允许开发者在同时对某一个值持有多个引用。举个例子：

.. code-block:: rust

    fn main() {
        #[derive(Debug)]
        struct Point{x:i32, y:i32};

        let mut pt = Point{x:6, y:9}; 
        let x = &pt; 
        let y = &pt; // 这里不会报错。
        println!("Hello, world!{:?}", x);
        println!("Hello, world!{:?}", y);
    }

上面的例子中，我们不再是传递值给 x 或者 y，而是创建一个 pt 的引用，然后分别借给 x，y。也就是我们常说的指针。就像我们在注释中说的那样，在第二次传递 pt 的引用的时候，编译器不会报错。因为这里的指针是允许被共享的。但是与正常的指针不太一样的时候，我们没有办法通过这些指针来修改这个对象。一旦我们尝试修改，编译的时候就会报错。

如果想要通过某一个指针来修改对象，可以用可修改的指针引用。这种引用有点像之前的 ownership，同一时间只有一个引用。例子如下：


.. code-block:: rust

    fn main() {
        #[derive(Debug)]
        struct Point(i32, i32);

        let mut pt = Point(6, 9); 
        let x = &mut pt; 
        let y = &pt; // cannot borrow `pt` as immutable because it is also borrowed as mutable
        let z = &mut pt; // cannot borrow `pt` as mutable more than once at a time
        println!("Hello, world!{:?}", x);
        println!("Hello, world!{:?}", y);
    }

上面的例子中，我们创建了一个独一无二的引用，而不是共享指针。在我们的代码里面，后面的 y，z 又像重复引用这个对象，这种时候会在编译时报错。这种报错跟我们在最开始的看 ownership 的时候有点类似。

简单来说，borrowing 有两种不同的形式，

1. Immutable references，这种形式可以被共享，大家都可以来读，但是不可以写。
2. Mutable references，这种形式可以被更新，但是不可以被共享。同一时间只有一个引用。

