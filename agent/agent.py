import os
import json
import subprocess
import traceback

import openai

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def list_files(folder: str = ".") -> list:
    cmd = ["ls", folder]
    result = subprocess.check_output(cmd).decode()
    return result.split('\n')


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def rewrite_file(file_path: str, content: str) -> None:
    user_int = input(f'About to write to {file_path}:\n {content} \nPress enter to continue or "No" to skip...')
    if user_int == "No":
        return None
    with open(file_path, 'w') as f:
        f.write(content)

def mkdir_terraform():
    cmd = ["mkdir", "terraform"]
    subprocess.run(cmd)

def create_main_tf():
    with open("terraform/main.tf", "w") as f:
        pass

def terraform_init() -> None:
    cmd = ["terraform", "init"]
    subprocess.run(cmd)


def terraform_plan() -> None:
    cmd = ["terraform", "plan"]
    subprocess.run(cmd)


def terraform_apply() -> None:
    cmd = ["terraform", "apply", "-auto-approve"]
    subprocess.run(cmd)


def terraform_destroy() -> None:
    cmd = ["terraform", "destroy", "-auto-approve"]
    subprocess.run(cmd)


def run_agent(task: str, path: str) -> None:

    sys_prompt = """You are an AI agent that function as a highly skilled DevOps engineer with a specialization in using Terraform for infrastructure as code and deploying applications on Amazon Web Services (AWS).
The agent possesses deep knowledge of cloud architectures, security best practices, and efficient resource management.
"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List all files in a folder",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "folder": {
                            "type": "string",
                            "description": "The folder to list files from",
                        },
                    },
                    "required": ["folder"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        },
                    },
                    "required": ["file_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "rewrite_file",
                "description": "Rewrite a file with new content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to rewrite",
                        },
                        "content": {
                            "type": "string",
                            "description": "The new content to write to the file",
                        },
                    },
                    "required": ["file_path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mkdir_terraform",
                "description": "make a terraform directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_main_tf",
                "description": "make main.tf file in terraform directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                },
            },
        },
    ]

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Your task is: {task} in project {path}"},
    ]

    running = True
    while running:
        print('\33[32m~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ Agent Loop ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\33[0m')
        try:
            completion = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=messages,
                tools=tools,
            )
            new_message = completion.choices[0].message
            print(f'\33[32mAgent response: {new_message}\33[0m')
            messages.append(new_message)

            print("Agent: ", new_message.content)

            if new_message.tool_calls is None:
                running = False
                print("No tool calls - FINISH!")
                return ""

            # Execute tools:
            for tool in new_message.tool_calls:
                print(f'\33[36mAgent is executing tool: {tool.function.name}\33[0m')
                print(f'\33[36margs: {tool.function.arguments}\33[0m')
                args = json.loads(tool.function.arguments)

                if tool.function.name == "list_files":
                    result = list_files(args['folder'])
                    print(f'\33[33mResult: {result}\33[0m')

                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": str(result)})
                elif tool.function.name == "mkdir_terraform":
                    result = mkdir_terraform()
                    print(f'\33[33mResult: {result}\33[0m')

                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": str(result)})
                elif tool.function.name == "create_main_tf":
                    result = create_main_tf()
                    print(f'\33[33mResult: {result}\33[0m')
                else:
                    print("FUCCCCK")

                print("----")

        except Exception as e:
            running = False
            print(traceback.format_exc())
            return ""


if __name__ == '__main__':
    user_input = input("\033[1;32;40mDevOpAI % \033[0;37;40m")
    run_agent(task=user_input, path='.')
