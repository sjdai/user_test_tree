FROM nginx
#COPY default.conf /etc/nginx/conf.d/default.conf
RUN mkdir /usr/share/nginx/html/pilot
RUN mkdir /usr/share/nginx/html/user_study
COPY ./pilot/RL.html /usr/share/nginx/html/pilot
COPY ./pilot/rec.html /usr/share/nginx/html/pilot
COPY ./pilot/rec_tag.html /usr/share/nginx/html/pilot
COPY ./user_study/RL.html /usr/share/nginx/html/user_study
COPY ./user_study/rec.html /usr/share/nginx/html/user_study
COPY ./user_study/rec_tag.html /usr/share/nginx/html/user_study
