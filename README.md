# ZWU 自动打卡程序

## 为什么自动打卡

不为什么
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

## 截图设置

### ！！***程序会自动获取前一天的截图放在今天，screenshot中的内容用于备用***

将件康马截图放在screenshot1文件夹内，使用`学号+jpeg`来进行命名，

如果截图的文件格式不是jpeg也不用担心，直接修改成jpeg如果能打开就没问题

注意：没有将图片放在screenshot文件夹内, 也没有正常获取的昨天的截图，也可以正常打卡，不过图片会空着，打卡后端不会验证是否上传了图片。

多账号不适合在持续集成服务上使用，因为多用户之间有随机时间间隔，所耗时间较长。
