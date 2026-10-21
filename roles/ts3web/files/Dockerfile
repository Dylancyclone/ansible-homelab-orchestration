FROM php:8.4-apache
RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
COPY webinterface /var/www/html
COPY config.php /var/www/html/config.php
# quit() runs from the destructor even when connect() failed, and PHP 8 turns fputs() on the
# empty-string socket into a fatal TypeError that @ cannot suppress. The grep fails the build if
# the patch stops applying.
RUN sed -i 's/private function quit() {/&\n\t\tif(!$this->isConnected()) return;/' /var/www/html/ts3admin.class.php \
 && grep -q 'if(!$this->isConnected()) return;' /var/www/html/ts3admin.class.php
RUN chown -R www-data:www-data /var/www/html
WORKDIR /var/www/html
ENTRYPOINT ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
