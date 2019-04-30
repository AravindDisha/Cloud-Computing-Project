gen_final.py is the python program that allows a user to deploy a micro service with round-robin distribution of requests. 

Python moldule Requirements:
flask
flask-cors
requests
docker

First, fill up the required information in the specs.txt file which in is json format. 
Make sure that the image you are to use is available on the local machine.
Make sure that the maximum number of containers are equal to the number of provided ports.

Execute the program by :

sudo python3 gen_final.py
