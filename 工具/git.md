**前言**
一直以来使用git都没什么总结，几个常用的命令虽然知道，但未曾深入了解，有时忘记了也要从新去找，这次开始好好整理一下

目前还比较乱，后面慢慢整理

参考：
[最好用的git学习工具](https://learngitbranching.js.org/?locale=zh_CN)

# 一、git初始化和配置

*略过安装*

## 1、初始配置：
- 生成密钥
ssh-keygen -t rsa -C "email@example.com"
ssh-add id_rsa

- 配置用户
git config --global user.name "John Doe"
git config --global user.email johndoe@example.com

### 在mac上使用多个git账号
参考
- [Mac 上配置多个git账号](https://www.jianshu.com/p/698f82e72415)
- [git config的全局和本地配置](https://www.jianshu.com/p/fa1c798a81e9)
当有多个账号的时候每个项目可能需要配置对应的账号
```
git config --local user.name "name"
git config --local user.email "email"
```
思考如何直接省略这一步

## 2.0 删除分支
git checkout branch_name 切换分支
git branch -d branch_name 删除分支

## 2.1 修改分支名称
git checkout old_name
git pull
git branch -m old_name new_name
git push origin :old_name
git push origin new_name
git branch --set-upstream-to=origin/new_name new_name

## 2.2 新增分支
git branch -b branch_name 以当前分支为准创建并切换分支 
git push origin new_name: new_name
git push --set-upstream origin rebase

## 2.3 拉取新的分支
git fetch origin dev（dev为远程仓库的分支名）
git checkout -b dev(本地分支名称) origin/dev(远程分支名称)

## 2.4 rebase合并分支

在当前分支
1. git rebase main 如果冲突，修改冲突位置
1.1 git rebase -i main 这里可以把分支上的commit合并为一个后再rebase
1.2 输入后进入交互界面，将想要舍弃的commit id前面的"pick"改为"s"，保存后继续修改合并后的commit的名称，再保存之后就可以了
2. git add .
3. git rebase --continue

4.1 方式一
git push -f origin branch_name 直接覆盖远程分支
4.2 方式二
git pull 修改冲突
git add .
git commit
git push 
或者在本地修改冲突后更新到远程分支

5. git checkout main 回到主分支
6.1 方式一
从本地更新远程主分支
git rebase branch_name
git push
6.2 方式二
在网页上提merge request，然后merge
git pull 将本地main前进到最新位置

7、中途放弃rebase
git rebase --abort 

问题：
main分支
A分支
B分支
如果A分支先rebase并且提了merge request，然后B分支rebase也提了merge request，A分支发现有问题然后重新修改，那么此时B分支会怎么样？
我的理解是，假设A分支回滚到rebase之前，那么B分支应该不受影响，但是加入A分支并没有回滚，而是继续修改和提交commit，那么实际上就从当前点又切分出一个commit，如果再次合并，那么就会合到B分支之后，需要测试一下

## 2.5 版本回滚（可以用来撤销rebase）
删除回滚位置之后的修改：git reset --hard 版本号
https://blog.csdn.net/allanGold/article/details/111372750
保留回滚位置之后的修改：git revert commit commit_id

## 2.6 日志
查看提交树: git log --pretty=format:"%h %s" –-graph 
查看提交记录：git log --file_name

## 2.7 tag
列出tag：git tag 
过滤：git tag  -l "v3.3*"
创建tag：git tag v1.1
推送到远程：git push origin v1.1
在tag的基础上切出分支：git checkout -b newbranch tag1.1

## 2.8 add后删除
git rm --cached file_name