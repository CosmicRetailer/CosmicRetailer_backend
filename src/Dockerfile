# FROM python:3.8-slim-buster

# # Set the working directory to /app
# WORKDIR /app

# # Copy the current directory contents into the container at /app
# COPY . /app

# # Install any needed packages specified in requirements.txt
# RUN pip install --trusted-host pypi.python.org -r requirements.txt

# # Make port 80 available to the world outside this container
# EXPOSE 7566

# ENTRYPOINT [ "flask", "run" ]

FROM ubuntu

RUN apt update
RUN apt install python3-pip -y
RUN pip3 install Flask

WORKDIR /app

COPY . .

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]