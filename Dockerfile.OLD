FROM python:3.8-alpine
EXPOSE 5000/tcp

COPY ./deploy_key ./deploy_key.pub /
RUN apk --update --no-cache add openssh git sqlite && \
	eval $(ssh-agent -s) && \
	ssh-add /deploy_key && \
	GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" git clone git@github.com:Advanced-Software-Engineering-S5/user-microservice.git /user-microservice && \
	mkdir /db

VOLUME /db
WORKDIR /user-microservice
RUN pip install -r requirements.txt
CMD python start.py /db/userdb.db
