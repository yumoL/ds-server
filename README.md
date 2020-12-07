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
Deploy the script that dumps data from Redis to Mysql to the node where Redis and Mysql are installed by `scp -r redis_to_db/ your_virtual_mahcine_ip:your_home_dir/`

#### Deploy chat_servers
- Run `scp -r chat_server/ your_virtual_mahcine_ip:your_home_dir/`



