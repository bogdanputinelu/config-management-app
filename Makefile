sample-configs:
	@echo "Creating sample configurations..."
	@mkdir -p ingsoft/configs/web-app ingsoft/configs/api-service ingsoft/backups
	@echo "database:\n  host: localhost\n  port: 5432\nfeatures:\n  debug: true" > ingsoft/configs/web-app/dev.yaml
	@echo "database:\n  host: prod-db.com\n  port: 5432\nfeatures:\n  debug: false" > ingsoft/configs/web-app/production.yaml
	@echo "database:\n  host: localhost\n  port: 5432\nredis:\n  host: localhost\n  port: 6379" > ingsoft/configs/api-service/dev.yaml
	@echo "Sample configurations created!"
