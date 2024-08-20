# Adjudicator App

The Adjudicator App is a web application that allows users to create and participate in debates, submit arguments, and receive AI-powered judgments. This README provides instructions for setting up and running both the backend and frontend components of the application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running the Application](#running-the-application)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.8 or higher
- Node.js 14 or higher
- npm (usually comes with Node.js)
- Git

## Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/adjudicator-app.git
   cd adjudicator-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory and add the following environment variables:
   ```
   SECRET_KEY=your_secret_key
   JWT_SECRET_KEY=your_jwt_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```
   Replace `your_secret_key`, `your_jwt_secret_key`, and `your_openai_api_key` with your actual secret keys and OpenAI API key.

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the required npm packages:
   ```
   npm install
   ```

## Running the Application

1. Start the backend server:
   - Ensure you're in the root directory and your virtual environment is activated
   - Run the following command:
     ```
     python main.py
     ```
   The backend server should now be running on `http://localhost:5000`

2. Start the frontend development server:
   - Open a new terminal window
   - Navigate to the frontend directory:
     ```
     cd frontend
     ```
   - Run the following command:
     ```
     npm start
     ```
   The frontend development server should now be running on `http://localhost:3000`

3. Open your web browser and navigate to `http://localhost:3000` to use the application.

## Usage

1. Register a new account or log in with an existing account.
2. From the dashboard, you can create new debate sessions or join existing ones.
3. In a debate session, submit your arguments and wait for your opponent to do the same.
4. Once all arguments are submitted and locked, you can request an AI judgment.
5. View the AI's decision and reasoning on the session page.

## Troubleshooting

- If you encounter any issues with missing dependencies, make sure you've installed all required packages for both the backend and frontend.
- Ensure that your `.env` file is properly configured with the necessary API keys and secret keys.
- If you're having trouble connecting to the backend API, check that the backend server is running and that the frontend is configured to send requests to the correct URL.
- For any persistent issues, please check the application logs or consult the error messages in the browser console and terminal.

For additional help or to report bugs, please open an issue on the GitHub repository.

--- 

This README provides a basic guide to setting up and running the Adjudicator App. As the application evolves, remember to update this document with any new setup requirements or usage instructions.