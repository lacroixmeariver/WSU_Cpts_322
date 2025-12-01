# CPTS 322 SWE Project - F25

## Contributors

## Installation and setup
1. Make sure to have python available with version compatible with pyproject spec
2. Ensure you are in the correct directory and make python virtual env in folder with name ".venv":
    `python3 -m venv .venv/`
3. Activate venv before proceeding to package install, may vary depending on system. For Unix-like systems, try: `source .venv/bin/activate`
4. Before installation do a final check with `which python`, validate that the output file path is your local venv!
5. Download packages with respect to dev dependencies called out in the pyproject spec. Give `python -m pip install -e ".[dev]"` a try.
    - Note: The double quotes around `".[dev]"` may be critical depending on your shell, for example they are required so that zsh doesn't misunderstand.
6. **Enable pre-commit hooks with `pre-commit install`**, _this step is critical otherwise tools will not be enabled to validate git commits!!!_
7. Once installed, make sure pre-commit is doing stuff with command `pre-commit run`
8. Start building!

## Helpful Scripts
shell scripts located in ./tools directory

| Script Name | Function | Arguments |
| --- | --- | :---: |
| `start_server` | starts the flask web app in debug mode | - |
| `tailwindcss` | start tail wind with input/output css file path fixed | append any args like `--watch` for watch mode |
| `flask --app attendance_tracker init-db` | deletes tables and recreates schema from scratch | - |
| `flask --app attendance_tracker load-from-email` | load email data from an email into the tables | - |
| `flask --app attendance_tracker gen-sample-data` | creates sample csv data into /docs | - |
| `flask --app attendance_tracker send-email-test` | sends test emails /docs | - |


## Docker Help
- Docker containers are used to handle multiple services for this project, but they are all managed using docker compose which allows users to build and run automatically with a single command!
- when starting the project from scratch, make sure you have docker desktop installed and internet access, then run `docker compose up --build -d`. This will build all the individual containers, pulling updated versions from the web as needed, and then launch the services in detached mode! From there the web service will be available on **localhost:8001**, which is a placeholder until the final hostname is determined.
- At any point all of the services can be stopped by running the command `docker compose down`
