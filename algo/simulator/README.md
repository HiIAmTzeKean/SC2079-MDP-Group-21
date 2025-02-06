# Algorithm Simulator (Web)

## Setup Instructions

\*Please setup api.py by following the `README.md` in `/api` directory to setup backend before attempting to run simulator. You need to start the flask server before proceeding.

\*Please also ensure that you have `yarn` installed.

1. In the `/simulator` directory, install the required dependencies.

```bash
yarn
```
2. In `/simulator/src/hooks/useFetch.ts`, make sure to change `const serverDomainUrl` to the one you see on command prompt when running flask.

1. In the same directory, start the application.

```bash
yarn start
```

And you are ready to start using the Algorithm Simulator! Please make sure you are running BOTH the flask(for backend) and yarn(for frontend) in 2 terminals. The application is running on http://localhost:3000. The page will reload when you make changes.
