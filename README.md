# Outlier AI Training

A profile editing application with a Flask backend and React frontend.

## Features

- Profile viewing and editing
- User selection via dropdown
- Mock database for testing

## Project Structure

- `app.py`: Flask backend server
- `User.py`: User class and database operations
- `ProfilePage.jsx`: Main React component
- `EditProfileForm.jsx`: Form for editing user profiles
- `components/ProfileCard.jsx`: Component for displaying user profile

## Setup and Running

1. Start the Flask backend:
```
python app.py
```

2. Open index.html in a browser or start a simple HTTP server:
```
python -m http.server
```

3. Or use the convenience script:
```
python start.py
```

## Notes

- Mock user database with IDs 0-2
- UI displays IDs as 1-3 for user-friendly display 