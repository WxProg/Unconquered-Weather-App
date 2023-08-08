# Unconquered-Weather-App
A personal weather built for the people by a Meteorologist.
A simple Flask-based web application to fetch and display weather information for user-selected cities.

## Features:

- User registration and authentication.
- Add cities to fetch real-time weather details.
- Delete added cities from the list.
- Retrieve forgotten username or password.
- Update/reset password.
- Display the current year on the login page.
- (Future scope) Changeable background based on user preference.

## Setup and Installation

### Prerequisites

1. Python (>= 3.6 recommended)
2. pip
3. MongoDB

### Installation Steps:

1. Clone the repo:

```bash
git clone [YOUR_REPOSITORY_URL]
cd [YOUR_PROJECT_DIRECTORY]
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

(Note: If you haven't created a `requirements.txt`, you can generate it using `pip freeze > requirements.txt`)

3. Set up your environment variables in a `.env` file at the root of your project directory:

```txt
appSecretKey=[YOUR_APP_SECRET]
mongodb_password=[YOUR_MONGODB_PASSWORD]
mailServer=[YOUR_MAIL_SERVER]
mailPort=[YOUR_MAIL_PORT]
defaultSender=[YOUR_DEFAULT_EMAIL_SENDER]
mailUsername=[YOUR_MAIL_USERNAME]
flaskMailPassword=[YOUR_MAIL_PASSWORD]
appSecretPassword=[YOUR_APP_SECRET_PASSWORD]
```

4. Start the application:

```bash
python [YOUR_APP_MAIN_FILE].py
```

The application will start, and you can access it at `http://127.0.0.1:5000/`

## Usage:

1. **Home Page**: 
   - Visit the home page to see the current year displayed.
   
2. **Signup & Login**:
   - New users can register by providing a unique username, email, and password.
   - Returning users can login using their registered username and password.
   
3. **Weather Details**:
   - After logging in, users can add up to 6 cities to fetch the current weather details.
   - Added cities can be deleted as needed.

4. **Account Recovery**:
   - Users can retrieve their forgotten username or reset their password by providing their registered email.

## Contributing:

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License:

[MIT](https://choosealicense.com/licenses/mit/)
