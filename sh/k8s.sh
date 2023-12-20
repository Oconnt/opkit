#!/bin/bash

# 时间服务器（根据具体环境修改！^）
TIME_SERVER="ntp1.aliyun.com"

# kubeadm镜像仓库
KADM_IMAGE_REPO="registry.cn-hangzhou.aliyuncs.com\/google_containers"

# 安装位置
INSTALL_DIR="/usr/local/"
# kubeadm配置位置
KADM_YML="/etc/kubeadm/kubeadm.yml"
# calico配置位置
CALICO_YAML="/etc/calico/calico.yaml"

# containerd配置
CONTAINERD_CONFIG_FILE="/etc/containerd/config.toml"
# 初始化完成标识
ADJ_CONF_TMP="/tmp/adj_conf.tmp"
# cni安装完成标识
CNI_INS_TMP="/tmp/cni_install.tmp"
# k8s组件安装完成标识
K8S_INS_TMP="/tmp/k8s_install.tmp"
# kubeadm初始化成功标识
KADM_INIT_TMP="/tmp/kadm_init.tmp"

TMP_SET=($ADJ_CONF_TMP $CNI_INS_TMP $K8S_INS_TMP $KADM_INIT_TMP)

# master节点（根据具体ip修改！^）
MASTER_NODE="192.168.1.121"
NET_DOMAIN=$(echo $MASTER_NODE | cut -d '.' -f 1-2)
# node节点（根据具体ip修改！）
NODES=("192.168.1.122" "192.168.1.123")

# 默认join token（失效后需要重新申请！^）
DEFAULT_JOIN_TOKEN="abcdef.0123456789abcdef"

# 版本号定义（根据版本号修改，请确保各组件版本兼容问题！^）
K8S_VERSION="1.27.4-0"
CONTAINERD_VERSION="1.7.3"
RUNC_VERSION="1.1.7"
CNI_VERSION="1.3.0"
CALICO_VERSION="3.26.1"

# 软件包下载地址（^）
CTR_URL="https://github.com/containerd/containerd/releases/download/v${CONTAINERD_VERSION}"
CTR_SERVICE_URL="https://raw.githubusercontent.com/containerd/containerd/main/containerd.service"
RUNC_URL="https://github.com/opencontainers/runc/releases/download/v${RUNC_VERSION}"
CNI_URL="https://github.com/containernetworking/plugins/releases/download/v${CNI_VERSION}"
CALICO_YAML_URL="https://raw.githubusercontent.com/projectcalico/calico/v${CALICO_VERSION}/manifests/calico.yaml"


function arch() {
    os_type=$(uname -p)
    if [ $os_type = 'x86_64' ]; then
        arch='amd64'
    else
        echo "arm环境尚未测试，谨慎使用！！！！！！！！！！！！"
        arch='arm64'
    fi

    echo $arch
}

function get_node_ip() {
    echo $(hostname -I | awk '{print $1}')
}

function is_master() {
    if [ "$(get_node_ip)" = "$MASTER_NODE" ];then
        echo 1
    else
        echo 0
    fi
}

function install_containerd() {
    # 安装containerd
    echo "开始安装containerd..."
    local ctrd_tar="containerd-${CONTAINERD_VERSION}-linux-${1}.tar.gz"
    local ctrd_path=${INSTALL_DIR}${ctrd_tar}
    if [ ! -e ${ctrd_path} ];then
        echo "${ctrd_path}不存在，开始下载containerd..."
        wget -P ${INSTALL_DIR} ${CTR_URL}/${ctrd_tar}
        if [ $? -ne 0 ]; then
            echo "containerd下载失败, 请检查网络或配置代理加速！"
            exit 1
        fi
    fi
    tar Cxzvf ${INSTALL_DIR} ${ctrd_path}
    containerd -v
    if [ $? -eq 0 ];then
        echo "containerd安装成功！"
        rm -f ${ctrd_path}
    else
        echo "containerd安装失败，请检查包结构是否正确后重试！"
        exit 1
    fi

    # 生成containerd配置
    mkdir -p /etc/containerd
    containerd config default > $CONTAINERD_CONFIG_FILE
    sed -i "s/SystemdCgroup = false/SystemdCgroup = true/g" $CONTAINERD_CONFIG_FILE
    sed -i "s/registry.k8s.io/registry.aliyuncs.com\/google_containers/g" $CONTAINERD_CONFIG_FILE

    if [ ! -e /usr/local/lib/systemd/system/containerd.service ];then
        mkdir -p /usr/local/lib/systemd/system
        wget -P /usr/local/lib/systemd/system ${CTR_SERVICE_URL}
        if [ $? -ne 0 ];then
            # 由于网络问题无法下载时，手动编辑containerd.service
            cat << EOF >/usr/local/lib/systemd/system/containerd.service
# Copyright The containerd Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
#uncomment to fallback to legacy CRI plugin implementation with podsandbox support.
#Environment="DISABLE_CRI_SANDBOXES=1"
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5
# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity
LimitNOFILE=infinity
# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
EOF
        fi
    fi

    systemctl daemon-reload
    systemctl enable --now containerd
    if [ $? -eq 0 ];then
        echo "containerd服务已启动！"
    fi
}

function install_runc() {
    echo "开始安装runc..."
    local runc="runc.${1}"
    local runc_path="${INSTALL_DIR}${runc}"
    if [ ! -e ${runc_path} ];then
        echo "${runc_path}不存在，开始下载runc..."
        wget -P ${INSTALL_DIR} ${RUNC_URL}/${runc}
        if [ $? -ne 0 ]; then
            echo "runc下载失败, 请检查网络或配置代理加速！"
            exit 1
        fi
    fi
    install -m 755 "${runc_path}" ${INSTALL_DIR}sbin/runc
    rm -f "${runc_path}"
}

function install_cni() {
    echo "开始安装cni插件..."
    local cni="cni-plugins-linux-${1}-v${CNI_VERSION}.tgz"
    local cni_path="${INSTALL_DIR}${cni}"
    if [ ! -e "${cni_path}" ]; then
        echo "${cni_path}不存在，开始下载cni插件"
        wget -P ${INSTALL_DIR} ${CNI_URL}/cni-plugins-linux-${1}-v${CNI_VERSION}.tgz
        if [ $? -ne 0 ]; then
            echo "cni插件下载失败, 请检查网络或配置代理加速！"
            exit 1
        fi
    fi
    tar Cxzvf ${INSTALL_DIR}bin ${INSTALL_DIR}cni-plugins-linux-${1}-v${CNI_VERSION}.tgz

    if [ $? -eq 0 ]; then
        touch ${CNI_INS_TMP}
    fi
    rm -f ${INSTALL_DIR}cni-plugins-linux-${arch}-v${CNI_VERSION}.tgz

}

function install_k8s() {
    yum clean all
    # 配置k8s源（^）
    cat <<- 'EOF' > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
        http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
exclude=kubelet kubeadm kubectl
EOF
    yum makecache
    yum install -y kubelet-${K8S_VERSION} kubeadm-${K8S_VERSION} kubectl-${K8S_VERSION} --disableexcludes=kubernetes
    if [ $? -eq 0 ]; then
        touch ${K8S_INS_TMP}
    fi
}

function install_inf() {
    local arch=$(arch)

    echo "开始下载containerd，runc，cni及k8s组件，如果因网络问题下载失败请手动下载到${INSTALL_DIR}后重试！"
    if ! systemctl is-active --quiet containerd || [ "$(containerd -v | awk '{print $3}')" != "v${CONTAINERD_VERSION}" ];then
        install_containerd ${arch}
    fi

    # 安装runc
    if [ ! -e ${INSTALL_DIR}sbin/runc ];then
        install_runc ${arch}
    fi

    # 安装cni
    if [ ! -e ${CNI_INS_TMP} ];then
        install_cni ${arch}
    fi

    # 安装k8s组件
    if [ ! -e ${K8S_INS_TMP} ];then
        install_k8s
    fi
    
    check_install
}

function check_install() {
    if ! systemctl is-active --quiet containerd; then
        echo "containerd未安装！"
        exit 1
    elif [ ! -e /usr/local/sbin/runc ]; then
        echo "runc未安装！"
        exit 1
    elif [ ! -e /usr/local/bin/vlan ]; then
        echo "cni未安装！"
        exit 1
    elif [ ! -e /usr/bin/kubelet ]; then
        echo "kubeadm未安装！"
        exit 1
    elif [ ! -e /usr/bin/kubeadm ]; then
        echo "kubeadm未安装！"
        exit 1
    elif [ ! -e /usr/bin/kubectl ]; then
        echo "kubectl未安装！"
        exit 1
    else
        echo "基础组件安装成功！"
        return 1
    fi

}

function pull_image() {
    echo "开始拉取镜像${1}..."
    ctr i list | grep -q "${1}"
    if [ $? -ne 0 ];then
        ctr i pull "${1}"
        echo "镜像${1}拉取成功！"
    else
        echo "镜像${1}已存在！"
    fi


}

function create_k8s() {
    # 设置kubeadm配置
    local kadm_etc_dir=$(dirname ${KADM_YML})
    mkdir -p "${kadm_etc_dir}"

    kubeadm config print init-defaults > ${KADM_YML}
    sed -i "s/advertiseAddress: 1.2.3.4/advertiseAddress: ${MASTER_NODE}/g" ${KADM_YML}
    sed -i "s/serviceSubnet: 10.96.0.0\/12/serviceSubnet: ${NET_DOMAIN}.0.0\/12/g" ${KADM_YML}
    sed -i "s/imageRepository: registry.k8s.io/imageRepository: ${KADM_IMAGE_REPO}/g" ${KADM_YML}

    local hn=$(hostname)
    sed -i "s/name: node/name: ${hn}/g" ${KADM_YML}

    # 向内核中加载模块
    modprobe br_netfilter
    # 开启ipv4转发
    if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf;then
        echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
        sysctl -p
    fi

    if [ ! -e ${KADM_INIT_TMP} ]; then
        if [ "$(is_master)" -eq 1 ];then
            # 手动拉取镜像
            for img in $(kubeadm config images list --config ${KADM_YML}) ;
            do
                pull_image "${img}"
            done

            kubeadm init --config=${KADM_YML} --upload-certs
            if [ $? -ne 0 ]; then
                echo "kubeadm初始化失败!"
                exit 1
            else
                touch ${KADM_INIT_TMP}
            fi

            mkdir -p $HOME/.kube
            sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
            sudo chown $(id -u):$(id -g) $HOME/.kube/config

            # 环境变量设置
            export KUBECONFIG=/etc/kubernetes/admin.conf

            # 同步worker节点k8s-admin信息
            for node in "${NODES[@]}"
            do
                scp /etc/kubernetes/admin.conf root@${node}:/etc/kubernetes/admin.conf
                ssh root@${node} "echo KUBECONFIG=/etc/kubernetes/admin.conf >> /etc/environment && source /etc/environment && exit"
            done
        else
            kubeadm join "${MASTER_NODE}":6443 --token="${DEFAULT_JOIN_TOKEN}" --discovery-token-unsafe-skip-ca-verification
            if [ $? -ne 0 ];then
                node_ip=$(get_node_ip)
                echo "备节点：${node_ip} 加入主节点：${MASTER_NODE}失败，请检查master节点拉起情况或默认token是否过期"
                exit 1
            fi

            systemctl enable --now kubelet
        fi
    fi

}

function create_calico_pod() {
    local calico_etc_dir=$(dirname ${CALICO_YAML})
    mkdir -p "${calico_etc_dir}"
    if [ ! -e ${CALICO_YAML} ]; then
        curl -O ${CALICO_YAML} "${CALICO_YAML_URL}"
        if [ $? -ne 0 ];then
            echo "calico.yaml 拉取失败，请手动拉取到/etc/calico/下重试！"
            exit 1
        fi
    fi

    # 拉取镜像
    for img in $(cat ${CALICO_YAML} | grep docker.io | awk {'print $2'} | uniq)
    do
        pull_image "${img}"
    done

    kubectl apply -f ${CALICO_YAML}

    if [ $? -eq 0 ]; then
        echo "calico deployment创建成功!, 请执行'kubectl get pod -n kube-system' 查看"
    fi

}

function adj_conf() {
    if [ -e ${ADJ_CONF_TMP} ];then
        return 1
    fi

    # 配置hosts
    if ! grep -q "$MASTER_NODE k8s-master" /etc/hosts;then
        echo "$MASTER_NODE k8s-master" >> /etc/hosts
    fi

    for index in "${!NODES[@]}"
    do
        sign=$((index + 1))
        if ! grep -q "${NODES[$index]} k8s-node$sign" /etc/hosts;then
            echo "${NODES[$index]} k8s-node$sign" >> /etc/hosts
        fi
    done

    # 生成密钥建立ssh互信，master和worker节点的互信，worker节点间不建立互信
    pub_key="${HOME}/.ssh/id_rsa.pub"
    if [ ! -e "$pub_key" ];then
        ssh-keygen -t rsa
    fi

    if [ "$(is_master)" -eq 1 ];then
        for node in "${NODES[@]}"
        do
            # 将公钥复制到目标主机
            ssh-copy-id -i "$pub_key" "$node"
        done
    else
        ssh-copy-id -i "$pub_key" "$MASTER_NODE"
    fi

    # 关闭firewalld dnsmasq NetworkManager
    if systemctl is-active --quiet firewalld; then
        systemctl disable --now firewalld
    fi

    if systemctl is-active --quiet dnsmasq; then
        systemctl disable --now dnsmasq
    fi

    if systemctl is-active --quiet NetworkManager; then
        systemctl disable --now NetworkManager
    fi

    setenforce 0
    sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/sysconfig/selinux
    sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

    # 关闭swap交换
    swapoff -a
    sed -ri 's/.*swap.*/#&/' /etc/fstab

    # 同步时间
    yum -y install ntpdate
    ntpdate $TIME_SERVER

    if [ $? -ne 0 ]; then
        echo "系统配置失败失败，请使用k8s.sh 1来追踪报错!"
        exit 1
    else
        # 创建临时文件保证短时间内不会重复执行
        touch ${ADJ_CONF_TMP}
    fi
}

function clean_tmp_file() {
    file_string=$(IFS=' ' ; echo "${TMP_SET[*]}")
    rm -f ${file_string}
}

function main() {
    adj_conf
    install_inf
    create_k8s
    create_calico_pod
    clean_tmp_file
}

function sex_main() {
    set -x
    main
    set +x
}


echo "========================================================================"
echo "=                     k8s集群一键部署脚本                                 ="
echo "=      请注意，当前脚本只支持centos7系统！局域网环境请修改为私有镜像源后再执行！    ="
echo "=      请注意，修改集群ip后再执行！                                         ="
echo "========================================================================"
if [ "$1" = 1 ];then
    sex_main
else
    main
fi