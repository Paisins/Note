我没有想django一样系统看过fastapi，完全是通过项目认识到的，也就是work_wechat_robot项目，目前已经了解了
- 接口定义、参数传入和校验、以及接口文档查看
- 数据库表以及部分查询（了解不深）

# 基础
- 服务ip:port/docs#/：不仅可以展示接口文档，而且也可以输入参数进行调试
- 如果使用uvicorn启动项目，安装uvloop也是被自动使用的

# pydantic
数据接口schema定义与检查的库

[Pydantic](https://www.cnblogs.com/fengqiang626/p/13307771.html)
[Python笔记：Pydantic库简介](https://blog.csdn.net/codename_cys/article/details/107675748)

fastapi的文档功能很好，输入参数的信息都很好的展示了出来，那么如何展示返回结果的信息呢？
在router的位置可以添加
# toroise
[toroise-Models](https://tortoise-orm.readthedocs.io/en/latest/models.html)
[异步orm之 tortoise-orm](https://blog.csdn.net/MeteorCountry/article/details/105170311)

定义数据库表， register_tortoise，配置数据库；