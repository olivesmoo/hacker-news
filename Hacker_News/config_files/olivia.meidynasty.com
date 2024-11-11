server {
    listen 80;
    server_name olivia.meidynasty.com www.olivia.meidynasty.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name olivia.meidynasty.com www.olivia.meidynasty.com;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";

    ssl_certificate /etc/letsencrypt/live/olivia.meidynasty.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/olivia.meidynasty.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

    location /static {
        alias /home/olives/Hacker_News/hackernews/static;
    }
    location / {
        proxy_pass http://localhost:8000;
        include /etc/nginx/proxy_params;
        proxy_redirect off;
    }
}
