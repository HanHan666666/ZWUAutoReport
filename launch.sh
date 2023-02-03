# 此脚本可以用于在持续集成服务中启动

pip3 install requests yagmail[all]
# 版本号自行修改，用于解决多版本Python，会使pip安装无效
# 3.10以上的Python发邮件可能报错，原因是你的服务商用了上古TLS协议，还不更新
python3.7 ./main.py