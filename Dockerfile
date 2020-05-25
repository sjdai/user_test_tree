FROM nginx
#COPY default.conf /etc/nginx/conf.d/default.conf
COPY ./RL.html /usr/share/nginx/html
COPY ./rec.html /usr/share/nginx/html
COPY ./rec_tag.html /usr/share/nginx/html
