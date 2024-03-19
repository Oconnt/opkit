# opkit

## shell

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