# Fetch Rewards Coding Excercise
Backend Software Engineering

This app is an HTTP web service built in [Python](https://www.python.org/) and the [FastAPI](https://fastapi.tiangolo.com/) framework 

## Assumptions

### Environment
* [python3.10](https://www.python.org/downloads/release/python-3100/)
* ***Mac*** or linux based environment or optionally docker

### Solution

As outlined in the problem statement and from the context gathered in the directions throughout I am focusing on a single user.  With more time and more complex requirements I would assume a more complex data model for payers/users/points.  

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
cd app
uvicorn main:app --reload
```
---

### Run Tests

```bash
docker run -it -v ${PWD}/:/usr/src/app fetch_rewards pytest --cov=app
```

or 

```bash
pytest --cov=app
```

## Development Notes

I'm running a docker container for development.  

Any changes will be picked up by the servers reload feature

```bash
docker run -it -p 8000:80 -v ${PWD}/app:/usr/src/app fetch_rewards 
```

or locally

```bash
uvicorn app/main:app --reload
```


## Challenge notes / questions / assumptions

```json

{ "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" }
{ "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" }
{ "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" }
{ "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" }
{ "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }

```