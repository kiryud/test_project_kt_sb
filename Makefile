# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jijeong <jijeong@student.42seoul.kr>       +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/27 00:00:00 by jijeong           #+#    #+#              #
#    Updated: 2026/09/27 00:00:00 by jijeong          ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

SRCS:="./srcs"
VOLUME_DIR:="./volume"

all: up

ps:
	sudo docker-compose --env-file .env -f $(SRCS)/docker-compose.yml ps


up: volume
	sudo docker-compose --env-file .env -f $(SRCS)/docker-compose.yml up --build

build:
	sudo docker-compose --env-file .env -f $(SRCS)/docker-compose.yml up -d --build

down:
	sudo docker-compose --env-file .env -f $(SRCS)/docker-compose.yml down

clean:
	sudo docker-compose --env-file .env -f $(SRCS)/docker-compose.yml down -v
re:
	sudo make fclean
	sudo make up

fclean:
	sudo make clean
	sudo docker system prune --all --force --volumes
	sudo docker network prune --force
	sudo docker volume prune --force
	sudo rm -fr $(VOLUME_DIR)

volume:
	sudo mkdir -p $(VOLUME_DIR)/db

.PHONY: all ps up build down clean re fclean volume
