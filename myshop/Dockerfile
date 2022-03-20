
# 建立 python 环境
 FROM python:3.8.5

 MAINTAINER gzy
 
 # 设置 python 环境变量
 ENV PYTHONUNBUFFERED 1
 
 COPY pip.conf /root/.pip/pip.conf
 
 # 创建 项目 文件夹
 RUN mkdir -p /var/www/html/myshop
 
 # 将 项目 文件夹为工作目录
 WORKDIR /var/www/html/myshop
 
 # 将当前目录加入到工作目录中（. 表示当前目录）
 ADD . /var/www/html/myshop
 
 # 更新pip版本
 RUN /usr/local/bin/python -m pip install --upgrade pip
 
 # 利用 pip 安装依赖
 RUN pip install -r requirements.txt
 
 # 去除windows系统编辑文件中多余的\r回车空格
 RUN sed -i 's/\r//' ./start.sh
 
 # 给start.sh可执行权限
 RUN chmod +x ./start.sh