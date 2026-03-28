COMPOSE = docker compose -f infrastructure/docker/docker-compose.yml --env-file infrastructure/docker/.env

include infrastructure/docker/.env
export

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

ps:
	$(COMPOSE) ps

db-shell:
	$(COMPOSE) exec db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

logs:
	$(COMPOSE) logs -f

restart:
	$(COMPOSE) down && $(COMPOSE) up -d