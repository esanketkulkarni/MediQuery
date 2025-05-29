from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import os
from dotenv import load_dotenv
from uuid import UUID
import traceback
load_dotenv()

app = FastAPI(debug=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# === Predefined topic -> domain mappings ===
DOMAIN_FILTERS_BY_TOPIC = {
    "drug_info": ["drugs.com", "rxlist.com"],
    "symptoms": ["mayoclinic.org", "clevelandclinic.org"],
    "treatment_guidelines": ["msdmanuals.com", "cdc.gov"],
    "public_health": ["cdc.gov", "who.int"],
    "clinical_research": ["pubmed.ncbi.nlm.nih.gov", "nejm.org"]
}

# === Request/Response Models ===
class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    search_context_size: str


class Message(BaseModel):
    role: str
    content: str


class Delta(BaseModel):
    role: str
    content: str


class Choice(BaseModel):
    index: int
    finish_reason: str
    message: Message
    delta: Delta


class CompletionResponse(BaseModel):
    id: UUID
    model: str
    created: int
    usage: Usage
    citations: list[str]
    object: str
    choices: list[Choice]

class TopicFormat(BaseModel):
    topic_name: str

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    topic: str
    domain_filter: list
    answer: str
    citations: list

# === Environment variable for API key ===
SONAR_API_KEY = os.getenv("SONAR_API_KEY")
SONAR_API_URL = "https://api.perplexity.ai/chat/completions"

async def classify_topic(question: str) -> str:
    print(f"Classifying topic: {question}")
    try:
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "Classify the user medical question into one of these categories: drug_info, symptoms, treatment_guidelines, public_health, clinical_research, diagnosis_support, Unknown. Ensure to strictly return one of these values."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            "max_tokens": 50,
            "temperature": 0.2,
            "top_p": 0.9,
            "search_domain_filter": [],
            "return_images": False,
            "return_related_questions": False,
            "top_k": 0,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": TopicFormat.model_json_schema()},
            },
            "web_search_options": {"search_context_size": "low"}
        }
        
        print(f"\n=== Classification Request Details ===")
        print(f"URL: {SONAR_API_URL}")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    SONAR_API_URL,
                    headers={
                        "Authorization": f"Bearer {SONAR_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                print(f"\n=== Classification Response Details ===")
                print(f"Status Code: {resp.status_code}")
                print(f"Headers: {dict(resp.headers)}")
                print(f"Response Text: {resp.text[:1000]}...")  # Print first 1000 chars of response
                
                resp.raise_for_status()
                result = resp.json()
                output = CompletionResponse.model_validate(result)
                topic = TopicFormat.model_validate(json.loads(output.choices[0].message.content))
                print(f"\n=== Classification Result ===")
                print(f"Detected Topic: {topic.topic_name}")
                return topic.topic_name
            except httpx.HTTPError as http_err:
                print(f"\n=== HTTP Error Details ===")
                print(f"HTTP Error occurred: {http_err}")
                print(f"Error Response: {getattr(http_err, 'response', None)}")
                print(f"Request Info: {getattr(http_err, 'request', None)}")
                raise
    except Exception as e:
        print("\n=== Exception Details ===")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")
        print("Full Traceback:")
        traceback.print_exc()
        raise

async def query_sonar(question: str, domains: list) -> CompletionResponse:
    try:
        payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "max_tokens": 5000,
                "temperature": 0.2,
                "top_p": 0.9,
                "search_domain_filter": domains,
                "return_images": False,
                "return_related_questions": False,
                "top_k": 0,
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 1,
                "web_search_options": {"search_context_size": "low"},
                "chain_of_thought": True,
                "include_citations": True
            }

        print(f"\n=== HTTP Request Details ===")
        print(f"URL: {SONAR_API_URL}")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(3000.0)) as client:
            try:
                resp = await client.post(
                    SONAR_API_URL,
                    headers={"Authorization": f"Bearer {SONAR_API_KEY}"},
                    json=payload
                )
                print(f"\n=== HTTP Response Details ===")
                print(f"Status Code: {resp.status_code}")
                print(f"Response Text: {resp.text}...")
                
                resp.raise_for_status()
                result = resp.json()
                output = CompletionResponse.model_validate(result)
                return output
            except httpx.HTTPError as http_err:
                print(f"\n=== HTTP Error Details ===")
                print(f"HTTP Error occurred: {http_err}")
                print(f"Error Response: {getattr(http_err, 'response', None)}")
                print(f"Request Info: {getattr(http_err, 'request', None)}")
                raise
    except Exception as e:
        print("\n=== Exception Details ===")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Message: {str(e)}")
        print("Full Traceback:")
        traceback.print_exc()
        raise

@app.post("/ask", response_model=QueryResponse)
async def ask_medical_question(req: QueryRequest):
    print("Received request")
    question = req.question
    try:
        print("Classifying topic")
        topic = await classify_topic(question)
        domains = DOMAIN_FILTERS_BY_TOPIC.get(topic)
        print("Domains", domains)
        if not domains:
            raise HTTPException(status_code=400, detail=f"Unknown topic: {topic}")

        print("Querying Sonar")
        sonar_result = await query_sonar(question, domains)
        print("Sonar result", sonar_result)
        return QueryResponse(
            topic=topic,
            domain_filter=domains,
            answer=sonar_result.choices[0].message.content,
            citations=sonar_result.citations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))