import socket


class ServerSocketBase:
    def __init__(self,
                 host='127.0.0.1', port=5057, buffer_size=1024, max_conn=10, block_stats=True):
        self.host = host
        self.port = port
        self.max_conn = max_conn
        self.block_stats = block_stats
        self.buffer_size = buffer_size
        self.address = (self.host, self.port)
        self.conn = 0

    def create_server_socket(self):
        """创建一个服务端Socket"""
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 在ctrl+c断开服务端后，使用下面这行允许立刻重启服务
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server_socket.bind(self.address)
        tcp_server_socket.setblocking(self.block_stats)
        # 设置最大连接数为10
        tcp_server_socket.listen(self.max_conn)
        return tcp_server_socket

    def create_client_socket(self):
        """创建一个客户端Socket"""
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client_socket.connect(self.address)
        tcp_client_socket.setblocking(self.block_stats)
        return tcp_client_socket

