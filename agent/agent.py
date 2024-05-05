import os
import json
import subprocess
import traceback

import openai
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def list_files(folder: str = ".") -> list:
    cmd = ["ls", folder]
    result = subprocess.check_output(cmd).decode()
    return result.split('\n')


def read_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    folder = os.path.dirname(file_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    user_int = input(f'About to write to {file_path}:\n {
                     content} \nPress enter to continue or "No" to skip...')
    if user_int == "No":
        return "Skipped writing to file!"
    with open(file_path, 'w') as f:
        f.write(content)
    return f"Written to {file_path}!"


def cd_to_path(path: str) -> str:
    try:
        os.chdir(path)
        return f"Changed directory to {path}"
    except Exception as e:
        traceback_str = traceback.format_exc()
        return traceback_str


def make_dir(directory: str) -> str:
    try:
        os.makedirs(directory, exist_ok=True)
        return f"Directory {directory} created!"
    except Exception as e:
        traceback_str = traceback.format_exc()
        return traceback_str


def run_awscli_command(command: str) -> str:
    try:
        cmd = command.split(" ")
        if cmd[0] != "aws":
            cmd = ["aws"] + cmd
        output = subprocess.check_output(cmd).decode()
        return output
    except Exception as e:
        tarceback_str = traceback.format_exc()
        return tarceback_str


def edit_main_tf(maintf_folder: str, code: str) -> None:
    with open(maintf_folder + "/main.tf", "w") as f:
        f.write(code)

    return f"{maintf_folder + "/main.tf"} file updated!"


def terraform_init() -> str:
    try:
        result = subprocess.run(
            ["terraform", "init"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        try:
            # generate graph from the terraform (terraform graph | dot -Tpng > graph.png)
            subprocess.run(
                ["terraform", "graph", "|", "dot", "-Tpng", ">", "graph.png"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # show graph png:
            plt.imshow(mpimg.imread('graph.png'))
            plt.show()
        except Exception as e:
            print("Error generating graph: ", e)
            print("Skipping graph generation...")

        return result.stdout + " / " + result.stdout
    except Exception:
        # Capture and return traceback if an exception occurs
        traceback_str = traceback.format_exc()
        return traceback_str


def terraform_plan() -> str:
    try:
        result = subprocess.run(
            ["terraform", "plan"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.stdout + " / " + result.stdout
    except Exception:
        traceback_str = traceback.format_exc()
        return traceback_str


def terraform_apply() -> str:
    try:
        result = subprocess.run(["terraform", "apply", "-auto-approve"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.stdout + " / " + result.stdout
    except Exception:
        traceback_str = traceback.format_exc()
        return traceback_str


def terraform_destroy() -> str:
    try:
        result = subprocess.run(["terraform", "destroy", "-auto-approve"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.stdout + " / " + result.stdout
    except Exception:
        traceback_str = traceback.format_exc()
        return traceback_str


def ask_input_from_user(prompt: str) -> str:
    return input(prompt)


def run_agent(task: str, path: str) -> None:

    sys_prompt = f"""You are an AI agent that function as a highly skilled DevOps engineer with a specialization in using Terraform for infrastructure as code and deploying applications on Amazon Web Services (AWS).
The agent possesses deep knowledge of cloud architectures, security best practices, and efficient resource management.

Do not ask the user for input unless it is extremely necessary. You, as highly skilled DevOps, should make decisions by yourself and only ask the user for input when it is absolutely required.

Current PWD: {os.getcwd()}

RULES:
1. You must use Terraform for managing resoucres. Only use AWS CLI to list and check resources.
2. Always use region us-east-1
3. Make sure you understand the code you need to work with before executing the given task.
"""
    name_to_function = {
        "list_files": list_files,
        "read_file": read_file,
        "write_file": write_file,
        "edit_main_tf": edit_main_tf,
        "terraform_init": terraform_init,
        "terraform_plan": terraform_plan,
        "terraform_apply": terraform_apply,
        "ask_input_from_user": ask_input_from_user,
        "run_awscli_command": run_awscli_command,
        "make_dir": make_dir,
        "cd_to_path": cd_to_path,
    }
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
                "name": "write_file",
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
        },
        {
            "type": "function",
            "function": {
                "name": "make_dir",
                "description": "Create a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory to create",
                        },
                    },
                    "required": ["directory"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "cd_to_path",
                "description": "Change directory to the specified path",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to change to",
                        },
                    },
                    "required": ["path"],
                },
            },
        }
    ]

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Your task is: {
            task}. You should create whatever resources are needed to accomplish this task."},
    ]

    running = True
    respone_without_tools = 0
    while running:
        print('\33[32m\n\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ Agent Loop ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n\33[0m')
        try:
            completion = client.chat.completions.create(
                model="gpt-4-turbo",
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
                print(f'\33[36mkwargs: {tool.function.arguments}\33[0m')
                kwargs = json.loads(tool.function.arguments)
                function_to_call = name_to_function.get(tool.function.name)
                if function_to_call:
                    result = function_to_call(**kwargs)
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": str(result)})
                else:
                    messages.append(
                        {"role": "tool", "tool_call_id": tool.id, "content": "Tool not found!"})

                print("***"*10)
                print(f'\33[33m\nResult:\n{messages[-1]}\33[0m')
                print("----")
                print("----")
                print(f'\33[33m\nResult:\n{messages[-1]["content"]}\33[0m')
                print("***"*10)
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
