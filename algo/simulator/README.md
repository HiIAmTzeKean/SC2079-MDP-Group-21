# Algorithm Simulator (Web)

![Simulator image](https://i.gyazo.com/cc52b61251f930f531db95e0a83af5ba.png)

## Setup Instructions

Please setup api.py by following the `README.md` in `/api` directory to setup backend before attempting to run simulator. You need to start the flask server before proceeding.

Please also ensure that you have `yarn` installed.

1. In the `algo/simulator` directory, install the required dependencies.

```bash
yarn
```

### React Web Dev Server (Frontend)
1. In `algo/simulator/src/constants/index.ts`, change `API_IP` to your PC's local IPv4 address (can be found using ipconfig command in Command Prompt) and `PORT` to the port used by the Flask API server. 

2. In the `algo/simulator` directory, start the application.

```bash
yarn start
```

### Flask API Server (Backend)
1. In a new terminal, navigate to `api/` directory.

2. Follow the `README.md` instructions in `api/` directory to start the API server.

And you are ready to start using the Algorithm Simulator! Please make sure you are running BOTH the web simulator frontend and API server backend simultaneously in 2 different terminals. The application will be running on `http://localhost:3000` or `http://{your local IP}:3000`. The page will reload when you make changes.

## Credits
Thank you to Group 11 from AY23/24 S2 for the simulator base code. We extended their code by extensive refactoring and implementing additional tests and debugging features.