from litellm import completion


def send_messages(model, messages: list) -> str:

    response = completion(
        model=model,
        messages=messages)

    print(response['usage'])

    return response.choices[0].message.content
