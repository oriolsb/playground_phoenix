"""Start the Katacombs REST API: python -m brown_field"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("brown_field.api:app", host="127.0.0.1", port=8000)
