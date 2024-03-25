import os
import base64
import platform

if platform.system() == 'Windows':
    from crypto.PublicKey import RSA
    from crypto.Cipher import PKCS1_v1_5
else:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from opkit.common.constants import PEM_START_FLAG


def encrypt(message, public_key, passphrase=None):
    """
    rsa加密函数
    :param message: 待加密信息
    :param public_key: 公钥
    :param passphrase: 密码短语
    :return:
    """
    key = RSA.import_key(public_key, passphrase)
    cipher = PKCS1_v1_5.new(key)
    ciphertext = cipher.encrypt(message.encode())
    return base64.b64encode(ciphertext).decode()


def decrypt(ciphertext, private_key, passphrase=None):
    """
    rsa解密函数
    :param ciphertext: 加密文本
    :param private_key: 私钥
    :param passphrase: 密码短语
    :return:
    """
    key = RSA.import_key(private_key, passphrase)
    cipher = PKCS1_v1_5.new(key)
    message = cipher.decrypt(ciphertext, None)
    return message.decode()


def encrypt_file(message, path, passphrase=None):
    """
    rsa加密函数，通过路径加载公钥
    :param message: 待加密信息
    :param path: 公钥路径
    :param passphrase: 密码短语
    :return:
    """
    if not os.path.isfile(path):
        return message

    with open(path, 'r') as f:
        public_key = f.read()

    return encrypt(message, public_key, passphrase)


def decrypt_file(ciphertext, path, passphrase=None):
    """
    rsa解密函数，通过路径加载私钥
    :param passphrase:
    :param ciphertext: 加密文本
    :param path: 私钥路径
    :return:
    """
    if not os.path.isfile(path):
        return ciphertext

    with open(path, 'r') as f:
        private_key = f.read()

    return decrypt(ciphertext, private_key, passphrase)


def get_private_from_file(path, password=None, format=serialization.PrivateFormat.TraditionalOpenSSL):  # noqa
    """
    通过证书文件获取私钥
    :param password: 证书密码(可选)
    :param path: 证书文件路径
    :param format: 输出私钥格式字段，默认为openssl
    :return:
    """
    if not os.path.isfile(path):
        return

    with open(path, "rb") as f:
        cert_bytes = f.read()

    return get_private_from_data(cert_bytes, password, format)


def get_private_from_data(cert_bytes, password=None, format=serialization.PrivateFormat.TraditionalOpenSSL):  # noqa
    """
    通过证书字串获取私钥
    :param cert_bytes: 证书字串
    :param password: 证书密码(可选)
    :param format: 输出私钥格式字段，默认为openssl
    :return:
    """
    if isinstance(password, str):
        password = password.encode('utf-8')

    private_key = serialization.load_pem_private_key(
        cert_bytes,
        password=password,
        backend=default_backend()
    )

    algorithm = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption  # noqa

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=format,
        encryption_algorithm=algorithm
    )

    return private_bytes.decode('utf-8')


def get_public_from_x509_file(path):
    if not os.path.isfile(path):
        return

    with open(path, 'rb') as f:
        cert_data = f.read()

    return get_public_from_x509_data(cert_data)


def get_public_from_x509_data(data):
    """
    根据x509证书提取公钥
    :param data: 证书
    :return: str
    """
    if PEM_START_FLAG in str(data):
        cert = x509.load_pem_x509_certificate(data, default_backend())
    else:
        cert = x509.load_der_x509_certificate(data, default_backend())

    public_key = cert.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return public_key_bytes.decode("utf-8")
