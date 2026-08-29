import aioboto3

from app.core.config import settings


async def send_message(message_body: str, delay_seconds: int = 0):
    """Send a message to AWS SQS (async using aioboto3).

    Requires AWS credentials to be available in environment or IAM role.
    """
    session = aioboto3.Session()
    async with session.client("sqs", region_name=settings.AWS_REGION) as client:
        await client.send_message(QueueUrl=settings.AWS_SQS_QUEUE_URL, MessageBody=message_body, DelaySeconds=delay_seconds)


async def receive_messages(max_number: int = 10, wait_time: int = 10):
    session = aioboto3.Session()
    async with session.client("sqs", region_name=settings.AWS_REGION) as client:
        resp = await client.receive_message(QueueUrl=settings.AWS_SQS_QUEUE_URL, MaxNumberOfMessages=max_number, WaitTimeSeconds=wait_time)
        return resp.get("Messages", [])
