import os
import sys
import re

def extract_info(file_path):
    """
    Extract information from a Lux test file.

    This function reads a Lux test file and extracts various pieces of information,
    including documentation, comments, invoke logs, and progress information.

    Args:
    file_path (str): The path to the Lux test file to be processed.

    Returns:
    tuple: A tuple containing four elements:
        - doc_description (str): The documentation description extracted from the file.
        - comments (list): A list of comments found in the file.
        - invoke_logs (list): A list of invoke log entries found in the file.
        - progress_info (list): A list of progress information entries found in the file.

    The function supports two formats for documentation:
    1. [doc <description>]
    2. [doc] <description> [enddoc]

    It also extracts:
    - Comments starting with '#'
    - Invoke logs in the format [invoke log <information>]
    - Progress information in the format [progress <information>]
    """
    comments = []
    doc_description = ""
    invoke_logs = []
    progress_info = []
    with open(file_path, 'r') as file:
        content = file.read()
        
        # Extract [doc <description>] format
        doc_match = re.search(r'\[doc\s+(.+?)\]', content, re.DOTALL)
        if doc_match:
            doc_description = doc_match.group(1).strip()
        else:
            # Extract [doc] <description> [enddoc] format
            doc_match = re.search(r'\[doc\](.*?)\[enddoc\]', content, re.DOTALL)
            if doc_match:
                doc_description = doc_match.group(1).strip()
        
        # Extract [invoke log <information>]
        invoke_logs = re.findall(r'\[invoke log\s+(.+?)\]', content)
        
        # Extract [progress <information>]
        progress_info = re.findall(r'\[progress\s+(.+?)\]', content)
        
        # Extract comments
        for line in content.split('\n'):
            if line.strip().startswith('#'):
                comments.append(line.strip()[1:].strip())
    
    return doc_description, comments, invoke_logs, progress_info

def summarize_lux_tests(root_dir):
    """
    Summarize Lux test files in a given directory and its subdirectories.

    This function walks through the directory tree starting from root_dir,
    processes all .lux files, and collects information about each test.
    It extracts documentation, comments, invoke logs, and progress information.

    Args:
    root_dir (str): The root directory to start searching for .lux files.

    Returns:
    dict: A dictionary where keys are directory names and values are dictionaries
          containing 'doc' (str), 'comments' (list), 'invoke_logs' (list),
          and 'progress' (list) for each directory.

    Note:
    - The function assumes that the extract_info() function is available to process
      individual .lux files.
    - If multiple .lux files in a directory have documentation, only the first
      encountered documentation is retained.
    """
    summary = {}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.lux'):
                file_path = os.path.join(dirpath, filename)
                dir_name = os.path.basename(dirpath)
                
                if dir_name not in summary:
                    summary[dir_name] = {'doc': '', 'comments': [], 'invoke_logs': [], 'progress': []}
                
                doc, comments, invoke_logs, progress = extract_info(file_path)
                if doc and not summary[dir_name]['doc']:
                    summary[dir_name]['doc'] = doc
                summary[dir_name]['comments'].extend(comments)
                summary[dir_name]['invoke_logs'].extend(invoke_logs)
                summary[dir_name]['progress'].extend(progress)
    
    return summary

def write_summary(summary, output_file):
    """
    Write a summary of Lux test information to a file.

    This function takes a dictionary containing summarized information about Lux tests
    and writes it to a specified output file. The summary includes test descriptions,
    comments, invoke logs, and progress information for each test directory.

    Args:
    summary (dict): A dictionary where keys are directory names and values are dictionaries
                    containing 'doc' (str), 'comments' (list), 'invoke_logs' (list),
                    and 'progress' (list) for each directory.
    output_file (str): The name of the file to write the summary to.

    The function writes the following information for each test directory:
    - Test name (directory name)
    - Description (if available)
    - Comments (if any)
    - Invoke Logs (if any)
    - Progress Information (if any)

    Each section is clearly labeled, and individual items are prefixed with a hyphen.
    A blank line is added between each test directory's information for readability.
    """
    with open(output_file, 'w') as f:
        for dir_name, info in summary.items():
            f.write(f"Test: {dir_name}\n")
            if info['doc']:
                f.write(f"Description: {info['doc']}\n")
            if info['comments']:
                f.write("Comments:\n")
                for comment in info['comments']:
                    f.write(f"- {comment}\n")
            if info['invoke_logs']:
                f.write("Invoke Logs:\n")
                for log in info['invoke_logs']:
                    f.write(f"- {log}\n")
            if info['progress']:
                f.write("Progress Information:\n")
                for progress in info['progress']:
                    f.write(f"- {progress}\n")
            f.write("\n")

if __name__ == "__main__":
    print("Enter the path to your lux tests directory:")
    root_directory = input().strip()
    
    if not os.path.isdir(root_directory):
        print(f"Error: '{root_directory}' is not a valid directory.")
        sys.exit(1)
    
    output_file = "lux_tests_summary.txt"
    
    summary = summarize_lux_tests(root_directory)
    write_summary(summary, output_file)
    print(f"Summary written to {output_file}")
