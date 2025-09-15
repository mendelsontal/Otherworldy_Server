# main entrypoint (starts server, listens for clients)

from config import settings, logging as log_config, database

logger = log_config.setup_logging()

def main():
    logger.info("Starting game server...")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug: {settings.DEBUG}")
    logger.info(f"Database: {database.DATABASE_URL}")

if __name__ == "__main__":
    main()
