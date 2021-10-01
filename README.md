# Networks Lab 2 - REST API

Lim Jun Wei 1004379

## Setup

Make sure you have [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed.

Run `docker-compose up` and make sure you get "Welcome to the Game Shop!" by going to [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Checkoff Walkthrough

The accompanying .http unit test files are in the checkoff folder. Since the database is empty, let us start with POST requests.

### POST

From the post_requests.http file, run *1. Create a new game*.
This route requires an **apikey** if not the request will result in a 401 unauthorized. 
The request will generate a new game in the database, let us create a couple to test out the following functions.

### GET

From get_requests.http file, run *1. Retrieve ALL games*. Take note of an ID, we will need it to run the next request.
Run *2. Retrieve a game by ID*.
Run *3. Retrieve a limited number of games*.
Run *4. Retrieve games sorted by price in ascending order*.
Run 5. *Retrieve games, offseting the front by a number*.
Lastly, you can run with any combination of the query parameters. The given request is *6. Retrieve 3 games, sorted by price and offset by 1*.

### DELETE

From delete_requests.http file, run *1. Delete a game by ID*.
Use the same ID and check it with the request from earlier, *2. Retrieve a game by ID*.
Either that or you can run *1. Retrieve ALL games* and note that it is deleted from the database


### Idempotent routes

All GET, DELETE routes are idempotent, because an idempotent method is a method that can be invoked many times with the same result.
All the GET routes can be called multiple times and there will be no changes to the response as long as the request remains the same.
For the DELETE requests, the first request will delete the game from the database if it exists with a 200 OK response. However subsequent similar requests will return 404 response as the game is already deleted. For the batch delete, the response will not change either. 

### Authorization route

The POST and DELETE routes require an **apikey** in the Headers which is like a password to access. If the apikey is missing or incorrect, the request will result in a 401 Unauthorized response.

### Special batch delete

From delete_requests.http file, *run 2. Delete a batch of games* by either name | above_price | below_price
The request will delete multiple games according to the given parameters in the request body.

```
{
    "name": "Poke",
    "above_price": 29.99,
    "below_price": 1
}
```

name: delete all games whose name contains the given substring.
above_price: delete all games whose price >= given price.
below_price: delete all games whose price < given price.

### Improvements to be made

Currently, creating a game takes O(n) time because I loop through the existing game IDs to check that the generated game ID is not a duplicate. I can actually use SISMEMBER command to check if the generated ID exists in the existing game IDs set which has a time complexity of O(1). So I only need to generate another game ID if SISMEMBER returns True, thus improving the current time needed to create a game. 
