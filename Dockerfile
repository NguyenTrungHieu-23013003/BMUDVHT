FROM php:8.2-apache

# Cài thư viện SQLite hệ thống trước
RUN apt-get update && apt-get install -y libsqlite3-dev && rm -rf /var/lib/apt/lists/*

# Bật extension SQLite cho PHP
RUN docker-php-ext-install pdo pdo_sqlite

# Tạo thư mục lưu database
RUN mkdir -p /var/data && chmod 777 /var/data

# Copy code vào Apache
COPY src/ /var/www/html/

EXPOSE 80
