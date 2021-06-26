参考：
- [python-redis操作](https://www.runoob.com/w3cnote/python-redis-intro.html)
- [redis命令详解](https://www.runoob.com/redis/redis-sets.html)

# scan类命令
- [深入理解Redis的scan命令](https://www.jianshu.com/p/be15dc89a3e8)
- [SCAN cursor](https://redis.io/commands/scan)

目标是**非阻塞式查询**

方式1：scan、hscan、sscan、zscan
方式2：keys、smembers

1的优点是迭代式取值，对redis压力小；缺点是返回结果可能重复，在查询中间有状态变化的key（例如新增或者删除），不确保会在结果中返回
2的优点是一次返回结果，缺点造成redis阻塞（redis是单线程的）

```python
cache = await get_redis_connection('default')

# scan类的方法返回结果可能重复
keys = set()
begin_pos = 0
while len(keys) < limit:
    # 设置1000是为了优化匹配数量特别少的key
    begin_pos, slice_data = await cache.scan(begin_pos, f"*{key}*", 1000)
    keys = keys | set(slice_data)
    if begin_pos == 0:
    break
```

