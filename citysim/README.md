# Using the Docker image

```bash
# From the root of the repo, build the citysim:latest image
$ docker build citysim --tag citysim

# Run the image, daemonise, auto-remove, expose port 8080, and name container "citysim"
$ docker run -d --rm -p 8080:8080 --name citysim citysim:latest

# Kill the container when you're done
$ docker kill citysim
```

# Updating the binary and other files

The `city` folder is created by the following sequence of commands:

- `wget http://docs.citysimulation.eu/server/city-sim_1.0.2_amd64.deb`
- `ar x city-*.deb`
- `tar -xzf data.tar.gz`
- `cd opt`
