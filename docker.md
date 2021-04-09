# DOCKER
## 一、安装
### 1、mac
```
brew cask install docker
```
### 2、ubuntu
```
# 卸载旧版本
sudo apt-get remove docker docker-engine docker.io
# 添加使用 HTTPS 传输的软件包以及 CA 证书
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
# 添加软件源的 GPG 密钥
$ curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add 
# 官方源
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# 向 sources.list 中添加 Docker 软件源
sudo add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
# 官方源
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
# 安装 Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
到最后一步的时候卡住了，提示
```
E: Package 'docker-ce' has no installation candidate
E: Unable to locate package docker-ce-cli
```
我以为跟前面一步添加GPG密钥时弹出的警告apt-key被弃用有关，但是也无法验证，最后发现是版本问题
> Docker has not released the repository for focal fossa (20.04) yet. As @Wared said, running.will get docker from ubuntu repository.

```
# ubuntu 20.04
sudo apt install -y docker.io
```
## 二、入门概念

参考资料：
https://yeasy.gitbook.io/docker_practice/

### 1、Docker架构
docker 使用客户端-服务器（C/S）架构模式，通过远程api来管理和创建docker容器；docker容器通过docker镜像来创建，两者类似与类和对象的关系。

- images: docker镜像，用于创建docker容器的模板，相当于文件系统

- container: 容器是独立运行一个或一组应用
> 按照 Docker 最佳实践的要求，容器不应该向其存储层内写入任何数据，容器存储层要保持无状态化。所有的文件写入操作，都应该使用 数据卷（Volume）、或者 绑定宿主目录，在这些位置的读写会跳过容器存储层，直接对宿主（或网络存储）发生读写，其性能和稳定性更高。
数据卷的生存周期独立于容器，容器消亡，数据卷不会消亡。因此，使用数据卷后，容器删除或者重新运行之后，数据却不会丢失。

- client: docker客户端， 通过命令行或其他工具使用docker API与docker守护进程通信
- host: docker主机， 一个物理或虚拟的用于执行docker守护进程和容器的机器
- registry: docker仓库，用来保存镜像，如同代码仓库
- docker machine: 简化docker安装的命令行工具


## 三、使用操作
### 1、准备
```
# 启动docker
sudo systemctl enable docker
sudo systemctl start docker
# 创建docker组（我创建的时候提示组已经存在）
sudo groupadd docker
# 将当前用户加入 docker 组：
$ sudo usermod -aG docker $USER
```

### 2、镜像
> 镜像的唯一标识是其 ID 和摘要，ls展示的是一部分id

#### 2.1 拉取镜像
```
# 将仓库名称和标签改成个人账号的仓库和标签，应该也可以？待测试
docker pull [选项] [Docker Registry 地址[:端口号]/]仓库名[:标签]
```
示例：
```
docker pull ubuntu:18.04
```
#### 2.2 列出镜像
```
docker image ls
# 仓库名
docker image ls ubuntu
# 仓库名和标签
docker image ls ubuntu:18.04
# 只展示id
docker image ls -q
# 自定义输出格式
docker image ls --format "{{.ID}}: {{.Repository}}"
```
使用filter过滤器
```
# since，before自某个镜像之后/之前的镜像
docker image ls -f since=ubuntu:18.04
docker image ls -f before=ubuntu:18.04
# 如果镜像构建时，定义了 LABEL，还可以通过 LABEL 来过滤。
docker image ls -f label=com.example.version=0.1
```
镜像体积与dockerhub的不太一样是因为压缩，查看镜像、容器、数据卷占用的空间
```
root@vultr:~# docker system df
TYPE                TOTAL               ACTIVE              SIZE                RECLAIMABLE
Images              2                   1                   63.27MB             63.25MB (99%)
Containers          2                   0                   0B                  0B
Local Volumes       0                   0                   0B                  0B
Build Cache         0                   0                   0B                  0B
```
#### 2.3 删除镜像
```
docker image rm [选项] <镜像1> [<镜像2> ...]
# 镜像短ID，足够与其他镜像区分即可
docker image rm 501(id的前三位)
# 镜像名，<仓库名>:<标签>
docker image rm centos
# 镜像摘要
感觉用不到
```
组合使用ls和rm
```
docker image rm $(docker image ls -q redis)
docker image rm $(docker image ls -q -f before=mongo:3.2)
```

#### 2.4 镜像标签
每次对一个镜像做标记，类似保存了一份镜像
```
docker tag IMAGE[:TAG] [REGISTRY_HOST[:REGISTRY_PORT]/]REPOSITORY[:TAG]
```
示例查看私人仓库部分


### 3、容器
#### 1、启动容器
```
# 普通启动
docker run -it --rm ubuntu:18.04 bash
# 守护态启动
docker run -dit --rm ubuntu:18.04 bash
```
- -it：这是两个参数，一个是 -i：交互式操作，一个是 -t 终端。我们这里打算进入 bash 执行一些命令并查看返回结果，因此我们需要交互式终端
- --rm：这个参数是说容器退出后随之将其删除。默认情况下，为了排障需求，退出的容器并不会立即删除，除非手动 docker rm。我们这里只是随便执行个命令，看看结果，不需要排障和保留结果，因此使用 --rm 可以避免浪费空间。
- ubuntu:18.04：这是指用 ubuntu:18.04 镜像为基础来启动容器。
- bash：放在镜像名后的是 命令，这里我们希望有个交互式 Shell，因此用的是 bash
- -d：让 Docker 在后台运行而不是直接把执行命令的结果输出在当前宿主机下

守护态启动示例
```
# 普通启动，ctrl+c退出
docker run ubuntu:18.04 /bin/sh -c "while true; do echo hello world; sleep 1; done"
# 守护态启动，会返回一个唯一id
docker run -d ubuntu:18.04 /bin/sh -c "while true; do echo hello world; sleep 1; done"
```
#### 2、容器列出，启动和停止
```
# 列出容器，只能查看运行中的容器
docker ps
docker container ls
# 查看全部，-a
docker ps -a
docker container ls -a
# 查看容器输出，可以不加contrainer
docker container logs [id]
# 终止容器，可以不加contrainer
docker container stop [id]
# 重新启动，可以不加contrainer
docker container start [id]
```
#### 3、进入容器
```
docker exec -it [id] bash
```
#### 4、导入和导出
```
# 导出
docker export 7691a814370e > ubuntu.tar
# 导入tar
cat ubuntu.tar | docker import - test/ubuntu:v1.0
# 导入url
docker import http://example.com/exampleimage.tgz example/imagerepo
```
#### 5、删除容器
```
docker container rm trusting_newton
# 强制删除运行中的容器
docker container rm -f trusting_newton
# 清理掉所有处于终止状态的容器
docker container prune
```

## 四、仓库

### 1、dockerhub
```
# 搜索镜像
docker search [name]
# 推送镜像到自己的仓库
docker push [username]/ubuntu:18.04
```
自动构建，这个功能太强了，一定要试一下，之前大数点的应该也是这种部署方式
> 自动构建（Automated Builds）功能对于需要经常升级镜像内程序来说，十分方便。
有时候，用户构建了镜像，安装了某个软件，当软件发布新版本则需要手动更新镜像。
而自动构建允许用户通过 Docker Hub 指定跟踪一个目标网站（支持 GitHub 或 BitBucket）上的项目，一旦项目发生新的提交 （commit）或者创建了新的标签（tag），Docker Hub 会自动构建镜像并推送到 Docker Hub 中。
要配置自动构建，包括如下的步骤：
登录 Docker Hub；
在 Docker Hub 点击右上角头像，在账号设置（Account Settings）中关联（Linked Accounts）目标网站；
在 Docker Hub 中新建或选择已有的仓库，在 Builds 选项卡中选择 Configure Automated Builds；
选取一个目标网站中的项目（需要含 Dockerfile）和分支；
指定 Dockerfile 的位置，并保存。
之后，可以在 Docker Hub 的仓库页面的 Timeline 选项卡中查看每次构建的状态。

### 2、私有仓库
在一个私人服务器上搭建私有仓库，用于存储、拉取、上传镜像。
#### 2.1 运行私有仓库
```
# 这样存储目录会被创建在容器的/var/lib/registry目录下
docker run -d -p 5000:5000 --restart=always --name registry registry
# 存储到外部目录
docker run -d -p 5000:5000 -v /paisins/docker/registry:/var/lib/registry --name registry registry
```
- --restart=always：意外退出时自动重启
- --name：给容器命名
- -p：端口映射
- -v：目录映射，如果本地目录不存在，会自动创建

#### 2.2 尝试上传拉取镜像
```
# 先把别人镜像tag一下
docker tag ubuntu:latest 45.77.104.131:5000/ubuntu:18.04
# 上传
docker push 45.77.104.131:5000/ubuntu:18.04
```
这时报错
```
The push refers to repository [45.77.104.131:5000/ubuntu]
Get https://45.77.104.131:5000/v2/: http: server gave HTTP response to HTTPS client
```
解决方法如下，之后关闭所有容器，重启docker可以
```
# 在/etc/docker目录下创建daemon.json
{
   "insecure-registries" :["45.77.104.131:5000"]
}   
```
如果是在mac上，进入perference里面docker engine修改配置后重启即可
#### 2.3 查看镜像及版本
```
# 查看所有镜像
curl [ip]:[port]/v2/_catalog
# 查看镜像的版本
curl 45.77.104.131:5000/v2/ubuntu/tags/list
```
#### 2.4 权限认证
#### 2.5 使用Nexus3
> 感觉这两个部分暂时用不到，先不看了

## 五、数据管理

### 1、数据卷
> 数据卷是一个可供一个或多个容器使用的特殊目录，它绕过 UFS，可以提供很多有用的特性
数据卷 可以在容器之间共享和重用
对数据卷的修改会立马生效
对数据卷的更新，不会影响镜像
数据卷 默认会一直存在，即使容器被删除

数据卷的作用很像我在腾讯时使用的挂载盘，但是应该只是效果比较像，在多个服务器共享数据空间，修改立即生效，默认一直存在等方面；从这个角度来看docker的数据卷，就很好理解了
```
# 创建数据卷
docker volume create my-vol
# 查询所有数据卷
docker volume ls
# 查看数据卷信息详情
docker volume inspect my-vol
```

启动容器时，通过`--mount`挂载容器，可以挂载多个容器

```
docker run -d -P --name web --mount \
source=my-vol,target=/usr/share/nginx/html nginx:alpine
# 等价于
docker run -d -P --name web -v my-vol:/usr/share/nginx/html nginx:alpine

# 查看容器内的数据卷详情，数据卷在输出的mount下面
docker inspect web
# 删除数据卷，如果数据卷与未删除的容器绑定，则删除的时候会报错
docker volume rm my-vol
# 清理数据卷
docker volume prune
```

### 2、挂载主机目录
使用` --mount`标记可以指定挂载一个本地主机的目录到容器中去
```
docker run -d -P \
    --name web \
    # -v /src/webapp:/usr/share/nginx/html \
    --mount type=bind,source=/src/webapp,target=/usr/share/nginx/html \
    nginx:alpine
```
`注意本地路径需要是绝对路径，如果不存在则会报错`，可以设置权限为只读
```docker run -d -P \
    --name web \
    # -v /src/webapp:/usr/share/nginx/html:ro \
    --mount type=bind,source=/src/webapp,target=/usr/share/nginx/html,readonly \
    nginx:alpine
```

甚至可以挂载一个文件
```
docker run --rm -it \
   # -v $HOME/.bash_history:/root/.bash_history \
   --mount type=bind,source=$HOME/.bash_history,target=/root/.bash_history \
   ubuntu:18.04 bash
```
可以看出来`--mount`的功能比`-v`强大很多

3、tmpfs mount
我搜索的时候还发现了这种挂载方式，可以挂载到内存里，这是一种非持久化数据存储方式，当容器停止时，数据就会内存清除掉。

## 六、构建镜像
### 1、commit
通过一个webserver的例子理解commit和多层存储
```
# 运行nginx服务
docker run --name webserver -d -p 80:80 nginx
# 进入容器
docker exec -it webserver bash
# 在终端内，覆盖原来的index页面
echo '<h1>Hello, Docker!</h1>' > /usr/share/nginx/html/index.html
```
之后，会发现页面更新了
```
# 查看容器中的修改
docker diff webserver
# commit
docker commit --author "Paisins Ji" --message "修改了默认网页" webserver nginx:v2
# 查看镜像修改历史
docker history nginx:v2
```
> 当我们运行一个容器的时候（如果不使用卷的话），我们做的任何文件修改都会被记录于容器存储层里。而 Docker 提供了一个 docker commit 命令，可以将容器的存储层保存下来成为镜像。换句话说，就是在原有镜像的基础上，再叠加上容器的存储层，并构成新的镜像。以后我们运行这个新镜像的时候，就会拥有原有容器最后的文件变化。
> 
首先，如果仔细观察之前的 docker diff webserver 的结果，你会发现除了真正想要修改的 /usr/share/nginx/html/index.html 文件外，由于命令的执行，还有很多文件被改动或添加了。这还仅仅是最简单的操作，如果是安装软件包、编译构建，那会有大量的无关内容被添加进来，将会导致镜像极为臃肿。
> 
此外，使用 docker commit 意味着所有对镜像的操作都是黑箱操作，生成的镜像也被称为 黑箱镜像，换句话说，就是除了制作镜像的人知道执行过什么命令、怎么生成的镜像，别人根本无从得知。而且，即使是这个制作镜像的人，过一段时间后也无法记清具体的操作。这种黑箱镜像的维护工作是非常痛苦的。
>
而且，回顾之前提及的镜像所使用的分层存储的概念，除当前层外，之前的每一层都是不会发生改变的，换句话说，任何修改的结果仅仅是在当前层进行标记、添加、修改，而不会改动上一层。如果使用 docker commit 制作镜像，以及后期修改的话，每一次修改都会让镜像更加臃肿一次，所删除的上一层的东西并不会丢失，会一直如影随形的跟着这个镜像，即使根本无法访问到。这会让镜像更加臃肿。
所以不要用commit来定制镜像

### 2、dockerfile
> Dockerfile 是一个文本文件，其内包含了一条条的 指令(Instruction)，每一条指令构建一层，因此每一条指令的内容，就是描述该层应当如何构建。

还是以nginx服务为例
```
FROM nginx
RUN echo '<h1>Hello, Docker!</h1>' > /usr/share/nginx/html/index.html
```
#### 1、FROM
定制镜像是在已有镜像基础上进行修改，所以首先要有一个基础镜像，这就是第一行的作用。Docker hub本身有很多成熟镜像可以用，另外还有空白镜像
```
FROM scratch
```
> 直接 FROM scratch 会让镜像体积更加小巧。使用 Go 语言 开发的应用很多会使用这种方式来制作镜像，这也是为什么有人认为 Go 是特别适合容器微服务架构的语言的原因之一。

#### 2、RUN
用以执行shell命令，有两种格式
- shell格式：例如上面修改html的示例
- exec格式：```RUN wget -O redis.tar.gz "http://download.redis.io/releases/redis-5.0.3.tar.gz"```

每一次run都会构建一层，所以不要重复写run，而是尽量一行内完成
```
FROM debian:stretch

RUN set -x; buildDeps='gcc libc6-dev make wget' \
    && apt-get update \
    && apt-get install -y $buildDeps \
    && wget -O redis.tar.gz "http://download.redis.io/releases/redis-5.0.3.tar.gz" \
    && mkdir -p /usr/src/redis 
    ...
```
#### 3、用build构建
在Dockerfile所在的目录，执行以下命令
```
docker build -t nginx:v3 .
```

值得特别注意的是，最后的目录指定的不单单是Dockerfile的所在路径，更是指定了`上下文路径`，当我们需要在RUN中移动或复制文件时，一般使用相对路径，而相对的就是在build中输入的这个上下文路径，docker build的时候会把这个目录下的一切文件打包，所以build前应该将需要的文件移动到目录下，如果目录下有一些文件不希望打包，那可以通过.dockerignore文件来过滤掉

```
# 也可以通过url build
docker build -t hello-world https://github.com/docker-library/hello-world.git#master:amd64/hello-world

# ？？但是下载到哪里了呢？

# 下载解压，作为上下文路径
docker build http://server/context.tar.gz
# 从输入中构建，无法指定上下文路径
cat Dockerfile | docker build -
```
### 3、docker file 指令详解
#### 1、COPY
```
COPY package.json /usr/src/app/
```
> 还需要注意一点，使用 COPY 指令，源文件的各种元数据都会保留。比如读、写、执行权限、文件变更时间等
```
# --chown=<user>:<group>
COPY --chown=55:mygroup files* /mydir/
COPY --chown=bin files* /mydir/
```
> 如果源路径为文件夹，复制的时候不是直接复制该文件夹，而是将文件夹中的内容复制到目标路径。

#### 2、ADD
功能基本与COPY一致，在复制压缩文件到目标路径的时候，会自动解压缩，大部分情况下建议使用COPY

#### 3、CMD
与RUN相似，区别在于，CMD是默认命令，当容器启动时的默认命令类似于```/bin/bash```这种
```
exec 格式：CMD ["可执行文件", "参数1", "参数2"...]
CMD ["nginx", "-g", "daemon off;"]
```
另外值得注意的是，docker容器不是虚拟机，而是进程，所以所执行的命令都只能在前台，而不能放在后台
#### 4、ENTRYPOINT
```
<ENTRYPOINT> "<CMD>"
```
原文中提供的两个例子很好，简而言之，就是允许docker run的时候输入一些参数，这些参数会传到dockerfile中的entrypoint的地方处理，当然不只是在dockerfile写处理步骤，而是可以写一个单独的sh脚本，来根据参数决定后续操作
```
# 示例二
FROM alpine:3.4
...
RUN addgroup -S redis && adduser -S -G redis redis
...
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 6379
CMD [ "redis-server" ]
```
```
#!/bin/sh
...
# allow the container to be started with `--user`
if [ "$1" = 'redis-server' -a "$(id -u)" = '0' ]; then
    find . \! -user redis -exec chown redis '{}' +
    exec gosu redis "$0" "$@"
fi

exec "$@"
```
#### 5、ENV
设置环境变量
```
ENV VERSION=1.0 DEBUG=on \
    NAME="Happy Feet"
```
调用，跟shell一样
```
$NAME
```
#### 6、ARG
跟ENV很像，区别在于ARG在docker file定义之后，允许通过build命令指定参数修改对应的值
```
--build-arg <参数名>=<值>
```
另外ARG只在FROM之前生效，FROM之后的需要重新定义，所以多阶段构建的时候要注意
```
# 只在 FROM 中生效
ARG DOCKER_USERNAME=library
FROM ${DOCKER_USERNAME}/alpine
# 要想在 FROM 之后使用，必须再次指定
ARG DOCKER_USERNAME=library
RUN set -x ; echo ${DOCKER_USERNAME}
```
#### 7、VOLUME
等我看完数据卷再说

#### 8、EXPOSE
只是声明容器运行的时候端口的映射情况，并不会执行，类似一个说明
```
EXPOSE <端口1> [<端口2>...]
```
#### 9、WORKDIR
当作cd来用应该就行，再次需要说明的是docker file不是一个shell脚本，不会像shell那样连续的在相同的环境中执行一系列指令，我的理解中每一行每次执行一个docker 命令都是在做一次容器的修改，当这一行的修改结束之后，下一行的命令就是重启一个新的容器，环境是发生了变化的
#### 10、USER
```
USER <用户名>[:<用户组>]
```
> USER 指令和 WORKDIR 相似，都是改变环境状态并影响以后的层。WORKDIR 是改变工作目录，USER 则是改变之后层的执行 RUN, CMD 以及 ENTRYPOINT 这类命令的身份

```
# 建立 redis 用户，并使用 gosu 换另一个用户执行命令
RUN groupadd -r redis && useradd -r -g redis redis
# 下载 gosu
RUN wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/1.12/gosu-amd64" \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true
# 设置 CMD，并以另外的用户执行
CMD [ "exec", "gosu", "redis", "redis-server" ]
```
#### 11、HEALTHCHECK
健康检查，用来判断docker容器是否正常运行的命令，支持三个参数选项
```
--interval=<间隔>：两次健康检查的间隔，默认为 30 秒；
--timeout=<时长>：健康检查命令运行超时时间，如果超过这个时间，本次健康检查就被视为失败，默认 30 秒；
--retries=<次数>：当连续失败指定次数后，则将容器状态视为 unhealthy，默认 3 次。
```
示例
```
FROM nginx
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK --interval=5s --timeout=3s \
  CMD curl -fs http://localhost/ || exit 1
```
当一个容器启动之后，我们可以在查询容器信息的时候，在status列查看容器状态，而检查的输出可以通过```docker inspect```命令查看
#### 12、ONBUILD
当下一级镜像以当前镜像为基础镜像构建时，才会调用的命令，感觉暂时不会用到吧？

## TODO 待做实验
### 1、构建docker file，在新的环境快速部署服务
### 2、使用自动构建功能，尝试自动构建




