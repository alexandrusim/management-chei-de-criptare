version: '3.8'
services:
  mariadb:
    image: mariadb:latest
    container_name: MariaDB-SI
    environment:
      MARIADB_ROOT_PASSWORD: rares
      MARIADB_DATABASE: SIproiect
    ports:
      - "3306:3306"
    volumes:

      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

      - mariadb_data:/var/lib/mysql

volumes:
  mariadb_data: