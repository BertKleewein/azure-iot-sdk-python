# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class SocketLoggingWrapper(object):
    def __init__(self, socket, name):
        self._socket = socket
        self.name = name

    def __str__(self):
        return str(self._socket)

    def __repr__(self):
        return "wrapped {} socket for {}".format(self.name, repr(self._socket))

    @property
    def family(self):
        return self._socket.family

    @property
    def proto(self):
        return self._socket.proto

    @property
    def type(self):
        return self._socket.type

    def accept(self):
        return self._socket.accept()

    def bind(self, address):
        self._socket.bind(address)

    def close(self):
        self._socket.close()

    def connect(self, address):
        self._socket.connect(address)

    def connect_ex(self, address):
        self._socket.connect_ex(address)

    def fileno(self):
        return self._socket.fileno()

    def getpeername(self):
        return self._socket.getpeername()

    def getsockname(self):
        return self._socket.getsockname()

    def getsockopt(self, optname, buflen=None):
        return self._socket.getsockopt(optname, buflen=buflen)

    def listen(self, backlog=None):
        self._socket.listen(backlog)

    def makefile(self, *args, **kwargs):
        return self._socket.makefile(*args, **kwargs)

    def recv(self, bufsize, flags=0):
        # print("{}: calling recv {} bytes".format(self.name, bufsize))
        try:
            ret = self._socket.recv(bufsize, flags)
            # print( "{}: recv {} bytes returned {} bytes: {}".format( self.name, bufsize, len(ret), ret.hex()))
            return ret
        except Exception:
            # print("{}: recv {} bytes raised {}".format(self.name, bufsize, e))
            raise

    def recv_into(self, buffer, nbytes=None, flags=0):
        # print("{}: calling recv_into {} bytes".format(self.name, nbytes))
        try:
            ret = self._socket.recv_info(buffer, nbytes, flags)
            # print("{}: recv_info {} bytes returned {} bytes".format(self.name, nbytes, ret))
            return ret
        except Exception:
            # print("{}: recv_into {} bytes raised {}".format(self.name, nbytes, e))
            raise

    def recvfrom(self, bufsize, flags=0):
        return self._socket.recvfrom(bufsize, flags)

    def recvfrom_into(self, buffer, nbytes=None, flags=0):
        return self._socket.recvfrom_into(buffer, nbytes, flags)

    def send(self, message, flags=0):
        # print("{}: send {} bytes".format(self.name, len(message)))
        try:
            ret = self._socket.send(message, flags)
            # print("{}: send {} bytes returned {}".format(self.name, len(message), ret))
            return ret
        except Exception:
            # print("{}: send {} bytes raised {}".format(self.name, len(message), e))
            raise

    def sendall(self, message, flags=0):
        return self._socket.sendall(message, flags)

    def sendto(self, message, flags=0, address=None):
        return self._socket.sendto(message, flags, address)

    def setblocking(self, flag):
        self._socket.setblocking(flag)

    def settimeout(self, value):
        self._socket.settimeout(value)

    def gettimeout(self):
        return self._socket.gettimeout()

    def setsockopt(self, level, optname, value):
        self._socket.setsockopt(level, optname, value)

    def shutdown(self, how):
        self._socket.shutdown(how)

    # PEP 543 adds the following methods.

    def _do_handshake_step(self):
        return self._socket._do_handshake_step()

    def do_handshake(self):
        return self._socket.do_handshake()

    def setcookieparam(self, param):
        self._socket.setcookieparam(param)

    def cipher(self):
        return self.socket.cipher()

    def negotiated_protocol(self):
        return self._socket.negotiated_protocol()

    @property
    def context(self):
        return self._socket.context

    def negotiated_tls_version(self):
        return self._socket.negotiated_tls_version()

    def unwrap(self):
        return self._socket
