import json
import boto3
import streamlit as st
from typing import Dict, List

# st.title('🦜🔗 Quickstart App')
session = boto3.session.Session()
endpoint_name = "jumpstart-dft-hf-llm-mistral-7b-instruct"

def format_instructions(instructions: List[Dict[str, str]]) -> List[str]:
    """Format instructions where conversation roles must alternate user/assistant/user/assistant/..."""
    prompt: List[str] = []
    for user, answer in zip(instructions[::2], instructions[1::2]):
        prompt.extend(["<s>", "[INST] ", (user["content"]).strip(), " [/INST] ", (answer["content"]).strip(), "</s>"])
    prompt.extend(["<s>", "[INST] ", (instructions[-1]["content"]).strip(), " [/INST] "])
    return "".join(prompt)


def print_instructions(prompt: str, response: str) -> None:
    bold, unbold = '\033[1m', '\033[0m'
    print(f"{bold}> Input{unbold}\n{prompt}\n\n{bold}> Output{unbold}\n{response[0]['generated_text']}\n")


def generate_payload(instructions: List[Dict[str, str]]) -> Dict[str, str]:
    return {
    "inputs": format_instructions(instructions),
    "parameters": {"max_new_tokens": 256, "do_sample": True}
}



def query_endpoint(payload):
    client = session.client('sagemaker-runtime')
    response = client.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="application/json", Body=json.dumps(payload).encode("utf-8")
    )
    response = response["Body"].read().decode("utf8")
    response = json.loads(response)
    return response

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# User-provided prompt
if prompt := st.chat_input(disabled=False):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# # Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            print(f'raw prompt: {prompt}')
            response = query_endpoint(generate_payload([{"role": "user", "content": prompt}]))
            print(f'raw response: {str(response)}')
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item['generated_text']
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)