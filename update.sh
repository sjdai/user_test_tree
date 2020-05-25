docker stop nginx-webserver
docker rm nginx-webserver
docker build . -t my-nginx-image
docker run -p 7777:80 --name nginx-webserver -d my-nginx-image
