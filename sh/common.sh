#!/bin/bash

M_MODE="lan"

MRY_DIR="/mry"
M_BIN="$MRY_DIR/bin"
M_LIB="$MRY_DIR/lib"
M_OPT="$MRY_DIR/opt"
M_RESOURCE="$MRY_DIR/resource"
MRY_PROFILE="/etc/profile.d/mry_profile.sh"

CHECK_FILE_LIST=(
  $MRY_PROFILE
  $M_BIN
  $M_LIB
  $M_OPT
  $M_RESOURCE
)

function source_profile() {
    source $MRY_PROFILE
}

function add_profile() {
    if grep -q "$1" "$MRY_PROFILE"; then
        lwarn "环境变量已存在！"
    else
        echo "$1" >> $MRY_PROFILE
        source_profile
    fi

}

function log() {
    local level=$1
    local msg="$2"

    local color
    if [ $level = "debug" ]; then
        color='\033[1;30m'
    elif [ $level = "info" ]; then
        color=''
    elif [ $level = "warn" ]; then
        color='\033[1;33m'
    elif [ $level = "error" ]; then
        color='\033[0;31m'
    else
        echo "Invalid log level: $level"
        return 1
    fi

    local reset_color='\033[0m'

    echo -en $color
    echo -n "$msg"
    echo -e $reset_color
}

function ldebug() { log debug "$1"; }
function linfo() { log info "$1"; }
function lwarn() { log warn "$1"; }
function lerror() { log error "$1"; }

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

function check_resource_integrity() {
    # 检查文件完整性
    for f in "${CHECK_FILE_LIST[@]}"
    do
        if [ ! -e "$f" ]; then
            return
        fi
    done
}

function check_system() {
    linfo "开始检测系统版本...."
    if [[ -n $(find /etc -name "redhat-release") ]] || grep </proc/version -q -i "centos"; then
        # 检测系统版本号
        centos_version=$(rpm -q centos-release | awk -F "[-]" '{print $3}' |
        awk -F "[.]" '{print $1}')
        if [[ -z "${centos_version}" ]] && grep </etc/centos-release "release 8"; then
            centos_version=8
        fi
        release="centos"
    fi

    if [[ -z ${release} ]] || [[ ${centos_version} != 7 ]]; then
        lwarn "目前只支持red hat centos7，程序退出！"
    else
        linfo "检测完成"
    fi

}
