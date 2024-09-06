import re
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import defaultdict, Counter
from sklearn.decomposition import PCA
from nltk import bigrams, ngrams
from nltk.corpus import stopwords
import nltk
import os

# Download necessary NLTK data (run this once)
nltk.download('stopwords', quiet=True)

# Add this at the beginning of your script or in a setup function
nltk.download('stopwords')

# Then, when you use stopwords, make sure to call it as a set:
stop_words = set(stopwords.words('english'))

def is_number(word):
    return word.replace('.', '', 1).isdigit()

def should_exclude(word):
    return (word in stop_words or 
            is_number(word) or 
            re.match(r'^eng-\d+', word))

def read_test_data(file_path):
    """
    Read and parse the test data from the given file, excluding summary tags.

    Args:
        file_path (str): Path to the file containing test data.

    Returns:
        dict: A dictionary where keys are test names and values are test contents.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Split the content into individual tests
    tests = re.split(r'\nTest:', content)
    test_data = {}
    
    for test in tests[1:]:  # Skip the first empty split
        lines = test.strip().split('\n')
        test_name = lines[0].strip()
        
        # Initialize an empty list to store relevant content
        relevant_content = []
        
        # Flag to track whether we're in a section to include
        include_section = True
        
        for line in lines[1:]:
            # Check for summary tags and set the flag accordingly
            if line.startswith(('Description:', 'Comments:', 'Invoke Logs:', 'Progress Information:')):
                include_section = False
                continue
            
            # If we encounter a new test or reach the end, reset the flag
            if line == '' or line.startswith('Test:'):
                include_section = True
                continue
            
            # If we're in a section to include, add the line to relevant content
            if include_section:
                relevant_content.append(line)
        
        # Join the relevant content and store it in the dictionary
        test_data[test_name] = ' '.join(relevant_content)

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
            - KMeans: The fitted KMeans model.
            - np.ndarray: The TF-IDF transformed data.
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

    return clusters, vectorizer, kmeans, X

def get_cluster_summary(cluster_contents, vectorizer, top_n=5):
    """
    Generate a summary of the most common bigrams in a cluster.

    Args:
        cluster_contents (list): List of test contents in the cluster.
        vectorizer (TfidfVectorizer): The fitted TF-IDF vectorizer.
        top_n (int): Number of top bigrams to include in the summary.

    Returns:
        str: A comma-separated string of the most common bigrams.
    """
    # Combine all content in the cluster
    combined_content = ' '.join(cluster_contents)

    # Tokenize and create bigrams
    words = combined_content.lower().split()
    filtered_words = [word for word in words if not should_exclude(word)]
    bigram_list = list(ngrams(filtered_words, 2))

    # Count bigram occurrences
    bigram_counts = Counter(bigram_list)

    # Sort by frequency and return top N bigrams
    common_bigrams = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)
    return ', '.join([' '.join(bigram) for bigram, _ in common_bigrams[:top_n]])

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

def visualize_clusters(X, kmeans):
    """
    Visualize the clusters using PCA.

    Args:
        X (np.ndarray): The TF-IDF transformed data.
        kmeans (KMeans): The fitted KMeans model.
    """
    # Reduce dimensionality for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X.toarray())

    # Create a scatter plot
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=kmeans.labels_, cmap='viridis')
    plt.title('Document Clusters')
    plt.colorbar(scatter)

    # Add labels for cluster centers
    centroids_pca = pca.transform(kmeans.cluster_centers_)
    for i, centroid in enumerate(centroids_pca):
        plt.annotate(f'Cluster {i}', xy=centroid, xytext=(5, 5),
                     textcoords='offset points', fontweight='bold')

    plt.tight_layout()
    plt.show()

def print_top_terms(test_data, clusters, n=5):
    for cluster_id, test_names in clusters.items():
        # Combine all content in the cluster
        cluster_content = ' '.join([test_data[name] for name in test_names])
        
        # Tokenize and create bigrams
        words = cluster_content.lower().split()
        filtered_words = [word for word in words if not should_exclude(word)]
        bigram_list = list(bigrams(filtered_words))
        
        # Count bigram occurrences
        bigram_counts = Counter(bigram_list)
        
        # Sort by frequency and get top N bigrams
        common_bigrams = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)[:n]
        
        print(f"\nCluster {cluster_id}:")
        print(", ".join([f"{w1} {w2}" for (w1, w2), _ in common_bigrams]))

def print_cluster_histograms(test_data, clusters, kmeans, n=10):
    for cluster_id, test_names in clusters.items():
        cluster_content = ' '.join([test_data[name] for name in test_names])
        
        words = cluster_content.lower().split()
        filtered_words = [word for word in words if not should_exclude(word)]
        bigram_list = list(bigrams(filtered_words))
        
        bigram_counts = Counter(bigram_list)
        common_bigrams = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)[:n]
        
        bigram_labels = [f"{w1} {w2}" for (w1, w2), _ in common_bigrams]
        bigram_values = [count for _, count in common_bigrams]

        plt.figure(figsize=(12, 6))
        plt.bar(bigram_labels, bigram_values)
        plt.title(f'Top {n} Bigrams for Cluster {cluster_id}')
        plt.xlabel('Bigrams')
        plt.ylabel('Frequency (Number of Occurrences)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

def write_clusters_to_file(clusters, output_file="grouped_tests.txt"):
    """
    Write the clustered test names to a text file.

    Args:
        clusters (dict): Clustered test names.
        output_file (str): Name of the output file.
    """
    with open(output_file, 'w') as f:
        for cluster_id, test_names in clusters.items():
            f.write(f"Cluster {cluster_id + 1}:\n")
            for test_name in test_names:
                f.write(f"  - {test_name}\n")
            f.write("\n")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Cluster Lux tests based on content similarity.")
    parser.add_argument("-f", "--file-path", default="lux_tests_summary.txt",
                        help="Path to the lux_tests_summary.txt file (default: lux_tests_summary.txt)")
    parser.add_argument("-n", "--num-clusters", type=int, default=5,
                        help="Number of clusters to create (default: 5)")
    parser.add_argument("--histogram", action="store_true",
                        help="Print histograms of cluster centers")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    test_data = read_test_data(args.file_path)
    clusters, vectorizer, kmeans, X = cluster_tests(test_data, args.num_clusters)
    print_clusters(clusters, test_data, vectorizer)
    print_top_terms(test_data, clusters)  # Modified this line
    
    # Write clusters to file
    write_clusters_to_file(clusters)
    print(f"Grouped tests have been written to 'grouped_tests.txt'")
    
    if args.histogram:
        print_cluster_histograms(test_data, clusters, kmeans)
    
    visualize_clusters(X, kmeans)
