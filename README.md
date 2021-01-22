# Custom CLI
### To install

`pip3 install polidoro_cli`

Then add to your `.bashrc`
```
export PATH="$HOME/bin:$HOME/.local/bin/:$PATH"
```

### To use:
`cli --help`

### Tips:
Create alias:

Add in your `.bashrc`
```
alias dk='cli docker'
alias ex='cli elixir'
alias rb='cli ruby'
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
This CLI will use the **current directory** as **container name**!

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

#### Ruby `cli ruby COMMAND` or `rb COMMAND`
```
console   Run "bundle exec rails console"
migrate   Run "bundle exec rails db:migrate"
create    Run "bundle exec rails db:create"
```

[comment]: <> (#### Unified Docker Compose `cli unifieddockercompose COMMAND` or `udc COMMAND`)

[comment]: <> (```)

[comment]: <> (up        Run "docker-compose up")

[comment]: <> (down      Run "docker-compose down")

[comment]: <> (restart   Restart the container)

[comment]: <> (```)

[comment]: <> (In the first run will ask for de Unified Docker Compose directory &#40;*absolute path!*&#41;.)

[comment]: <> (The CLI will run the docker-compose command in this directory using the current directory as container name)

[comment]: <> (Example:)

[comment]: <> (```)

[comment]: <> (/home/workspace/my_project$ udc up)

[comment]: <> (+ docker-compose up my_project)

[comment]: <> (```)
