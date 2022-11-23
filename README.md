# Tech Bloc Airflow

## Configuration values

These are environment variables that can be modified to change `just` behavior:

- `SSH_DIRECTORY`: Directory to mount into the container for use in ssh operations. The keys are copied into a different directory within the container so permissions are preserved. Defaults to `~/.ssh`.
- `IS_PROD`: Determines which docker-compose override file to use. If set to `true`, [docker-compose.prod.yml](./docker-compose.prod.yml) is used. All other values will use [docker-compose.dev.yml](./docker-compose.dev.yml).
- `SERVICE`: Determines which service to use when running certain `just` commands (e.g. `just ipython`, `just tests`, etc). Defaults to `scheduler`. Note that changing this to the webserver may result in unexpected behavior because the database is not migrated at startup during the webserver's init (although it is for the scheduler).
