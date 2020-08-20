FROM elixir

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update -qq && apt-get install -y  \
    nodejs \
    postgresql-client \
    inotify-tools \
    vim

## CONFIGURE DIRECTORIES OF PROJECT
RUN mkdir /$project_dir
WORKDIR /$project_dir

COPY . /$project_dir

## INSTALL PHOENIX DEPENDENCIES (--force not to be interactive)
RUN mix local.hex --force && \
    mix local.rebar --force && \
    mix archive.install hex phx_new 1.4.11 --force

RUN npm i --prefix assets

# APPLICATION PORT
EXPOSE 4000
