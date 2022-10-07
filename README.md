# A tool that helps to automate github action secrets configuration across many repositories in a project

# HOW TO INSTALL

    ```
        chmod +x install
        sudo ./install
    ```

# HOW TO RUN

    ```
        github-secrets -f <your file path>
    ```

## configuration file structure

```
authorization:
  token: <your github personal token>

secrets:

  server_host:
    name: <name to insert in github>
    value: <value of that secret>
  
  ### other secrets are listed here

repositories:
  appname: 
    name: user/repo # repository name formatted like <owner>/<repo>
    url: <repository url>
    secrets: 
      - server_host
      # and other secrets needed for this repo

  # other apps are listed here

```