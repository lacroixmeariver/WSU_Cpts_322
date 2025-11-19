# python base image, I think its debian based
FROM python:3.12-slim

# make folder to put our stuff in
WORKDIR /app

# copy only files necessary to run web server
COPY attendance_tracker ./attendance_tracker
COPY sqlite ./sqlite
COPY pyproject.toml ./
COPY .env ./

# create virtual env, activate it, and download deps
# note: RUN commands execute at image creatino, CMD runs every startup :)
RUN python -m pip install .

# start up prod server
# -b = host addr:port
# -w = number of workers, set to 1 since we dont know how many cpu cores avail
# last positional arg = path to flask app init function
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "1", "attendance_tracker.__init__:create_app()"]
