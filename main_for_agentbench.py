from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Initialize the transformer model
model = pipeline('text-generation', model='gpt2')


@app.route('/predict', methods=['POST'])
def predict():
    # Extract data from request
    data = request.json
    print("data", data)
    prompt = data.get('prompt', '')  # Use .get to avoid KeyError
    print("prompt", prompt)
    # Generate a response using the model
    response = model(prompt, max_length=50, num_return_sequences=1)
    print("response:", response)
    # Extract the generated text from the response
    full_response = response[0]['generated_text']
    print("full response:", full_response)
    # Extract only the agent's response
    # Assuming the agent's response is after "AGENT:" and ends at the next newline
    agent_response = full_response.split("AGENT:")[1].split('\n')[0].strip() if "AGENT:" in full_response else ""

    print("Generated agent response:", agent_response)

    # Return only the agent's response
    return jsonify([{"generated_text": agent_response}])


if __name__ == '__main__':
    app.run(debug=True, port=6000)

