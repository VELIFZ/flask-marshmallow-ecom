ECom API
## Overview

This is a Flask REST API for managing users, orders, books, and addresses for a second-hand book selling platform. It is built using Flask for the web framework and SQLAlchemy for the ORM (Object Relational Mapping). The API supports search, pagination, and optional includes for retrieving related data.

## How to Run

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Set up the database:

```bash
flask db upgrade
```

### Run the server:

```bash
flask run
```

The API is available at (http://127.0.0.1:5000/)

## Endpoints

### Authentication

- **Register** → `POST /auth/register`
  - Creates a new user account

- **Login** → `POST /auth/login`
  - Authenticates user and returns JWT token

- **Refresh Token** → `POST /auth/refresh`
  - Refreshes an existing JWT token

- **Request Password Reset** → `POST /auth/reset-password`
  - Requests a password reset link

- **Reset Password** → `POST /auth/reset-password/<token>`
  - Resets password using token

- **Get Current User** → `GET /auth/me`
  - Gets the current authenticated user's information

### Users

- **Create User** → `POST /users`
    - Allows guest users (password is optional)

- **Get All Users (Search & Pagination)** → `GET /users`
    - Supports searching by name, last name, or email
    - Supports pagination (`?page=1&limit=10`)

- **Get a Single User (Optional Includes)** → `GET /user/<id>`
    - Can include orders and addresses using `?include=orders,addresses`

- **Update a User** → `PUT /user/<id>`
    - Updates only the provided fields.

- **Delete a User** → `DELETE /user/<id>`

### Orders

- **Create Order** → `POST /orders`

- **Get All Orders** → `GET /orders`

- **Get a Single Order (With Books)** → `GET /order/<id>?include=books`

- **Cancel an Order (Instead of Delete)** → `PUT /order/<id>/cancel`

### Books

- **Create Book** → `POST /books`
    - Authenticated endpoint, sets seller to current user

- **Get All Books** → `GET /books`
    - Basic search and pagination

- **Advanced Search** → `GET /books/search`
    - Comprehensive filtering by price, genre, condition, etc.
    - Sorting options (`?sort_by=price&sort_order=desc`)

- **Get Featured Books** → `GET /books/featured`
    - Returns newest available books

- **Get a Single Book** → `GET /book/<id>`
    - Optional includes with `?include=seller,reviews`

- **Update a Book** → `PUT /book/<id>`
    - Authenticated endpoint, only book owner can update

- **Delete a Book** → `DELETE /book/<id>`
    - Authenticated endpoint, only book owner can delete

- **Upload Book Image** → `POST /book/<id>/upload-image`
    - Allows uploading an image for a book

### Reviews

- **Create Review** → `POST /reviews`
    - Create a new review for a seller or book

- **Get All Reviews** → `GET /reviews`
    - List all reviews with pagination

- **Get a Single Review** → `GET /review/<id>`
    - Get details of a specific review

- **Update a Review** → `PUT /review/<id>`
    - Update an existing review (only by review creator)

- **Delete a Review** → `DELETE /review/<id>`
    - Delete a review (only by review creator) 

- **Get User Reviews** → `GET /users/<id>/reviews?type=received`
    - Get all reviews for a specific user (received as seller or given as buyer)

- **Get Book Reviews** → `GET /books/<id>/reviews`
    - Get all reviews for a specific book

### Addresses

- **Create Address** → `POST /addresses`

- **Get All Addresses** → `GET /addresses`

- **Get a Single Address** → `GET /address/<id>`

- **Update an Address** → `PUT /address/<id>`

- **Delete an Address** → `DELETE /address/<id>`

## Features

- **Authentication**: JWT-based authentication system with token refresh
- **Search**: Advanced search with multiple filters
- **Pagination**: Limit results and navigate through pages
- **Optional Includes**: Load related data based on request needs
- **Image Upload**: Support for book cover images
- **Reviews & Ratings**: User and book review system with rating calculation

@app.route('/test')
def test():
    return "Test route is working!"