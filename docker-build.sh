#!/bin/bash

# -------------------------------------------------------------------
# This scripts is a wrapper around docker-compose
# It ensures that a .env file exists before starting the containers
# -------------------------------------------------------------------s
RED='\033[0;31m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color


# Create .env before docker-compose reads it
if [ "$1" = "up" ] && [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${CYAN}✓ .env file created successfully!${NC}"
fi

# Remove old database migration files
find app/backend -type d -name "migrations" | while read -r migration_dir; do
    echo "Processing: $migration_dir"
    find "$migration_dir" -type f ! -name "__init__.py" -delete
    echo -e "${GREEN}  ✓ Cleaned${NC}"
done

echo -e "${CYAN}Migration cleanup complete!${NC}"

# Run docker-compose with all arguments passed to this script
{
    docker-compose "$@"
} || {
    echo -e "${RED}Docker-compose command failed..."
    echo -e "${NC}>>> ${RED}Please check if Docker is running and try again."
    exit 1
}
