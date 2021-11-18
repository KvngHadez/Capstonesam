import json
HEADERS = {'Access-Control-Allow-Headers': 'Content-Type',
           'Access-Control-Allow-Origin': '*',
           'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'}

# import requests

def handle_exception(status, error_data):
    """
    Exception handler for endpoints. 
    Use this in except block or return statement to return relvent error 
    message to the client
    :param int status: HTTP status code to send back. Default 500
    :param str error_data: Error data to send back
    """
    return {
        "statusCode": status,
        'headers': HEADERS,
        "body": json.dumps(error_data, indent=2),
    }


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    if(event['body'] == None):
       return handle_exception(405, {"message" : "You have given us any information"})
    else: 
        if (event['httpMethod'] == 'POST'):
                event_body = json.loads(event['body'])
                return post(event_body)
        else:
                return handle_exception(405, {"message": "Method not allowed."})

def post(event_body):

    try:
        if (not (event_body['distance'] == None)) and (not (event_body['time'] == None)) and (not (event_body['direction'] == None)):
            return {
                    "statusCode": 200,
                    'headers': HEADERS,
                    "body": json.dumps({"distance": event_body['distance'], "time":event_body['time'], "direction":event_body['direction']}, indent=2),
            }
        else:
             return handle_exception(405, {"message": "Your missing an input"})

    except Exception as e:
         return handle_exception(500, {"message": "Something went wrong. more info: {}".format(e)})
