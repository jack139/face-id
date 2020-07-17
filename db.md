
## 数据结构定义

### 1.特征库结构

```
|- 特征库
   |- 分组一（group_id）
      |- 用户01（user_id）
         |- 人脸（faceid）
      |- 用户02（user_d）
         |- 人脸（faceid）
         |- 人脸（faceid）
         ....
       ....
   |- 分组二（group_id）
   |- 分组三（group_id）
   ....
```



### 2. 表结构

#### (1) groups

> 用户分组信息

| 字段名   | 描述     | 类型   | 可空 | 索引 | 备注 |
| -------- | -------- | ------ | ---- | ---- | ---- |
| group_id | 分组id   | string |      | Y    |      |
| memo     | 描述     | string | Y    |      |      |
| time_t   | 创建时间 | string |      |      |      |



#### (2) users

> 用户分组信息

| 字段名     | 描述         | 类型   | 可空 | 索引 | 备注             |
| ---------- | ------------ | ------ | ---- | ---- | ---------------- |
| user_id    | 用户id       | string |      | Y    |                  |
| group_id   | 分组id       | string |      | Y    |                  |
| name       | 姓名         | string | Y    |      |                  |
| mobile     | 手机号码     | string | Y    | Y    |                  |
| memo       | 其他信息     | string | Y    |      |                  |
| face_list  | 人脸特征列表 | array  |      |      |                  |
| need_train | 训练标记     | int    | Y    |      | 标记是否在临时库 |
| time_t     | 创建时间     | string |      |      |                  |
| last_t     | 最后修改时间 | string |      |      |                  |



#### (3) faces

> 人脸特征信息

| 字段名     | 描述         | 类型      | 可空 | 索引 | 备注                 |
| ---------- | ------------ | --------- | ---- | ---- | -------------------- |
| face_id    | 人脸特征id   | string    |      | Y    | 使用 _id             |
| mode_id    | 模型id       | string    |      | Y    | 计算特征的使用的模型 |
| encodings  | 特征数据     | key-value |      |      |                      |
| image      | 人脸图片数据 | array     |      |      | numpy array数据      |
| ref_count  | 引用计数     | int       |      |      | 计数为0，说明可删除  |
| time_t     | 创建时间     | string    |      |      |                      |
| file_ref   | 上传文件名   | string    |      |      | 仅做参考             |
| weight_ref | 模型权重版本 | string    |      |      | 仅做参考             |



#### (4) faces_temp

> 识别请求的临时人脸数据

| 字段名     | 描述         | 类型   | 可空 | 索引 | 备注 |
| ---------- | ------------ | ------ | ---- | ---- | ---- |
| group_id   | 分组id       | string |      | Y    |      |
| request_id | 接口调用id   | string |      | Y    |      |
| api_name   | 接口名称     | string |      |      |      |
| image      | 人脸图片数据 | string |      |      |      |
| result     | 接口调用结果 | array  | Y    |      |      |
| is_correct | 接口反馈结果 | int    | Y    |      |      |
| last_t     | 最后修改时间 | string |      |      |      |



## mongodb索引

```js
db.groups.createIndex({group_id:1},{ background: true })
db.users.createIndex({group_id:1, user_id:1},{ background: true })
db.users.createIndex({group_id:1, need_train:1},{ background: true })
db.users.createIndex({group_id:1, mobile:1},{ background: true })
db.users.createIndex({user_id:1},{ background: true })
db.faces_temp.createIndex({request_id:1, group_id:1},{ background: true })
```

