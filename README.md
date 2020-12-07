# Distributed chatroom
A course project of Distributed System

### Environment
Host machine: Ubuntu 18.04

3 virtual machines: Ubuntu 20.04

### Installation
#### Install Redis
- Before installing Redis server on a virtual machine, please make sure that the host machine could communicate with the virtual machine (for example host can ping virtual machine).

- Install Redis server on virtual machine.

- Open port 6379 for outside access to redis server.

- Reconfigure redis server by editing etc/redis/redis.conf file.
  - bind virtual machine IP address
  
  - set protected-mode to no
  
  - If it still could not be accessed from host machine, shut down the firewall of virtual machine by `sudo ufw allow 6379`. 
  
#### Install Mysql
- Install Mysql in the same node as Redis.
- Create a new user as Mysql may refuse root to connect to it remotely. 
```
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON *.* TO 'your_username'@'localhost'WITH GRANT OPTION;
CREATE USER 'your_username'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON *.* TO 'your_username'@'%' WITH GRANT OPTION;
```
- Create database and necessary schemas:
```
CREATE DATABASE IF NOT EXISTS dsp;
use dsp;
create table user_info(user_name varchar(20), user_id int, pwd varchar(20));
alter table user_info add primary key(user_id) ;
insert into user_info value("test1",1,"111");
insert into user_info value("test2",2,"222");
insert into user_info value("test3",3,"333");

create table room_info(room_name varchar(20), room_id int) ;
alter table room_info add primary key(room_id) ;
insert into room_info value("groupchat",1) ;
select*from room_info;

create table user_room_info(user_id int, room_id int) ;
alter table user_room_info add primary key(user_id,room_id) ;
insert into user_room_info value(1,1) ;
insert into user_room_info value(2,1) ;
insert into user_room_info value(3,1) ;

create table chat_logs_info(user_id int, room_id int, timestamp varchar(20), content varchar(200)) ;
alter table chat_logs_info add primary key(user_id,room_id,timestamp) ;
select*from chat_logs_info;
```
- Deploy the script that dumps data from Redis to Mysql to the node where Redis and Mysql are installed by `scp -r redis_to_db/ your_virtual_mahcine_ip:your_home_dir/`

- Remember to change the configuration of Redis and Mysql in chat_server/config.py and redis_to_db/config.py

#### Deploy chat_servers to another two virtual machines
- Run `scp -r chat_server/ your_virtual_mahcine_ip:your_home_dir/`
- Install python3 -pip and necessary python packages `pip3 install redis pymysql`
- Remember to change the ip address of socket in chat_server/config.py

### Synchronize NTP time of virtual machines to the host machine
- Follow the [instruction](https://linuxconfig.org/ubuntu-20-04-ntp-server).


### Running the application
- First start the coordinator
- Then the dumper script (redis_to_db/redis_to_db.py) and backup script (redis_to_db/backup.py)
- Start chat servers (chat_server/server.py)
- Start client application(s) (client/client.py). Use inserted user information to login (for example, test1 as username and 111 as password)
- Logs will be saved in each node locally.





