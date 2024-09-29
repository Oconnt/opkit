# opkit

## shell工具

### 拉取sh脚本方法

curl -O -s https://raw.githubusercontent.com/Oconnt/opkit/master/sh/mry_host.sh && chmod +x mry_host.sh && source mry_host.sh



### install.sh脚本使用方法

作用：快速搭建软件环境

**参数一：ASKME**
作用：是否询问，若为0则等价于yum -y

**其他参数（可选）：java python go等**
指定需要安装的脚本

示例：
install.sh 0 python
install.sh 1 java python go



**mjava，mpy，mgo使用方法：**

执行命令后添加版本号，若报错则可能为版本号不存在，如3.12版本，需细化到3.12.0



### ca.sh脚本使用方法

作用：快速生成证书、公私钥



### k8s.sh脚本使用方法

作用：快速搭建k8s



## opkit命令行

### opkitctl

```shell
[root@mry-host ~ o ] opkitctl -h
Usage: opkitctl [OPTIONS] COMMAND [ARGS]...

  The entry point for all system operation and maintenance work, which can
  access various sub functions through sub commands

Options:
  -v, --version  Get the opkit tool version number
  -h, --help     Help info

Commands:
  grab     Based on the original packet capture tool encapsulation, add...
  monitor  Monitor the resource usage and utilization rate of the system...
  trace    Process tracking command, which allows opkit tools to easily...
```

主命令行，主要输出版本和帮助信息 

### grab

```shell
[root@mry-host ~ o ] opkitctl grab -h
Usage: opkitctl grab [OPTIONS]

  Based on the original packet capture tool encapsulation, add processes and
  namespaces as filtering criteria for filtering

Options:
  -c, --count INTEGER       Packet count, default 0
  -w, --worker INTEGER      Specify worker thread, default 1
  -f, --filters TEXT        Packet filter rule
  -i, --iface TEXT          Network card
  -p, --pid TEXT            If the PID is set, packets will be captured from
                            the port that the specified process is listening
                            to
  -r, --protocol TEXT       communication protocol
  -s, --sip TEXT            Filtering criteria, which will be converted to the
                            src host of the BPF filtering rule
  -d, --dip TEXT            Filtering criteria, which will be converted to the
                            dst host of the BPF filtering rule
  -S, --sport TEXT          Filtering criteria, which will be converted to the
                            src port of the BPF filtering rule
  -D, --dport TEXT          Filtering criteria, which will be converted to the
                            dst port of the BPF filtering rule
  -n, --namespace TEXT      Setting a network namespace will filter all
                            process packages under this namespace
  -m, --mark TEXT           Filter conditional connectors, and or or
  -k, --worker_params TEXT  Multi threading parameters
  -t, --timeout INTEGER     Packet capture timeout exit time, default 30s
  -o, --out TEXT            The output method after capturing the package,
                            default output log, see kit.grab.handle for
                            details
  -I, --include TEXT        Include column, separated by commas
  -E, --exclude TEXT        Exclude column, separated by commas
  -h, --help                Help info
```

抓包，功能类似tcpdump

### monitor

```
[root@mry-host ~ o ] opkitctl monitor -h
Usage: opkitctl monitor [OPTIONS]

  Monitor the resource usage and utilization rate of the system or process,
  and if no parameters are passed in, output the current operating system's
  resource usage rate by default

Options:
  -P, --part TEXT  Default load monitor, multiple separated by commas
  -p, --pid TEXT   Output monitoring information for the specified process
  -i, --info       Output process info, Need to be used in conjunction with -
                   p
  -h, --help       Help info
```

轻型监控，主要是针对进程监控cpu，内存等

### trace

```

```

基于gdb实现程序注入功能，可实现性能探测