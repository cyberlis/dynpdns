# dynpdns
Custom dyndns with powerdns and custom python script

https://blog.heckel.xyz/2016/12/31/your-own-dynamic-dns-server-powerdns-mysql/


https://repo.powerdns.com/
sudo apt-get install pdns-backend-sqlite3
https://doc.powerdns.com/md/authoritative/backend-generic-sqlite/


    # in pdns.conf
    launch=gsqlite3
    gsqlite3-database=/var/lib/powerdns/pdns.sqlite3


https://github.com/PowerDNS/pdns/blob/master/modules/gsqlite3backend/schema.sqlite3.sql


    cd /var/lib/powerdns
    sudo sqlite3 pdns.sqlite3 < schema.sqlite3.sql


config main.py


    DBFILENAME = '/var/lib/powerdns/pdns.sqlite3'
    LOGIN = 'myuser'
    PASSWORD = 'mypassword'
    SERVERIP = ''
    SERVERPORT = 10001
    DOMAIN = 'cloud.rccraft.ru'
    SOA_CONTENT = 'dyndns.ns.rccraft.ru admin.rccraft.ru {} 60 60 60 60'


run python3 main.py