import ssl
import socket
import threading
from pickle import dumps, loads
from abc import abstractmethod
from threading import Lock
from queue import Queue
from socket import AF_INET
from socket import SOCK_STREAM
from socket import socket
from time import time, sleep
from traceback import print_exc
from typing import Dict
from typing import Tuple

from .message import MessageToSend
from ..debugLogPrinter import DebugLogPrinter
from ..types import Address
from ..types import Component
from ..types import ComponentRole
from ..types import MessageSubSubType
from ..types import MessageSubType
from ..types import MessageType
from ..tools.terminate import terminate
from .message import MessageReceived

SEP = b','


def send_message(s: socket, messageInDict: dict):
    messageInBytes = dumps(messageInDict)
    msg_len = len(messageInBytes)
    messageInBytes = msg_len.to_bytes(4, byteorder='big') + b',' + messageInBytes
    s.sendall(messageInBytes)


def receive_message(buffer, clientSocket: socket):
    while len(buffer) < 5:
        ret = clientSocket.recv(4096)
        if not ret:
            raise Exception('Connection disconnected')
        buffer += ret
    msg_len = int.from_bytes(buffer[:4], byteorder='big')
    m = buffer[5:]

    if len(m) >= msg_len:
        messageInDict = loads(m[:msg_len])
        return messageInDict, msg_len, m[msg_len:]

    remaining = msg_len - len(m)
    buffer = b''
    while remaining > 0:
        ret = clientSocket.recv(4096)
        if not ret:
            raise Exception('Connection disconnected')
        if len(ret) > remaining:
            m += ret[:remaining]
            buffer = ret[remaining:]
            break
        m += ret
        remaining -= len(ret)
    messageInDict = loads(m)
    return messageInDict, msg_len, buffer


class Connection:
    def __init__(self,
                 tls_enabled,
                 recv_queue,
                 send_queue,
                 buffer,
                 addr=None,
                 socket_obj=None,
                 max_retries=10,
                 retry_delay=1):
        self.tls_enabled = tls_enabled
        self.is_proactive = socket_obj is None
        self.buffer = buffer
        self.addr = addr
        self.socket = socket_obj
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.threads = []

        if self.is_proactive:
            self._connect_with_retries()
            self._start_threads()
        else:
            if not self.socket:
                raise ValueError("A socket object must be provided for passive mode")
            self._start_threads()

    def _connect_with_retries(self):
        attempts = 0
        while attempts < self.max_retries:
            try:
                self.socket = create_socket(tls_enabled=self.tls_enabled, dest_addr=self.addr)
                return
            except Exception as e:
                attempts += 1
                sleep(self.retry_delay)
        raise Exception(f"Failed to connect to {self.addr} after {self.max_retries} attempts")

    def _start_threads(self):
        self.recv_thread = threading.Thread(target=self._recv_task)
        self.send_thread = threading.Thread(target=self._send_task)
        self.recv_thread.daemon = True
        self.send_thread.daemon = True
        self.recv_thread.start()
        self.send_thread.start()
        self.threads.append(self.recv_thread)
        self.threads.append(self.send_thread)

    def _recv_task(self):
        while True:
            try:
                content, packetSize, buffer = receive_message(self.buffer, self.socket)
                self.buffer = buffer
                if content:
                    message = MessageReceived.fromDict(content)
                    self.recv_queue.put((message, packetSize))
                else:
                    self._handle_socket_error("Connection closed by the server")
            except Exception as e:
                raise Exception(f"Receive error: {e}")

    def _send_task(self):
        while True:
            messageInDict = self.send_queue.get()
            send_message(self.socket, messageInDict)

    def _handle_socket_error(self,
                             message,
                             send_data='socket connection closed without message'):
        self.socket.close()
        if self.is_proactive:
            self._connect_with_retries()
            self._start_threads()
        else:
            if send_data:
                self.send_queue.put(send_data)
            self._terminate_threads()
            raise Exception(message)

    def _terminate_threads(self):
        for thread in self.threads:
            if thread.is_alive():
                try:
                    thread.join()
                except Exception:
                    pass
        self.threads.clear()

    def send_message(self,
                     message):
        self.send_queue.put(message)

    def close(self):
        self.socket.close()
        self._terminate_threads()


def create_socket(tls_enabled: bool,
                  dest_addr: Address):
    client_socket = socket(AF_INET, SOCK_STREAM)
    if tls_enabled:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        client_socket = context.wrap_socket(client_socket,
                                            server_hostname=dest_addr[0])

    client_socket.connect(dest_addr)
    return client_socket


class Connections(dict):

    def __init__(self):
        super().__init__()
        self._lock = Lock()

    def acquire(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()


class MessageSender(Component, DebugLogPrinter):

    def __init__(
            self,
            role: ComponentRole,
            addr: Address,
            logLevel: int,
            messagesReceivedQueue: Queue[
                Tuple[MessageReceived, int]],
            conns: Connections[str, Connection],
            ignoreSocketError: bool = False,
            tls_enabled: bool = False):
        DebugLogPrinter.__init__(self, logLevel)
        Component.__init__(self, role=role, addr=addr)
        self.tls_enabled = tls_enabled

        self.messagesToSendQueue: Queue[
            Tuple[MessageToSend, bool, bool]] = Queue()
        self.messagesReceivedQueue = messagesReceivedQueue
        self.ignoreSocketError = ignoreSocketError
        self.conns = conns

    def sendMessage(
            self,
            messageToSend: MessageToSend = None,
            data: Dict = None,
            destination: Component = None,
            messageType: MessageType = MessageType.NONE,
            messageSubType: MessageSubType = MessageSubType.NONE,
            messageSubSubType: MessageSubSubType = MessageSubSubType.NONE,
            ignoreSocketError: bool = None,
            showFailure: bool = True):

        if messageToSend is None:
            messageToSend = MessageToSend(
                messageType=messageType,
                data=data,
                destination=destination,
                messageSubType=messageSubType,
                messageSubSubType=messageSubSubType)
        messageToSend.sentAtSourceTimestamp = time() * 1000

        destination = messageToSend.destination
        component = Component.fromDict(destination.toDict())
        messageToSend.destination = component

        self.messagesToSendQueue.put(
            (messageToSend, ignoreSocketError, showFailure))

    @abstractmethod
    def _receiving_helper(self,
                          source_addr: Address,
                          thread_name: str):
        raise NotImplementedError

    def messageSender(self):
        while True:
            try:
                messageToSend, ignoreSocketError, showFailure = self.messagesToSendQueue.get()
                messageInDict = messageToSend.toDict()
                messageInDict['source'] = self.toDict()
                dest_addr = messageToSend.destination.addr
                self.conns.acquire()
                if dest_addr not in self.conns:
                    conn = Connection(
                        buffer=b'',
                        tls_enabled=self.tls_enabled,
                        recv_queue=self.messagesReceivedQueue,
                        send_queue=Queue(),
                        addr=dest_addr)
                    self.conns[dest_addr] = conn
                else:
                    conn = self.conns[dest_addr]
                self.conns.release()
                conn.send_message(messageInDict)

            except Exception:
                print_exc()
                if self.role not in (ComponentRole.REMOTE_LOGGER, ComponentRole.MASTER):
                    self.debugLogger.error('Failed to send message. Exiting')
                    terminate()
