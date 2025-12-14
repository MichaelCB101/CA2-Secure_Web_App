#use a python runtime slim image
FROM python:3.11-slim
LABEL authors="Michael"
#set up environment variables
ENV APP_HOME=/home/app
ENV APP_USER=app
#make an app directory
RUN useradd -m -d ${APP_HOME} -s /bin/bash ${APP_USER}
WORKDIR ${APP_HOME}
#copy the requirements file created
COPY requirements.txt .

#install all the python dependencies needed
RUN pip install --no-cache-dir -r requirements.txt

#copy the app code
COPY . .
#make sure instance folder exists
RUN mkdir -p ${APP_HOME}/instance && chown -R ${APP_USER}:${APP_USER} ${APP_HOME}/instance
# create logs directory and give permissions
RUN mkdir -p ${APP_HOME}/logs && chown -R ${APP_USER}:${APP_USER} ${APP_HOME}/logsCA2

#copies the scrupt that automatically runs the app, fuzzing script and user creation script
COPY auto_start.sh /home/app/auto_start.sh
RUN chmod +x /home/app/auto_start.sh
#switch to a user that is not a root user
USER ${APP_USER}

#expose the port the web app is configured to listen on and run the automation script that runs the app and fuzzing and user scripts
EXPOSE 5000
ENTRYPOINT ["/home/app/auto_start.sh"]