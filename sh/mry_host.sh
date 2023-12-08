#!/bin/bash

MRY_PROFILE="/etc/profile.d/mry_profile.sh"
DOWNLOAD_FILE="/mry/common/download"
MRY_DIR=(
    "/mry"
    "/mry/bin"
    "/mry/lib"
    "/mry/sh"
    "/mry/etc"
    "/mry/resource"
    "/mry/log"
)

function mry_profile() {
    cat <<- 'EOF' > $MRY_PROFILE
alias h="history"
alias md="mkdir"
alias rd="rmdir"
alias vi="vim"
alias u="whoami"
alias g="groups"
alias lsp="lsof -p"
alias lsi="lsof -i"
alias cpr="cp -r"
alias rmrf="rm -rf"
alias rmf="rm -f"
alias sctl="systemctl"

HISTSIZE=1000
TMOUT=36000

export h md rd vi u g lsp lsi cpr rmrf rmf sctl HISTSIZE TMOUT PATH="$PATH:/mry/bin"
EOF
    chmod +rw $MRY_PROFILE
    source $MRY_PROFILE
}

function set_ps1() {
    echo 'export PS1='\''[\u@\h \W \[\033[01;$(($?==0?32:31))m\]$([[ $? == 0 ]] && echo "o" || echo "x")\[\033[00m\] ] '\'' '  >> $MRY_PROFILE
    source $MRY_PROFILE
}

function md_mry() {
    for dir in "${MRY_DIR[@]}"
    do
        mkdir -p $dir
    done
}

function download() {
    if [ -e $DOWNLOAD_FILE ]; then
        while read line
        do
            wget -P /mry/resource/ $line
        done < $DOWNLOAD_FILE
    fi
}

function install_env() {
    mry_profile
    set_ps1
}

function main() {
    md_mry
    install_env
}

main
