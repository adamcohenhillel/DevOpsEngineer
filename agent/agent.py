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
    user_int = input(f'About to write to {file_path}:\n {
                     content} \nPress enter to continue or "No" to skip...')
    if user_int == "No":
        return None
    with open(file_path, 'w') as f:
        f.write(content)


def run_awscli_command(command: str) -> str:
    try:
        cmd = command.split(" ")
        output = subprocess.check_output(cmd).decode()
        return output
    except Exception as e:
        return str(e)


def edit_main_tf(code: str) -> None:
    os.makedirs("terraform", exist_ok=True)
    with open("terraform/main.tf", "w") as f:
        f.write(code)


def terraform_init(folder: str = "./terraform") -> None:
    try:
        os.chdir(folder)
        cmd = ["terraform", "init"]
        subprocess.run(cmd)
        os.chdir("..")
        return "Terraform initialized!"
    except Exception as e:
        print("************"*10)
        print(e)
        print("************"*10)
        return str(e)


def terraform_plan(folder: str = "./terraform") -> str:
    try:
        os.chdir(folder)
        cmd = ["terraform", "plan"]
        output = subprocess.check_output(cmd).decode()
        os.chdir("..")
        return output
    except Exception as e:
        return str(e)


def terraform_apply(folder: str = "./terraform") -> None:
    try:
        os.chdir(folder)
        cmd = ["terraform", "apply", "-auto-approve"]
        subprocess.run(cmd)
        os.chdir("..")
        return "Terraform applied!"
    except Exception as e:
        return str(e)


def terraform_destroy(folder: str = "./terraform") -> None:
    try:
        os.chdir(folder)
        cmd = ["terraform", "destroy", "-auto-approve"]
        subprocess.run(cmd)
        os.chdir("..")
        return "Terraform destroyed!"
    except Exception as e:
        return str(e)


def ask_input_from_user(prompt: str) -> str:
    return input(prompt)


def run_agent(task: str, path: str) -> None:

    sys_prompt = """You are an AI agent that function as a highly skilled DevOps engineer with a specialization in using Terraform for infrastructure as code and deploying applications on Amazon Web Services (AWS).
The agent possesses deep knowledge of cloud architectures, security best practices, and efficient resource management.

Do not ask the user for input unless it is extremely necessary. You, as highly skilled DevOps, should make decisions by yourself and only ask the user for input when it is absolutely required.

You can use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables to authenticate to AWS.

RULES:
1. You must use Terraform for managing resoucres. Only use AWS CLI to list and check resources.
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
                "name": "write_main_tf",
                "description": "Write code into main.tf file in terraform directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to write to main.tf",
                        },
                    },
                },
                "required": ["code"],
            },
        },
        {
            "type": "function",
            "function": {
                "name": "terraform_init",
                "description": "Initialize terraform in the terraform directory",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "terraform_plan",
                "description": "Run terraform plan",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "terraform_apply",
                "description": "Run terraform apply",
            },
        },
        {
            "type": "function",
            "function": {
                "name": "ask_input_from_user",
                "description": "Ask for input from the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "What to ask the user for",
                        },
                    },
                },
                "required": ["prompt"],
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_awscli_command",
                "description": "Run an AWS CLI command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The AWS CLI command to run",
                        },
                    },
                },
                "required": ["command"],
            },
        }
    ]

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Your task is: {task} in project {path}"},
    ]

    running = True
    respone_without_tools = 0
    while running:
        print('\33[32m\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ Agent Loop ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n\33[0m')
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
                respone_without_tools += 1
                if respone_without_tools == 2:
                    running = False
                    print("No tool calls - FINISH!")
                    return ""
                else:
                    messages.append(
                        {"role": "user", "content": "You did not provide any tools to execute, if you don't use any tools, the program will exit."})

                    print(
                        f"\33[33m\nResult:\nYou did not provide any tools to execute, if you don't use any tools, the program will exit.\33[0m")

                    continue

            respone_without_tools = 0
            for tool in new_message.tool_calls:
                print(f'\33[36mAgent is executing tool: {
                      tool.function.name}\33[0m')
                print(f'\33[36margs: {tool.function.arguments}\33[0m')
                args = json.loads(tool.function.arguments)

                if tool.function.name == "list_files":
                    result = list_files(args['folder'])
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": str(result)})

                elif tool.function.name == "read_file":
                    result = read_file(args['file_path'])
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": result})

                elif tool.function.name == "rewrite_file":
                    rewrite_file(args['file_path'], args['content'])
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": "File rewritten!"})

                elif tool.function.name == "write_main_tf":
                    edit_main_tf(args['code'])
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": "Code written to main.tf!"})

                elif tool.function.name == "ask_input_from_user":
                    result = ask_input_from_user(args['prompt'])
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": result})

                elif tool.function.name == "terraform_init":
                    result = terraform_init()
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": result})

                elif tool.function.name == "terraform_plan":
                    result = terraform_plan()
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": result})

                elif tool.function.name == "terraform_apply":
                    terraform_apply()
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": result})

                elif tool.function.name == "run_awscli_command":
                    result = run_awscli_command(args['command'])
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": result})

                else:
                    print("FUCCCCK")

                print(f'\33[33m\nResult:\n{messages[-1]["content"]}\33[0m')
                print("----")

        except Exception as e:
            running = False
            print(traceback.format_exc())
            return ""


if __name__ == '__main__':
    # user_input = input("\033[1;31;40mDevOpAI % \033[0;37;40m")
    # make user_input a orange color background:
    user_input = input("\033[1;31;43mDevOpAI % \033[0;37;40m")
    run_agent(task=user_input, path='.')
