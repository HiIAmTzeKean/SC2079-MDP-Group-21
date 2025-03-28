# mdp-algo

To make the necessary modifications when tuning your robot, refer to the `TODO` sections.

## Setup 

1. Clone the repository
2. Open the terminal and navigate to `/algo` directory
3. Create a python virtual environment
    ```bash
    python -m venv .venv
    ```
4. Activate the virtual environment for the directory

    Mac:
    ```bash
    source .venv/bin/activate
    ```

    Windows:
    ```bash
    .venv/Scripts/activate
    ```

5. Install the required packages
    ```bash
    pip install -r requirements.txt
    ```

## Running Web Simulation

1. Refer to `README.md` in `/simulator` directory



## Testing Algorithm directly

To call the algorithm code directly without using the API,
1. Navigate to `/algo` directory
2. Activate the virtual environment for the directory

    Mac:
    ```bash
    source .venv/bin/activate
    ```

    Windows:
    ```bash
    .venv/Scripts/activate
    ```
3. Optionally modify `main.py` to change the obstacles or parameters according to requirements.
4. Run the algorithm using the following command
    ```bash
    python main.py
    ```

## Credits
Thank you to Group 30 from AY24/25 S1 for the algorithm base code. We extended their code by extensive refactoring and optimizing it for a faster runtime.