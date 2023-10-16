import io
import json

# Example class that processes an inference stream:
class SmrInferenceStream:
    
    def __init__(self, sagemaker_runtime, endpoint_name):
        self.sagemaker_runtime = sagemaker_runtime
        self.endpoint_name = endpoint_name
        # A buffered I/O stream to combine the payload parts:
        self.buff = io.BytesIO() 
        self.read_pos = 0
        
    def stream_inference(self, request_body):
        # Gets a streaming inference response 
        # from the specified model endpoint:
        response = self.sagemaker_runtime\
            .invoke_endpoint_with_response_stream(
                EndpointName=self.endpoint_name, 
                Body=json.dumps(request_body), 
                ContentType="application/json"
        )
        # Gets the EventStream object returned by the SDK:
        event_stream = response['Body']
        for event in event_stream:
            print(f'raw event:{event}')
            # Passes the contents of each payload part
            # to be concatenated:
            self._write(event['PayloadPart']['Bytes'])
            # Iterates over lines to parse whole JSON objects:
            for line in self._readlines():
                # byte_string.decode("utf-8")
                # print(f'raw line:{line.decode("utf-8")}')
                # resp = json.loads(line[0])
                # part = resp.get("generated_text")
                # Returns parts incrementally:
                yield line
    
    # Writes to the buffer to concatenate the contents of the parts:
    def _write(self, content):
        self.buff.seek(0, io.SEEK_END)
        self.buff.write(content)

    # The JSON objects in buffer end with '\n'.
    # This method reads lines to yield a series of JSON objects:
    def _readlines(self):
        self.buff.seek(self.read_pos)
        for line in self.buff.readlines():
            self.read_pos += len(line)
            yield line[:-1]