FROM rust:slim AS builder

# a dirty way to update crates.io index
RUN cargo search >/dev/null
RUN ["apt", "update"]
RUN ["apt", "install", "-y", "libssl-dev", "pkg-config"]

WORKDIR /usr/src/sktg
COPY . .
RUN ["cargo", "install", "--path", "."]


FROM debian:stable-slim AS runner

RUN ["apt", "update"]
RUN ["apt", "install", "-y", "ca-certificates"]
RUN ["apt", "clean"]

RUN ["update-ca-certificates"]

ENV DATABASE_FILE=/var/db/db.sqlite3
RUN dirname ${DATABASE_FILE} | xargs mkdir -p
RUN touch ${DATABASE_FILE}
VOLUME /var/db

COPY --from=builder /usr/local/cargo/bin/sktg /usr/local/bin/sktg
CMD ["sktg"]
STOPSIGNAL SIGINT
