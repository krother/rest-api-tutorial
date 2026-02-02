Hi Nikita,



I have deployed claude-opus-4-5 in our factory's cloud environment exclusively for the purpose of the next week's training. Immediately after the training the resource group will be deletded. Here are the endpoint and keys:



endpoint = "https://mwb-fastapi-foundry-training.services.ai.azure.com/anthropic/"
 deployment_name = "claude-opus-4-5"
 `api_key = "* * * * * * * * * * *"



Sample Code:
 

> from anthropic import AnthropicFoundry 
>
> 
>
> endpoint = "https://mwb-fastapi-foundry-training.services.ai.azure.com/anthropic/" 
>
> deployment_name = "claude-opus-4-5" 
>
> api_key = "YOUR_API_KEY" 
>
> 
>
> client = AnthropicFoundry( api_key=api_key, base_url=endpoint ) 
>
> 
>
> message = client.messages.create( model=deployment_name, messages=[ {"role": "user", "content": "What is the capital of France?"} ], max_tokens=1024, ) 
>
> 
>
> print(message.content)