FROM rust:1.60-slim as builder

RUN ["apt", "update"]
RUN ["apt", "install", "-y", "pkg-config", "libssl-dev"]

COPY Cargo.toml Cargo.toml
COPY src src

RUN cargo install --path .


FROM debian:buster-slim

RUN ["apt", "update"]
RUN ["apt", "install", "-y", "libssl1.1"]
RUN ["rm", "-rf", "/var/lib/apt/lists/"]

COPY --from=builder /usr/local/cargo/bin/sktg /usr/local/bin/sktg

CMD ["sktg"]
