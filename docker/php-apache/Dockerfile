FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    apache2 \
    php7.4 \
    php7.4-mysql \
    php7.4-mysqli \
    php7.4-pdo \
    php7.4-pdo-mysql \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod rewrite

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_PID_FILE /var/run/apache2/apache2.pid
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2

RUN mkdir -p /var/run/apache2 /var/lock/apache2

EXPOSE 80

CMD ["apache2-foreground"]
