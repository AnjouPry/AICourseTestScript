import json
import nbformat
import subprocess
import os
import tempfile
import sys
import logging
import ast

# Configuration logging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def argv_getter(argv, task_file):
    """
    Extract and validate the file paths from the command line argument argv, ensure their correctness, and return the
    source file path and output file path.
    :param argv: Contains a list of command line arguments.
    :param task_file: A string that represents the name of the task and is used to build the path to the source file.
    :return:
    """
    if len(argv) != 4:
        logging.error("Usage: python pingce.py <source_file_path> <executable_file_path> <result_json_path>")
        sys.exit(1)

    # Concatenate the folder path from argv[1] with the value of the task_name parameter to form the full path of
    # source_file. task_name is a.py file, so the path points to the Python file for the task.
    source_file = f'{argv[1]}/{task_file}'
    output_file = f'{argv[3]}'

    if not os.path.isfile(source_file):
        logging.error("Error: Source file %s does not exist.", source_file)
        sys.exit(1)
    return source_file, output_file


def save_json(output, output_file):
    """
    Save the JSON data to a file and record the error and exit the program if the save fails.
    :param output: Python object to save.
    :param output_file: Destination file path.
    :return:
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(json.dumps(output, ensure_ascii=False, indent=4))
    except IOError as e:
        logging.error("Could not write to file %s. %s", output_file, str(e))
        sys.exit(1)


def load_notebook(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return nbformat.read(f, as_version=4)


def syntax_check(student_code, task_point):
    try:
        parsed_code = ast.parse(student_code)
        syntax_error = False
        syntax_error_msg = None
    except SyntaxError as e:
        syntax_error = True
        syntax_error_msg = f"任务点{task_point}：    语法错误：{e}\n"

    return syntax_error, syntax_error_msg


def execute_code(student_code, template_path, insert_marker='# INSERT STUDENT CODE HERE', conda_env_name=None):
    """
    Insert the student-written code into a template file, execute the code in a temporary file, and capture the results
    of the execution.
    :param student_code:
    :param template_path:
    :param insert_marker:
    :param conda_env_name:
    :return:
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_file:
        temp_file_path = temp_file.name

    with open(template_path, 'r', encoding='utf-8') as template_file:
        template_content = template_file.read()

    modified_content = template_content.replace(insert_marker, student_code)

    with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        temp_file.write(modified_content)

    if conda_env_name:
        command = ['conda', 'run', '-n', conda_env_name, 'python', temp_file_path]
    else:
        command = ['python3', temp_file_path]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        success = True
        output = result.stdout
    except subprocess.CalledProcessError as e:
        success = False
        output = e.stderr
    finally:
        os.remove(temp_file_path)

    return success, output


def evaluate_student_code(student_file, template_files, env=None, cell_indices=None):
    """

    :param student_file:
    :param template_files:
    :param env:
    :param cell_indices:
    :return:
    """
    notebook = load_notebook(student_file)

    student_cells = [notebook.cells[i]['source'] for i in cell_indices if i < len(notebook.cells) and
                     notebook.cells[i].cell_type == 'code']

    output_list = []
    correct_count = 0
    task_point = 0
    for idx in range(len(student_cells)):
        task_point += 1
        student_code = student_cells[idx]
        error, message = syntax_check(student_code, task_point)

        if error:
            output_list.append(message)
        else:
            template_file = template_files.get(cell_indices[idx])
            success, output = execute_code(student_code, template_file, '# INSERT STUDENT CODE HERE', env)

            if success:
                output = output.strip()
                output = output.replace('\x1b[0m', '')
                bool_output = bool(int(output))
                if bool_output:
                    correct_count = correct_count + 1
                else:
                    message_fail = f"任务点{task_point}：\n    未完成任务所要求的功能！\n"
                    output_list.append(message_fail)
            else:
                message_fail = f"任务点{task_point}：\n    未完成任务所要求的功能：{output}\n"
                output_list.append(message_fail)

    if correct_count == len(student_cells):
        is_succeed = True
    else:
        is_succeed = False

    return is_succeed, output_list, correct_count, len(student_cells)


def write_json(is_succeed_signal, output_list_sigal, output_file, correct_count, student_cells):
    result = {
        "is_succeed": is_succeed_signal,
        "error_message": output_list_sigal,
        "results": [{
            "input": None,
            "expected": None,
            "actual": None,
            "passed": None
        }],
        "total_tasks": student_cells,
        "completed_tasks": correct_count,
        "completion_rate": correct_count / student_cells
    }

    save_json(result, output_file)


if __name__ == '__main__':
    # Get the absolute path of this script.
    script_path = os.path.dirname(__file__)
    student_file_path = '/task_6_display.ipynb'
    template_file_path = {
        7: f'{script_path}/task_6_template_7.py',
        12: f'{script_path}/task_6_template_12.py',
        17: f'{script_path}/task_6_template_17.py',
    }

    argv = sys.argv
    source_file, output_file = argv_getter(argv, student_file_path)

    cell_indices_to_evaluate = [7, 12, 17]
    local_env = None

    is_succeed_main, output_list_main, correct_count_main, student_cells_num = evaluate_student_code(source_file,
                                                                                                     template_file_path, local_env, cell_indices=cell_indices_to_evaluate)
    write_json(is_succeed_main, output_list_main, output_file, correct_count_main, student_cells_num)
