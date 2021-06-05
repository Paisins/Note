# 开始
## 1、安装依赖

```
# 安装django
python3 install Django==3.2.3
# 安装drf
pip3 install djangorestframework==3.12.4
```
## 2、开始项目
```
# 新建项目
django-admin startproject {project_name}
# 新建应用
python manage.py startapp {app_name}
# 命令行启动
python3 manage.py runserver 8000
# 迁移生成数据表
python manage.py makemigrations
python manage.py migrate
# 单独迁移应用
python manage.py makemigrations {app_name}
```

# 配置文件
```python
# 视情况添加项目路径
sys.path.insert(0, os.path.join(BASE_DIR, '{project_name}'))

# 添加app，用以生成对应的表，需要与项目路径对应
INSTALLED_APPS = [
    'app_1.apps.App1Config',
    'rest_framework'
]

# 语言和时区
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

# 日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/background.log"),
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'ERROR',
        },
    }
}
```
如何配置多个level的hander？

# 模型
```python
from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=11)

    def __str__(self):
        return self.name
    class meta(self):
        
```

# 视图
```python
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class Person(APIView):

    def get(self, request):
        name = request.query_params.get("name")
        # 查询
        ret = Person.objects.filter(name=user).values()
        # 更新
        # Person.objects.filter(name=user).update(permission=False)
        return Response({'msg': 'OK'}, status=status.HTTP_200_OK)
        # list(queryset)转为list
```

- 分页
  虽然django有自己的分页，但是我用的比较多的还是每次重复查询，改变offset的方式；
  优化思路：假如每次页面显示10页，即用户可以选择序号为1-10页中间的任意一页，那么一次请求十页的内容，将目标页数的数据返回给前端，等下次选择11-20页的时候再发送下一次请求

- 序列化：将query_set转为目标格式，例如json
- 图片数据：```myFile = request.FILES.get("filename", None)```

# 权限管理
django的权限系统
参考：[Django权限详解](https://pythondjango.cn/django/advanced/8-permissions/)

rest_framework中的权限类
这里控制的是用户访问接口的权限

```python
# 创建一个permission.py文件
from rest_framework.permissions import BasePermission
class SuperAdminPermission(BasePermission):
    """超级管理员权限"""

    # 无权限的显示信息
    message = "You don't have permission! 您没有权限查看！"

    def has_permission(self, request, view):
        # 获取权限
        permission = request.redis_cache["permission"]
        if permission == "admin":
            return True
        else:
            return False
# 在视图中
class API(APIView):
    permission_classes = [SuperAdminPermission]
    
    def get(self, request):
        pass
```
# 中间件
> 注意django3跟之前的版本实现方式不一样
```python
# 新建一个middleware.py

# django1和2版本
from django.utils.deprecation import MiddlewareMixin

class NewMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'ok':
            pass
        else:
            return 'Response'
    def process_response(self, request, response):
        return response

# django3
class TestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 进入视图前添处理
        response = self.get_response(request)
        # 视图处理完后添加处理
        # 如果对response有修改需要添加下面的代码使其生效
        response._is_rendered = False
        response.render()
        return response
      
# 需要在setting文件中添加
MIDDLEWARE = [
    "NewMiddleware",
]
```
中间件的执行顺序是按照setting中的MIDDLEWARE列表中从上到下的顺序，先执行每个中间件类的process_request的方法，然后进入视图后得到response，再按照从下到上的顺序执行每个方法的process_response，但是假如process_request有返回结果，就不会执行后续的process_request，也不会进入视图，而是执行当前类的process_response，然后返回结果。

[讨论为什么需要render](https://stackoverflow.com/questions/44112528/editing-response-content-in-django-middleware)
jsonrender看起来是个很不错的点子

# 缓存
[Redis和Memcache的区别总结-京东阿里面试](https://www.cnblogs.com/aspirant/p/8883871.html)
redis
```
# redis相关操作
# mac下启动
brew services start redis
# 停止redis服务
redis-cli SHUTDOWN
# 启动客户端
redis-cli
```
```python
在配置文件setting.py中添加
REDIS_HOST = "{ip}"
REDIS_PORT = "{port}"
REDIS_DATABASE = "0"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://" + REDIS_HOST + ":" + REDIS_PORT + "/" + REDIS_DATABASE,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS":
                {"max_connections": 20,  # Redis连接池的最大连接数量：20
                 "decode_responses": True}  # 把Redis读取出来的bytes类型转换成string类型
        }
    },
}

# 使用redis
from django_redis import get_redis_connection
conn = get_redis_connection("default")
# 查询
conn.hget(key, filed)
# 添加
pl = conn.pipeline()
pl.hset(key, filed, value)
pl.execute
```
memcache

# 会话与cookies
> 基本上会话和cookies也是属于缓存的一种的机制，我的经验中基本就是用redis缓存实现会话，但是不同的框架一定有更加成熟的会话管理机制

[简单理解cookie/session机制](http://www.woshipm.com/pd/864133.html)
[Django学习笔记（5）——cookie和session](https://www.cnblogs.com/wj-1314/p/10496253.html)

```python
# 设置cookies
rep.set_cookie(key,value) 
# 设置加密cookies
rep.set_signed_cookie(key,value,salt='加密盐')
# 读取cookies
cookies = request.COOKIES.get('k')
# 读取加密cookies
cookies = request.get_signed_cookie('k' , salt = 'name')
```
初次使用的时候会发现生成的cookies是明文的，类似于
```
log_in=True:1lmp6y:0Zn3y96plyT2j8vm8p6vpXlrROftJEQOKZMPvBOlAFM; Path=/;
```
理论上存储在cookies都是非绝对重要的信息，例如密码这种的，本身就是从用户方发给我们的，我们只是不希望cookies中的数据不管被出于什么目的人为修改，，所以后面的加密的字符串可以作为是否修改的唯一id，假使返回的cookies中的信息发生了修改，就可以通过后面的id辨别出来

cookies常见应用场景：
- 登录状态凭证（未登录的话，需要重定向到登录页面）

其他：
cookies有效时间


# 消息队列/异步任务
[celery redis rabbitMQ各是什么及之间的区别？](https://blog.csdn.net/qq_17513503/article/details/88389766)
[保姆级别的RabbitMQ教程！一看就懂！](https://www.cnblogs.com/ZhuChangwu/p/14093107.html)
[celery配置参考](https://www.pythonf.cn/read/129031)
[django开发傻瓜教程-3-celery异步处理](https://www.cnblogs.com/pxy7896/p/9930377.html)

- 使用场景
当请求的任务不需要立刻返回结果，或者任务可能中断，需要不断重复，而这个过程不需要客户端等待时，可以作为异步任务处理
- 问题
消息队列如何去调用执行其他步骤的？
- 猜想
不断监听，有些人说这是 生产者-消费者 模型，我的问题是那么每个消费者难道都要不间歇接听消费者，这样客观占据进程难道不是性能的浪费吗？

celery + rabbitmq + django

```shell
# 安装rabbitmq
brew install rabbitmq
# 启动，访问地址http://127.0.0.1:15672/， 默认账号guest，密码guest
brew services start rabbitmq 
# 开机自启动
chkconfig rabbitmq-server on
# 停止
brew services stop rabbitmq 

# 安装celery
pip3 install celery
# 启动celery
celery worker -A {porjcet} -l debug
# 关闭celery
ps auxww|grep "celery worker"|grep -v grep|awk '{print $2}'|xargs kill -9

# celery 版本5之后
# 启动
celery -A mysite worker --loglevel=INFO
# 关闭
```

```python
# 在项目setting同级目录下创建celery.py，主要是用来生成celery的实例app，注意根据sys_path中项目路径的不同，可能会导致重名
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project}.settings')

# 使用rabbitmq
# celery：version 4
# app = Celery('{project}', backend='amqp', broker='amqp://guest:guest@127.0.0.1:5672')
# celery：version 5
app = Celery('{project}', broker='amqp://guest:guest@127.0.0.1:5672')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```
指定broker的参数也可以写在配置文件中，便于动态修改
```
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_SERIALIZER = 'json'
# CELERY_BROKER_BACKEND = 'amqp'
CELERY_BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672'
CELERYD_MAX_TASKS_PER_CHILD = '1'
```
但是命名为celery.py会有导入问题，难道其他人没有遇见吗？有

```python
# 在项目初始化文件中添加
from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ['celery_app']

# 在应用下新建task.py文件，文件名不可修改
from __future__ import absolute_import, unicode_literals
from celery import shared_task

@shared_task
def func():
    return True
```

celery是独立进程，如果对task有修改，需要重启;
版本5的使用还需要多加了解

## 报错
1、提示```No module named celery.backends.amqp```

解决方法：重新安装```pip install celery==4.4.1```，也有人用```pip install celery==4.4.6```

我看了一下导致这个错误的原因是```CELERY_BROKER_BACKEND = 'amqp'```，而我看一些人说这个已经弃用了，所以说要么保持这种写法，使用版本4的celery，或者使用版本5点celey，修改写法

# 接口文档自动生成
- [Django自动生成Swagger接口文档](https://www.jianshu.com/p/5eac22bd018f)
- [生成 Swagger 文檔上](https://zoejoyuliao.medium.com/%E7%94%A8-django-rest-framework-%E6%92%B0%E5%AF%AB-restful-api-%E4%B8%A6%E7%94%9F%E6%88%90-swagger-%E6%96%87%E6%AA%94-%E4%B8%8B-%E7%94%9F%E6%88%90-swagger-%E6%96%87%E6%AA%94-60c45e04afa8)
- [生成 Swagger 文檔下](https://zoejoyuliao.medium.com/%E7%94%A8-django-rest-framework-%E6%92%B0%E5%AF%AB-restful-api-%E4%B8%A6%E7%94%9F%E6%88%90-swagger-%E6%96%87%E6%AA%94-%E4%B8%8B-%E7%94%9F%E6%88%90-swagger-%E6%96%87%E6%AA%94-60c45e04afa8)
```
# 安装
pip install -U drf-yasg
# 在setting中添加
INSTALLED_APPS = [
   'drf_yasg',
   'api'
]

# get
@swagger_auto_schema(
    operation_summary='我是 GET 的摘要',
    manual_parameters=[
        openapi.Parameter(
            name='email',
            in_=openapi.IN_QUERY,
            description='Email',
            type=openapi.TYPE_STRING
        )
    ]
)
# post
@swagger_auto_schema(
    operation_summary='我是 POST 的摘要',       
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(
                 type=openapi.TYPE_STRING,
                 description='User Name'
            )
        }
    )
)
# 弃用api
@swagger_auto_schema(
    operation_summary='我是 POST 的摘要',
    operation_description='我是 POST 的說明',
    depracated=True        
)
```
参数
```
openapi.IN_BODY，參數在 request 的 body，例如 POST 請求。
openapi.IN_QUERY，參數在 request 的 quey，例如 user/?name=123。
openapi.IN_FORM，參數在 request 的 form 表單，例如檔案上傳。
openapi.IN_PATH，參數在 request 的 path，比方說 /user/<id>/
type：參數的型別，如：openapi.TYPE_STRING、openapi.TYPE_NUMBER、openapi.TYPE_INTEGER、openapi.TYPE_BOOLEAN、openapi.TYPE_ARRAY、openapi.TYPE_FILE等，更多資訊可參考官方文檔。
```

查看效果http://127.0.0.1:8000/redoc/或者http://127.0.0.1:8000/swagger/

问题：
如何导出为文件？

# nginx + uwsgi + supervisor
[为什么 Django 需要uWSGI和nginx](https://blog.just666.com/2020/06/30/why-django-need-uwsgi/)

## 1、uwsgi
[Linux下uwsgi+nginx部署Django2.2.x](https://blog.csdn.net/qq28129019/article/details/107161104)

```
# 安装uwsgi
pip3 install uwsgi
# 测试，新建一个test文件
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return "Hello World".encode('utf-8')
# 启动
uwsgi --http :8001 --wsgi-file test_wsgi.py

# 启动uWSGI服务器
uwsgi --ini uwsgi.ini
# 重启uWSGI服务器
service uwsgi restart
# 查看所有uWSGI进程
ps aux | grep uwsgi
ps -ef | grep uwsgi
# 停止所有uWSGI进程

```
本质上是使用uwsgi启动Django服务，替代之前的manage runserver，

1、打开http://127.0.0.1:8001,查看是否有输出
2、 修改配置setting文件
```
DEBUG = False
ALLOWED_HOSTS = ["*"]
```
3、uwsgi配置文件
```
[uwsgi]
#如果单独使用uwsgi来部署Django项目时，就用这一行。
http=0.0.0.0:8000
#如果使用nginx+uwsgi来部署Django项目时，就用这行。其中，8001端口用来跟nginx通信。也要在阿里云防火墙中添加8001端口。
# socket=0.0.0.0:8001
#你项目的完整路径。
chdir=/Users/jichengjian/编程开发/兴趣项目/test_django/mysite
# 设置虚拟环境的路径
home=mysite/test_wsgi_env
#给socket文件赋权限，这里不用管。
# chmod-socket=664
#启用主线程。
master=true
processes=4
threads=2
#指定日志文件(会自动创建)。这个很重要，如果uwsgi出现错误，可以通过日志文件来查错。
logto=uwsgi.log
#指定进程号文件(会自动创建)。这个也很重要，如果要重启和关闭uwsgi，则需要这个文件，里面记录了进程号。
pidfile=uwsgi.pid
#指定wsgi文件。在与settings.py同级目录中会有一个wsgi.py文件。
module=mysite.wsgi:application
```

报错：
```
[uWSGI] getting INI configuration from uwsgi.ini
Abort trap: 6

*** Starting uWSGI 2.0.19.1 (64bit) on [Sun May 30 11:14:06 2021] ***
compiled with version: 4.2.1 Compatible Apple LLVM 11.0.3 (clang-1103.0.32.62) on 29 May 2021 23:45:50
os: Darwin-20.5.0 Darwin Kernel Version 20.5.0: Sat May  8 05:10:33 PDT 2021; root:xnu-7195.121.3~9/RELEASE_X86_64
nodename: V_JCJJI-MB1
machine: x86_64
clock source: unix
pcre jit disabled
detected number of CPU cores: 8
current working directory: /Users/jichengjian/编程开发/兴趣项目/test_django/mysite/mysite
writing pidfile to uwsgi.pid
detected binary path: /Users/jichengjian/编程开发/virtualenv/test_django/bin/uwsgi
chdir() to /Users/jichengjian/编程开发/兴趣项目/test_django/mysite
your processes number limit is 1392
your memory page size is 4096 bytes
detected max file descriptor number: 2560
lock engine: OSX spinlocks
thunder lock: disabled (you can enable it with --thunder-lock)
uWSGI http bound on 0.0.0.0:8000 fd 4
uwsgi socket 0 bound to TCP address 127.0.0.1:63391 (port auto-assigned) fd 3
Python version: 3.7.3 (v3.7.3:ef4ec6ed12, Mar 25 2019, 16:52:21)  [Clang 6.0 (clang-600.0.57)]
Set PythonHome to /Users/jichengjian/编程开发/virtualenv/test_django_wsgi
Fatal Python error: initfsencoding: unable to load the file system codec
ModuleNotFoundError: No module named 'encodings'
```
似乎答案：https://github.com/unbit/uwsgi/issues/1688
**终于发现问题了，不能使用virtualenvawrapper生成的虚拟环境，只能使用virtualenv生成的虚拟环境**

## 2、supervisor + uwsgi + django
[使用uwsgi和supervisor部署Django程序](https://blog.just666.com/2017/12/23/django-uwsgi-supervisor/)
[supervisor参数详解](https://agvszwk.github.io/2019/06/23/supervisor%E7%9A%84%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86/)
我们希望用supervisor来管理uwsgi的进程，避免服务中断，所以supervisor应该有以下的作用
- 监控uwsgi的运行情况（如果可以的话，监控是否存在进程堵塞的情况）
- 假如uwsgi服务崩溃，记录日志，能够重启服务

1、安装supervisor
```
pip3 install supervisor
```
2、新建supervisor的配置文件
```
[supervisord]
nodaemon=True  # 值为false时supervisor在后台运行
logfile=supervisord.log   # supervisor　的日志
pidfile=supervisord.pid       # supervisor　的日志

[program:django_test]
command=uwsgi --ini uwsgi.ini
stopsignal=HUP
stopasgroup=true
killasgroup=true
autostart = true
autorestart = true
startretries = 3
stdout_logfile=uwsgi.log  # uwsgi　的日志
stderr_logfile=uwsgi.log  # uwsgi　的日志

[group:django_test]
programs=django_test
```
3、启动
```
supervisord -c supervisord.conf
```

## 3、nginx + uwsgi + django
[nginx 之 proxy_pass详解](https://www.jianshu.com/p/b010c9302cd0)
[Nginx 配置常用参数，看这一篇就够了](https://learnku.com/articles/36768)
```
# mac 启动nginx，有问题
nginx -c nginx.conf
# 停止
nginx -s stop
```
### 3.1 nginx 配置
首先可以通过```nginx -h```命令查看默认的nginx配置文件，例如在mac上
```
nginx version: nginx/1.21.0
Usage: nginx [-?hvVtTq] [-s signal] [-p prefix]
             [-e filename] [-c filename] [-g directives]

Options:
  -?,-h         : this help
  -v            : show version and exit
  -V            : show version and configure options then exit
  -t            : test configuration and exit
  -T            : test configuration, dump it and exit
  -q            : suppress non-error messages during configuration testing
  -s signal     : send signal to a master process: stop, quit, reopen, reload
  -p prefix     : set prefix path (default: /usr/local/Cellar/nginx/1.21.0/)
  -e filename   : set error log file (default: /usr/local/var/log/nginx/error.log)
  -c filename   : set configuration file (default: /usr/local/etc/nginx/nginx.conf)
  -g directives : set global directives out of configuration file
```
第一、我发现如果想要指定配置文件的时候，都会jia shang会加上prefix参数中的路径，所以指定配置文件的同时必须指定路径前缀
```
nginx -p ./ -c nginx.conf
```
第二、一些常用的配置项会用的到文件也放在默认目录下（mac：/usr/local/etc/nginx/），也就是说如果想要指定自己的配置文件的时候，要么将文件路径修改为默认目录，要么将文件复制一份到新路径下，我觉得第二种比较好，因为这些文件基本也是配置项，可能会根据不同情况修改，所以最好放在项目下

```
# 我的nginx配置(测试使用)
worker_processes  1;

error_log  {自定义nginx_error_file};
error_log  {自定义nginx_error_file} notice;
error_log  {自定义nginx_error_file}  info;
pid        logs/nginx.pid;

events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;
    upstream django {
        # 注意这里的server要和uwsgi.ini配置文件中的socket保持一致
        server 127.0.0.1:8000;
    }
    server {
        listen       8080;
        server_name  localhost;
        charset utf-8;

        #access_log  logs/host.access.log  main;

        location / {
            # proxy_pass http://127.0.0.1:8080;
            uwsgi_pass django;
            include uwsgi_params;
        }
    include servers/*;
}

```

配置中的include参数调用的就是上面第二点提到的，例如uwsgi_params
### 3.2、报错
```
2021/05/30 18:42:00 [error] 17826#0: *140 upstream prematurely closed connection while reading response header from upstream, client: 127.0.0.1, server: localhost, request: "GET /app_1/person/50x.html HTTP/1.1", upstream: "uwsgi://127.0.0.1:8000", host: "127.0.0.1:8080"

Traceback (most recent call last):
  File "/Users/jichengjian/编程开发/兴趣项目/test_django/mysite/mysite/test_wsgi_env/lib/python3.7/site-packages/django/core/handlers/wsgi.py", line 132, in __call__
    request = self.request_class(environ)
  File "/Users/jichengjian/编程开发/兴趣项目/test_django/mysite/mysite/test_wsgi_env/lib/python3.7/site-packages/django/core/handlers/wsgi.py", line 80, in __init__
    self.method = environ['REQUEST_METHOD'].upper()
KeyError: 'REQUEST_METHOD'
```
发现原来要在nginx.conf旁边新建一个uwsgi_params文件
```
uwsgi_param QUERY_STRING $query_string;
uwsgi_param REQUEST_METHOD $request_method;
uwsgi_param CONTENT_TYPE $content_type;
uwsgi_param CONTENT_LENGTH $content_length;
uwsgi_param REQUEST_URI $request_uri;
uwsgi_param PATH_INFO $document_uri;
uwsgi_param DOCUMENT_ROOT $document_root;
uwsgi_param SERVER_PROTOCOL $server_protocol;
uwsgi_param HTTPS $https if_not_empty;
uwsgi_param REMOTE_ADDR $remote_addr;
uwsgi_param REMOTE_PORT $remote_port;
uwsgi_param SERVER_PORT $server_port;
uwsgi_param SERVER_NAME $server_name;
```

ok，可以正常启动，启动前要单独启动uwsgi，并确保ip:post配置与nginx中的一致如果想动静态分离，需要设计url匹配规则；负载均衡的话需要修改```upstram```参数，添加均衡配置逻辑

# docker
[实战 Django](https://yeasy.gitbook.io/docker_practice/compose/django)
示例
```
FROM python:3.7.3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
```

# 性能测试
[压测工具如何选择? ab、locust、Jmeter、go压测工具【单台机器100w连接压测实战】](https://segmentfault.com/a/1190000020211494)

# 常用业务
ip禁止
访问频率限制

# 后台管理系统
``` python
# 创建超级管理员，输入用户名、邮箱和密码
python manage.py createsuperuser
# 在应用的apps.py中添加
class App2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_2'
    # 在后台管理系统中显示
    verbose_name = '图片服务'
```

```python
# 自定制admin类，修改应用的admin文件
class PersonAdmin(admin.ModelAdmin):
    # 不可以显示多对多的关联字段,注意这些都是元组，注意末尾的逗号
    list_display = ('name', 'phone')
    # 设置字段可垂直搜索
    # filter_horizontal = ('name', 'phone')
    #设置每页显示的条目
    list_per_page = 10
    #根据字段搜索,关联字段加__，三个字段中重复的部分都会被搜索到
    search_fields = ('name', 'phone')
    #根据字段过滤
    list_filter = ('name',)
    #根据字段排序，可以多个字段，依次排序，‘-id’表示降序排
    ordering = ('name',)
    #添加书籍时隐藏字段，列表里必须是元组
    fieldsets = [
        #默认显示name,fieldes是固定的，后面跟列表
        (None,{'fields':['name',]}),
        #将下列字段以折叠的方式显示
        ('other information',{'fields':['phone'],'classes':['phone',]}),
    ]


admin.site.register(Person, PersonAdmin)
```

# 疑问
1、将一些请求对应的信息封装在request中真的好吗？直觉上感觉怪怪的