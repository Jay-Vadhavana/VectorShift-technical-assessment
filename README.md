# VectorShift-technical-assessment

## Description
This project integrates Notion, Airtable, and HubSpot, combining these platforms for seamless functionality. The technologies used to develop and enhance this project include React.js, Python, FastAPI, and Redis.

## Table of Contents
- [Installation](#installation)
    - [Frontend Setup](#frontend-setup)
    - [Backend Setup](#backend-setup)
    - [Redis Setup](#redis-setup)
- [Usage](#usage)
    - [Running the frontend](#running-the-frontend)
    - [Running the backend](#running-the-backend)
- [Completion](#completion)

## Installation
- You can download the source code from [VectorShift-technical-assessment](https://github.com/Jay-Vadhavana/VectorShift-technical-assessment).
- This project consists of two main folders: frontend and backend. To run the project successfully, both parts need to be set up and configured properly.

### Frontend Setup
- Navigate the "frontend" folder.
- Open a command prompt (CMD) in this directory.
- Run `npm install` to install the required dependencies.
- Once the installation is complete, run `npm start` to launch the project.

### Backend Setup
- Navigate the "backend" folder.
- Open a command prompt(CMD) in this directory.
- You'll find the `requirements.txt` file, which lists the necessary packages to install.
- To install the packages from the `requirements.txt` file, run the following command:
```
pip install -r requirements.txt
```
- Please note that you may encounter errors during package installation due to version conflicts. In such cases, it's recommended to install those packages individually.
- once the installation is complete, run the following command to start the project:
```
uvicorn main:app --reload
```

### Redis Setup
- If you don’t have Redis installed on your machine, you can install it by following the instructions for your operating system.
    #### For windows: 
    - Redis is not officially supported on Windows, but you can use Windows Subsystem for Linux (WSL).
    - Follo the below steps to install the wsl:
        - Open PowerShell.
        - Run the command `wsl --install`.
        - Reboot your PC.
    #### For macOS: 
    - Use Homebrew to install Redis:
    ```
    brew install redis
    ```
    #### For Linux: 
    - Use the package manager to install Redis:
    ```
    sudo apt update
    sudo apt install redis-server
    ```
- To start the Redis, run the following command 
```
sudo service redis-server start
```

## Usage
### Running the frontend
- Open a command prompt (CMD) in the "frontend" directory.
- Run the following command to start the frontend:
```
npm start
```
- The site will be accessible at `localhost:3000` through browser.

### Running the backend
- Open a command prompt (CMD) in the "backend" directory.
- Run the following command to start the backend:
```
uvicorm main:app --reload
```
- Start Redis by running the following command:
```
sudo service redis-server start
```
- **Note**: Starting Redis is essential for the proper functioning of the application.

## Completion
- Congratulations! The project has been successfully set up!