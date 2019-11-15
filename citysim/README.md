# Using the Docker image

```bash
# From the root of the repo, build the citysim:latest image
$ docker build citysim --tag citysim

# Run the image, daemonise, auto-remove, expose port 8080, and name container "citysim"
$ docker run -d --rm -p 8080:8080 --name citysim citysim:latest

# Kill the container when you're done
$ docker kill citysim
```

# How is the `server2` folder in this repo used?

It's not. It's only extracted from the installer they gave us,
for your viewing pleasure.

The Dockerfile downloads and extracts the installer and will use
the original `server2` files, and not any files from this repository.

You (or someone) will need to add some extra stuff to the `Dockerfile` / instructions
to add support for custom server data.

# Updating the binary and other files

The `city` folder is created by the following sequence of commands:

- `wget http://docs.citysimulation.eu/server/city-sim_1.0.2_amd64.deb`
- `ar x city-*.deb`
- `tar -xzf data.tar.gz`
- `cd opt`
