# mdp-algo

## Setup 

---

1. Clone the repository
2. Open the terminal and navigate to the repository root
3. Create a virtual environment using your python (Only tested with Python 3.8 at the moment)
    ```bash
    python3 -m venv mdp-venv
    ```
4. Activate the virtual environment
    ```bash
    source mdp-venv/bin/activate
    ```
5. Install the required packages
    ```bash
    pip install -r requirements.txt
    ```



## Running Simulation

---

1. Navigate to the repository root  
2. Activate the virtual environment for the project
    ```bash
    source mdp-venv/bin/activate
    ```
3. Optionally modify `main.py` to change the simulation parameters according to your simulation requirements. You can 
refer to the Simulation class- it's functionality provided in `algorithms/simulation.py`.
4. Run the simulation using the following command
    ```bash
    python main.py
    ```
5. After the simulation is complete, if `sim.plot_optimal_path_animation()` is called in `main.py`, the resulting gif of
the simulation will be saved in the `animations` directory. The gif will be named `optimal_path.gif`.

Example of the simulation output:  
![Simulation Output](https://github.com/MDP-grp-30-24-25/mdp-algo/blob/main/animations/optimal_path.gif)