import os
import sys
import re

def extract_info(file_path):
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
