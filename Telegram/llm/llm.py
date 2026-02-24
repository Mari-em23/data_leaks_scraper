from gpt4all import GPT4All
import re

# GPT4All setup (CPU-only)
model_path = r"C:\Users\benta\AppData\Local\nomic.ai\GPT4All\Meta-Llama-3-8B-Instruct.Q4_0.gguf"
gpt = GPT4All(model_path)  # CPU inference



def get_first_line(text):
    for line in text.splitlines():
        line = line.strip()
        if line and re.search(r"[A-Za-z]", line) and not line.startswith("Here is ") and not line.startswith("A single"):
            return line
    return ""


def generate_leak_name(post):
    prompt = (
        "Write a short English cybersecurity incident title.\n"
        "Maximum 15 words.\n"
        "Neutral, factual, professional tone.\n"
        "Output only the title.\n\n"
        "Post:\n"
        f"{post}\n\n"
        "Title:"
    )

    output = gpt.generate(
        prompt,
        max_tokens=18,
        temp=0.5
    )

    return get_first_line(output).strip()


def generate_leak_description(post):
    prompt = (
        "Telegram message:\n"
        f"{post}\n\n"
        "Write ONE single-sentence English description of this Telegram message above posted by some hackers group about a potential cybersecurity incident or threat or illegal cyber action targeting Tunisia.\n"
        "Rules:\n"
        "- Maximum 100 words\n"
        "- Neutral, professional cybersecurity tone\n"
        "- No explanations\n"
        "- No formatting\n"
        "- No quotes\n"
        "- No emojis\n"
        "- Give your answer like a threat hunter working for a Tunisian security agency\n\n"
        
        "Output:"
    )

    raw = gpt.generate(
        prompt,
        max_tokens=80,
        temp=0.5
    )

    return get_first_line(raw)




