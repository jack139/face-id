
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

| 字段名   | 描述   | 类型   | 可空 | 索引 | 备注 |
| -------- | ------ | ------ | ---- | ---- | ---- |
| group_id | 分组id | string |      | Y    |      |
| memo     | 描述   | string | Y    |      |      |



#### (2) users

> 用户分组信息

| 字段名   | 描述     | 类型   | 可空 | 索引 | 备注 |
| -------- | -------- | ------ | ---- | ---- | ---- |
| user_id  | 用户id   | string |      | Y    |      |
| group_id | 分组id   | string |      | Y    |      |
| name     | 姓名     | string |      |      |      |
| mobile   | 手机号码 | string | Y    | Y    |      |
| memo     | 其他信息 | string | Y    |      |      |



#### (2) faces

> 人脸特征信息

| 字段名    | 描述       | 类型   | 可空 | 索引 | 备注                 |
| --------- | ---------- | ------ | ---- | ---- | -------------------- |
| face_id   | 人脸特征id | string |      | Y    | 使用 _id             |
| group_id  | 分组id     | string |      | Y    |                      |
| user_id   | 用户id     | string |      | Y    |                      |
| mode_id   | 模型id     | string |      | Y    | 计算特征的使用的模型 |
| encodings | 特征数据   | string |      |      |                      |

