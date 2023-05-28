FROM alpine:3.7
WORKDIR /acts
COPY . /acts
RUN chmod 777 acts.csv
RUN chmod 777 categories.csv
RUN chmod 777 upvotes.csv
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
	rm -r /root/.cache && \
	pip3 install Flask && \
	pip3 install requests && \
	pip3 install -U flask-cors
EXPOSE 80
ENV TEAM_ID=CC_067_071_107_115
CMD python3 app.py