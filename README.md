# ScorePad - Light-weight score keeper for card games

## Docker Compose

Here are the steps to get this tool running in your docker instance with Docker Compose
1. Create a folder for ScorePad and move into it
2. Save the below as `docker-compose.yml`
```yaml
services:
  scorepad:
    container_name: scorepad
    image: jma1ice/scorepad:latest
    restart: unless-stopped
    volumes:
      - scorepad_data:/app
    ports:
      - 2283:2283

volumes:
  scorepad_data:
    driver: local
```
3. In the terminal of your choice, navigate to your ScorePad directory and run `docker compose up -d`

The dashboard will be available at `localhost:2283`
