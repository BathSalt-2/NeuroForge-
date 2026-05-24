"""
NeuroForge — Content Delivery Service (PoC Mock)
Delivers learning modules and resources. In production this would integrate
with a CDN, blob storage, and support streaming/downloads.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

app = FastAPI(title="NeuroForge Content Delivery Service", version="0.1.0")

# ── Mock content store ───────────────────────────────────────
MOCK_CONTENT = {
    "module_intro_ml_video": {
        "moduleId": "module_intro_ml_video",
        "title": "Introduction to Machine Learning - Video",
        "type": "VIDEO",
        "contentUrl": "https://www.youtube.com/watch?v=ukzFI9rgwfU",
        "contentHtml": """
            <div class="content-module">
                <h2>Introduction to Machine Learning</h2>
                <p>Machine Learning is a subset of Artificial Intelligence that enables systems
                to learn and improve from experience without being explicitly programmed.</p>
                <div class="video-embed">
                    <iframe width="560" height="315"
                        src="https://www.youtube.com/embed/ukzFI9rgwfU"
                        title="Introduction to Machine Learning"
                        frameborder="0" allowfullscreen></iframe>
                </div>
                <h3>Key Takeaways:</h3>
                <ul>
                    <li>ML uses algorithms to find patterns in data</li>
                    <li>Three main types: Supervised, Unsupervised, and Reinforcement Learning</li>
                    <li>Real-world applications: image recognition, NLP, recommendation systems</li>
                </ul>
            </div>
        """,
        "estimatedDurationMinutes": 25,
    },
    "module_neural_networks_article": {
        "moduleId": "module_neural_networks_article",
        "title": "Understanding Neural Networks - Article",
        "type": "ARTICLE",
        "contentUrl": None,
        "contentHtml": """
            <div class="content-module">
                <h2>Understanding Neural Networks</h2>
                <p>Neural networks are computing systems inspired by biological neural networks
                in the human brain. They consist of interconnected nodes (neurons) organized in layers.</p>

                <h3>Architecture</h3>
                <p>A typical neural network consists of:</p>
                <ul>
                    <li><strong>Input Layer:</strong> Receives the raw data features</li>
                    <li><strong>Hidden Layers:</strong> Process information through weighted connections</li>
                    <li><strong>Output Layer:</strong> Produces the final prediction or classification</li>
                </ul>

                <h3>How They Learn</h3>
                <p>Neural networks learn through a process called <em>backpropagation</em>:</p>
                <ol>
                    <li>Data flows forward through the network (forward pass)</li>
                    <li>The output is compared to the expected result (loss calculation)</li>
                    <li>Errors are propagated backward to adjust weights (backward pass)</li>
                    <li>This process repeats over many iterations (epochs)</li>
                </ol>

                <h3>Common Types</h3>
                <ul>
                    <li><strong>CNNs:</strong> Convolutional Neural Networks — excellent for image tasks</li>
                    <li><strong>RNNs:</strong> Recurrent Neural Networks — designed for sequential data</li>
                    <li><strong>Transformers:</strong> Attention-based models powering modern LLMs</li>
                </ul>

                <h3>Practice Exercise</h3>
                <p>Try building a simple neural network using PyTorch to classify handwritten digits (MNIST dataset).</p>
            </div>
        """,
        "estimatedDurationMinutes": 15,
    },
    "module_python_basics_interactive": {
        "moduleId": "module_python_basics_interactive",
        "title": "Python Basics - Interactive Tutorial",
        "type": "INTERACTIVE_SIMULATION",
        "contentUrl": "https://www.learnpython.org/",
        "contentHtml": """
            <div class="content-module">
                <h2>Python Basics — Interactive Tutorial</h2>
                <p>Python is a versatile, high-level programming language known for its
                clean syntax and readability. It's the most popular language for AI/ML.</p>

                <h3>Core Concepts</h3>

                <h4>1. Variables & Data Types</h4>
                <pre><code class="language-python">
# Variables don't need type declarations
name = "NeuroForge"      # string
version = 1.0             # float
is_active = True           # boolean
modules = ["ML", "NN"]    # list
                </code></pre>

                <h4>2. Control Flow</h4>
                <pre><code class="language-python">
# Conditionals
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"

# Loops
for module in ["ML", "Neural Nets", "Python"]:
    print(f"Learning: {module}")
                </code></pre>

                <h4>3. Functions</h4>
                <pre><code class="language-python">
def calculate_progress(completed, total):
    \"\"\"Calculate learning progress percentage.\"\"\"
    return (completed / total) * 100

progress = calculate_progress(3, 10)
print(f"Progress: {progress}%")  # 30.0%
                </code></pre>

                <h3>Try It Yourself</h3>
                <p>Visit <a href="https://www.learnpython.org/" target="_blank">LearnPython.org</a>
                for hands-on interactive exercises.</p>
            </div>
        """,
        "estimatedDurationMinutes": 30,
    },
    "module_ml_supervised_quiz": {
        "moduleId": "module_ml_supervised_quiz",
        "title": "Supervised Learning - Quiz",
        "type": "QUIZ",
        "contentUrl": None,
        "contentHtml": """
            <div class="content-module">
                <h2>Supervised Learning — Quick Quiz</h2>
                <p>Test your understanding of supervised learning concepts.</p>
            </div>
        """,
        "quizData": {
            "questions": [
                {
                    "id": "q1",
                    "text": "What type of data does supervised learning require?",
                    "options": [
                        "Unlabeled data",
                        "Labeled data with input-output pairs",
                        "Random data",
                        "No data at all"
                    ],
                    "correctIndex": 1,
                    "explanation": "Supervised learning requires labeled data — each training example has an input paired with the correct output."
                },
                {
                    "id": "q2",
                    "text": "Which of the following is a supervised learning task?",
                    "options": [
                        "Clustering customers into groups",
                        "Predicting house prices based on features",
                        "Finding anomalies in network traffic",
                        "Reducing data dimensions"
                    ],
                    "correctIndex": 1,
                    "explanation": "Predicting house prices is a regression task — a classic supervised learning problem using labeled data."
                },
                {
                    "id": "q3",
                    "text": "What's the difference between classification and regression?",
                    "options": [
                        "There is no difference",
                        "Classification predicts categories, regression predicts continuous values",
                        "Regression predicts categories, classification predicts continuous values",
                        "Both predict categories"
                    ],
                    "correctIndex": 1,
                    "explanation": "Classification assigns data to discrete categories (e.g., spam/not spam). Regression predicts continuous numerical values (e.g., temperature, price)."
                }
            ]
        },
        "estimatedDurationMinutes": 10,
    },
    "module_deep_learning_video": {
        "moduleId": "module_deep_learning_video",
        "title": "Deep Learning Fundamentals - Video",
        "type": "VIDEO",
        "contentUrl": "https://www.youtube.com/watch?v=aircAruvnKk",
        "contentHtml": """
            <div class="content-module">
                <h2>Deep Learning Fundamentals</h2>
                <p>Deep learning uses multi-layered neural networks to learn
                hierarchical representations of data.</p>
                <div class="video-embed">
                    <iframe width="560" height="315"
                        src="https://www.youtube.com/embed/aircAruvnKk"
                        title="Deep Learning Fundamentals"
                        frameborder="0" allowfullscreen></iframe>
                </div>
            </div>
        """,
        "estimatedDurationMinutes": 20,
    },
    "module_python_data_structures": {
        "moduleId": "module_python_data_structures",
        "title": "Python Data Structures - Tutorial",
        "type": "ARTICLE",
        "contentUrl": None,
        "contentHtml": """
            <div class="content-module">
                <h2>Python Data Structures</h2>
                <p>Master the essential data structures in Python that form
                the backbone of any programming project.</p>

                <h3>Lists</h3>
                <pre><code class="language-python">
# Ordered, mutable collections
scores = [95, 87, 92, 78, 88]
scores.append(91)
top_3 = sorted(scores, reverse=True)[:3]
                </code></pre>

                <h3>Dictionaries</h3>
                <pre><code class="language-python">
# Key-value pairs for fast lookup
student = {
    "name": "Alex",
    "progress": 0.75,
    "skills": ["python", "ml"]
}
                </code></pre>

                <h3>Sets & Tuples</h3>
                <pre><code class="language-python">
# Sets — unique elements, fast membership testing
completed = {"module_1", "module_2", "module_3"}

# Tuples — immutable sequences
coordinates = (42.3601, -71.0589)
                </code></pre>
            </div>
        """,
        "estimatedDurationMinutes": 20,
    },
}


# ── Endpoints ────────────────────────────────────────────────
@app.get("/content/{module_id}")
async def get_content(module_id: str):
    """Deliver content for a specific module."""
    content = MOCK_CONTENT.get(module_id)
    if not content:
        return {
            "moduleId": module_id,
            "title": f"Content for {module_id}",
            "type": "PLACEHOLDER",
            "contentHtml": f"<p>Placeholder content for module <strong>{module_id}</strong>. "
                           f"Full content would be delivered from CDN/storage in production.</p>",
            "estimatedDurationMinutes": 0,
        }
    return content


@app.get("/content")
async def list_content():
    """List all available content modules."""
    return {
        "total": len(MOCK_CONTENT),
        "modules": [
            {
                "moduleId": m["moduleId"],
                "title": m["title"],
                "type": m["type"],
                "estimatedDurationMinutes": m.get("estimatedDurationMinutes"),
            }
            for m in MOCK_CONTENT.values()
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "content_delivery_service",
        "note": "PoC mock — serving static content",
        "availableModules": len(MOCK_CONTENT),
    }
