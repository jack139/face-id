
### CentOS 7 需要安装的包

```shell
yum update
yum groupinstall "Development Tools"

yum install epel-release
yum install python36
yum install python3-devel openssl-devel pcre-devel
yum install nginx
yum install cmake

pip3 install -U pip
pip3 install uwsgi
```



### nginx配置文件

> nginx.conf:

```nginx
client_max_body_size 8m;

server {
    listen       5000;

    access_log   /var/log/nginx/access_face.log;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/uwsgi_face.sock;
        uwsgi_param UWSGI_CHDIR /usr/share/nginx/html/face-id;
        uwsgi_param UWSGI_SCRIPT app:app;
    }

    location /static/ {
        root /usr/share/nginx/html/face-id;
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
    }
}
```




### Kafka需要修改的配置

> server.properties:

```Kafka
message.max.bytes=5242880
replica.fetch.max.bytes=6291456
```

