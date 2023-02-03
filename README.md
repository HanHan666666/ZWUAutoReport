# ZWU 自动打卡程序

## 为什么自动打卡

社会已经全面放开，继续健康打卡毫无意义，完全是形式主义，官僚主义的产物。

## 账户设置

程序会优先在当前目录下读取`config.json`加载需要打卡的用户(需要手动创建)

如果没有找到`config.json`则会在环境变量`config`中读取，该项主要应用于在持续集成服务中使用。

如果不需要发送邮件，将Email设置为notSend

`AdminEmail`用于设置你的邮箱，程序执行结束后会将log以邮件的的形式发送到你的邮箱

### `config.json`

```json
{
    "account": [
        {
            "Account": "1232131231",
            "Name": "张三",
            "Password": "aazzxx",
            "Email": "example@outlook.com"
        },
        {
            "Account": "202005552",
            "Name": "李四",
            "Password": "lpassword",
            "Email": "example@qq.com"
        },
        {
            "Account": "2020056565",
            "Name": "Jack",
            "Password": "shshshhs",
            "Email": "notSend"
        }
    ],
    "STMP": {
        "enable": false,
        "Host": "smtpdm.example.com",
        "Port": 465,
        "Username": "noreply@mail.example.com",
        "Password": "asasasjaksjaksa",
        "Sender": "李华"
    },
    "AdminEmail": "admin@outlook.com"
}

```

### 手动设置环境变量

直接把json文本设置成环境变量

```shell
export config=$(cat ./config.json)
```

多账号不适合在持续集成服务上使用，因为多用户之间有随机时间间隔，所耗时间较长。

如果没有随机间隔，脚本打卡行为特征过于明显
