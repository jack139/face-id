
## api 文档

### 1. 全局接口定义

输入参数

| 参数         | 必选 | 类型   | 说明            |
| ------------ | ---- | ------ | --------------- |
| appid        | 是   | string | 后台分配的appid |
| unixtime     | 是   | int    | unix系统时间    |
| signature    | 是   | string | md5签名         |
| 接口输入参数 | 是   |        | 见各接口说明    |

> 1. signature签名算法：`<appid>+<unixtime>+<私钥>+<参数值字符串>` 连接成字符串做SHA256运算得到签名，签名使用大写字母。其中私钥线下提供，与appid配对，**注意：私钥不在api调用中传输**。
> 2. ”参数值字符串”生成规则：将接口输入参数**按参数名字母升序**排列，将所有参数的值转换为字符串后拼接成长字符串，即为“参数值字符串”。

签名示例：

```json
请求参数：
{
    "appid":"THISISTEST",
    "unixtime":1591943910,
    "group_id":"group1",
    "user_id":"gt",
    "face_id":"5ed21b1c262daabe314048f5"
}

参数字符串：
"5ed21b1c262daabe314048f5group1gt"

签名字符串（假设私钥为"xxxxxxxxxxxx"）：
"THISISTEST1591943910xxxxxxxxxxxx5ed21b1c262daabe314048f5group1gt"

SHA256签名结果：
"CB39800C85BEF8E477C6E5A7D1FF474679A6D196C30A64DEC7686EA2536DE767"
```

返回结果

| 参数 | 必选 | 类型   | 说明               |
| ---- | ---- | ------ | ------------------ |
| code | 是   | int    | 接口返回状态代码   |
| msg  | 是   | string | 出错是返回错误说明 |
| data | 否   | json   | 成功时返回结果数据 |

> 成功时：code为200， msg为"success"，data内容见各接口定义；
>
> 出错时：code返回错误代码，具体定义建各接口说明

返回示例

```json
{
    "msg": "success", 
    "code": 200, 
    "data": {
       ...
    }
}
```

全局出错代码

| 编码 | 说明                               |
| ---- | ---------------------------------- |
| 9800 | 无效签名                           |
| 9801 | 签名参数有错误                     |
| 9802 | 调用时间错误，unixtime超出接受范围 |



### 2. 人脸定位

> 检测图片中人脸并返回位置

请求URL

> http://127.0.0.1:5000/face/locate

请求方式

> POST

输入参数

| 参数         | 必选 | 类型   | 说明                                              |
| ------------ | ---- | ------ | ------------------------------------------------- |
| image        | 是   | string | base64编码图片数据                                |
| max_face_num | 否   | int    | 最多定位的人脸数量，默认为1，仅检测面积最大的一个 |

请求示例

```json
{
    "image" : "....", 
    "max_face_num" : 5
}
```

返回结果

| 参数                           | 必选 | 类型  | 说明                 |
| ------------------------------ | ---- | ----- | -------------------- |
| face_num                       | 是   | int   | 检测到的图片人脸数量 |
| locations                      | 是   | array | 人脸位置坐标列表     |
| + [ top, right, bottom, left ] | 是   | array | 人脸位置             |

返回示例

```json
{
    'data': {
        'locations': [
            [95, 337, 147, 285], 
            [107, 233, 159, 181], 
            [266, 437, 302, 401]
        ], 
        'face_num': 3
    }, 
    'msg': 'success', 
    'code': 200
}
```

出错代码

| 编码 | 说明                              |
| ---- | --------------------------------- |
| 9001 | 缺少参数                          |
| 9002 | 图片数据太大，base64数据不大于2MB |
| 9901 | base64编码异常                    |



### 3. 人脸对比

> 比对两张照片中人脸的相似度（1:1），返回相似度分值

请求URL

> http://127.0.0.1:5000/face/verify

请求方式

> POST

输入参数

| 参数   | 必选 | 类型   | 说明               |
| ------ | ---- | ------ | ------------------ |
| image1 | 是   | string | base64编码图片数据 |
| image2 | 是   | string | base64编码图片数据 |

请求示例

```json
{
    "image1": "....", 
    "image2": "....", 
}
```

返回结果

| 参数     | 必选 | 类型    | 说明                      |
| -------- | ---- | ------- | ------------------------- |
| is_match | 是   | boolean | 是否同一人，TRUE 或 FALSE |
| score    | 是   | array   | 相似度得分                |

返回示例

```json
{
    'data': {
        'is_match': True, 
        'score': [0.9765567779541016]
    }, 
    'code': 200, 
    'msg': 'success'
}
```

出错代码

| 编码 | 说明                              |
| ---- | --------------------------------- |
| 9001 | 缺少参数                          |
| 9002 | 图片数据太大，base64数据不大于2MB |
| 9901 | base64编码异常                    |



### 4. 人脸搜索

> 1:N识别，在指定人脸用户分组中，找到最相似的人脸；当指定user_id时，进行1:1验证

请求URL

> http://127.0.0.1:5000/face/search

请求方式

> POST

输入参数

| 参数         | 必选 | 类型   | 说明                                                         |
| ------------ | ---- | ------ | ------------------------------------------------------------ |
| image        | 是   | string | base64编码图片数据                                           |
| group_id     | 否   | string | 在指定分组内搜索，默认为'DEFAULT'分组                        |
| user_id      | 否   | string | 如果提供，则与指定user_id的用户进行比对，相当于1:1验证       |
| mobile_tail  | 否   | string | 手机后4位，如果提供，相当于双因素验证（人脸+手机号后4位）    |
| max_user_num | 否   | int    | 查找后返回的用户数量，返回相似度最高的几个用户，默认为5，最多返回5个 |

请求示例

```json
{
    "image": "....", 
    "group_id": "test", 
}
```

返回结果 

(1) 1:N 时 识别时，入参未提供user_id；双因素验证时，入参提供了mobile_tail

| 参数          | 必选 | 类型   | 说明                                  |
| ------------- | ---- | ------ | ------------------------------------- |
| request_id    | 是   | string | 本次查询请求id（用于结果反馈）        |
| user_list     | 是   | string | 匹配到的用户列表                      |
| + user_id     | 是   | string | 用户id                                |
| + name        | 是   | string | 用户姓名，如果注册时有提供            |
| + mobile_tail | 是   | string | 手机号后4位，如果注册了手机号         |
| + score       | 是   | float  | 相似度得分                            |
| + location    | 是   | array  | 人脸的位置 (top, right, bottom, left) |

返回示例

```json
{
    'data': {
        'user_list': [
            {
                'location': [67, 239, 196, 110], 
                'user_id': 'gt', 
                'mobile_tail': '4665', 
                'score': 0.816467638149025, 
                'name': 'gt'
            }
        ]
    }, 
    'msg': 'success', 
    'code': 200
}
```

(3) 1:1 验证时，入参提供了user_id

| 参数       | 必选 | 类型    | 说明                           |
| ---------- | ---- | ------- | ------------------------------ |
| request_id | 是   | string  | 本次查询请求id（用于结果反馈） |
| is_match   | 是   | boolean | 是否同一人，TRUE 或 FALSE      |
| score      | 是   | array   | 相似度得分                     |

返回示例

```json
{
    'msg': 'success', 
    'code': 200, 
    'data': {
        'is_match': True, 
        'score': [0.8164676381490252, 1.056736673098888]
    }
}
```

出错代码

| 编码 | 说明                              |
| ---- | --------------------------------- |
| 9001 | 缺少参数                          |
| 9002 | 图片数据太大，base64数据不大于2MB |
| 9003 | 参数格式错误                      |
| 9901 | base64编码异常                    |



### 5. 识别结果反馈

> 反馈最近搜索识别的结果是否正确，用于帮助系统提高识别准确率

请求URL

> http://127.0.0.1:5000/face/feedback

请求方式

> POST

输入参数

| 参数       | 必选 | 类型   | 说明                       |
| ---------- | ---- | ------ | -------------------------- |
| request_id | 是   | string | search接口返回的request_id |
| is_correct | 是   | int    | 1 结果正确； 0 结果不正确  |

请求示例

```json
{
    "request_id": "4316142b3b7165b11f9ae91f8f4fb5c4", 
    "is_correct": 1, 
}
```

返回示例

```json
{ 
    'code': 200, 
    'msg': 'success'
}
```

出错代码

| 编码 | 说明             |
| ---- | ---------------- |
| 9001 | 缺少参数         |
| 9002 | request_id不存在 |



### 6.特征库管理

#### (1) 特征库结构

```
|- 特征库
   |- 分组一（group_id）
      |- 用户01（user_id）
         |- 人脸（face_id）
      |- 用户02（user_d）
         |- 人脸（face_id）
         |- 人脸（face_id）
         ....
       ....
   |- 分组二（group_id）
   |- 分组三（group_id）
   ....
```



#### (2) 人脸注册

> 向特征库中添加人脸，当user_id在库中已经存在时，新注册的图片会追加到该user_id下

请求URL

> http://127.0.0.1:5000/facedb/face/reg

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                                                         |
| -------- | ---- | ------ | ------------------------------------------------------------ |
| image    | 是   | string | base64编码图片数据                                           |
| group_id | 否   | string | 用户分组id，默认为'DEFAULT'分组                              |
| user_id  | 是   | string | 用户id（由数字、字母、下划线组成），必须唯一，建议使用身份证号码 |
| name     | 是   | string | 用户姓名                                                     |
| mobile   | 否   | string | 手机号码                                                     |
| memo     | 否   | string | 用户其他信息，例如：姓名                                     |

请求示例

```json
{
    'image': '...',
    'group_id': 'group1',
    'user_id': 'gt2',
    'name': 'gt',
}
```

返回结果

| 参数    | 必选   | 类型             | 说明 |
| ------- | ------ | ---------------- | ---- |
| face_id | string | 人脸特征唯一标识 |      |

返回示例

```json
{
    'code': 200, 
    'msg': 'success',
    'data': {
        'face_id': '5ed7725e0d72875f136cdbbe'
    }, 
}
```

出错代码

| 编码 | 说明                              |
| ---- | --------------------------------- |
| 9001 | 缺少参数                          |
| 9002 | 图片数据太大，base64数据不大于2MB |
| 9901 | base64编码异常                    |
| 9003 | 未定位到人脸                      |
| 9004 | 用户组不存在                      |
| 9005 | user_id已存在                     |



#### (3) 人脸更新

> 更新特征库中指定用户下的人脸信息，使用新图替换库中该user_id下所有图片，若user_id不存在则报错

请求URL

> http://127.0.0.1:5000/facedb/face/update

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                               |
| -------- | ---- | ------ | ---------------------------------- |
| image    | 否   | string | base64编码图片数据，不提供则不修改 |
| group_id | 否   | string | 用户分组id，默认为'DEFAULT'分组    |
| user_id  | 是   | string | 用户id                             |
| mobile   | 否   | string | 手机号码，不提供则不修改           |
| name     | 否   | string | 用户姓名，不提供则不修改           |
| memo     | 否   | string | 用户其他信息，不提供则不修改       |

请求示例

```json
{
    'image': '...',
    'group_id': 'group1',
    'user_id': 'gt2',
}
```

返回结果

| 参数    | 必选   | 类型             | 说明                                |
| ------- | ------ | ---------------- | ----------------------------------- |
| face_id | string | 人脸特征唯一标识 | 只更新用户信息，不更新图片，则返回0 |

返回示例

```json
{
    'code': 200, 
    'msg': 'success', 
    'data': {
        'face_id': '5ed77468b643e4aa5b27cf49'
    }
}
```

出错代码

| 编码 | 说明                              |
| ---- | --------------------------------- |
| 9001 | 缺少参数                          |
| 9002 | 图片数据太大，base64数据不大于2MB |
| 9901 | base64编码异常                    |
| 9003 | 未定位到人脸                      |
| 9004 | user_id不存在                     |



#### (4) 人脸删除

> 删除指定用户的某张人脸特征数据

请求URL

> http://127.0.0.1:5000/facedb/face/remove

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                            |
| -------- | ---- | ------ | ------------------------------- |
| group_id | 否   | string | 用户分组id，默认为'DEFAULT'分组 |
| user_id  | 是   | string | 用户id                          |
| face_id  | 是   | string | 人脸特征标识                    |

请求示例

```shell
curl -X POST --data '{"group_id":"group1","user_id":"gt","face_id":"5ed21b1c262daabe314048f5"}' http://127.0.0.1:5000/facedb/face/remove
```

返回结果

| 参数       | 必选 | 类型   | 说明                          |
| ---------- | ---- | ------ | ----------------------------- |
| type | 是   | string | 成功返回SUCCESS |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "type": "SUCCESS"
    }
}
```

出错代码

| 编码 | 说明                    |
| ---- | ----------------------- |
| 9001 | 缺少参数                |
| 9002 | user_id不存在           |
| 9003 | 用户没有face_id人脸数据 |



#### (5) 用户信息查询

> 查询特征库中某个用户的详细信息

请求URL

> http://127.0.0.1:5000/facedb/user/info

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                            |
| -------- | ---- | ------ | ------------------------------- |
| group_id | 否   | string | 用户分组id，默认为'DEFAULT'分组 |
| user_id  | 是   | string | 用户id                          |

请求示例

```shell
curl -X POST --data '{"group_id":"test","user_id":"obama"}' http://127.0.0.1:5000/facedb/user/info
```

返回结果

| 参数      | 必选 | 类型   | 说明                           |
| --------- | ---- | ------ | ------------------------------ |
| group_id  | 是   | string | 分组id                         |
| user_id   | 是   | string | 用户id                         |
| name      | 是   | string | 用户姓名                       |
| mobile    | 否   | string | 手机号码，如果注册时有提供     |
| memo      | 否   | string | 用户其他信息，如果注册时有提供 |
| image_num | 是   | int    | 此user_id下已注册的照片数量    |
| ctime     | 是   | string | 注册时间                       |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "image_num": 1, 
        "group_id": "test", 
        "user_id": "obama", 
        "name": "obama", 
        "memo": "", 
        "ctime": "2020-05-30 16:36:40", 
        "mobile": ""
    }
}
```

出错代码

| 编码 | 说明          |
| ---- | ------------- |
| 9001 | 缺少参数      |
| 9002 | user_id不存在 |



#### (6) 获取用户人脸列表

> 获取某个用户组中的全部人脸列表

请求URL

> http://127.0.0.1:5000/facedb/user/face_list

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                            |
| -------- | ---- | ------ | ------------------------------- |
| group_id | 否   | string | 用户分组id，默认为'DEFAULT'分组 |
| user_id  | 是   | string | 用户id                          |

请求示例

```shell
curl -X POST --data '{"group_id":"test","user_id":"gt"}' http://127.0.0.1:5000/facedb/user/face_list
```

返回结果

| 参数      | 必选 | 类型  | 说明                  |
| --------- | ---- | ----- | --------------------- |
| face_list | 是   | array | 人脸特征face_id的列表 |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "face_list": [
            "5ed21b1c262daabe314048f5", 
            "5ed21b1d262daabe314048f6"
        ]
    }
}
```

出错代码

| 编码 | 说明          |
| ---- | ------------- |
| 9001 | 缺少参数      |
| 9002 | user_id不存在 |



#### (7) 获取用户列表

> 查询指定用户组中的用户列表

请求URL

> http://127.0.0.1:5000/facedb/user/list

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                            |
| -------- | ---- | ------ | ------------------------------- |
| group_id | 否   | string | 用户分组id，默认为'DEFAULT'分组 |
| start    | 否   | int    | 起始位置，默认为0               |
| length   | 否   | int    | 返回数量，默认100，最大1000     |

请求示例

```shell
curl -X POST --data '{"group_id":"test"}' http://127.0.0.1:5000/facedb/user/list
```

返回结果

| 参数      | 必选 | 类型  | 说明            |
| --------- | ---- | ----- | --------------- |
| user_list | 是   | array | 用户user_id列表 |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "user_list": [
            "biden", 
            "obama", 
            "alex_lacamoire", 
            "gt", 
            "zhiqiang", 
            "obama2", 
            "kit_harington", 
            "obama1", 
            "rose_leslie"
        ]
    }
}
```

出错代码

| 编码 | 说明 |
| ---- | ---- |
|      |      |



#### (8) 复制用户

> 将指定用户复制到另外的人脸组

请求URL

> http://127.0.0.1:5000/facedb/user/copy

请求方式

> POST

输入参数

| 参数         | 必选 | 类型   | 说明                 |
| ------------ | ---- | ------ | -------------------- |
| user_id      | 是   | string | 用户id               |
| src_group_id | 是   | string | 从指定组里复制信息   |
| dst_group_id | 是   | string | 需要添加用户的分组id |

请求示例

```shell
curl -X POST --data '{"user_id":"gt","src_group_id":"test","dst_group_id":"group1"}' http://127.0.0.1:5000/facedb/user/copy
```

返回结果

| 参数 | 必选 | 类型   | 说明            |
| ---- | ---- | ------ | --------------- |
| type | 是   | string | 成功返回SUCCESS |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "type": "SUCCESS"
    }
}
```

出错代码

| 编码 | 说明                      |
| ---- | ------------------------- |
| 9001 | 缺少参数                  |
| 9002 | user_id不存在             |
| 9003 | user_id在目的用户组已存在 |



#### (9) 删除用户

> 删除指定用户

请求URL

> http://127.0.0.1:5000/facedb/user/remove

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                            |
| -------- | ---- | ------ | ------------------------------- |
| group_id | 否   | string | 用户分组id，默认为'DEFAULT'分组 |
| user_id  | 是   | string | 用户id                          |

请求示例

```shell
curl -X POST --data '{"user_id":"gt","group_id":"group1"}' http://127.0.0.1:5000/facedb/user/remove
```

返回结果

| 参数 | 必选 | 类型   | 说明            |
| ---- | ---- | ------ | --------------- |
| type | 是   | string | 成功返回SUCCESS |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "type": "SUCCESS"
    }
}
```

出错代码

| 编码 | 说明          |
| ---- | ------------- |
| 9001 | 缺少参数      |
| 9002 | user_id不存在 |



#### (10) 创建用户组

> 创建一个新的用户组，如果用户组已存在 则返回错误

请求URL

> http://127.0.0.1:5000/facedb/group/new

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明                                               |
| -------- | ---- | ------ | -------------------------------------------------- |
| group_id | 是   | string | 用户组id，标识一组用户（由数字、字母、下划线组成） |

请求示例

```shell
curl -X POST --data '{"group_id":"group1"}' http://127.0.0.1:5000/facedb/group/new
```

返回结果

| 参数 | 必选 | 类型   | 说明            |
| ---- | ---- | ------ | --------------- |
| type | 是   | string | 成功返回SUCCESS |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "type": "SUCCESS"
    }
}
```

出错代码

| 编码 | 说明           |
| ---- | -------------- |
| 9001 | 缺少参数       |
| 9002 | group_id已存在 |



#### (11) 删除用户组

> 删除指定用户组，如果组不存在 则返回错误。**组内用户将一同删除，需谨慎操作！**

请求URL

> http://127.0.0.1:5000/facedb/group/remove

请求方式

> POST

输入参数

| 参数     | 必选 | 类型   | 说明       |
| -------- | ---- | ------ | ---------- |
| group_id | 是   | string | 用户分组id |

请求示例

```shell
curl -X POST --data '{"group_id":"group1"}' http://127.0.0.1:5000/facedb/group/remove
```

返回结果

| 参数 | 必选 | 类型   | 说明            |
| ---- | ---- | ------ | --------------- |
| type | 是   | string | 成功返回SUCCESS |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "type": "SUCCESS"
    }
}
```

出错代码

| 编码 | 说明           |
| ---- | -------------- |
| 9001 | 缺少参数       |
| 9002 | group_id不存在 |



#### (12) 获取用户组列表

> 查询特征库中用户组的列表

请求URL

> http://127.0.0.1:5000/facedb/group/list

请求方式

> POST

输入参数

| 参数   | 必选 | 类型 | 说明                        |
| ------ | ---- | ---- | --------------------------- |
| start  | 否   | int  | 起始位置，默认为0           |
| length | 否   | int  | 返回数量，默认100，最大1000 |

请求示例

```shell
curl -X POST --data '{}' http://127.0.0.1:5000/facedb/group/list
```

返回结果

| 参数       | 必选 | 类型  | 说明               |
| ---------- | ---- | ----- | ------------------ |
| group_list | 是   | array | 用户组group_id列表 |

返回示例

```json
{
    "code": 200, 
    "msg": "success", 
    "data": {
        "user_list": [
            "test", 
            "train3", 
            "train2", 
            "test2", 
            "test3"
        ]
    }
}
```

出错代码

| 编码 | 说明 |
| ---- | ---- |
|      |      |

