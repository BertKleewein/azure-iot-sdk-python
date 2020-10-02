# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import paho.mqtt.client
import azure.iot.device.common.mqtt_transport
import mbedtls.tls as mbed_ssl
import mbedtls.x509 as mbed_x509
import ssl as default_ssl
import time
import select
import socket
import platform
import errno
from socket_logging_wrapper import SocketLoggingWrapper

logger = logging.getLogger(__name__)

mbed_ssl._set_debug_level(4)

# Copied from Paho.  This is how Paho handles recv calls with no data available
if platform.system() == "Windows":
    EAGAIN = errno.WSAEWOULDBLOCK
else:
    EAGAIN = errno.EAGAIN


def monkeypatch():
    logger.info("Patching paho and azure.iot.device  to use mbed_tls")
    ssl_wrapper = SSLWrapper()
    paho.mqtt.client.ssl = ssl_wrapper
    azure.iot.device.common.mqtt_transport.ssl = ssl_wrapper


def run_with_select(mbed_socket, func, *args, **kwargs):
    timeout = mbed_socket.gettimeout()
    print("timeout={}".format(timeout))
    if timeout is not None:
        start = time.time()
    while True:
        try:
            print("calling")
            return func(*args, **kwargs)
        except (mbed_ssl.WantReadError, mbed_ssl.WantWriteError):
            print("exc")
            if timeout is None or time.time() > start + timeout:
                raise
            result = select.select(
                [mbed_socket], [mbed_socket], [], timeout - (time.time() - start)
            )
            if result == [[], [], []]:
                raise TimeoutError()


class SSLSocketWrapper(object):
    def __init__(self, mbed_socket):
        self.mbed_socket = mbed_socket
        self.timeout = None

    def do_handshake(self):
        print("do_handshake")
        return run_with_select(mbed_socket=self.mbed_socket, func=self.mbed_socket.do_handshake)

    def settimeout(self, timeout):
        self.timeout = timeout

    def setblocking(self, f):
        # TODO
        pass

    def fileno(self):
        return self.mbed_socket.fileno()

    def send(self, buffer, flags=None):
        try:
            print("send buffer_size = {}".format(len(buffer)))
            return self.mbed_socket.send(buffer, flags or 0)
        except mbed_ssl.WantReadError:
            raise socket.error(default_ssl.SSL_ERROR_WANT_READ, "WantReadError")
        except mbed_ssl.WantWriteError:
            raise socket.error(default_ssl.SSL_ERROR_WANT_WRITE, "WantWriteError")

    def recv(self, bufsize, flags=None):
        try:
            ret = self.mbed_socket.recv(bufsize, flags or 0)
            print("wrapper: returning {}".format(ret.hex()))
            return ret
        except mbed_ssl.WantReadError:
            raise socket.error(default_ssl.SSL_ERROR_WANT_READ, "WantReadError")
        except mbed_ssl.WantWriteError:
            raise socket.error(default_ssl.SSL_ERROR_WANT_WRITE, "WantWriteError")
        except mbed_ssl.RaggedEOF:
            raise socket.error(EAGAIN, "RaggedEOF")
        except Exception as e:
            print("*************8transport exception: {},{}".format(type(e), str(e)))
            raise


class SSLContextWrapper(object):
    def __init__(self, protocol):
        assert protocol == mbed_ssl.TLSVersion.TLSv1_2
        # TODO: plumb validate_certificate patam of TLSConfiguratoin ctor
        # TODO: plumb certificate_chain and trust_store param on TLSConfiguration ctor
        trust_store = mbed_ssl.TrustStore.system()
        # cert = mbed_x509.CRT.from_file("./Baltimore_CyberTrust_Root.pem")
        # trust_store.add(cert)
        # TODO: validate_certificates must be True!
        config = mbed_ssl.TLSConfiguration(
            lowest_supported_version=protocol,
            highest_supported_version=protocol,
            trust_store=trust_store,
            validate_certificates=False,
        )
        mbed_ssl._enable_debug_output(config)
        self.context = mbed_ssl.ClientContext(config)

    def load_default_certs(self):
        # TODO
        pass

    def wrap_socket(self, sock, server_hostname, do_handshake_on_connect):
        # TODO: deal with do_handshake_on_connect
        logger.info("Wrapping socket for {}".format(server_hostname))
        # TODO: do we apply context.wrap_socket here or in the SSLSocketWrapper ctor
        return SocketLoggingWrapper(
            SSLSocketWrapper(
                self.context.wrap_socket(
                    socket=SocketLoggingWrapper(sock, name="encrypted"),
                    server_hostname=server_hostname,
                )
            ),
            name="decrypted",
        )


class SSLWrapper(object):
    PROTOCOL_TLSv1_2 = mbed_ssl.TLSVersion.TLSv1_2
    CERT_REQUIRED = 2
    SSL_ERROR_WANT_READ = default_ssl.SSL_ERROR_WANT_READ
    SSL_ERROR_WANT_WRITE = default_ssl.SSL_ERROR_WANT_WRITE

    class CertificateError(Exception):
        pass

    def SSLContext(self, protocol):
        logger.info("Creating SSLContextWrapper for protocol {}".format(protocol))
        return SSLContextWrapper(protocol)
