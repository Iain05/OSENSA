Demo site: http://34.145.78.29:3000/
# Running the Application

Clone the repository:

```bash
git clone https://github.com/Iain05/Osensa.git
cd Osensa
```

Start the application using Docker Compose:

```powershell
docker compose up
```

Once the services are up access the frontend at:

http://localhost:3000

# Architecutre

## frontend (Restaurant Container)
The restaurant docker container hosts a Svelte application that serves a static site using nginx. We map port 3000 to its port 80 to access it, and the frontend connects to the MQTT broker to send and receive ORDER and FOOD messages.

## MQTT Broker (Mosquitto Container)
The Mosquitto container runs the MQTT broker, which facilitates communication between the frontend and backend services. It listens port 9001 for WebSocket connections.

## backend (Backend Container)
The backend container runs a Python application that connects to the MQTT broker to process incoming ORDER messages and respond with FOOD messages. It connects to the broker using the service name "mosquitto" defined in the Docker Compose file.
