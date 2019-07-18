# Graphy

Graphy is the main project for the thesis.

## Requirements

- [Docker](https://docs.docker.com/install/)

- [Docker-Compose](https://docs.docker.com/compose/install/)

- [Python 3.x](https://www.python.org/downloads/)

## Setup

After cloned this project, you have two ways to run Graphy. You can either install it on your local machine, or open it 
with the [Pycharm IDE](https://www.jetbrains.com/pycharm/) and run it in the IDE.

Just please make sure that you run the following commands in the Graphy directory:

```
sudo python3 setup.py install   # Installs the requirements and cretes some folders needed for this project.
sudo docker-compose up -d       # Run the containers needed by Graphy.
```

## Run
Copy your trace file to the Graphy/data folder and change the corresponding configuration in the 
[config.yaml](graphy/config.yaml) file:

```
TRACE_FILE: "data/file_name.jsonl"
```

Graphy can run in PyCharm executing the 'Run/Debug Configuration', or by running the [app.py](graphy/app.py) file,
 or with the following command:

```
sudo python3 setup.py run
```

## Configuration

You can modify some configurations regarding the application communication and interaction with other components, for 
this use the [config.json](graphy/config.yaml) file.

## OTP (OpenTracing Processor)

The OpenTracing processor developed using Java Stream API is available in the following [repository](https://github.com/jaimelive/OpenTracingProcessor).

## Service Analysis Algorithms

- Available in the [Notebooks directory](../notebooks).
