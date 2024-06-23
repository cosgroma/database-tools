# Docker Compose Notes

## Basic Commands

### Build and Run

```bash
docker compose up
```

### Build and Run in Background

```bash
docker compose up -d
```

### Stop Containers

```bash
docker compose down
```

### Stop and Remove Volumes

```bash
docker compose down -v
```

## Details

```text
Usage:  docker compose [OPTIONS] COMMAND

Define and run multi-container applications with Docker

Options:
      --all-resources              Include all resources, even those not used by services
      --ansi string                Control when to print ANSI control characters ("never"|"always"|"auto") (default "auto")
      --compatibility              Run compose in backward compatibility mode
      --dry-run                    Execute command in dry run mode
      --env-file stringArray       Specify an alternate environment file
  -f, --file stringArray           Compose configuration files
      --parallel int               Control max parallelism, -1 for unlimited (default -1)
      --profile stringArray        Specify a profile to enable
      --progress string            Set type of progress output (auto, tty, plain, quiet) (default "auto")
      --project-directory string   Specify an alternate working directory
                                   (default: the path of the, first specified, Compose file)
  -p, --project-name string        Project name

Commands:
  attach      Attach local standard input, output, and error streams to a service's running container
  build       Build or rebuild services
  config      Parse, resolve and render compose file in canonical format
  cp          Copy files/folders between a service container and the local filesystem
  create      Creates containers for a service
  down        Stop and remove containers, networks
  events      Receive real time events from containers
  exec        Execute a command in a running container
  images      List images used by the created containers
  kill        Force stop service containers
  logs        View output from containers
  ls          List running compose projects
  pause       Pause services
  port        Print the public port for a port binding
  ps          List containers
  pull        Pull service images
  push        Push service images
  restart     Restart service containers
  rm          Removes stopped service containers
  run         Run a one-off command on a service
  scale       Scale services
  start       Start services
  stats       Display a live stream of container(s) resource usage statistics
  stop        Stop services
  top         Display the running processes
  unpause     Unpause services
  up          Create and start containers
  version     Show the Docker Compose version information
  wait        Block until the first service container stops
  watch       Watch build context for service and rebuild/refresh containers when files are updated

Run 'docker compose COMMAND --help' for more information on a command.
```

```bash
docker volume ls
```

```bash
docker volume inspect mongo_stack_v2_mongo_data
```

```json
[
    {
        "CreatedAt": "2024-06-14T16:46:10Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "mongo_stack_v2",
            "com.docker.compose.version": "2.27.0",
            "com.docker.compose.volume": "mongo_data"
        },
        "Mountpoint": "/var/lib/docker/volumes/mongo_stack_v2_mongo_data/_data",
        "Name": "mongo_stack_v2_mongo_data",
        "Options": null,
        "Scope": "local"
    }
]
```


## Environment Variables

### Useful Links

* [Securely Handle Sensitive Information](https://docs.docker.com/compose/environment-variables/best-practices/#handle-sensitive-information-securely)
* [Understand the Precedence of Environment Variables](https://docs.docker.com/compose/environment-variables/best-practices/#understand-environment-variable-precedence)
* [Use Specific Environment Files](https://docs.docker.com/compose/environment-variables/best-practices/#use-specific-environment-files)
* [Understand Interpolation](https://docs.docker.com/compose/environment-variables/best-practices/#know-interpolation)
* [Command Line Overrides](https://docs.docker.com/compose/environment-variables/best-practices/#command-line-overrides)

### Best Practices

Always include sensitive data in environment variables. Use [Secrets](https://docs.docker.com/compose/use-secrets/) to manage sensitive information.

Docker Compose manages the [precedence of environment variables](https://docs.docker.com/compose/environment-variables/envvars-precedence/) from various sources (`.env` files, shell variables, Dockerfiles).

Our application functions in various environments. Use different `.env` files for development, testing, production as needed.

Leverage [interpolation](https://docs.docker.com/compose/environment-variables/variable-interpolation/) functions within compose files for dynamic configurations.

Remember that you can [override environment variables](https://docs.docker.com/compose/environment-variables/set-environment-variables/#cli) from the command line when starting containers. This is beneficial for testing or temporary changes.


```bash
docker run -it -v $(pwd):/tmp mongodb/mongodb-community-server:$MONGODB_VERSION mongoexport --collection=COLLECTION --out=/tmp/COLLECTION.json "mongodb://username:password@clusterURL/database"
```

```bash
docker run -it -v $(pwd):/tmp mongodb/mongodb-community-server:$MONGODB_VERSION mongoimport --drop --collection=COLLECTION "mongodb+srv://user:password@clusterURL/database" /tmp/COLLECTION.json
```

## Secrets

```yaml
services:
   db:
     image: mysql:latest
     volumes:
       - db_data:/var/lib/mysql
     environment:
       MYSQL_ROOT_PASSWORD_FILE: /run/secrets/db_root_password
       MYSQL_DATABASE: wordpress
       MYSQL_USER: wordpress
       MYSQL_PASSWORD_FILE: /run/secrets/db_password
     secrets:
       - db_root_password
       - db_password

   wordpress:
     depends_on:
       - db
     image: wordpress:latest
     ports:
       - "8000:80"
     environment:
       WORDPRESS_DB_HOST: db:3306
       WORDPRESS_DB_USER: wordpress
       WORDPRESS_DB_PASSWORD_FILE: /run/secrets/db_password
     secrets:
       - db_password


secrets:
   db_password:
     file: db_password.txt
   db_root_password:
     file: db_root_password.txt

volumes:
    db_data:
```


```yaml
version: '3'
services:
  myapplication:
    image: mongodb/mongodb-community-server:6.0-ubi8
    environment:
      - CONN_STR=mongodb://user:pass@mongodb
    command: '/bin/bash -c "sleep 5; mongosh $$CONN_STR --eval \"show dbs;\""'
    depends_on:
      - mongodb
  mongodb:
    image: mongodb/mongodb-community-server:6.0-ubi8
    environment:
      - MONGO_INITDB_ROOT_USERNAME=user
      - MONGO_INITDB_ROOT_PASSWORD=pass
    volumes:
      - type: bind
        source: ./data
        target: /data/db
```
