FROM python:3.12

# Set the working directory in the container
WORKDIR /

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /

# Make port 5000 available
EXPOSE 5000

# Define environment variable If required
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
