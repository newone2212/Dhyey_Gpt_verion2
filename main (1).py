from flask import Flask, request, jsonify
import subprocess
import socket
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

app = Flask(__name__)

# Initialize the variable at the global level
ollama_subprocess = None

#@app.route('/start_ollama', methods=['GET'])
def stop_ollama():
    global ollama_subprocess
    if ollama_subprocess is not None:
        ollama_subprocess.terminate()
        ollama_subprocess.wait()
        ollama_subprocess = None
        return
    else:
        return 

def is_port_in_use(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
    
def start_ollama():
    if not is_port_in_use(11434):
       global ollama_subprocess
       # Start Ollama server
       ollama_subprocess = subprocess.Popen(['ollama', 'serve'])

    else:
       return
      
@app.route('/invoke_chat', methods=['POST'])
def invoke_chat():
    start_ollama()  
    global ollama_subprocess
    # if ollama_subprocess is None or ollama_subprocess.poll() is not None:
    #     return jsonify({"error": "Ollama server is not running"}), 400
    
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        
        chat = ChatOllama(model="llama3")
        aim_response = chat.invoke([HumanMessage(content=user_message)])
        
        # Assuming the aim_response is an AIMessage object that needs to be serialized
        # Extract needed data and form a serializable response
        response_content = {
            "content": aim_response.content,
            "type": aim_response.type,
            # Add other fields as necessary
        }
        stop_ollama()
        return jsonify({"response": response_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == "__main__":
    app.run(port=5000)
