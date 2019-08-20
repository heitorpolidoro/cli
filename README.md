# Custom CLI
To install clone this repository in anywhere you want. Use the `stable` branch.

Run `./install.sh` and choose the command you want to call the CLI.

Install the [packages](packages) you want to use.

Use `COMMAND --help` for more information

### [Packages](#packages)
These are the default packages 
#### gitlab
**Commands**

- `pipeline`
    - `start`: Start a pipeline for the current commit, if not exits.
        - `-m, --monitor`: Start the monitor after starting the pipeline.
        - `-b BRANCH, --branch BRANCH`: Start a pipeline in the BRANCH.
        - `-f, --force`: Force to start a pipeline.
    - `monitor`: Monitor the pipeline for the current commit.
        - `-p PIPELINE, --pipeline PIPELINE`: Monitor the pipeline with ID=PIPELINE.
        - `-b BRANCH, --branch BRANCH`: Monitor the pipeline for the branch BRANCH


