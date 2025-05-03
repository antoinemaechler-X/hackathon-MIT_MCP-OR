from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from your frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only! Use your real domain in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Your model functions to implement ---
def solve_model(start, end):
    # For debugging: just return a message
    return {"message": "Solving model"}

def query_model(comment):
    # TODO: Implement your logic here
    # Example return:
    return {"status": "success", "echo": comment}

# --- API Endpoints ---

@app.post("/api/solve")
async def solve(request: Request):
    data = await request.json()
    start = data.get("start")
    end = data.get("end")
    result = solve_model(start, end)
    return result

@app.post("/api/comment")
async def comment(request: Request):
    data = await request.json()
    comment = data.get("comment")
    result = query_model(comment)
    return result