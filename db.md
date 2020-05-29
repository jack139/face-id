
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

| 字段名    | 描述         | 类型   | 可空 | 索引 | 备注 |
| --------- | ------------ | ------ | ---- | ---- | ---- |
| user_id   | 用户id       | string |      | Y    |      |
| group_id  | 分组id       | string |      | Y    |      |
| name      | 姓名         | string | Y    |      |      |
| mobile    | 手机号码     | string | Y    | Y    |      |
| memo      | 其他信息     | string | Y    |      |      |
| face_list | 人脸特征列表 | array  |      |      |      |
| time_t    | 创建时间     | string |      |      |      |
| last_t    | 最后修改时间 | string |      |      |      |



#### (3) faces

> 人脸特征信息

| 字段名    | 描述       | 类型   | 可空 | 索引 | 备注                 |
| --------- | ---------- | ------ | ---- | ---- | -------------------- |
| face_id   | 人脸特征id | string |      | Y    | 使用 _id             |
| mode_id   | 模型id     | string |      | Y    | 计算特征的使用的模型 |
| encodings | 特征数据   | string |      |      |                      |
| ref_count | 引用计数   | int    |      |      | 计数为0，说明可删除  |
| time_t    | 创建时间   | string |      |      |                      |



#### (4) facelog

> 人脸识别日志

| 字段名 | 描述       | 类型   | 可空 | 索引 | 备注                 |
| ------ | ---------- | ------ | ---- | ---- | -------------------- |
| api    | 人脸特征id | string |      | Y    |                      |
| param  | 调用参数   | string |      |      | 不记录图片和特征数据 |
| result | 返回参数   | string |      |      | 不记录图片和特征数据 |
| extra  | 附加信息   | string |      |      | 各接自己定义具体内容 |
| time_t | 创建时间   | string |      |      |                      |

