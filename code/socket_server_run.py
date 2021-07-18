# coding='utf-8'

import time
import select
import uvloop
import asyncio
import functools
import multiprocessing
from queue import Queue
from tornado.ioloop import IOLoop
from socket_base import ServerSocketBase
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class ServerSocket(ServerSocketBase):
    @staticmethod
    def deal_msg(msg):
        """处理信息，生成返回结果"""
        for i in range(1, 4):
            asyncio.sleep(1)  # time.sleep(1)
            # 如果是其他耗时操作，也需要手动写call_soon吗？
            print(f'sleep: {i}, {msg}, {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        return bytes('[%s]收到 %s' % (time.ctime(), msg.decode('utf-8')), encoding='utf-8')

    @staticmethod
    async def async_sleep(num, print_str):
        time.sleep(num)
        print(print_str % num)

    async def async_deal_msg(self, msg):
        """处理信息，生成返回结果"""
        print_str = f'sleep: %d, {msg}, {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}'
        # for i in range(1, 4):
        await self.async_sleep(4, print_str)
        return bytes('[%s]收到 %s' % (time.ctime(), msg.decode('utf-8')), encoding='utf-8')

    def single_work(self, client_tcp_socket):
        """同步阻塞io：任务函数"""

        # 循坏接收发送的数据
        while True:
            data = client_tcp_socket.recv(self.buffer_size)

            # 连接中断
            if not data:
                print(f'client no data: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
                client_tcp_socket.close()
                self.conn -= 1
                print(f'连接减一，当前连接数{self.conn}')
                break

            # 关闭客户端连接
            if data == b'client close':
                client_tcp_socket.close()
                self.conn -= 1
                print(f'连接减一，当前连接数{self.conn}')
                break

            res_msg = self.deal_msg(data)
            client_tcp_socket.send(res_msg)

    def single_work_2(self, client_tcp_socket):
        """同步阻塞io：任务函数"""

        # 循坏接收发送的数据
        try:
            # 非阻塞情况，此处一直运行，且在没有获取到数据的时候会报错："Resource temporarily unavailable"
            data = client_tcp_socket.recv(self.buffer_size)
        except Exception as e:
            # print('recv: ', e)
            return

        # 连接中断
        if not data:
            print(f'server no data: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
            # 客户端未接收到返回结果前中断，导致报错
            client_tcp_socket.close()
            self.conn -= 1
            print(f'连接减一，当前连接数{self.conn}')
            return

        # 关闭客户端连接
        if data == b'client close':
            client_tcp_socket.close()
            self.conn -= 1
            print(f'连接减一，当前连接数{self.conn}')
            return

        res_msg = self.deal_msg(data)
        client_tcp_socket.send(res_msg)

    def close_socket_with_lock(self, socket_cls, lock):
        socket_cls.close()
        with lock:
            self.conn -= 1
        print(f'连接减一，当前连接数{self.conn}')

    def multi_work(self, client_tcp_socket, lock):
        with lock:
            self.conn += 1
            print(f"有客户端连接: {self.conn}")
        # 接收发送的数据
        while True:
            data = client_tcp_socket.recv(self.buffer_size)

            # 连接在处理前中断
            if not data:
                print(f'server no data: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
                # 客户端未接收到返回结果前中断，导致报错
                self.close_socket_with_lock(client_tcp_socket, lock)
                break

            # 关闭客户端连接
            if data == b'client close':
                self.close_socket_with_lock(client_tcp_socket, lock)
                break

            res_msg = self.deal_msg(data)
            client_tcp_socket.send(res_msg)

    async def async_select_epoll_work(self, timeout):
        tcp_server_socket = self.create_server_socket()

        message_queues = {}
        epoll = select.epoll()
        epoll.register(tcp_server_socket.fileno(), select.EPOLLIN)
        fd_to_socket = {tcp_server_socket.fileno(): tcp_server_socket}

        print("等待客户端的链接")
        while True:
            # 轮询注册的事件集合，返回值为[(文件句柄，对应的事件)，(...),....]
            try:
                # 这里对于并发难道不是限制吗？
                events = epoll.poll(timeout)
            except Exception as e:
                print(e)
                continue
            print('events: ', events)
            if not events:
                print("epoll超时无活动连接，重新轮询......")
                continue
            print(f"有{len(events)}个新事件，开始处理......")

            for fd, event in events:
                socket = fd_to_socket[fd]
                # 如果活动socket为当前服务器socket，表示有新连接
                if socket == tcp_server_socket:
                    connection, address = tcp_server_socket.accept()
                    print("新连接：", address)
                    # 新连接socket设置为非阻塞
                    connection.setblocking(False)
                    # 注册新连接fd到待读事件集合
                    epoll.register(connection.fileno(), select.EPOLLIN)
                    # 把新连接的文件句柄以及对象保存到字典
                    fd_to_socket[connection.fileno()] = connection
                    # 以新连接的对象为键值，值存储在队列中，保存每个连接的信息
                    message_queues[connection] = Queue()
                    print('step 1 finished: ', epoll.closed)
                # 关闭事件
                elif event & (select.EPOLLHUP | select.EPOLLERR):
                    print('client close')
                    # 在epoll中注销客户端的文件句柄
                    epoll.unregister(fd)
                    # 关闭客户端的文件句柄
                    fd_to_socket[fd].close()
                    # 在字典中删除与已关闭客户端相关的信息
                    del fd_to_socket[fd]
                # 可读事件
                elif event & select.EPOLLIN:
                    # 接收数据
                    data = socket.recv(1024)
                    if data and data != b'client close':
                        print(f"收到数据：{data}客户端：", socket.getpeername())
                        # 将数据放入对应客户端的字典
                        message_queues[socket].put(data)
                        # 修改读取到消息的连接到等待写事件集合(即对应客户端收到消息后，再将其fd修改并加入写事件集合)
                        epoll.modify(fd, select.EPOLLOUT)
                    else:
                        # 备选连接在处理前中断
                        print(f'server no data: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
                        # 在epoll中注销客户端的文件句柄
                        epoll.unregister(fd)
                        # 关闭客户端的文件句柄
                        fd_to_socket[fd].close()
                        # 在字典中删除与已关闭客户端相关的信息
                        del fd_to_socket[fd]
                # 可写事件
                elif event & select.EPOLLOUT:
                    try:
                        # 从字典中获取对应客户端的信息
                        msg = message_queues[socket].get_nowait()
                    except Exception:  # Queue.Empty
                        print(socket.getpeername(), " queue empty")
                        # 修改文件句柄为读事件
                        epoll.modify(fd, select.EPOLLIN)
                    else:
                        print(f"收到数据：{msg}客户端：", socket.getpeername())
                        # 发送数据
                        # res_msg = self.deal_msg(msg)
                        res_msg = await self.async_deal_msg(msg)
                        socket.send(res_msg)
                        # 将fd放到可读
                        epoll.modify(fd, select.EPOLLIN)
            # 在epoll中注销服务端文件句柄
        epoll.unregister(tcp_server_socket.fileno())
        # 关闭epoll
        epoll.close()
        # 关闭服务器socket
        tcp_server_socket.close()

    def single_run(self):
        """ 同步阻塞io：运行"""

        tcp_server_socket = self.create_server_socket()
        print("等待客户端的链接，结束连接使用：client close")
        client_tcp_socket_list = list()
        try:
            while True:
                client_tcp_socket, address = tcp_server_socket.accept()
                self.conn += 1
                print(f"连接加一，当前客户端连接数: {self.conn}")
                self.single_work(client_tcp_socket)
                client_tcp_socket_list.append(client_tcp_socket)
        except Exception as e:
            print(e)
            tcp_server_socket.shutdown(2)
            tcp_server_socket.close()

    def single_run_2(self):
        """ 同步非阻塞io：运行"""

        tcp_server_socket = self.create_server_socket()
        print("等待客户端的链接，结束连接使用：client close")
        client_tcp_socket_list = list()
        while True:
            try:
                client_tcp_socket, address = tcp_server_socket.accept()
                self.conn += 1
                print(f"连接加一，当前客户端连接数: {self.conn}")
                self.single_work_2(client_tcp_socket)
                client_tcp_socket_list.append(client_tcp_socket)
            except Exception as e:
                # 跳过等待连接或者等待数据的错误
                if 'Resource temporarily unavailable' in str(e):
                    pass
                else:
                    print(e)
                for client_tcp_socket in client_tcp_socket_list:
                    self.single_work_2(client_tcp_socket)

    def multi_run(self, threading_num):
        """ 多线程同步非阻塞io：运行"""

        tcp_server_socket = self.create_server_socket()
        print("等待客户端的链接")
        try:
            m = multiprocessing.Manager()
            lock = m.Lock()
            # ProcessPoolExecutor | ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=threading_num) as executor:
                while True:
                    tcp_client_socket, addr = tcp_server_socket.accept()
                    executor.submit(self.multi_work, tcp_client_socket, lock)
        except Exception as e:
            print(e)

    def select_select_run(self):
        pass

    def select_poll_run(self):
        pass

    def select_epoll_run(self, timeout=10):
        """epoll 异步"""

        tcp_server_socket = self.create_server_socket()

        message_queues = {}
        epoll = select.epoll()
        epoll.register(tcp_server_socket.fileno(), select.EPOLLIN)
        fd_to_socket = {tcp_server_socket.fileno(): tcp_server_socket}

        print("等待客户端的链接")
        while True:
            # 轮询注册的事件集合，返回值为[(文件句柄，对应的事件)，(...),....]
            try:
                # 这里对于并发难道不是限制吗？
                events = epoll.poll(timeout)
            except Exception as e:
                print(e)
                continue
            print('events: ', events)
            if not events:
                print("epoll超时无活动连接，重新轮询......")
                continue
            print(f"有{len(events)}个新事件，开始处理......")

            for fd, event in events:
                socket = fd_to_socket[fd]
                # 如果活动socket为当前服务器socket，表示有新连接
                if socket == tcp_server_socket:
                    connection, address = tcp_server_socket.accept()
                    print("新连接：", address)
                    # 新连接socket设置为非阻塞
                    connection.setblocking(False)
                    # 注册新连接fd到待读事件集合
                    epoll.register(connection.fileno(), select.EPOLLIN)
                    # 把新连接的文件句柄以及对象保存到字典
                    fd_to_socket[connection.fileno()] = connection
                    # 以新连接的对象为键值，值存储在队列中，保存每个连接的信息
                    message_queues[connection] = Queue()
                    print('step 1 finished: ', epoll.closed)
                # 关闭事件
                elif event & (select.EPOLLHUP | select.EPOLLERR):
                    print('client close')
                    # 在epoll中注销客户端的文件句柄
                    epoll.unregister(fd)
                    # 关闭客户端的文件句柄
                    fd_to_socket[fd].close()
                    # 在字典中删除与已关闭客户端相关的信息
                    del fd_to_socket[fd]
                # 可读事件
                elif event & select.EPOLLIN:
                    # 接收数据
                    data = socket.recv(1024)
                    if data and data != b'client close':
                        print(f"收到数据：{data}客户端：", socket.getpeername())
                        # 将数据放入对应客户端的字典
                        message_queues[socket].put(data)
                        # 修改读取到消息的连接到等待写事件集合(即对应客户端收到消息后，再将其fd修改并加入写事件集合)
                        epoll.modify(fd, select.EPOLLOUT)
                    else:
                        # 备选连接在处理前中断
                        print(f'server no data: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
                        # 在epoll中注销客户端的文件句柄
                        epoll.unregister(fd)
                        # 关闭客户端的文件句柄
                        fd_to_socket[fd].close()
                        # 在字典中删除与已关闭客户端相关的信息
                        del fd_to_socket[fd]
                # 可写事件
                elif event & select.EPOLLOUT:
                    try:
                        # 从字典中获取对应客户端的信息
                        msg = message_queues[socket].get_nowait()
                    except Exception:  # Queue.Empty
                        print(socket.getpeername(), " queue empty")
                        # 修改文件句柄为读事件
                        epoll.modify(fd, select.EPOLLIN)
                    else:
                        print(f"收到数据：{msg}客户端：", socket.getpeername())
                        # 发送数据
                        res_msg = self.deal_msg(msg)
                        socket.send(res_msg)
                        # 将fd放到可读
                        epoll.modify(fd, select.EPOLLIN)
        # 在epoll中注销服务端文件句柄
        epoll.unregister(tcp_server_socket.fileno())
        # 关闭epoll
        epoll.close()
        # 关闭服务器socket
        tcp_server_socket.close()

    def async_select_epoll_run(self, timeout=10):
        """epoll 异步"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        tasks = [self.async_select_epoll_work(timeout)]
        loop.run_until_complete(asyncio.gather(*tasks))

    def uvloop_select_epoll_run(self, timeout=10):
        """epoll 异步"""
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)

        tasks = [self.async_select_epoll_work(timeout)]
        loop.run_until_complete(asyncio.gather(*tasks))

    def handle_client(self, cli_addr, fd_map, ioloop, message_queue_map, fd, event):
        s = fd_map[fd]
        if event & IOLoop.READ:  # receive the data
            data = s.recv(1024)
            if data and data != b'client close':
                print("receive %s from %s" % (data, cli_addr))
                ioloop.update_handler(fd, IOLoop.WRITE)
                message_queue_map[s].put(data)
            else:
                print("closing %s  " % cli_addr)
                ioloop.remove_handler(fd)
                s.close()
                del message_queue_map[s]
        if event & IOLoop.WRITE:
            try:
                next_msg = message_queue_map[s].get_nowait()
            except Exception:  # Queue.Empty
                print("%s Queue Empty" % cli_addr)
                ioloop.update_handler(fd, IOLoop.READ)   # CHANGE THE SITUATION
            else:
                print("sending %s to %s " % (next_msg, cli_addr))
                # res_msg = self.deal_msg(next_msg)
                res_msg = self.async_deal_msg(next_msg)
                s.send(res_msg)
                ioloop.update_handler(fd, IOLoop.READ)
        if event & IOLoop.ERROR:
            print("%s EXCEPTION ON" % cli_addr)
            ioloop.remove_handler(fd)
            s.close()
            del message_queue_map[s]

    def handle_server(self, fd_map, message_queue_map, fd, event):
        s = fd_map[fd]
        if event & IOLoop.READ:
            get_connection, cli_addr = s.accept()
            print("connection %s " % cli_addr[0])
            get_connection.setblocking(0)
            get_connection_fd = get_connection.fileno()
            fd_map[get_connection_fd] = get_connection

            io_loop = IOLoop.current()
            handle = functools.partial(self.handle_client, cli_addr[0], fd_map, io_loop, message_queue_map)
            io_loop.add_handler(get_connection_fd, handle, IOLoop.READ)
            # io_loop.spawn_callback(handle, get_connection_fd, IOLoop.READ)
            message_queue_map[get_connection] = Queue()

    def tornado_ioloop_run(self):
        tcp_server_socket = self.create_server_socket()
        print("等待客户端的链接")

        fd_map = {}
        fd = tcp_server_socket.fileno()
        fd_map[fd] = tcp_server_socket
        message_queue_map = {}

        io_loop = IOLoop.instance()
        handle_server_partial = functools.partial(self.handle_server, fd_map, message_queue_map)
        io_loop.add_handler(fd, handle_server_partial, io_loop.READ)
        try:
            io_loop.start()
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            print("exit")
        finally:
            io_loop.stop()


def main():
    # 服务端：同步阻塞io
    # socket_server = ServerSocket()
    # socket_server.single_run()

    # 服务端：同步单线程非阻塞io：处理多连接（可以同时启动多个client进行测试）
    # socket_server = ServerSocket(block_stats=False)
    # socket_server.single_run_2()

    # 服务端：多线程阻塞io：处理多连接(与上面不同的是，可以看到服务端并发处理两个请求，打印的内容可以交叉)
    # 将ProcessPoolExecutor替换为ProcessPoolExecutor，可以使用多进程，此时服务端没有问题，但关闭连接时客户端并未断开，会卡在recv, 原因未知
    # socket_server = ServerSocket()
    # socket_server.multi_run(2)

    # io多路复用

    # 服务端：select.select，单进程处理多连接，此时进程堵塞在调用select时

    # 服务端：select.poll，单进程处理多连接

    # 服务端：select.epoll，单进程处理多连接
    # linux下才能调用select.epoll，使用云服务器测试
    # socket_server = ServerSocket(block_stats=False, max_conn=100)
    # socket_server.select_epoll_run(timeout=50)

    # 服务端: select.epoll + 协程asyncio 处理多连接
    socket_server = ServerSocket(block_stats=False, max_conn=100)
    socket_server.async_select_epoll_run(timeout=50)
    # socket_server.uvloop_select_epoll_run(timeout=50)

    # 服务端：tornado ioloop
    # 可以看到跟上面的select.epoll的逻辑基本是一样的，同时IOLoop是基于asyncio
    # socket_server = ServerSocket(block_stats=False, max_conn=100)
    # socket_server.tornado_ioloop_run()


if __name__ == '__main__':
    main()
