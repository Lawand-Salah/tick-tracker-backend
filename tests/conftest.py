import httpx


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))