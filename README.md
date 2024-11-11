# Hacker News

## Description

Project to learn about Python web application development. Originally hosted at: [olivia.meidynasty.com](https://olivia.meidynasty.com), but the server is no longer running. A demo video of the app can be found at [this link](https://drive.google.com/file/d/1el8H_lsGaPh-TujUrk1Twk7KBGlY5GHO/view?usp=sharing). Features the top posts from Hacker News and allows users to login through Auth0 to like/dislike these posts. It also has an Admin view which allows the deletion of users and posts.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configs](#configs)
- [Testing](#testing)

## Features
- [Home](https://olivia.meidynasty.com)  
The home page contains a paginated list of the top Hacker News posts based on its popularity on my website and how recently it was posted to Hacker News. When logged in, the user is able to like or dislike each post.
- [Login](https://olivia.meidynasty.com/login)  
The login page uses Auth0 to log the user in.
- [Profile](https://olivia.meidynasty.com/account)  
Accessible only when the user is logged in. Can also get to this page through the Account link in the Navbar when signed in. Displays the user's name, email, and profile picture.
- [Get Admin Role](https://olivia.meidynasty/get_admin)  
When signed in, grants the user an admin role. This link is also accessible through the side bar on the website. After clicking the link, it will redirect the user back to the home page. In order to actually gain access to the admin pages, they must logout and login again.
- [Admin User Dashboard](https://olivia.meidynasty.com/admin_user)  
If the user is signed into an account with admin privileges, they can access the Admin User Dashboard. Here, they can delete other users (which deletes the corresponding likes associated with that user) by clicking the red delete button on each profile.
- [Admin Post Dashboard](https://olivia.meidynasty.com/admin_post)  
If the user is signed into an account with admin privileges, they can access the Admin Post Dashboard. Here, they can delete posts (and the corresponding likes associated with that post) by clicking the black "x" in the top right corner of each post.

## Installation

### Settings for the Linode Machine:
- Image: Ubuntu 22.04 LTS
- Region: Newark, NJ
- Linode Plan: Nanode 1GB
- Linode Label: cop4521_om21

### Setting Up the Server
- [ ] 
    ```
    apt update
    ```
- [ ] 
    ```
    apt upgrade
    ```
- [ ] 
    ```
    hostnamectl set-hostname om21-server
    ```
- [ ] edit `/etc/hosts`
    - [ ]   
        ```
        97.107.137.128 om21-server
        ```
- [ ] add users
    - [ ] 
        ```
        adduser olives
        ```
    - [ ] 
        ```
        adduser olives sudo
        ```
    - [ ] 
        ```
        adduser grader
        ```
    - [ ] 
        ```
        adduser grader sudo
        ```

### Installing Lynis
- [ ] [Access the Lynis repository](https://github.com/CISOfy/lynis)
- [ ] Clone the repository in root
    - [ ] 
        ```
        sudo -i
        ```
    - [ ]
        ```
        git clone https://github.com/CISOfy/lynis.git
        ```
- [ ] Run lynis
    - [ ] 
        ```
        cd lynis
        ```
    - [ ] 
        ```
        ./lynis audit system
        ```
### Improving Lynis Hardening Index
- [ ] Adding ssh key to limited user
    - [ ] Create a .ssh folder:
        ```
        mkdir .ssh
        sudo chmod 700 ~/.ssh/
        ```
    - [ ] On local machine: 
        ```
        ssh-keygen -t rsa
        scp ~/.ssh/id_rsa.pub olives@97.107.137.128:~/.ssh/authorized_keys
        ```
    - [ ] 
        ```
        sudo chmod 600 ~/.ssh/*
        ```
- [ ] Adding ssh key to grader
    - [ ] 
        ```
        mkdir .ssh
        sudo chmod 700 ~/.ssh/
        ```
    - [ ] On local machine: 
        ```
        scp Downloads/id_rsa.pub grader@97.107.137.128:~/.ssh/authorized_keys
         ```
    - [ ] 
        ```
        sudo chmod 600 ~/.ssh/*
        ```
- [ ] Edit sshd_config file
    - [ ] 
        ```
        sudo vim /etc/ssh/sshd_config
        ```
    - [ ] Disabling Root login
        - [ ] Change PermitRootLogin to no
        - [ ] Change PasswordAuthentication to no
        - [ ] Change to:
            ```
            Port 2048
            AllowTcpForwarding: no
            ClientAliveCountMax: 2
            LogLevel: VERBOSE
            MaxAuthTries: 3
            MaxSessions: 2
            TCPKeepAlive: no
            X11Forwarding: no
            AllowAgentForwarding: no
            ```
    - [ ] 
        ```
        sudo systemctl restart sshd
        ```
- [ ] Remove sudo password
    - [ ] 
        ```
        sudo visudo
        ```
    - [ ] Add the line 
        ```
        %sudo ALL=(ALL:ALL) ALL             // find this line
        %sudo ALL=(ALL:ALL) NOPASSWD:ALL    // add this line below
        ```
- [ ] Configuring firewall to only allow port 2048
    ```
    sudo ufw default allow outgoing
    sudo ufw default deny incoming
    sudo ufw allow 2048
    sudo ufw enable
    ```
    - [ ] to check status: `sudo ufw status`
- [ ] Set password on GRUB boot loader
    - [ ] 
        ```
        grub-mkpasswd-pbkdf2
        ```
    - [ ] Copy the hash
    - [ ] `sudo vim /etc/grub.d/40_custom`
    - [ ] Add the following to the file:
        ```
        set superusers=root
        password_pbkdf2 root grub.pbkdf2.sha512.10000.63C7F6468A224D600753D0B4A28D1203792AECA43F60BDF77E245B1E7066799F41A8DDA2B509E847BB62EA2C5E808BA4683F41DBE2D05F0E6CA39184AE3FEB67.F5B703258973A822B448676B5F513A48B733E8C1CB88F17C0B7F737F99AB1CC9AB5D765DD10BAA304B70A029778F329ED8A65226E89455CBEAA5F8A6C047E671
        ```
    - [ ] 
        ```
        sudo update-grub
        ```
- [ ] Install Stuff
    - [ ] PAM Module: 
        ```
        sudo apt install libpam-passwdqc
        ```
    - [ ] debsums: 
        ```
        sudo apt install debsums
        ```
        - [ ] to use: 
            ```
            sudo debsums --all --generate=all
            ```
    - [ ] apt-show-versions: 
        ```
        sudo apt install apt-show-versions
        ```
        - [ ] to use: 
            ```
            apt-show-versions
            ```
    - [ ] malware scanner: 
        ```
        apt install rkhunter
        ```
        - [ ] to use:  
            ```
            sudo rkhunter --check
            ```
    - [ ] auditd: 
        ```
        sudo apt install auditd
        ```
        - [ ] to use: 
            ```
            sudo systemctl start auditd
            systemctl enable auditd
            ```
    - [ ] file integrity tool:
        ```
        sudo apt install aide
        ```
        - [ ] to use: 
            ```
            aideinit
            ```           
        - [ ] 
            ```
            cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
            ```
    - [ ] Process accounting:
        ```
        sudo apt install acct
        sudo systemctl start acct
        sudo systemctl enable acct
        ```
- [ ] Hardening Kernel
    - [ ] `vim /etc/sysctl.conf`
        - [ ] Uncomment the following:
            ```
            net.ipv4.conf.all.log_martians = 1 
            net.ipv4.conf.all.rp_filter = 1
            net.ipv4.conf.all.send_redirects = 0
            net.ipv4.conf.default.log_martians = 1
            ```
        - [ ] Add the following:
            ```
            dev.tty.ldisc_autoload = 0
            fs.protected_fifos = 2
            fs.suid_dumpable = 0
            kernel.kptr_restrict = 2
            kernel.modules_disabled = 1
            kernel.perf_event_paranoid = 3
            kernel.sysrq = 0
            kernel.unprivileged_bpf_disabled = 1
            net.core.bpf_jit_harden = 2
            ```
    - [ ] 
        ```
        sudo sysctl -p
        ```
    - [ ] Resolve systemd
        - [ ] `sudo vim /etc/systemd/resolved.conf`
        - [ ] 
            ```
            DNSSEC=yes
            ```
        - [ ] `sudo systemctl restart systemd-resolved`
    - [ ] Enable systat
        - [ ] `sudo vim /etc/default/sysstat`
        - [ ] 
            ```
            ENABLED="true"
            ```
    - [ ] Change umask default:
        - [ ] `sudo vim /etc/login.defs`
        - [ ] 
            ```
            UMASK 27
            ```
### Setting Up Default Nginx
```
sudo apt install nginx
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
```
Access: `sudo vim /etc/nginx/sites-enabled/olivia.meidynasty.com`
Add the following to see the default Nginx page:
```Python
server {
    listen 80;
    server_name olivia.meidynasty.com www.olivia.meidynasty.com;

    location / {
        root /var/www/html;
        index index.html;
    }
}
```
```
sudo ln -s /etc/nginx/sites-enabled/olivia.meidynasty.com /etc/nginx/sites-available/
```

### Setting Up Certbot
~~I would clone the repository here, if you haven't already~~
```
sudo snap install --classic certbot
```
```
sudo certbot --nginx
```
Change the Nginx config at `sudo vim /etc/nginx/sites-enabled/olivia.meidynasty.com`:
```Python
server {
    listen 80;
    server_name olivia.meidynasty.com www.olivia.meidynasty.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name olivia.meidynasty.com www.olivia.meidynasty.com;

    ssl_certificate /etc/letsencrypt/live/olivia.meidynasty.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/olivia.meidynasty.com/privkey.pem;


    location / {
        root /var/www/html/;
        index index.html;
    }
}
```
```
sudo certbot renew --dry-run
sudo systemctl reload nginx
sudo nginx -t
sudo service nginx restart
```
To view errors: 
```
sudo tail -n 20 /var/log/nginx/error.log
```

### Static Files Permissions
```
sudo chown -R www-data:www-data *
sudo chmod -R 755 /home
sudo chmod 644 /home/olives/Hacker_News/hackernews/static/index.html
```

### Creating a Virtual Environment
Note: my venv is in the repository so creating a new one is not necessary
create venv: 
```
python3 -m venv Hacker_News/venv``
```
to enter venv:
```
cd Hacker_News
source venv/bin/activate
```
to install project packages:
```
pip install -r requirements.txt
```
to exit venv: 
```
deactivate
```


### Gunicorn
~~(Not necessary for project recreation) inside of venv:
`pip install gunicorn`~~

edit nginx configuration with what is in the configuration file

~~(Not necessary for project recreation) create a run.py (already in the repository)~~

```
sudo apt install supervisor
```
create the supervisor conf file (contents of file in [repository](Hacker_News/config_files/hackernews.conf)):
```
sudo vim /etc/supervisor/conf.d/hackernews.conf
```
create other logs:
```
sudo mkdir -p /var/log/hackernews
sudo touch /var/log/hackernews/hackernews.err.log
sudo touch /var/log/hackernews/hackernews.out.log
sudo supervisorctl reload
```

### Flask SQL Alchemy
This section is not necessary unless you need to recreate the db
~~in venv:`pip install flask-sqlalchemy`~~

In the python console: `python`
```python
>>> from hackernews import app, db
>>> from hackernews.models import User
>>> app.app_context().push
>>> with app.app_context():
...     db.create_all()                 #to create all tables
...     db.drop_all()                   #to delete all tables
...     User.__table__.drop(db.engine)  #to delete the User table
```

### Cron Jobs
To edit the cronjobs: 
```
crontab -e
```
Add this job to run data.py every hour
```
0 * * * * /home/olives/Hacker_News/venv/bin/python /home/olives/Hacker_News/data.py
```
To view jobs:
```
crontab -l 
```

### Pylint
to use the pylint in my venv:
```
/home/olives/Hacker_News/venv/bin/pylint routes.py
```

## Configs
All configuration files are located in Hacker_News/config_files.
- [Nginx Configurations](Hacker_News/config_files/olivia.meidynasty.com)
- [Supervisor Configurations](Hacker_News/config_files/hackernews.conf)
- [Crontab Configuration](Hacker_News/config_files/crontab)


## Testing
The tests are located in [Hacker_News/tests](Hacker_News/tests/__init__.py).
To run the tests, one would:
- Go to the Hacker_News directory. 
- Start the virtual environment with: ```source venv/bin/activate```. 
- We then run the tests with the command:  ```coverage run -m pytest test_routes.py```. 
- To see the percentage of coverage, run the command: ```coverage report```
