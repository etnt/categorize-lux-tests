import re
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import defaultdict, Counter

def read_test_data(file_path):
    """
    Read and parse the test data from the given file.

    Args:
        file_path (str): Path to the file containing test data.

    Returns:
        dict: A dictionary where keys are test names and values are test contents.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    tests = re.split(r'\nTest:', content)
    test_data = {}
    for test in tests[1:]:  # Skip the first empty split
        lines = test.strip().split('\n')
        test_name = lines[0].strip()
        test_content = ' '.join(lines[1:])
        test_data[test_name] = test_content

    return test_data

def cluster_tests(test_data, num_clusters):
    """
    Cluster the tests based on their content similarity.

    Args:
        test_data (dict): A dictionary of test names and their contents.
        num_clusters (int): The number of clusters to create.

    Returns:
        tuple: A tuple containing:
            - dict: Clustered test names.
            - TfidfVectorizer: The fitted vectorizer for further analysis.
    """
    test_names = list(test_data.keys())
    test_contents = list(test_data.values())

    # Convert text to TF-IDF features
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(test_contents)

    # Perform K-means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)

    # Group test names by cluster
    clusters = defaultdict(list)
    for test_name, cluster_id in zip(test_names, kmeans.labels_):
        clusters[cluster_id].append(test_name)

    return clusters, vectorizer

def get_cluster_summary(cluster_contents, vectorizer, top_n=5):
    """
    Generate a summary of the most common terms in a cluster.

    Args:
        cluster_contents (list): List of test contents in the cluster.
        vectorizer (TfidfVectorizer): The fitted TF-IDF vectorizer.
        top_n (int): Number of top terms to include in the summary.

    Returns:
        str: A comma-separated string of the most common terms.
    """
    # Combine all content in the cluster
    combined_content = ' '.join(cluster_contents)
    
    # Get feature names (words) from the vectorizer
    feature_names = vectorizer.get_feature_names_out()
    
    # Count word occurrences
    word_counts = Counter(combined_content.split())
    
    # Filter words that are in the feature names and sort by frequency
    common_words = sorted(
        [(word, count) for word, count in word_counts.items() if word in feature_names],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Return top N words
    return ', '.join([word for word, _ in common_words[:top_n]])

def print_clusters(clusters, test_data, vectorizer):
    """
    Print the clustered tests with summaries.

    Args:
        clusters (dict): Clustered test names.
        test_data (dict): Original test data.
        vectorizer (TfidfVectorizer): The fitted TF-IDF vectorizer.
    """
    for cluster_id, test_names in clusters.items():
        cluster_contents = [test_data[name] for name in test_names]
        summary = get_cluster_summary(cluster_contents, vectorizer)
        print(f"Cluster {cluster_id + 1} (Common terms: {summary}):")
        for test_name in test_names:
            print(f"  - {test_name}")
        print()

def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Cluster Lux tests based on content similarity.")
    parser.add_argument("-f","--file-path", type=str, default="./lux_tests_summary.txt",
                        help="Path to the lux_tests_summary.txt file (default: ./lux_tests_summary.txt)")
    parser.add_argument("-n", "--num-clusters", type=int, default=5,
                        help="Number of clusters to create (default: 5)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    test_data = read_test_data(args.file_path)
    clusters, vectorizer = cluster_tests(test_data, args.num_clusters)
    print_clusters(clusters, test_data, vectorizer)
