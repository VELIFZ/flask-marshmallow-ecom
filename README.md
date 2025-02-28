ECom API
## Overview

This is a Flask REST API for managing users, orders, products, and addresses. It is built using Flask for the web framework and SQLAlchemy for the ORM (Object Relational Mapping). The API supports search, pagination, and optional includes for retrieving related data.

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

### Users

- **Create User** → `POST /users`
    - Allows guest users (password is optional)

- **Login User** → `POST /users/login`

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

- **Get a Single Order (With Products)** → `GET /order/<id>?include=products`

- **Cancel an Order (Instead of Delete)** → `PUT /order/<id>/cancel`

### Products

- **Create Product** → `POST /products`

- **Get All Products** → `GET /products`

- **Get a Single Product** → `GET /product/<id>`

- **Update a Product** → `PUT /product/<id>`

- **Delete a Product** → `DELETE /product/<id>`

### Addresses

- **Create Address** → `POST /addresses`

- **Get All Addresses** → `GET /addresses`

- **Get a Single Address** → `GET /address/<id>`

- **Update an Address** → `PUT /address/<id>`

- **Delete an Address** → `DELETE /address/<id>`

## Features

- **Search**: `GET /users?search=john`
- **Pagination**: `GET /users?page=1&limit=5`
- **Optional Includes**: `GET /user/1?include=orders,addresses`