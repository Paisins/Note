import time
from socket_base import ServerSocketBase
from concurrent.futures import ThreadPoolExecutor


class ClientSocket(ServerSocketBase):
    def single_work(self, tcp_client_socket):
        """单个连接单个请求的请求函数"""

        while True:
            data = input(">:")
            if not data:
                continue
            data = bytes(data, encoding="utf-8")
            try:
                tcp_client_socket.send(data)
                print(f'客户端发送：{data}')
                try:
                    response = tcp_client_socket.recv(self.buffer_size)
                except Exception as e:
                    continue
                # 断开连接
                # print(response)
                if not response:
                    break
            except Exception as e:
                print(e)
                break
            print('服务端回复: ' + response.decode('utf-8'))
        tcp_client_socket.close()

    def multi_work(self, tcp_client_socket, data_list):
        """单个连接多个请求的请求函数"""
        for data in data_list:
            if not data:
                continue
            data = bytes(data, encoding="utf-8")
            try:
                tcp_client_socket.send(data)
                print(f'客户端发送：{data}')
                response = tcp_client_socket.recv(self.buffer_size)
                if not response:
                    break
            except Exception as e:
                print(e)
                break
            print('服务端回复: ' + response.decode('utf-8'))

        tcp_client_socket.close()

    def threading_socket_client(self, tcp_client_socket, num):
        with ThreadPoolExecutor(max_workers=num) as executor:
            for index, i in enumerate(range(num)):
                try:
                    print(f'run {index}, {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
                    executor.submit(self.multi_work, tcp_client_socket, [f'msg: {i}', 'client close'])
                except Exception as exc:
                    print('generated an exception: %s' % (exc))
        tcp_client_socket.close()

    def single_run(self):
        """单个连接，逐次请求"""

        tcp_client_socket = self.create_client_socket()
        self.single_work(tcp_client_socket)

    def single_conn_multi_query(self, threading_num):
        """单个连接，多个请求"""

        tcp_client_socket = self.create_client_socket()
        self.threading_socket_client(tcp_client_socket, threading_num)


def main():
    client_socket = ClientSocket(host='45.77.104.12')  # block_stats=False

    # 单个连接，逐次请求
    client_socket.single_run()

    # 单个连接，多个请求
    # 容易发生粘包问题
    # client_socket.single_conn_multi_query(2)

    # 多个连接，每个连接单个请求
    # client_socket.multi_conn_single_query(2)


if __name__ == '__main__':
    main()