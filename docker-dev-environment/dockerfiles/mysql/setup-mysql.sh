mysqld &
sleep 5
echo "CREATE DATABASE amara_dev;" | mysql -u root
echo "CREATE USER 'amara_dev'@'%' IDENTIFIED BY 'amara_dev';" | mysql -u root
echo "GRANT ALL ON amara_dev.* TO amara_dev@'%';" | mysql -u root
