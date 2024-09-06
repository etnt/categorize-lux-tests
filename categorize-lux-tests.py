import os
import sys
import re
import argparse

def extract_info(file_path, extract_doc, extract_comments, extract_invoke_logs, extract_progress, include_full_content):
    """
    Extract information from a Lux test file based on provided switches.

    Args:
    file_path (str): The path to the Lux test file to be processed.
    extract_doc (bool): Whether to extract documentation description.
    extract_comments (bool): Whether to extract comments.
    extract_invoke_logs (bool): Whether to extract invoke logs.
    extract_progress (bool): Whether to extract progress information.
    include_full_content (bool): Whether to include the full file content.

    Returns:
    dict: A dictionary containing the requested information.
    """
    info = {}
    with open(file_path, 'r') as file:
        content = file.read()
        
        if include_full_content:
            info['full_content'] = content
        
        if extract_doc:
            # Extract [doc <description>] format
            doc_match = re.search(r'\[doc\s+(.+?)\]', content, re.DOTALL)
            if doc_match:
                info['doc'] = doc_match.group(1).strip()
            else:
                # Extract [doc] <description> [enddoc] format
                doc_match = re.search(r'\[doc\](.*?)\[enddoc\]', content, re.DOTALL)
                if doc_match:
                    info['doc'] = doc_match.group(1).strip()
        
        if extract_invoke_logs:
            info['invoke_logs'] = re.findall(r'\[invoke log\s+(.+?)\]', content)
        
        if extract_progress:
            progress_items = re.findall(r'\[progress\s+(.+?)\]', content)
            info['progress'] = [item.replace('\\n', ' ').strip() for item in progress_items]
        
        if extract_comments:
            info['comments'] = [line.strip()[1:].strip() for line in content.split('\n') if line.strip().startswith('#')]
    
    return info

def summarize_lux_tests(root_dir, extract_doc, extract_comments, extract_invoke_logs, extract_progress, include_full_content):
    """
    Summarize Lux test files in a given directory and its subdirectories.

    Args:
    root_dir (str): The root directory to start searching for .lux files.
    extract_doc (bool): Whether to extract documentation description.
    extract_comments (bool): Whether to extract comments.
    extract_invoke_logs (bool): Whether to extract invoke logs.
    extract_progress (bool): Whether to extract progress information.
    include_full_content (bool): Whether to include the full file content.

    Returns:
    dict: A dictionary where keys are directory names and values are dictionaries
          containing the requested information for each directory.
    """
    summary = {}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.lux'):
                file_path = os.path.join(dirpath, filename)
                dir_name = os.path.basename(dirpath)
                
                if dir_name not in summary:
                    summary[dir_name] = {}
                
                info = extract_info(file_path, extract_doc, extract_comments, extract_invoke_logs, extract_progress, include_full_content)
                
                for key, value in info.items():
                    if key not in summary[dir_name]:
                        summary[dir_name][key] = value if key in ['doc', 'full_content'] else []
                    if key not in ['doc', 'full_content']:
                        summary[dir_name][key].extend(value)
    
    return summary

def write_summary(summary, output_file):
    """
    Write a summary of Lux test information to a file.

    Args:
    summary (dict): A dictionary where keys are directory names and values are dictionaries
                    containing the extracted information for each directory.
    output_file (str): The name of the file to write the summary to.
    """
    with open(output_file, 'w') as f:
        for dir_name, info in summary.items():
            f.write(f"Test: {dir_name}\n")
            if 'doc' in info:
                f.write(f"Description: {info['doc']}\n")
            if 'comments' in info:
                f.write("Comments:\n")
                for comment in info['comments']:
                    f.write(f"- {comment}\n")
            if 'invoke_logs' in info:
                f.write("Invoke Logs:\n")
                for log in info['invoke_logs']:
                    f.write(f"- {log}\n")
            if 'progress' in info:
                f.write("Progress Information:\n")
                for progress in info['progress']:
                    # Remove any remaining '\n' and extra spaces
                    cleaned_progress = progress.replace('\\n', ' ').strip()
                    f.write(f"- {cleaned_progress}\n")
            if 'full_content' in info:
                f.write("Full Content:\n")
                # Remove '\n' notation from full content as well
                cleaned_content = info['full_content'].replace('\\n', '\n')
                f.write(cleaned_content)
                f.write("\n")
            f.write("\n")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Summarize Lux test files.")
    parser.add_argument("root_directory", help="Path to the root directory containing Lux test files")
    parser.add_argument("--no-doc", action="store_false", dest="extract_doc", help="Don't extract documentation description")
    parser.add_argument("--no-comments", action="store_false", dest="extract_comments", help="Don't extract comments")
    parser.add_argument("--no-invoke-logs", action="store_false", dest="extract_invoke_logs", help="Don't extract invoke logs")
    parser.add_argument("--no-progress", action="store_false", dest="extract_progress", help="Don't extract progress information")
    parser.add_argument("--include-full-content", action="store_true", help="Include full content of Lux files")
    parser.add_argument("-o", "--output", default="lux_tests_summary.txt", help="Output file name (default: lux_tests_summary.txt)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not os.path.isdir(args.root_directory):
        print(f"Error: '{args.root_directory}' is not a valid directory.")
        sys.exit(1)
    
    summary = summarize_lux_tests(
        args.root_directory,
        args.extract_doc,
        args.extract_comments,
        args.extract_invoke_logs,
        args.extract_progress,
        args.include_full_content
    )
    write_summary(summary, args.output)
    print(f"Summary written to {args.output}")
