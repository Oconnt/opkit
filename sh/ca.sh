#!/bin/bash

# ========================以下为根证书配置========================
password="mry@75500230"
country="CN"
state="guangdong"
locality="shenzhen"
organization="mry"
organizational_unit="mry"
common_name="mry"
email="1825793535@qq.com"
#challenge_password="$password"
#optional_company_name="mry"
# CA证书私钥长度
private_key_len=2048
# CSR文件有效期
csr_ttl=7300
# CRT文件有效期
crt_ttl=7300

# ========================以下为服务器证书配置========================
server_password="mry@75500230"
server_country="CN"
server_state="guangdong"
server_locality="shenzhen"
server_organization="mry"
server_organizational_unit="mry"
server_common_name="mry"
server_email="1825793535@qq.com"
#challenge_password="$password"
#optional_company_name="mry"
# CA证书私钥长度
server_private_key_len=2048
# CSR文件有效期
server_csr_ttl=365
# CRT文件有效期
server_crt_ttl=365

function check_cmd_success() {
    if [ $? -ne 0 ]; then
        lerror "$2"
        exit 1
    else
        linfo "$1"
    fi
}

function create_root_ca() {
    linfo "开始创建根证书......"
    local pass_text="pass:$password"
    # 1.生成CA根证书私钥
    openssl genrsa -aes128 -passout $pass_text -out ca-private.key $private_key_len
    check_cmd_success "生成CA证书私钥成功!" "生成CA证书私钥失败!"

    # 2.生成CA根证书请求文件
    openssl req -new -key ca-private.key -passin $pass_text -out ca-req.csr -days $csr_ttl \
    -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizational_unit/CN=$common_name/emailAddress=$email" \
    -reqexts SAN \
    -config <(cat /etc/pki/tls/openssl.cnf \
    <(printf "[SAN]\nsubjectAltName=DNS:$common_name"))
    check_cmd_success "生成CA证书请求文件成功!" "生成CA证书请求文件失败!"

    # 3.生成CA根证书
    openssl x509 -req -in ca-req.csr -signkey ca-private.key -out ca-root.crt -days $crt_ttl -passin $pass_text
    check_cmd_success "生成CA根证书成功!" "生成CA根证书失败!"

    linfo "创建根证书成功!"
}

function create_server_ca() {
    linfo "开始创建服务器证书......"
    local root_pass_text="pass:$password"
    local pass_text="pass:$server_password"
    # 1.生成服务器证书私钥
    openssl genrsa -aes128 -passout $pass_text -out server-private.key $server_private_key_len
    check_cmd_success "生成服务器证书私钥成功!" "生成服务器证书私钥失败!"

    # 2.生成服务器证书请求文件
    openssl req -new -key server-private.key -passin $pass_text -out server-req.csr -days $server_csr_ttl \
    -subj "/C=$server_country/ST=$server_state/L=$server_locality/O=$server_organization/OU=$server_organizational_unit/CN=$server_common_name/emailAddress=$server_email" \
    -reqexts SAN \
    -config <(cat /etc/pki/tls/openssl.cnf \
    <(printf "[SAN]\nsubjectAltName=DNS:$common_name"))
    check_cmd_success "生成服务器证书请求文件成功!" "生成服务器证书请求文件失败!"

    # 3.生成服务器证书
    openssl x509 -req -in server-req.csr -days $server_crt_ttl \
    -CAkey ca-private.key -CA ca-root.crt -CAcreateserial \
    -out server.crt \
    -passin $root_pass_text
    check_cmd_success "生成服务器证书成功!" "生成服务器证书失败!"

    linfo "创建服务器证书成功!"
}

function init_openssl() {
    openssl version > /dev/null
    if [ $? -eq 127 ];then
        linfo "未安装openssl，将自动安装!"
        yum -y install openssl
        if [ $? -eq 0 ];then
            linfo "openssl安装成功!"
        else
            lwarn "openssl安装失败，请配置软件源或下载openssl后重试!"
            exit 1
        fi
    fi
}

function install_ca() {
    init_openssl
    create_root_ca
    create_server_ca
}

source /mry/sh/common.sh
install_ca
