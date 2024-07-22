import os.path
import ssl
from abc import abstractmethod
from queue import Queue
from socket import AF_INET
from socket import SO_REUSEADDR
from socket import SOCK_STREAM
from socket import socket
from socket import SOL_SOCKET
from threading import Event
from threading import Thread
from traceback import print_exc
from typing import Tuple
from time import sleep

from .message import MessageReceived
from .messageSender import MessageSender, Connection, Connections, receive_message, MessageToSend
from ..tools.terminate import terminate
from ..types import Address, ComponentRole, MessageType, MessageSubType


class MessageReceiver(MessageSender):

    def __init__(
            self,
            role: ComponentRole,
            addr: Address,
            portRange: Tuple[int, int],
            logLevel: int,
            ignoreSocketError: bool = False,
            messagesReceivedQueue: Queue[
                Tuple[MessageReceived, int]] = Queue(),
            threadNumber: int = 8,
            cert_file: str = None,
            key_file: str = None,
            tls_enabled: bool = False):

        self.conns: Connections[str, Connection] = Connections()
        self.messagesReceivedQueue: Queue[
            Tuple[MessageReceived, int]] = messagesReceivedQueue
        MessageSender.__init__(
            self,
            role=role,
            addr=addr,
            logLevel=logLevel,
            messagesReceivedQueue=self.messagesReceivedQueue,
            ignoreSocketError=ignoreSocketError,
            conns=self.conns)
        self.portRange = portRange
        self.serverSocket = socket(
            AF_INET,
            SOCK_STREAM)
        self.cert_file = cert_file
        self.key_file = key_file
        self.tls_enabled = tls_enabled
        if self.tls_enabled:
            if not self.cert_file or not self.key_file:
                self.debugLogger.error('TLS enabled but no cert or key file provided')
            elif not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
                self.debugLogger.error('TLS enabled but no cert or key file not exist in path: %s or %s',
                                       self.cert_file, self.key_file)
                terminate()
            else:
                self.debugLogger.info('TLS enabled with cert file: %s and key file: %s', self.cert_file, self.key_file)

        self.tls_socket = None

        self.threadsNumber: int = threadNumber
        self.serveEvent: Event = Event()
        self.autoListen()
        self.prepareThreadsPool()

    def prepareThreadsPool(self):
        j = 0
        for i in range(self.threadsNumber):
            Thread(
                target=self.messageSender,
                name=f'MessageSender{j}').start()
            j += 1
            k = 0
            for _ in range(4):
                Thread(
                    target=self.handle,
                    name=f"BasicMessageHandler{j}-{k}").start()
                k += 1
        Thread(target=self.serve, name="ConnectionServer").start()

    def autoListen(self):

        listenSuccess = self.tryListeningOn(
            addr=self.addr, portRange=self.portRange)
        if not listenSuccess:
            print_exc()
            self.debugLogger.error(
                'Failed to listen on addr: %s [%d, %d)',
                str(self.addr), self.portRange[0], self.portRange[1])
            terminate()

    def serve(self):
        self.serveEvent.set()
        i = 0
        while True:
            try:
                client_socket, clientAddress = self.serverSocket.accept()
                if self.tls_enabled:
                    client_socket = self.wrap_socket_tls(client_socket, server_side=True)
                self.debugLogger.info(f'KEEP RECEIVING: {clientAddress}')
                messageInDict, packetSize, buffer = receive_message(b'', client_socket)
                message = MessageReceived.fromDict(messageInDict)
                source_addr = message.source.addr
                self.conns.acquire()
                if source_addr not in self.conns or client_socket != self.conns[source_addr].socket:
                    self.conns[source_addr] = Connection(
                        buffer=buffer,
                        tls_enabled=self.tls_enabled,
                        recv_queue=self.messagesReceivedQueue,
                        send_queue=Queue(),
                        socket_obj=client_socket,
                        addr=source_addr)
                self.conns.release()
                # forward log messages when role is MASTER
                #  Due to security requirementsUser, actor and task executor do not see RemoteLogger
                # they send logs to Master and Master forwards them to RemoteLogger.
                # This will reduce the attack surface.
                if (self.role == ComponentRole.MASTER and
                        message.type == MessageType.LOG and
                        message.type != MessageSubType.ALL_RESOURCES_PROFILES):
                    self.sendMessage(messageToSend=MessageToSend.fromDict(messageInDict))
                    continue
                self.messagesReceivedQueue.put((message, packetSize))
                i += 1
            except ssl.SSLError:
                self.debugLogger.error(f'Received invalid TLS connection from {clientAddress}')
                client_socket.close()
                continue
            except Exception:
                print_exc()
                if self.role not in (ComponentRole.REMOTE_LOGGER, ComponentRole.MASTER):
                    self.debugLogger.error('Failed to send message. Exiting')
                    terminate()
                continue

    def tryListeningOn(self,
                       addr: Address,
                       portRange: Tuple[int, int]) -> bool:
        ip, targetPort = '0.0.0.0', addr[1]
        portLower, portUpper = portRange
        if targetPort != 0 and \
                (targetPort < portLower or targetPort >= portUpper):
            raise Exception('Port %s is out of config [%d, %d)' % (
                targetPort, portLower, portUpper))
        # Specified port
        if targetPort != 0:
            try:
                success = self.listenOn(addr=(ip, targetPort))
                if success:
                    return True
            except Exception:
                from traceback import print_exc
                print_exc()
                return False

        # Did not specify port
        for targetPort in range(portRange[0], portRange[1]):
            try:
                success = self.listenOn(addr=(ip, targetPort))
                if success:
                    return True
            except OSError:
                self.debugLogger.warning("Failed to listen on port %d, sleep and try next port", targetPort)
                sleep(0.1)
                continue
        return False

    def wrap_socket_tls(self,
                        socket_object,
                        server_side=True):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.cert_file, self.key_file)
        tls_socket = context.wrap_socket(socket_object, server_side=server_side)
        return tls_socket

    def listenOn(self,
                 addr: Address) -> bool:
        self.addr = (self.addr[0], addr[1])
        self.serverSocket.setsockopt(
            SOL_SOCKET,
            SO_REUSEADDR,
            1)
        self.serverSocket.bind(addr)
        self.serverSocket.listen()
        self.debugLogger.info(
            'Listening at %s' % str(self.serverSocket.getsockname()))
        self.debugLogger.info(
            'Advertise addr is at %s' % str(self.addr))
        return True

    @abstractmethod
    def handle(self):
        pass

    @abstractmethod
    def handleMessage(self):
        pass
