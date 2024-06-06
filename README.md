Please "reply all" to the thread that sent you this assessment invitation. In your reply, include the following:

Github repo link of the project
Link to the hosted serverless compute application:


POST https://4rkfjzh87b.execute-api.us-west-1.amazonaws.com/knightpath
body_params: 
```
{
  "body": {
    "source": "A1",
    "target": "D5"
  }
}
```

response:

```
{
    "statusCode": 201,
    "body": "Operation Id fc760f34-95a2-4aa6-b6f4-4999f8f64329 was created. Please query it to find your results."
}
```

GET https://4rkfjzh87b.execute-api.us-west-1.amazonaws.com/knightpath?operationId=fc760f34-95a2-4aa6-b6f4-4999f8f64329

response:

```
{
    "starting": "A1",
    "ending": "D5",
    "shortestPath": "A1:C2:B4:D5",
    "numberOfMoves": "3",
    "operationId": "fc760f34-95a2-4aa6-b6f4-4999f8f64329"
}
```


In a few paragraphs, explain your key design choices and implementation. Include any notes you wish to let us know as we review your project.


For this project, I chose to setup 3 serverless functions on AWS. I chose to store my data in dynamodb, since I felt that it would serve my storage needs well as I didn't have to worry about strong consistency considerations and my data is not relational in nature. 

I chose two tables - one table meant to store knightpath operations and results, and another table used to store computed {source}->{target} paths. The second table is meant to be an optimization, to avoid having to calculate paths twice. I was considering using dynamo as my cache mechanism while calculating paths, but decided against it since the chess board itself is small in size (8*8), so my program is not really going to be cpu-bound.


I chose to create restful endpoints and to that end, I did not comingle query params with a post request as the example github repo intended.

The actual implementation of the knightspath algorithm uses breadth first search and a visited set to check to see if calculated paths have already been computed.
