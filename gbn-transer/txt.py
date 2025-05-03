import random

subjects = ["The cat", "A man", "The dog", "She", "He", "They", "The bird", "My friend", "An old lady"]
verbs = ["eats", "likes", "hates", "finds", "sees", "watches", "creates", "destroys", "reads"]
objects = ["an apple.", "the book.", "a car.", "the newspaper.", "a song.", "the movie.", "a sandwich.", "the game.", "a flower."]

def generate_sentence():
    return f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}\n"

target_size = 3 * 1024 * 1024  # 3MB
output_file = "test.txt"

with open(output_file, "w", encoding="utf-8") as f:
    total_bytes = 0
    while total_bytes < target_size:
        sentence = generate_sentence()
        f.write(sentence)
        total_bytes += len(sentence.encode("utf-8"))

print("File generated:", output_file)
