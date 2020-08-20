# Custom CLI
### To install

`pip install polidoro_cli`

### To use:
`cli --help`

### Tips:
Create alias:

Add in your `.bashrc`
```
alias dk='cli docker'
alias ex='cli elixir'
alias udc='cli unifieddockercompose'
```

### Commands:
#### Docker `cli docker COMMAND` or `dk COMMAND`
```
exec      Run "docker exec"
up        Run "docker-compose up"
down      Run "docker-compose down"
stop      Run "docker stop"
run       Run "docker run"
logs      Run "docker logs
ps        Run "docker ps"
bash      Run "docker exec -it $container bash"
```
This CLI will use the current directory as container name when needed

Example:
```
/home/workspace/my_project$ dk bash
+ docker exec -it my_project bash
```

#### Elixir `cli elixir COMMAND` or `ex COMMAND`
```
new       Run "mix phx.new"
compile   Run "mix compile"
credo     Run "mix credo"
deps      Run "mix deps.get"
iex       Run "iex -S mix"
test      Run "MIX_ENV=test mix test"
setup     Run "mix ecto.setup"
reset     Run "mix ecto.reset"
migrate   Run "mix ecto.migrate"
up        Run "mix phx.server"
schema    Run "mix phx.gen.schema"
gettext   Run "mix gettext.extract --merge"
```
All elixir commands accepts the parameter `-d` to run user the Docker exec command.
Example:
```
/home/workspace/my_project$ ex iex
+ iex -S mix
/home/workspace/my_project$ ex iex -d
+ docker exec -it my_project iex -S mix
```

#### Unified Docker Compose `cli unifieddockercompose COMMAND` or `udc COMMAND`
```
up        Run "docker-compose up"
down      Run "docker-compose down"
restart   Restart the container
```
In the first run will ask for de Unified Docker Compose directory (*absolute path!*).
The CLI will run the docker-compose command in this directory using the current directory as container name

Example:
```
/home/workspace/my_project$ udc up
+ docker-compose up my_project
```
