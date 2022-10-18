# Fetch Rewards Coding Excercise
Backend Software Engineering

This app is an HTTP web service built in [Python](https://www.python.org/) and the [FastAPI](https://fastapi.tiangolo.com/) framework 

## Assumptions

### Environment
* [python3.10](https://www.python.org/downloads/release/python-3100/)
* ***Mac*** or linux based environment or optionally docker

### Solution

As outlined in the problem statement and from the context gathered in the directions throughout I am focusing on a single user.  With more time and more complex requirements I would assume a more complex data model for payers/users/points.  

### Transactions

Since the provided series of transactions included a negative transaction with a timestamp that is before there was enough points to be spent for said transaction I have assumed that there is a processing of these transactions before a spend would happen versus validating these on the add transaction call.  I have opinions on this and questions but this is how I choose to solve the problem based on the context.

---

## Quickstart

Docker

```bash
docker build -t fetch_rewards .
docker run -it -p 8000:80 -v ${PWD}/:/usr/src/app fetch_rewards
```

or 

Linux based

```bash
python3.10 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
---

### OpenAPI Documentation

After app is running open [documentation here](http://localhost:8000/)

### Run Tests

```bash
docker run -it -v ${PWD}/:/usr/src/app fetch_rewards pytest --cov-report html --cov=app
```

or 

```bash
pytest  --cov-report html --cov=app
```

Open ```./htmlcov/index.html``` in a browser to view coverage report

## Development Notes

I'm running a docker container for development.  

Any changes will be picked up by the servers reload feature

```bash
docker run -it -p 8000:80 -v ${PWD}/app:/usr/src/app fetch_rewards 
```

or locally

```bash
uvicorn app.main:app --reload
```


## Challenge notes / questions / assumptions

```json

{ "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" }
{ "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" }
{ "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" }
{ "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" }
{ "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }

```