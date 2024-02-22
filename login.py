from flask import Flask, request
from flask_restful import Api, Resource
import sqlite3

app = Flask(__name__)
api = Api(app)

# SQLite connection configuration
conn = sqlite3.connect('database.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()


class Login(Resource):
    def post(self):
        try:
            # Get username and password from request JSON
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Query the database to check if the user exists
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cur.fetchone()

            if user:
                # Check if the provided password matches the password in the database
                if password == user[2]:  # Assuming password is stored in the third column
                    return {'message': 'Login successful'}, 200
                else:
                    return {'message': 'Invalid username or password'}, 401
            else:
                return {'message': 'User does not exist. Please create a new user.'}, 404
        except Exception as e:
            return {'message': f'Error logging in: {str(e)}'}, 500
        finally:
            cur.close()

class CreateUser(Resource):
    def post(self):
        try:
            # Get username and password from request JSON
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Check if the username already exists in the database
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                return {'message': 'Username already exists. Please choose a different username.'}, 400
            else:
                # Insert the new user into the database
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return {'message': 'User created successfully'}, 201
        except Exception as e:
            return {'message': f'Error creating user: {str(e)}'}, 500
        finally:
            cur.close()

# Add the Login and CreateUser resources to the API
api.add_resource(Login, '/login')
api.add_resource(CreateUser, '/create_user')

if __name__ == '__main__':
    app.run(debug=True)
