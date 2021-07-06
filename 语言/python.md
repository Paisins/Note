本文用于整理面试题中关于python可能涉及的要点

# 垃圾回收机制
垃圾回收机制以引用计数为主，以标记清除为辅，并使用分代回收优化回收效率。
> 引用计数：Python在内部维护了针对每一个对象的引用计数， 当一个对象创建或者被引用时，其引用计数将加1，当一个对象被销毁或作用域失效时， 其引用计数将减1。只有对象的引用计数为0时，这个对象将会被回收。引用计数的优点：简单、具有实时性。缺点：对象循环引用时将永远不会被销毁。

> 标记清除：对于对象循环引用的状况Python使用标记清除来解决，Python在内部实现了一个循环检测器， 不停的检测对象是否存在循环引用，如果两个对象互相循环引用并且不包含其他第三者对象时， 其将会被收回。

> 分代回收是基于这样的一个统计事实，对于程序，存在一定比例的内存块的生存周期比较短；而剩下的内存块，生存周期会比较长，甚至会从程序开始一直持续到程序结束。生存期较短对象的比例通常在 80%～90% 之间，这种思想简单点说就是：对象存在时间越长，越可能不是垃圾，应该越少去收集。这样在执行标记-清除算法时可以有效减小遍历的对象数，从而提高垃圾回收的速度。

1、垃圾回收时，Python不能进行其它的任务，频繁的垃圾回收将大大降低Python的工作效率；
2、Python只会在特定条件下，自动启动垃圾回收（垃圾对象少就没必要回收）
3、当Python运行时，会记录其中分配对象(object allocation)和取消分配对象(object deallocation)的次数。当两者的差值高于某个阈值时，垃圾回收才会启动。

# 内存池
> Python使用了内存池机制来管理内存，其内存以金字塔的形式对内存功能进行划分，-1、-2层主要用于对操作系统进行操作， 0层中是C的malloc,、free等等内存分配和释放函数。1、2层是一个内存池， 当对象小于265K时将直接由这片内存池进行分配内存，否则将调用第0层中的C函数来分配内存，当小于265K的对象被销毁时， 其内存也不会被销毁， 只是返回给了内存池以便二次利用。2层是对Python对象进行操作。第3层：最上层，用户对Python对象的直接操作

对我来说，参考线程池就比较容易理解内存池

# 多进程、多线程、协程

参考资料：
多进程、多线程：https://blog.csdn.net/weixin_42134789/article/details/82992326
进程Queue和普通Queue的区别：https://blog.csdn.net/qq_32446743/article/details/79785684
多线程与异步的区别：https://www.cnblogs.com/dream844/archive/2012/06/12/2546083.htm

## 一、认识GIL
来源：https://zhuanlan.zhihu.com/p/94909455
> NRMUTEX中的thread_id就表明GIL锁目前被哪个thread拥有，只有一个线程拥有了GIL锁，他才能被解释器解释执行，同一个python进程里面的其他线程就需要等待NRMUTEX的释放。举个例子类比下，正常的多线程程序就像多个人同时干原本一个人干的活，由于多个人同时干，那么自然就会快不少，但是在Python的情况里面，这多个工人都得拿到一张令牌后才能干活，而令牌只有一个，一次只能发给一个工人，其他没拿到令牌的工人就得原地等待，直到拿到令牌为止，这样时时刻刻其实仍然只有最多一个工人在干活。这就会导致如下这个场景的问题出现：

终于对GIL有比较形象的认识了

> 但是由于CPython中GIL锁的存在，C1调度执行T1的时候，GIL锁被T1占着，T2拿不到GIL锁，处于阻塞的状态，等到T1执行结束或者执行的字节码行数到了设定的阈值，T1就会释放GIL锁，然后T2获得GIL锁之后再继续执行。这样的结果就是，这个拥有2个纯CPU计算线程的python程序进程运行结束需要8s，因为每个时刻，python进程中永远只有一个线程再被运行。那这就很胃疼了，这么看似乎python的多线程就没用了？也不是的， 上述情况下多线程没用，是因为我们假定的是每个线程运行代码都是纯CPU计算过程，不会遇到IO等阻塞操作，只在执行结束或者“轮转时间片”到了之后才会被切换，（ 之所以打引号，是因为python的多线程调度的轮转时间片并不是常规CPU时间片，而是按照字节码来算的）。但是如果T1线程有IO操作会被阻塞，会在IO操作前提前释放GIL锁，进而T2线程获得GIL，可以正常被CPU调度执行，这样Python程序进程仍然处于继续运行的状态，而不会像单线程的时候遇到IO会被阻塞等待。话虽如此，除了少部分高端玩家，大部分情况下，我们用python的多线程时，不但没有发挥出多线程的并行威力，反而还承受了多线程的高昂的切换开销以及应对复杂的锁同步的问题。那么这个开销到底有多高昂呢？

有个问题是，如果判断区分io操作和纯cpu计算呢？io当然是指读写，而cpu计算指视频解码或者数学逻辑计算等。有时候我们不能简单拆分开来，例如ffmpeg处理的时候是既有cpu计算，也有写入，当然我们可以研究一下ffmpeg是如何实现自己的并行的
## 二、GIL和引用计数以及垃圾回收
来源：https://zhuanlan.zhihu.com/p/194990821
> 这种方法虽然使得python多线程没法利用多核，但是从加锁的角度来讲是足够简单的，对线程的性能影响也是足够小的。当然了，不能使用多核也不是说python的多线程没用，当遇到IO比较多的场景下，python的多线程还是比较有用的。虽然没法多核，但是却能总体上让进程使用更多的CPU时间，进而加速了完成任务所需要的时间。因为当python线程调用一些阻塞调用时，会事先释放掉GIL锁让别的线程继续执行，然后自己继续执行阻塞调用，执行完阻塞调用之后再重新申请获得GIL。当释放GIL锁执行阻塞调用时，此时的python线程与操作系统其它的线程一致，可以被多核调度。比如以python中的sleep为例， 当调用sleep时，其底层的源码实现如下，我们看到再调用select/Sleep这样的阻塞调用之前，都会有 Py_BEGIN_ALLOW_THREADS， 阻塞调用结束之后，都会有Py_END_ALLOW_THREADS， 这两个分别就是释放锁和重新申请获得锁的操作。一旦重新申请获得锁，该线程就得等待其他线程释放锁。而在此期间，由于自己释放了锁，别的线程得到了继续往下执行的机会，没有浪费自己等待的时间。

那我比较好奇的是这两句
> 这种方法虽然使得python多线程没法利用多核

> 当释放GIL锁执行阻塞调用时，此时的python线程与操作系统其它的线程一致，可以被多核调度

我感觉有些矛盾，多核到底是如何提高了python的多线程效率的呢？有点懂了

## 二、再次理解并发和并行
来源：https://zhuanlan.zhihu.com/p/96048314

> 并发
计算机中每一个线程都是一个执行任务，假设我们现在有一个单核的CPU，CPU每时每刻只能调度执行一个线程，我们第一种做法就是让所有的线程排好队，一个任务一个任务的依次执行，执行完一个执行下一个。采用这种方式的调度带来的问题就是，如果当前执行的任务陷入了死循环，那么CPU会一直卡在这个任务上，导致后续的任务无法执行。所以，操作系统采用的方案是，每个任务分一个时间片来执行，时间片结束之后便切换任务，换另一个执行，做到雨露均沾。假设我们有4个任务，每个任务都分250ms进行计算，那么1s后，每个任务的拥有者都发现自己的任务往前进行了一点，这就是我们提到的并发（concurrency）。在POSIX中，并发的定义要求“延迟调用线程的函数不应该导致其他线程的无限期延迟”。我们上面的四个任务中，并发操作之间可能任意交错，对任务的拥有者来说，1s后四个任务都往前推进了一部分，好像四个任务是并行执行的，但是实际CPU执行任务的时候还是一个一个执行的，所以并发不代表操作同时进行。那么如果我有四个核心的CPU会怎么样呢，4个CPU核心会各自拿一个任务执行，这种情况才是我们常说的并行。
并行
并行只在多处理器的情况下才存在，因为每个处理器可以各自执行一个任务，这时四个任务便是并行执行的。单处理器的情况下是没办法做到并行的。所以我们回顾中会说，即使在多核的CPU计算资源情况下，python的多线程没有达到并行而只能达到并发，因为多个线程无法同时被执行，只能击鼓传花似的被依次的执行。

终于懂了点为什么协程的效率比多线程更高，因为切换线程的代价要比切换协程的代价高！

## 三、进程、线程和协程与资源、与任务的关系

多核可以开多进程，也可以开多线程

由于GIL，所以计算密集型，建议开多进程；IO密集型，建议多线程

多进程的数量跟cpu核有关；而多线程由于逻辑是并发的，所以跟cpu无关，但是跟其他内存等资源有关，因此要考虑其他限制

## 四、深入理解协程
最近实现socket的时候，我发现之前使用协程的方式有可能是错的，因为我调用的处理函数依旧是阻塞函数，而并非协程函数，由此我想深入理解一下协程的实现细节，同时以后也可以跟go语言的协程做比较。

**参考**
- 流畅的python

**切入点**

- 重写download-blob-videos中的下载代码，最好可以找一个视频下载比较一下
- 理解loop和async函数的内部实现，重点思考如何函数在遇到io的时候如何保存上下文，如何知道io完成，如何重新被唤醒；这里猜测每个协程库都在io的位置用某种方式添加上述逻辑，另外直觉上我不认为这里跟网络io一样使用的是文件修饰符的方式，效率上也太低了
- 目前看到很多cpython的实现都被隐藏了，可能会花费时间找到这部分

# 类
## 设计模式

### 单例模式
单例模式
单例是一种设计模式，应用该模式的类只会生成一个实例。

#### 使用函数装饰器实现
```python
def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner
    
@singleton
class Cls(object):
    def __init__(self):
        pass

cls1 = Cls()
cls2 = Cls()
print(id(cls1) == id(cls2))

```

#### 使用类装饰器实现
```
class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]

@Singleton
class Cls2(object):
    def __init__(self):
        pass

cls1 = Cls2()
cls2 = Cls2()
print(id(cls1) == id(cls2))
```

#### new方法实现
如果有参数，则不算单例模式，因为执行完new之后还要init方法，不同初始化是不一样的，从这个角度来讲，单例模式本身也不应该传入参数，所以应该还是对的
```
class Single(object):
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            # super可以不加参数
            cls._instance = super(Single, self).__new__(cls, *args, **kw)
        return cls._instance
    def __init__(self):
        pass

single1 = Single()
single2 = Single()
print(id(single1) == id(single2))
```
#### 文件实现
```
# 创建Singleton.py文件
class A(object):
    def foo(self):
       print('test')
v = A()
===============================================
# 创建另一文件，调用该实例
from singleton import A as a1
from singleton import A as a2

print(a1, id(a1))
print(a2, id(a2))
```

#### meta方法
```
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Cls4(metaclass=Singleton):
    pass

cls1 = Cls4()
cls2 = Cls4()
print(id(cls1) == id(cls2))
```

### 工厂模式
[Python与设计模式--工厂类相关模式](https://developer.aliyun.com/article/70417)

# 装饰器
四种类型：
- 函数装饰器装饰函数
- 函数装饰器装饰类
- 类装饰器装饰函数
- 类装饰器装饰类
```python
# 简单函数装饰器
def wrapper(func):
    def inner_func(*args, **kwargs):
        func(*args, **kwargs)
    return inner_func

@wrapper
def fun(*args, **kwargs):
    print('123')

# 装饰类
def wrapper(cls):
    def inner_func(*args, **kwargs):
        print(cls.__name__)
    return inner_func

@wrapper
class Cls:
    def __init__(self, *args, **kwargs):
        pass
    def func(self, *args, **kwargs):
        print(*args, **kwargs)
        
# 进阶
def outer_func(a, b, c):
    def warpper(func):
        def inner_func(*args, **kwargs):
            print(a, b, c)
            func(*args, **kwargs)
        return inner_func
    return wrapper

@outer_func(a, b, c)
def func(*args, **kwargs):
    print('123')

# 类装饰器
class outer:
    def __init__(self, a, b, c):
        self.a, self.b, self.c  = a, b, c
    def __call__(self, func):
        def wrapper(func):
            def inner_func(*args, **kwargs):
                print(self.a, self.b, self.c)
                func(*args, **kwargs)
            return inner_func
        return wrapper
@outer(a, b, c)
def func(*args, **kwargs):
    print('123')
    
class Outer:
    def __init__(self, cls):
        self.cls = cls
    def __call__(self, cls):
        def inner_func(*args, **kwargs):
            print(self.cls.__name__)
            cls(*args, **kwargs)
        return inner_func

@Outer
class Cls:
    def __init__(self, *args, **kwargs):
        pass
    def func(self, *args, **kwargs):
        print(*args, **kwargs)
```

# 小技巧

1、快捷条件操作：a is not None and b.append(a)
2、集合操作：交集：a & b 并集：a | b 差集：a -b 
3、functools.partial
4、指明类型
```python
def func(a:int, b:int) -> int:
    return 0
```

