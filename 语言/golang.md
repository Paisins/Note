# go入门
教材：
## 一、数据类型
### 1、声明变量
```
# 一般形式
var 变量名称 变量类型
# 声明时赋予初始值
var 变量名 变量类型 = 值
var 变量名 = 值
# 简短形式，只能用在函数内部
变量名称 := 变量类型 
```
> 如果使用了一般形式声明了一个变量名，之后又使用简短形式定义重名对变量会报错！即，简短形式只能定义新变量。但是如果左侧又多个变量，只要有一个新变量名就可以？？？这好奇怪！

### 2、go语言中的数据类型
- bool
- string
- int、int8、int16、int32、int64
- uint、uint8、uint16、uint32、uint64、uintptr
- byte // uint8 的别名
- rune // int32 的别名 代表一个 Unicode 码
- float32、float64
- complex64、complex128
> 像这样必须声明变量的语言，如何实现动态存储未知类型的数组数据呢？

### 3、允许多重赋值
```
a, b = b, a
```
### 4、匿名变量
下划线（_）任何类型的值赋给它都会被抛弃，不占用命名空间，不分配内存

### 5、作用域
- 句法块：在花括号中显示的声明的部分
- 词法块：未在花括号中显示声明的部分
- if、switch和for中的变量的作用域只局限在代码块（即花括号中）
> 在if等结构中修改了全局变量，那么会影响到外界，也就是说全局变量真的被修改了；但是如果是内部定义的新变量，则不能在外部被调用；假如在内部重新定义了一个与全局变量重名的变量，那么在外部调用的时候仍然调用的是全局变量的值，而不是这个局部变量

### 6、数值类型
- 整数
- 浮点
- 复数

整数一般使用int较多，处理速度也最快，但是值得注意的是，在不同的编译器上，int类型或为32或为64，另外还有int8，int16，int32，int64，以及无符号的四种。

浮点数有两种类型float32和float64，前者有6位十进制的精度，后者有15位十进制的进度，使用较多的是float64，因为float累计误差容易扩大，并且表示的正数不是很大。输出时，一般可以使用%g，%e，%f，三者都可以控制输出精度，%f使用较多。
> math包中提供了+Inf（无穷大），-Inf（无穷小），NaN（非数），另外尽量不要与这三个值比较来做判断，因为它们不是唯一的。

### 7、复数类型
- complex64
- complex128()
一般很少用到复数，除了做科学计算

### 8、bool值
- 只有相同类型的值才能进行比较（==、!=等）
- 布尔值不会隐式变为0或1
> 布尔值有true，false，以及比较表达式的结果
> 如果值的类型是借口（interface），那它们也必须实现了相同的接口

### 9、字符串
- \n,\r,\t,\u,\\(反斜杠)
- 转义，“`”括起来的字符串，同样也可以实现多行字符串
- 支持数字索引
- 支持+拼接
- 单引号只能包括一个字符，双引号可以包含多个
拓展：
- len():获取长度，在go中一个中文占三个字节
- utf8.RuneCountInString():如果想把中文当作一个字符来计算长度
- ASCII 字符串遍历直接使用下标
- Unicode 字符串遍历用 for range
- 切片和python一样，string[num1:num2]
- string.Index(),string.LastIndex():反向搜索
- 默认字符串不可修改，但是通过```[]byte(string)```将字符编程byte数组，就可以修改，然后再用string()变回字符串
> 字符串与比特类型的转换：angleBytes := []byte(angel)
- bytes.Buffer 进行高效的字符串连接，使用WriteString()和String()方法
- Sprintf:返回一个格式化之后的字符串，Printf:打印出格式化的字符串和字符串变量，Println:打印出字符串和变量

### 10、byte和rune
- byte: ASCII 码的一个字符，实际上就是uint8
- rune: 一个 UTF-8 字符，实际上就是int32
```go
\\ \x: 十六进制 \: 八进制
var ch byte = 65
var ch byte = '\x41'
var ch byte = '\377'
\\ unicode, \u: 后面跟长度为4的十六进制， \U: 后面跟长度为8的十六进制
var ch int = '\u0041'
var ch2 int = '\u03B2'
var ch3 int = '\U00101234'
```
### 11、数据类型转换
go中没有隐式的类型转换，全都是显式的
```
valueoftypeB = typeB(valueoftypeA)
```
### 12、指针
go的指针跟c的很像; 类型为*T，T为指针指向的变量类型
```go
// 取变量的地址
ptr := &v
// 取指针指向的值
v := *ptr
// 创建字符串类型指针
v := new(string)
*v = 'a'
```
### 13、常量和const关键词
go中使用关键词const来定义常量，且常量必须是在编译时就可以获取到的值，限于布尔、数值和字符串类型
```
// 定义一个常量
const pi = 3.1415926
// 定义多个常量
const = {
  a = 1.234
  b = 56.789
}
// 批量声明中的省略操作, a,b,c,d = 1,1,2,2
const = {
  a = 1
  b
  c = 2
  d
}
// iota:在定义枚举类型时较为常用
// 下面属于自定义类型，也可以通过下划线跳过部分值
type Weekday int
const (
    Sunday Weekday = iota
    Monday
    Tuesday
    Wednesday
    Thursday
    Friday
    Saturday
)
```
无类型常量：无类型的布尔型、无类型的整数、无类型的字符、无类型的浮点数、无类型的复数、无类型的字符串，如math.Pi
```
var x float32 = math.Pi
var x float64 = math.Pi
```
> 为什么不直接用int，而是自定义一个Weekday呢？

### 14、枚举
go中现在没有枚举，只是一些常量集合，但是我很感兴趣的是下面这个函数
```
func (c ChipType) String() string {
    switch c {
    case None:
        return "None"
    case CPU:
        return "CPU"
    case GPU:
        return "GPU"
    }
    return "N/A"
}
```
可以重写一个类型的格式化输出，感觉会很有用
### 15、注释
go doc 工具可以查看包的文档说明注释，如果在一个函数前面添加注释的话，这段注释的内容应该以函数名开头

## 二、容器（数据结构）
### 一、数组
在go中，数组是由固定长度的特定元素类型组成的序列，很少使用
```
// 定义数组，长度可以为表达式，但是编译时必须为确定值
var 数组变量名 [长度]元素类型
```
```
var list1 [10]int
// 初始化数组
var list2 [3]int = [3]int{1, 2, 3}
// 简化定义
list3 := [3]int{1, 2, 3}
// 自动确定长度
list2 := [...]int{1, 2}
fmt.Println(list[0])
```
默认情况下，每个元素被设定为对应元素类型的零值，

## 其他

0、命名规范
> https://studygolang.com/articles/13469

1、变量逃逸分析和生命周期
> http://c.biancheng.net/view/22.html

栈和堆在内存分配中的作用，局部变量一般使用栈来分配内存，当程序结束（如函数）自动回收，或者某个值被返回到函数外，这是会发生逃逸，内存分配到堆里；全局变量一般使用堆来分配内存；如果变量被取地址返回到函数外，也会将内存转移到堆中，防止不可预知的错误；放到堆中的内存由垃圾回收器自动回收
- 所谓不可预知的错误是指，栈中的内存被回收之后，这块内存地址可能会被分配给任意值，而引起的错误吗？
- 垃圾回收器是如何回收堆中的内存的？

一般来说，全局变量是与整个程序的运行周期一致，而局部变量则有很多可能，如果没有从局部作用域中逃逸，那么会随局部程序完结而被回收？
> 难道垃圾回收器会一遍一遍的遍历，这不是很浪费性能吗？

1、图像处理

2、垃圾回收

- image
- image/color
- image/png

3、编码
- encoding/base64

4、flag定义命令行参数

- flag.String(params, default, help)

5、time
- time.Duration
- time.Minute

6、类型别名与类型定义
- type a int
- type a = int

# 中等
[Golang开发新手常犯的50个错误](https://blog.csdn.net/gezhonglei2007/article/details/52237582)

# 面试
[超全golang面试题合集+学习指南+知识图谱](https://segmentfault.com/a/1190000038922260)