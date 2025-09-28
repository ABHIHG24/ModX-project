import grpc
import time
import threading
from concurrent import futures
from services import vector_store, vector_indexer
from services.vector_store import delete_document_from_store

# gRPC imports
import ai_pb2
import ai_pb2_grpc

# Your AI logic
from core import orchestrator

# FastAPI for Render health check
from fastapi import FastAPI
import uvicorn

# -------------------------------
# 1️⃣ gRPC Service Implementation
# -------------------------------
class AIServiceServicer(ai_pb2_grpc.AIServiceServicer):
    def GetChatbotResponse(self, request, context):
        print(f"[gRPC] Received chatbot query: '{request.query}'")
        answer_text = orchestrator.process_query(request.query)
        return ai_pb2.ChatReply(answer=answer_text)

    def GetUserRecommendations(self, request, context):
        doc_ids = vector_store.find_similar_document_ids(request.query_text, n_results=10)
        return ai_pb2.RecommendationReply(recommended_ids=doc_ids)

    def GetRelatedProjects(self, request, context):
        doc_ids = vector_store.find_similar_document_ids(request.query_text, n_results=6)
        return ai_pb2.RecommendationReply(recommended_ids=doc_ids)

    def SearchProjects(self, request, context):
        doc_ids = vector_store.find_similar_document_ids(request.search_query, n_results=6)
        return ai_pb2.RecommendationReply(recommended_ids=doc_ids)

    def IndexNewData(self, request, context):
        result = vector_indexer.index_new_data()
        return ai_pb2.IndexReply(status=result)

    def DeleteProjectFromIndex(self, request, context):
        project_id = request.project_id
        doc_id = f"project_{project_id}"
        delete_document_from_store(doc_id)
        return ai_pb2.IndexingResponse(message=f"Deleted {doc_id} from index")


def serve_grpc():
    """Start the gRPC server on port 50051."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ai_pb2_grpc.add_AIServiceServicer_to_server(AIServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("✅ gRPC server started on port 50051")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

# -------------------------------
# 2️⃣ FastAPI Health Check Server
# -------------------------------
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Service is running 🚀"}

def serve_http():
    """Start FastAPI health check server on port 10000."""
    print("✅ FastAPI health check server started on port 10000")
    uvicorn.run(app, host="0.0.0.0", port=10000)

# -------------------------------
# 3️⃣ Run both servers concurrently
# -------------------------------
if __name__ == "__main__":
    grpc_thread = threading.Thread(target=serve_grpc)
    grpc_thread.start()

    serve_http()  # Run FastAPI in main thread
