#!/bin/bash

ASKME=1

function install_redis() {
    if [ $M_MODE = "net" ]; then
        cat <<- 'EOF' > ${M_BIN}/mredis
version="$1"
redis_file="redis-${version}"
redis_tar_file="${redis_file}.tar.gz"
wget -P /mry/opt/redis/${version}/ https://download.redis.io/releases/$redis_tar_file && \
tar -xzf /mry/opt/redis/${version}/${redis_tar_file} && \
rm -f /mry/opt/redis/${version}/${redis_tar_file}

gcc -v >/dev/null 2>&1
if [ $? -ne 0 ];then
    echo "请先安装gcc和基础库devtoolset-9-gcc devtoolset-9-gcc-c++ devtoolset-9-binutils"
    exit 1
fi

cd /mry/opt/redis/${version}/${redis_file}/src
make
make install PREFIX=/mry/bin

# 创建 systemd 服务单元文件
cat > /etc/systemd/system/redis.service <<BLK
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
ExecStart=/mry/bin/redis-server
ExecStop=/mry/bin/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target
BLK

# 加载新的服务单元文件
systemctl daemon-reload
systemctl enable --now redis
EOF
    else
        cat <<- 'EOF' > ${M_BIN}/mredis
version="$1"
redis_file="redis-${version}"
redis_tar_file="${redis_file}.tar.gz"
cp /mry/resource/redis/${redis_tar_file} /mry/opt/redis/${version}/ && \
tar -xzf /mry/opt/redis/${version}/${redis_tar_file} && \
rm -f /mry/opt/redis/${version}/${redis_tar_file}

gcc -v >/dev/null 2>&1
if [ $? -ne 0 ];then
    echo "请先安装gcc和基础库devtoolset-9-gcc devtoolset-9-gcc-c++ devtoolset-9-binutils"
    exit 1
fi

cd /mry/opt/redis/${version}/${redis_file}/src
make
make install PREFIX=/mry/bin

# 创建 systemd 服务单元文件
cat > /etc/systemd/system/redis.service <<BLK
[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
ExecStart=/mry/bin/redis-server
ExecStop=/mry/bin/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target
BLK

# 加载新的服务单元文件
systemctl daemon-reload
systemctl enable --now redis
EOF
    fi

    chmod +x ${M_BIN}/mredis
    linfo "mredis 安装成功！"
}

function install_java() {
    if [ $M_MODE = "net" ];then
        cat <<- 'EOF' > ${M_BIN}/mjava
# x64jdk包下载地址
declare -A x_vers_map=(
    ["7"]="https://download.java.net/openjdk/jdk7u75/ri/openjdk-7u75-b13-linux-x64-18_dec_2014.tar.gz"
    ["8"]="https://download.java.net/openjdk/jdk8u43/ri/openjdk-8u43-linux-x64.tar.gz"
    ["9"]="https://download.java.net/openjdk/jdk9/ri/openjdk-9+181_linux-x64_ri.zip"
    ["10"]="https://download.java.net/openjdk/jdk10/ri/openjdk-10+44_linux-x64_bin_ri.tar.gz"
    ["11"]="https://download.java.net/openjdk/jdk11.0.0.1/ri/openjdk-11.0.0.1_linux-x64_bin.tar.gz"
    ["12"]="https://download.java.net/openjdk/jdk12/ri/openjdk-12+32_linux-x64_bin.tar.gz"
    ["13"]="https://download.java.net/openjdk/jdk13/ri/openjdk-13+33_linux-x64_bin.tar.gz"
    ["14"]="https://download.java.net/openjdk/jdk14/ri/openjdk-14+36_linux-x64_bin.tar.gz"
    ["15"]="https://download.java.net/openjdk/jdk15/ri/openjdk-15+36_linux-x64_bin.tar.gz"
    ["16"]="https://download.java.net/openjdk/jdk16/ri/openjdk-16+36_linux-x64_bin.tar.gz"
    ["17"]="https://download.java.net/openjdk/jdk17/ri/openjdk-17+35_linux-x64_bin.tar.gz"
    ["18"]="https://download.java.net/openjdk/jdk18/ri/openjdk-18+36_linux-x64_bin.tar.gz"
    ["19"]="https://download.java.net/openjdk/jdk19/ri/openjdk-19+36_linux-x64_bin.tar.gz"
    ["20"]="https://download.java.net/openjdk/jdk20/ri/openjdk-20+36_linux-x64_bin.tar.gz"
    ["21"]="https://download.java.net/openjdk/jdk21/ri/openjdk-21+35_linux-x64_bin.tar.gz"
)
# arm64jdk包下载地址
declare -A arm_vers_map=(
    ["15"]="https://download.java.net/java/GA/jdk15/779bf45e88a44cbd9ea6621d33e33db1/36/GPL/openjdk-15_linux-aarch64_bin.tar.gz"
    ["16"]="https://download.java.net/java/GA/jdk16/7863447f0ab643c585b9bdebf67c69db/36/GPL/openjdk-16_linux-aarch64_bin.tar.gz"
    ["17"]="https://download.java.net/java/GA/jdk17/0d483333a00540d886896bac774ff48b/35/GPL/openjdk-17_linux-aarch64_bin.tar.gz"
    ["18"]="https://download.java.net/java/GA/jdk18/43f95e8614114aeaa8e8a5fcf20a682d/36/GPL/openjdk-18_macos-aarch64_bin.tar.gz"
    ["19"]="https://download.java.net/java/GA/jdk19/877d6127e982470ba2a7faa31cc93d04/36/GPL/openjdk-19_macos-aarch64_bin.tar.gz"
    ["20"]="https://download.java.net/java/GA/jdk20/bdc68b4b9cbc4ebcb30745c85038d91d/36/GPL/openjdk-20_linux-aarch64_bin.tar.gz"
    ["21"]="https://download.java.net/java/GA/jdk21/fd2272bbf8e04c3dbaee13770090416c/35/GPL/openjdk-21_linux-aarch64_bin.tar.gz"
)

version="$1"
if [ -z $version ];then
    echo "请指定java版本"
    exit 1
fi

source /mry/sh/common.sh
arch=$(arch)
if [ $arch == 'amd64' ];then
    legal=$(echo "${!x_vers_map[@]}" | grep -wq "$version" &&  echo 1 || echo 0)
    if [ $legal -eq 1 ];then
        download_url=${x_vers_map[${version}]}
    else
        echo "暂不支持下载${version}版本的jdk"
        exit 0
    fi
else
    legal=$(echo "${!arm_vers_map[@]}" | grep -wq "$version" &&  echo 1 || echo 0)
    if [ $legal -eq 1];then
        download_url=${arm_vers_map[${version}]}
    else
        echo "暂不支持下载${version}版本的jdk"
        exit 0
    fi
fi

java_tar_file=$(echo $download_url | awk -F/ '{print $NF}')
dir="/mry/lib/java/${version}"
mkdir -p $dir

echo "=====================开始下载${java_tar_file}到${dir}====================="
wget -P $dir ${download_url} && tar Cxzvf $dir $dir/$java_tar_file

# 设置动态链接
java_dir=$(tar tf ${dir}/${java_tar_file} | head -n 1 | cut -f1 -d"/")
java_home=${dir}/${java_dir}
for f in ${java_home}/bin/*;do
    ln -sf $f /mry/bin/
done

# 设置环境变量
add_profile "export JAVA_HOME=${java_home}"

java -version

# 清理压缩包
rm -f $dir/$java_tar_file
EOF
    else
        cat <<- 'EOF' > ${M_BIN}/mjava
EOF

    fi

    chmod +x ${M_BIN}/mjava
    linfo "mjava 安装成功！"
}

function install_python() {
    if [ $M_MODE = "net" ];then
        cat <<- 'EOF' > ${M_BIN}/mpy
version="$1"
flag=0

# 校验版本号格式
IFS='.' read -r major minor patch <<< "$version"
if [ -z $version ];then
    echo "请指定python版本!"
    exit 1
elif ! [[ $major =~ ^[0-9]+$ ]] || ! [[ $minor =~ ^[0-9]+$ ]]; then
    echo "主要版本号：$major，次要版本号：$minor，主要版本号和次要版本号必须为整数"
    exit 1
elif [ "$major" -gt 3 ] || [[ "$major" -eq 3 && "$minor" -gt 7 ]]; then
    ssl_ver_flag=$(openssl version | awk '$2 > "1.0.2"')
    if [[ ! $ssl_ver_flag ]]; then
        echo "安装python 3.7及以上版本必须先更新openssl版本至1.0.2以上"
        exit 1
    fi
    flag=1
fi

dir="/mry/lib/python/${version}"
mkdir -p $dir

download_url=https://www.python.org/ftp/python/${version}/Python-${version}.tgz
python_tar_file=$(echo $download_url | awk -F/ '{print $NF}')
echo "====================开始下载${python_tar_file}到${dir}===================="
wget -P $dir $download_url && tar Cxzvf $dir ${dir}/${python_tar_file}

python_dir=$(tar tf ${dir}/${python_tar_file} | head -n 1 | cut -f1 -d"/")
python_src=${dir}/${python_dir}

# 先安装gcc等依赖
gcc -v &>/dev/null
if [ $? -ne 0 ];then
    yum -y install gcc openssl-devel bzip2-devel libffi-devel
fi
# 安装zlib-devel
yum -y install zlib-devel

# 编译安装
cd $python_src
if [ $flag -eq 0 ]; then
    ./configure --prefix=$dir && make && make install
else
    ./configure --prefix=$dir --with-openssl=/usr/local/openssl && make && make install
fi

# 设置环境变量
source /mry/sh/common.sh
add_profile 'export PATH="$PATH:'"$dir"'/bin"'

if [ ${version:0:1} == '3' ];then
    version_info=$(python3 -V)
else
    version_info=$(python -V)
fi

if [ $? -eq 0 ];then
    echo "${version_info} 安装成功！"
else
    echo "${version_info} 安装失败！"
fi

# 清理压缩包和源码目录
rm -f ${dir}/${python_tar_file}
rm -rf $python_src
EOF
    else
        cat <<- 'EOF'> ${M_BIN}/mpy
EOF
    fi

    chmod +x ${M_BIN}/mpy
    linfo "mpy 安装成功！"
}

function install_go() {
    if [ $M_MODE = "net" ];then
        cat <<- 'EOF' > ${M_BIN}/mgo
version="$1"
if [ -z $version ];then
    echo "请指定go版本!"
    exit 1
fi

source /mry/sh/common.sh
arch=$(arch)

go_tar_file="go${version}.linux-${arch}.tar.gz"
dir="/mry/lib/go/${version}"
mkdir -p $dir

echo "======================开始下载${go_tar_file}到${dir}======================"
wget -P $dir https://golang.google.cn/dl/${go_tar_file} && \
tar Cxzvf $dir $dir/$go_tar_file

add_profile 'export PATH="$PATH:'"$dir"'/go/bin"'
add_profile 'export GOPROXY="https://goproxy.cn,direct;GOSUMDB=off"'

version_info=$(go version)
if [ $? -eq 0 ];then
    echo "${version_info} 安装成功！"
else
    echo "${version_info} 安装失败！"
fi

# 清理压缩包
rm -f $dir/$go_tar_file

EOF
    else
        cat <<- 'EOF' > ${M_BIN}/mgo
version="$1"
versions="1.16，1.17，1.18，1.19，1.20"
if [[ -z "$version" || ! "$versions" == *"$version"* ]];then
    echo "请指定正确的go版本，可选版本：${versions}"
    exit 1
fi

source /mry/sh/common.sh
arch=$(arch)
go_tar_file="go${version}.linux-${arch}.tar.gz"
dir="/mry/lib/go/${version}"
mkdir -p $dir

cp /mry/resource/go/${go_tar_file} $dir/ && \
tar Cxzvf $dir $dir/$go_tar_file && \
rm -f $dir/$go_tar_file

add_profile 'export PATH="$PATH:'"$dir"'/bin"'
echo "内网环境下，请自行配置GOPROXY代理！"

version_info=$(go version)
if [ $? -eq 0 ];then
    echo "${version_info} 安装成功！"
else
    echo "${version_info} 安装失败！"
fi

# 清理压缩包
rm -f $dir/$go_tar_file
EOF
    fi

    chmod +x ${M_BIN}/mgo
    linfo "mgo 安装成功！"
}

#function install_openssl() {
#    if [ $M_MODE = "net" ];then
#        cat <<- 'EOF' > ${M_BIN}/mssl
#version=$1
#ssl_tar=openssl-${version}.tar.gz
#wget https://www.openssl.org/source/${ssl_tar} && tar -zxvf ${ssl_tar}
#
#EOF
#    else
#        cat <<- 'EOF' > ${M_BIN}/mssl
#EOF
#    fi
#
#    chmod +x ${M_BIN}/mssl
#    linfo "mssl 安装成功"
#}

function install_k8s() {
    if [ $M_MODE = "net" ];then
        cat <<- 'EOF' > ${M_BIN}/mk8s
source /mry/sh/k8s.sh
EOF
    else
        lwarn "非互联网环境暂不支持使用mk8s"
    fi

    chmod +x ${M_BIN}/mk8s
    linfo "mk8s 安装成功"
}

function set_mode() {
    # 测试次数增加到10次，减少误判率
    local ping_count=10
    if ping -c ${ping_count} 8.8.8.8 >/dev/null 2>&1; then
        M_MODE="net"
    else
        M_MODE="lan"
    fi

    add_profile "export M_MODE=${M_MODE}"

    ch=$(mode_ch $M_MODE)
    linfo "检测到当前网络环境为${ch}"
}

function mode_ch() {
    local mode=$1
    if [ "$mode" = "net" ]; then
        echo "互联网"
    else
        echo "局域网"
    fi
}

function set_repo() {
    if [ $ASKME -eq 1 ];then
        read -rp "是否清理repo文件及元数据？(y/n): " flag
        if [ $flag = 'y' ];then
            rm -rf /etc/yum.repos.d/*
            yum clean metadata
        fi
    else
        rm -rf /etc/yum.repos.d/*
        yum clean metadata
    fi

    if [ $M_MODE = "net" ]; then
        wget -P /etc/yum.repos.d/ http://mirrors.aliyun.com/repo/Centos-7.repo
        yum makecache
    else
        linfo "无法连接网络，开始搭建本地repo。"
    fi
}

function init_mry() {
    set_mode
    set_repo
}

function install_all() {
    install_java
    install_python
    install_go
    install_redis
    install_k8s
}

function install_soft() {
    if [ $# -eq 0 ];then
        install_all
    else
        for arg in "$@"
        do
            case $arg in
                redis)
                    install_redis
                    ;;
                k8s)
                    install_k8s
                    ;;
                java)
                    install_java
                    ;;
                python)
                    install_python
                    ;;
                go)
                    install_go
                    ;;
                *)
                    install_all
            esac
        done
    fi

}

# 加载common
source /mry/sh/common.sh
if [ $? -ne 0 ];then
    echo "加载/mry/sh/common.sh失败。"
    exit 1
fi

# 判断是否是centos7
check_system

# 设置询问模式
ASKME=${1:-$ASKME}
linfo "询问模式：${ASKME}"
shift

# 初始化
init_mry

# 安装软件
install_soft $@
