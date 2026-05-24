"""
NeuroForge — Neo4j Knowledge Graph Seed Script
Populates the graph with concepts, skills, content modules, assessments,
learning paths, and all their relationships per the data model spec.
"""

import os
import sys
import time

from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neuroforge_secret")


def wait_for_neo4j(driver, retries=30, delay=3):
    """Wait until Neo4j is ready."""
    for i in range(retries):
        try:
            with driver.session() as session:
                session.run("RETURN 1").single()
            print("✅ Neo4j is ready")
            return
        except Exception as e:
            print(f"⏳ Waiting for Neo4j ({i+1}/{retries})... {e}")
            time.sleep(delay)
    print("❌ Neo4j not available after retries, exiting")
    sys.exit(1)


def seed(tx):
    """Create all seed data in a single transaction."""

    # ── Clear existing data ──────────────────────────────────
    tx.run("MATCH (n) DETACH DELETE n")

    # ══════════════════════════════════════════════════════════
    # CONCEPTS
    # ══════════════════════════════════════════════════════════
    concepts = [
        {
            "conceptId": "concept_python_basics",
            "name": "Python Basics",
            "description": (
                "Python is a high-level, general-purpose programming language known for its "
                "clean syntax and readability. It supports multiple programming paradigms "
                "including procedural, object-oriented, and functional programming. Python is "
                "the most widely used language in AI/ML, data science, web development, and automation."
            ),
            "difficultyLevel": "Beginner",
            "domain": "Computer Science",
            "subDomain": "Programming",
            "keywords": ["python", "programming", "coding", "basics", "syntax"],
        },
        {
            "conceptId": "concept_data_structures",
            "name": "Data Structures",
            "description": (
                "Data structures are specialized formats for organizing, storing, and managing data "
                "efficiently. Common data structures include arrays, linked lists, stacks, queues, "
                "hash tables, trees, and graphs. Choosing the right data structure is fundamental "
                "to writing efficient algorithms and programs."
            ),
            "difficultyLevel": "Beginner",
            "domain": "Computer Science",
            "subDomain": "Programming",
            "keywords": ["data structures", "lists", "dictionaries", "arrays", "programming"],
        },
        {
            "conceptId": "concept_machine_learning",
            "name": "Machine Learning",
            "description": (
                "Machine Learning (ML) is a subset of Artificial Intelligence that enables systems "
                "to automatically learn and improve from experience without being explicitly programmed. "
                "ML algorithms build mathematical models based on training data to make predictions or "
                "decisions. The three main types are supervised learning (labeled data), unsupervised "
                "learning (unlabeled data), and reinforcement learning (reward-based)."
            ),
            "difficultyLevel": "Intermediate",
            "domain": "Computer Science",
            "subDomain": "Artificial Intelligence",
            "keywords": ["machine learning", "ML", "AI", "supervised", "unsupervised", "algorithms"],
        },
        {
            "conceptId": "concept_neural_networks",
            "name": "Neural Networks",
            "description": (
                "Neural networks are computing systems inspired by biological neural networks in the "
                "human brain. They consist of interconnected nodes (neurons) organized in layers — "
                "an input layer, one or more hidden layers, and an output layer. Each connection has "
                "a weight that adjusts during training through backpropagation. Neural networks are "
                "the foundation of deep learning and power applications from image recognition to "
                "natural language processing."
            ),
            "difficultyLevel": "Intermediate",
            "domain": "Computer Science",
            "subDomain": "Artificial Intelligence",
            "keywords": ["neural networks", "deep learning", "neurons", "backpropagation", "AI"],
        },
        {
            "conceptId": "concept_supervised_learning",
            "name": "Supervised Learning",
            "description": (
                "Supervised learning is a type of machine learning where the model is trained on "
                "labeled data — each training example is paired with the correct output. The model "
                "learns to map inputs to outputs and can then predict labels for new, unseen data. "
                "Common tasks include classification (predicting categories) and regression "
                "(predicting continuous values). Examples: spam detection, house price prediction."
            ),
            "difficultyLevel": "Intermediate",
            "domain": "Computer Science",
            "subDomain": "Artificial Intelligence",
            "keywords": ["supervised learning", "classification", "regression", "labeled data"],
        },
        {
            "conceptId": "concept_deep_learning",
            "name": "Deep Learning",
            "description": (
                "Deep learning is a subset of machine learning that uses neural networks with many "
                "layers (deep neural networks) to learn hierarchical representations of data. "
                "It excels at automatically discovering complex patterns in large datasets. "
                "Key architectures include Convolutional Neural Networks (CNNs) for images, "
                "Recurrent Neural Networks (RNNs) for sequences, and Transformers for language."
            ),
            "difficultyLevel": "Advanced",
            "domain": "Computer Science",
            "subDomain": "Artificial Intelligence",
            "keywords": ["deep learning", "CNN", "RNN", "transformers", "neural networks"],
        },
        {
            "conceptId": "concept_statistics_basics",
            "name": "Statistics Basics",
            "description": (
                "Statistics is the science of collecting, organizing, analyzing, and interpreting "
                "data. Key concepts include mean, median, mode, standard deviation, distributions, "
                "hypothesis testing, and correlation. Statistics provides the mathematical foundation "
                "for machine learning and data-driven decision-making."
            ),
            "difficultyLevel": "Beginner",
            "domain": "Mathematics",
            "subDomain": "Statistics",
            "keywords": ["statistics", "probability", "mean", "distribution", "data analysis"],
        },
        {
            "conceptId": "concept_linear_algebra",
            "name": "Linear Algebra",
            "description": (
                "Linear algebra is the branch of mathematics dealing with vectors, matrices, "
                "linear transformations, and systems of linear equations. It is essential for "
                "understanding machine learning algorithms, especially neural networks, where "
                "computations are fundamentally matrix operations."
            ),
            "difficultyLevel": "Intermediate",
            "domain": "Mathematics",
            "subDomain": "Linear Algebra",
            "keywords": ["linear algebra", "matrices", "vectors", "eigenvalues", "math"],
        },
    ]

    for c in concepts:
        tx.run("""
            CREATE (c:Concept {
                conceptId: $conceptId,
                name: $name,
                description: $description,
                difficultyLevel: $difficultyLevel,
                domain: $domain,
                subDomain: $subDomain,
                keywords: $keywords
            })
        """, **c)

    # ══════════════════════════════════════════════════════════
    # SKILLS
    # ══════════════════════════════════════════════════════════
    skills = [
        {
            "skillId": "skill_python_programming",
            "name": "Python Programming",
            "description": "Ability to write, debug, and maintain Python code for various applications.",
            "proficiencyLevels": ["Novice", "Competent", "Proficient", "Expert"],
            "domain": "Computer Science",
            "keywords": ["python", "programming", "coding"],
        },
        {
            "skillId": "skill_ml_fundamentals",
            "name": "Machine Learning Fundamentals",
            "description": "Understanding of core ML concepts, algorithms, model training, and evaluation.",
            "proficiencyLevels": ["Novice", "Competent", "Proficient", "Expert"],
            "domain": "Computer Science",
            "keywords": ["machine learning", "ML", "data science"],
        },
        {
            "skillId": "skill_data_analysis",
            "name": "Data Analysis",
            "description": "Ability to explore, clean, transform, and derive insights from datasets.",
            "proficiencyLevels": ["Novice", "Competent", "Proficient", "Expert"],
            "domain": "Computer Science",
            "keywords": ["data analysis", "pandas", "numpy", "visualization"],
        },
        {
            "skillId": "skill_critical_thinking",
            "name": "Critical Thinking",
            "description": "Ability to analyze information objectively, evaluate arguments, and form reasoned judgments.",
            "proficiencyLevels": ["Developing", "Competent", "Advanced"],
            "domain": "General",
            "keywords": ["critical thinking", "analysis", "reasoning"],
        },
    ]

    for s in skills:
        tx.run("""
            CREATE (s:Skill {
                skillId: $skillId,
                name: $name,
                description: $description,
                proficiencyLevels: $proficiencyLevels,
                domain: $domain,
                keywords: $keywords
            })
        """, **s)

    # ══════════════════════════════════════════════════════════
    # CONTENT MODULES
    # ══════════════════════════════════════════════════════════
    modules = [
        {
            "moduleId": "module_python_basics_interactive",
            "title": "Python Basics - Interactive Tutorial",
            "type": "INTERACTIVE_SIMULATION",
            "format": "text/html",
            "url": "https://www.learnpython.org/",
            "estimatedDurationMinutes": 30,
            "difficultyLevel": "Beginner",
            "description": "Hands-on interactive tutorial covering Python variables, types, control flow, and functions.",
            "publishedDate": "2024-01-15",
        },
        {
            "moduleId": "module_python_data_structures",
            "title": "Python Data Structures - Tutorial",
            "type": "ARTICLE",
            "format": "text/markdown",
            "url": None,
            "estimatedDurationMinutes": 20,
            "difficultyLevel": "Beginner",
            "description": "Comprehensive tutorial on lists, dictionaries, sets, and tuples in Python.",
            "publishedDate": "2024-01-20",
        },
        {
            "moduleId": "module_intro_ml_video",
            "title": "Introduction to Machine Learning - Video",
            "type": "VIDEO",
            "format": "video/mp4",
            "url": "https://www.youtube.com/watch?v=ukzFI9rgwfU",
            "estimatedDurationMinutes": 25,
            "difficultyLevel": "Beginner",
            "description": "A video tutorial covering the fundamentals of Machine Learning including types and applications.",
            "publishedDate": "2024-02-01",
        },
        {
            "moduleId": "module_ml_supervised_quiz",
            "title": "Supervised Learning - Quiz",
            "type": "QUIZ",
            "format": "application/json",
            "url": None,
            "estimatedDurationMinutes": 10,
            "difficultyLevel": "Intermediate",
            "description": "Interactive quiz to test understanding of supervised learning concepts.",
            "publishedDate": "2024-02-10",
        },
        {
            "moduleId": "module_neural_networks_article",
            "title": "Understanding Neural Networks - Article",
            "type": "ARTICLE",
            "format": "text/markdown",
            "url": None,
            "estimatedDurationMinutes": 15,
            "difficultyLevel": "Intermediate",
            "description": "In-depth article covering neural network architecture, backpropagation, and common types (CNN, RNN, Transformer).",
            "publishedDate": "2024-02-15",
        },
        {
            "moduleId": "module_deep_learning_video",
            "title": "Deep Learning Fundamentals - Video",
            "type": "VIDEO",
            "format": "video/mp4",
            "url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "estimatedDurationMinutes": 20,
            "difficultyLevel": "Intermediate",
            "description": "Video introduction to deep learning, multi-layer networks, and gradient descent.",
            "publishedDate": "2024-03-01",
        },
    ]

    for m in modules:
        tx.run("""
            CREATE (m:ContentModule {
                moduleId: $moduleId,
                title: $title,
                type: $type,
                format: $format,
                url: $url,
                estimatedDurationMinutes: $estimatedDurationMinutes,
                difficultyLevel: $difficultyLevel,
                description: $description,
                publishedDate: $publishedDate
            })
        """, **m)

    # ══════════════════════════════════════════════════════════
    # ASSESSMENTS
    # ══════════════════════════════════════════════════════════
    tx.run("""
        CREATE (a:Assessment {
            assessmentId: 'assessment_ml_basics',
            name: 'Machine Learning Basics Assessment',
            type: 'MULTIPLE_CHOICE_QUIZ',
            description: 'Comprehensive assessment covering ML fundamentals including supervised/unsupervised learning.',
            passingScoreThreshold: 0.7,
            maxScore: 100.0,
            estimatedTimeMinutes: 20
        })
    """)

    tx.run("""
        CREATE (a:Assessment {
            assessmentId: 'assessment_python_fundamentals',
            name: 'Python Fundamentals Assessment',
            type: 'CODING_CHALLENGE',
            description: 'Coding challenges testing Python basics including variables, loops, functions, and data structures.',
            passingScoreThreshold: 0.75,
            maxScore: 100.0,
            estimatedTimeMinutes: 30
        })
    """)

    # ══════════════════════════════════════════════════════════
    # LEARNING OBJECTIVES
    # ══════════════════════════════════════════════════════════
    objectives = [
        ("obj_explain_ml", "Learner can explain what machine learning is and name its three main types.",
         "Quiz score >= 70% on ML basics assessment"),
        ("obj_build_nn", "Learner can describe the architecture of a neural network and explain backpropagation.",
         "Written explanation or diagram assessment"),
        ("obj_write_python", "Learner can write Python functions using variables, loops, and conditionals.",
         "Coding challenge completion"),
    ]
    for oid, desc, criteria in objectives:
        tx.run("""
            CREATE (o:LearningObjective {
                objectiveId: $oid,
                description: $desc,
                measurableCriteria: $criteria
            })
        """, oid=oid, desc=desc, criteria=criteria)

    # ══════════════════════════════════════════════════════════
    # CREDENTIALS
    # ══════════════════════════════════════════════════════════
    tx.run("""
        CREATE (cr:Credential {
            credentialId: 'cred_ai_foundations',
            name: 'AI & ML Foundations Certificate',
            description: 'Certifies foundational knowledge in AI, machine learning, neural networks, and Python.',
            issuingOrganization: 'NeuroForge',
            imageUrl: 'https://via.placeholder.com/300x200?text=AI+Foundations+Certificate'
        })
    """)

    # ══════════════════════════════════════════════════════════
    # LEARNING PATH
    # ══════════════════════════════════════════════════════════
    tx.run("""
        CREATE (lp:LearningPath {
            pathId: 'path_ai_foundations',
            name: 'Foundations of AI & Machine Learning',
            description: 'A comprehensive learning path from Python basics through ML and neural networks.',
            estimatedTotalDurationMinutes: 120,
            targetAudience: 'Beginners with basic computer skills',
            isDynamic: false,
            createdBy: 'system'
        })
    """)

    # ══════════════════════════════════════════════════════════
    # RESOURCES
    # ══════════════════════════════════════════════════════════
    resources = [
        ("resource_python_docs", "Official Python Documentation", "TUTORIAL_WEBSITE",
         "https://docs.python.org/3/", "The official Python 3 documentation and tutorial."),
        ("resource_ml_coursera", "Machine Learning Specialization (Coursera)", "TUTORIAL_WEBSITE",
         "https://www.coursera.org/specializations/machine-learning-introduction",
         "Andrew Ng's comprehensive ML course on Coursera."),
        ("resource_pytorch_docs", "PyTorch Documentation", "SOFTWARE_TOOL",
         "https://pytorch.org/docs/stable/index.html",
         "Official documentation for the PyTorch deep learning framework."),
    ]
    for rid, name, rtype, url, desc in resources:
        tx.run("""
            CREATE (r:Resource {
                resourceId: $rid,
                name: $name,
                type: $rtype,
                url: $url,
                description: $desc
            })
        """, rid=rid, name=name, rtype=rtype, url=url, desc=desc)

    # ══════════════════════════════════════════════════════════
    # RELATIONSHIPS
    # ══════════════════════════════════════════════════════════
    print("  → Creating relationships...")

    # Concept prerequisites
    prerequisites = [
        ("concept_python_basics", "concept_data_structures"),
        ("concept_python_basics", "concept_machine_learning"),
        ("concept_statistics_basics", "concept_machine_learning"),
        ("concept_machine_learning", "concept_supervised_learning"),
        ("concept_machine_learning", "concept_neural_networks"),
        ("concept_neural_networks", "concept_deep_learning"),
        ("concept_linear_algebra", "concept_neural_networks"),
    ]
    for pre, post in prerequisites:
        tx.run("""
            MATCH (pre:Concept {conceptId: $pre}), (post:Concept {conceptId: $post})
            CREATE (pre)-[:PREREQUISITE_OF]->(post)
        """, pre=pre, post=post)

    # Related concepts
    related = [
        ("concept_machine_learning", "concept_neural_networks"),
        ("concept_supervised_learning", "concept_neural_networks"),
        ("concept_python_basics", "concept_statistics_basics"),
        ("concept_data_structures", "concept_python_basics"),
        ("concept_deep_learning", "concept_neural_networks"),
    ]
    for a, b in related:
        tx.run("""
            MATCH (a:Concept {conceptId: $a}), (b:Concept {conceptId: $b})
            CREATE (a)-[:RELATED_TO]->(b)
        """, a=a, b=b)

    # Part-of
    tx.run("""
        MATCH (a:Concept {conceptId: 'concept_supervised_learning'}),
              (b:Concept {conceptId: 'concept_machine_learning'})
        CREATE (a)-[:PART_OF]->(b)
    """)

    # Module → Concept (TEACHES_CONCEPT)
    teaches = [
        ("module_python_basics_interactive", "concept_python_basics"),
        ("module_python_data_structures", "concept_data_structures"),
        ("module_python_data_structures", "concept_python_basics"),
        ("module_intro_ml_video", "concept_machine_learning"),
        ("module_ml_supervised_quiz", "concept_supervised_learning"),
        ("module_ml_supervised_quiz", "concept_machine_learning"),
        ("module_neural_networks_article", "concept_neural_networks"),
        ("module_deep_learning_video", "concept_deep_learning"),
        ("module_deep_learning_video", "concept_neural_networks"),
    ]
    for mid, cid in teaches:
        tx.run("""
            MATCH (m:ContentModule {moduleId: $mid}), (c:Concept {conceptId: $cid})
            CREATE (m)-[:TEACHES_CONCEPT]->(c)
        """, mid=mid, cid=cid)

    # Module → Skill (DEVELOPS_SKILL)
    develops = [
        ("module_python_basics_interactive", "skill_python_programming"),
        ("module_python_data_structures", "skill_python_programming"),
        ("module_intro_ml_video", "skill_ml_fundamentals"),
        ("module_ml_supervised_quiz", "skill_ml_fundamentals"),
        ("module_neural_networks_article", "skill_ml_fundamentals"),
        ("module_deep_learning_video", "skill_ml_fundamentals"),
    ]
    for mid, sid in develops:
        tx.run("""
            MATCH (m:ContentModule {moduleId: $mid}), (s:Skill {skillId: $sid})
            CREATE (m)-[:DEVELOPS_SKILL]->(s)
        """, mid=mid, sid=sid)

    # Module → LearningObjective
    tx.run("""
        MATCH (m:ContentModule {moduleId: 'module_intro_ml_video'}),
              (o:LearningObjective {objectiveId: 'obj_explain_ml'})
        CREATE (m)-[:HAS_OBJECTIVE]->(o)
    """)
    tx.run("""
        MATCH (m:ContentModule {moduleId: 'module_neural_networks_article'}),
              (o:LearningObjective {objectiveId: 'obj_build_nn'})
        CREATE (m)-[:HAS_OBJECTIVE]->(o)
    """)
    tx.run("""
        MATCH (m:ContentModule {moduleId: 'module_python_basics_interactive'}),
              (o:LearningObjective {objectiveId: 'obj_write_python'})
        CREATE (m)-[:HAS_OBJECTIVE]->(o)
    """)

    # Assessment relationships
    tx.run("""
        MATCH (a:Assessment {assessmentId: 'assessment_ml_basics'}),
              (c:Concept {conceptId: 'concept_machine_learning'})
        CREATE (a)-[:EVALUATES_CONCEPT]->(c)
    """)
    tx.run("""
        MATCH (a:Assessment {assessmentId: 'assessment_ml_basics'}),
              (c:Concept {conceptId: 'concept_supervised_learning'})
        CREATE (a)-[:EVALUATES_CONCEPT]->(c)
    """)
    tx.run("""
        MATCH (a:Assessment {assessmentId: 'assessment_ml_basics'}),
              (s:Skill {skillId: 'skill_ml_fundamentals'})
        CREATE (a)-[:EVALUATES_SKILL]->(s)
    """)
    tx.run("""
        MATCH (a:Assessment {assessmentId: 'assessment_python_fundamentals'}),
              (c:Concept {conceptId: 'concept_python_basics'})
        CREATE (a)-[:EVALUATES_CONCEPT]->(c)
    """)
    tx.run("""
        MATCH (a:Assessment {assessmentId: 'assessment_python_fundamentals'}),
              (s:Skill {skillId: 'skill_python_programming'})
        CREATE (a)-[:EVALUATES_SKILL]->(s)
    """)

    # Learning Path relationships
    path_modules = [
        ("module_python_basics_interactive", 1, False),
        ("module_python_data_structures", 2, False),
        ("module_intro_ml_video", 3, False),
        ("module_ml_supervised_quiz", 4, False),
        ("module_neural_networks_article", 5, False),
        ("module_deep_learning_video", 6, True),
    ]
    for mid, order, optional in path_modules:
        tx.run("""
            MATCH (lp:LearningPath {pathId: 'path_ai_foundations'}),
                  (m:ContentModule {moduleId: $mid})
            CREATE (lp)-[:CONTAINS_MODULE {sequenceOrder: $order, isOptional: $optional}]->(m)
        """, mid=mid, order=order, optional=optional)

    # Path starts with first module
    tx.run("""
        MATCH (lp:LearningPath {pathId: 'path_ai_foundations'}),
              (m:ContentModule {moduleId: 'module_python_basics_interactive'})
        CREATE (lp)-[:STARTS_WITH_MODULE]->(m)
    """)

    # Path targets concepts
    for cid in ["concept_python_basics", "concept_machine_learning", "concept_neural_networks"]:
        tx.run("""
            MATCH (lp:LearningPath {pathId: 'path_ai_foundations'}),
                  (c:Concept {conceptId: $cid})
            CREATE (lp)-[:TARGETS_CONCEPT]->(c)
        """, cid=cid)

    # Path develops skills
    for sid in ["skill_python_programming", "skill_ml_fundamentals"]:
        tx.run("""
            MATCH (lp:LearningPath {pathId: 'path_ai_foundations'}),
                  (s:Skill {skillId: $sid})
            CREATE (lp)-[:DEVELOPS_SKILL_PATH]->(s)
        """, sid=sid)

    # Path leads to credential
    tx.run("""
        MATCH (lp:LearningPath {pathId: 'path_ai_foundations'}),
              (cr:Credential {credentialId: 'cred_ai_foundations'})
        CREATE (lp)-[:LEADS_TO_CREDENTIAL]->(cr)
    """)

    # Credential certifies skills/concepts
    tx.run("""
        MATCH (cr:Credential {credentialId: 'cred_ai_foundations'}),
              (s:Skill {skillId: 'skill_ml_fundamentals'})
        CREATE (cr)-[:CERTIFIES_SKILL {requiredProficiency: 'Competent'}]->(s)
    """)
    tx.run("""
        MATCH (cr:Credential {credentialId: 'cred_ai_foundations'}),
              (s:Skill {skillId: 'skill_python_programming'})
        CREATE (cr)-[:CERTIFIES_SKILL {requiredProficiency: 'Competent'}]->(s)
    """)

    # Module sequence (NEXT_IN_PATH)
    module_order = [
        "module_python_basics_interactive",
        "module_python_data_structures",
        "module_intro_ml_video",
        "module_ml_supervised_quiz",
        "module_neural_networks_article",
        "module_deep_learning_video",
    ]
    for i in range(len(module_order) - 1):
        tx.run("""
            MATCH (a:ContentModule {moduleId: $a}), (b:ContentModule {moduleId: $b})
            CREATE (a)-[:NEXT_IN_PATH {pathId: 'path_ai_foundations'}]->(b)
        """, a=module_order[i], b=module_order[i + 1])

    # Resource relationships
    tx.run("""
        MATCH (c:Concept {conceptId: 'concept_python_basics'}),
              (r:Resource {resourceId: 'resource_python_docs'})
        CREATE (c)-[:HAS_SUPPLEMENTARY_RESOURCE]->(r)
    """)
    tx.run("""
        MATCH (c:Concept {conceptId: 'concept_machine_learning'}),
              (r:Resource {resourceId: 'resource_ml_coursera'})
        CREATE (c)-[:HAS_SUPPLEMENTARY_RESOURCE]->(r)
    """)
    tx.run("""
        MATCH (c:Concept {conceptId: 'concept_deep_learning'}),
              (r:Resource {resourceId: 'resource_pytorch_docs'})
        CREATE (c)-[:HAS_SUPPLEMENTARY_RESOURCE]->(r)
    """)

    # LearningObjective → Concept/Skill
    tx.run("""
        MATCH (o:LearningObjective {objectiveId: 'obj_explain_ml'}),
              (c:Concept {conceptId: 'concept_machine_learning'})
        CREATE (o)-[:RELATES_TO_CONCEPT]->(c)
    """)
    tx.run("""
        MATCH (o:LearningObjective {objectiveId: 'obj_build_nn'}),
              (c:Concept {conceptId: 'concept_neural_networks'})
        CREATE (o)-[:RELATES_TO_CONCEPT]->(c)
    """)
    tx.run("""
        MATCH (o:LearningObjective {objectiveId: 'obj_write_python'}),
              (s:Skill {skillId: 'skill_python_programming'})
        CREATE (o)-[:RELATES_TO_SKILL]->(s)
    """)

    # Skill prerequisites
    tx.run("""
        MATCH (a:Skill {skillId: 'skill_python_programming'}),
              (b:Skill {skillId: 'skill_data_analysis'})
        CREATE (a)-[:PREREQUISITE_FOR_SKILL]->(b)
    """)
    tx.run("""
        MATCH (a:Skill {skillId: 'skill_python_programming'}),
              (b:Skill {skillId: 'skill_ml_fundamentals'})
        CREATE (a)-[:PREREQUISITE_FOR_SKILL]->(b)
    """)

    print("  → All relationships created!")


def create_indexes(session):
    """Create uniqueness constraints and indexes."""
    indexes = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.conceptId IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.skillId IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (m:ContentModule) REQUIRE m.moduleId IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Assessment) REQUIRE a.assessmentId IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (o:LearningObjective) REQUIRE o.objectiveId IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (cr:Credential) REQUIRE cr.credentialId IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (lp:LearningPath) REQUIRE lp.pathId IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Resource) REQUIRE r.resourceId IS UNIQUE",
    ]
    for idx in indexes:
        session.run(idx)
    print("✅ Indexes and constraints created")


def verify(session):
    """Print summary of seeded data."""
    labels = ["Concept", "Skill", "ContentModule", "Assessment",
              "LearningObjective", "Credential", "LearningPath", "Resource"]
    print("\n📊 Seed Summary:")
    for label in labels:
        result = session.run(f"MATCH (n:{label}) RETURN count(n) as cnt")
        count = result.single()["cnt"]
        print(f"   {label}: {count}")

    result = session.run("MATCH ()-[r]->() RETURN count(r) as cnt")
    rel_count = result.single()["cnt"]
    print(f"   Relationships: {rel_count}")
    print()


def main():
    print("🧠 NeuroForge Knowledge Graph Seeder")
    print("=" * 45)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    wait_for_neo4j(driver)

    with driver.session() as session:
        create_indexes(session)
        print("📝 Seeding knowledge graph...")
        session.execute_write(seed)
        print("✅ Seed data created!")
        verify(session)

    driver.close()
    print("🎉 Done! Knowledge graph is ready.")


if __name__ == "__main__":
    main()
