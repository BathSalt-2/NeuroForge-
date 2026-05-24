# NeuroForge: AI Mentor Initial Scaffolding Design

This document outlines the conceptual design for the initial scaffolding of the NeuroForge AI Mentor Service. It covers base LLM selection, memory mechanisms, interaction style customization, and integration with the Knowledge Graph.

## 1. Base LLM Selection

Choosing the right Large Language Model (LLM) is critical for the AI Mentor's success. The selection process should be driven by a balance of performance, cost, scalability, and customization capabilities.

**Key Considerations & Factors:**

*   **Performance:**
    *   **Accuracy & Coherence:** The LLM must provide factually accurate information (especially when not augmented by the Knowledge Graph) and generate coherent, easy-to-understand explanations.
    *   **Instruction Following:** Crucial for adhering to personas, verbosity levels, and incorporating context from memory or the Knowledge Graph.
    *   **Reasoning Ability:** The ability to understand user queries, infer intent, and break down complex topics is important.
    *   **Mathematical & Coding Proficiency:** Given NeuroForge's potential scope, proficiency in explaining and potentially debugging code or mathematical concepts would be a plus.

*   **Customization & Fine-tuning:**
    *   **Prompt Engineering:** All models allow for extensive prompt engineering to guide behavior.
    *   **Fine-tuning:** The ability to fine-tune the model on NeuroForge-specific data (e.g., curated Q&A, domain-specific language, desired interaction styles) can significantly enhance performance and alignment. This is a key differentiator.
    *   **Retrieval Augmented Generation (RAG):** The LLM must effectively utilize context provided from the memory mechanism and Knowledge Graph.

*   **Cost:**
    *   **API Costs:** For models like OpenAI GPT series or Google Gemini, costs are typically per-token (input and output). This can scale significantly with usage.
    *   **Self-hosting Costs (Open Source):** For models like Llama 3 or Mistral Large, this involves infrastructure costs (GPU servers), MLOps for deployment, maintenance, and scaling. Initial setup is higher, but per-interaction cost can be lower at scale.

*   **Scalability:**
    *   **API-based:** Generally offer high scalability managed by the provider.
    *   **Self-hosted:** Scalability depends on the deployed infrastructure and MLOps capabilities.

*   **Ethical Considerations & Safety Features:**
    *   **Bias Mitigation:** The model should ideally have mechanisms to reduce harmful biases.
    *   **Content Safety:** Features to prevent generation of inappropriate or harmful content are essential.
    *   **Data Privacy:** If using API models, data handling policies of the provider are crucial, especially with user interaction data. Self-hosting offers more control.

*   **Ecosystem & Tooling:**
    *   Availability of libraries (e.g., LangChain, LlamaIndex) and community support for the chosen model.

**Preliminary Recommendation / Selection Strategy:**

It's unlikely one model will be perfect across all dimensions from the outset. A phased approach is recommended:

1.  **Phase 1: Evaluation of Leading API-based Models:**
    *   **Candidates:** OpenAI GPT-4 / GPT-4o, Google Gemini Advanced.
    *   **Rationale:** These models currently represent the state-of-the-art in terms of general performance, reasoning, and instruction following. They are relatively easy to integrate for initial prototyping and testing.
    *   **Evaluation:** Develop a benchmark suite of questions and interaction scenarios relevant to NeuroForge. Assess performance, ease of use with RAG (from Knowledge Graph and simulated memory), and initial cost projections.

2.  **Phase 2: Evaluation of Leading Open-Source Models:**
    *   **Candidates:** Llama 3 (e.g., 70B variant), Mistral Large (if API access, or their open-weight models like Mixtral 8x7B).
    *   **Rationale:** Offer greater control, potential for deep fine-tuning, and potentially lower long-term costs at scale.
    *   **Evaluation:** Similar benchmark suite. Assess performance (pre-fine-tuning and potential for fine-tuning), infrastructure requirements, and MLOps overhead.

3.  **Decision Criteria:**
    *   **Primary:** Performance on NeuroForge-specific tasks, ability to follow complex instructions for persona and RAG.
    *   **Secondary:** Cost-effectiveness at projected scale, fine-tuning capabilities, data privacy implications.

**Initial Leaning:** Start with a high-performing API-based model like **GPT-4o** for rapid prototyping and to establish a performance baseline. Concurrently, begin evaluating open-source alternatives for long-term flexibility and cost optimization, with a plan to potentially switch or use a hybrid approach.

## 2. Memory Mechanism Design

The AI Mentor needs both short-term (session-specific) and long-term (persistent across sessions) memory to provide personalized and context-aware responses.

**Technologies:**

*   **Short-term Memory (Conversation Buffer):**
    *   **Mechanism:** Store recent turns of the current conversation directly in the AI Mentor Service's application memory (e.g., using a Python list or a Redis cache for distributed instances).
    *   **Purpose:** Provide immediate context for ongoing dialogue. This is typically included in the prompt to the LLM for each new user query.

*   **Long-term Memory (Vector Database):**
    *   **Technology:** **Pinecone** or **Weaviate** (managed services) or **FAISS/pgvector** integrated with PostgreSQL (self-managed).
        *   *Justification (from architecture doc):* Managed services simplify setup and scaling. Self-managed options offer more control and potentially lower cost if existing PostgreSQL infrastructure is leveraged. pgvector is particularly interesting as it keeps vector data alongside other relational data from NeuroForge if desired.
    *   **Mechanism:**
        1.  Generate embeddings for user queries and AI mentor responses using a sentence transformer model (e.g., from Hugging Face's Sentence Transformers library).
        2.  Store these embeddings along with their corresponding text and metadata in the vector database.

**Data to be Stored in Long-Term (Vector) Memory:**

*   **Conversation Chunks/Summaries:**
    *   Instead of storing entire raw conversations, store meaningful segments or AI-generated summaries of past dialogues. This keeps the context concise.
    *   `{ "chunkId": "uuid", "userId": "uuid", "conversationId": "uuid", "text": "Summary of discussion about X concept...", "embedding": [...], "timestamp": "datetime" }`
*   **Key Entities/Concepts Discussed:**
    *   Extract key concepts, skills, or topics mentioned. These could be linked to their IDs from the Knowledge Graph.
    *   `{ "entityId": "uuid", "userId": "uuid", "kgConceptId": "concept_abc", "kgSkillId": "skill_xyz", "mentionCount": 3, "lastDiscussed": "datetime", "embedding": [...], "text": "User frequently asks about Python list comprehensions." }`
*   **User's Stated Goals or Difficulties:**
    *   Explicit statements of learning goals or areas where the user is struggling.
    *   `{ "goalId": "uuid", "userId": "uuid", "text": "User wants to understand neural networks.", "status": "active/achieved", "timestamp": "datetime", "embedding": [...] }`
    *   `{ "difficultyId": "uuid", "userId": "uuid", "text": "User struggles with recursion in programming.", "relatedConceptId": "concept_recursion", "timestamp": "datetime", "embedding": [...] }`
*   **Feedback on Mentor Responses:**
    *   User ratings (thumbs up/down) or textual feedback on the helpfulness of specific AI responses. This can be used for Reinforcement Learning from Human Feedback (RLHF) if fine-tuning is pursued.
    *   `{ "feedbackId": "uuid", "userId": "uuid", "responseId": "uuid_of_ai_response", "rating": "positive/negative", "comment": "This explanation was very clear.", "timestamp": "datetime", "embedding": [...] }`

**Retrieval Process:**

1.  When a new user query is received:
    *   Generate an embedding for the user's query.
2.  Perform a semantic search (similarity search) against the user's long-term memory in the vector database using the query embedding.
    *   Retrieve the top-N most relevant memories (e.g., past conversation chunks, stated goals, difficulties).
3.  The retrieved memories, along with the short-term conversation buffer, are formatted and included as context in the prompt sent to the LLM.
    *   Example:
        ```
        System: You are a helpful AI learning mentor for NeuroForge.
        User: [User's current query]

        Recent conversation:
        User: [Previous query]
        AI: [Previous response]

        Relevant past interactions:
        - User previously struggled with: [Retrieved difficulty text]
        - User's goal: [Retrieved goal text]
        - Past discussion summary: [Retrieved conversation chunk]
        ```
4.  The LLM uses this combined context to generate a more personalized and informed response.

## 3. Interaction Style Customization

Allowing users or administrators to customize the AI Mentor's interaction style can significantly improve user experience and cater to diverse learning preferences.

**Aspects for Customization:**

*   **Persona:**
    *   **Socratic Questioner:** Asks guiding questions to help users arrive at their own understanding.
    *   **Encouraging Coach:** Provides positive reinforcement and motivation.
    *   **Direct Expert:** Offers clear, concise information and solutions.
    *   **Collaborative Partner:** Works through problems with the user as if they are a peer.
*   **Verbosity:**
    *   **Concise:** Short, to-the-point answers.
    *   **Detailed:** Comprehensive explanations with examples.
    *   **Adaptive:** Adjusts verbosity based on the topic's complexity or user's apparent understanding.
*   **Language/Tone:**
    *   **Formal vs. Informal:** Academic language vs. conversational and friendly.
    *   **Use of Analogies/Metaphors:** Tailor to user preference or subject matter.
    *   **Humor:** Option to enable/disable light humor.
*   **Proactivity:**
    *   **Reactive:** Only responds to direct queries.
    *   **Proactive Suggestions:** Offers related topics, quizzes, or encouragement based on user progress or inferred needs from their interactions (e.g., "I see you're working on X, you might find Y interesting.").

**Mechanisms for Implementation:**

1.  **System Prompts / Meta-Prompts:**
    *   This is the primary and most immediate method. A part of the system prompt provided to the LLM will define its persona, tone, and verbosity based on user settings.
    *   Example segment of a system prompt:
        ```
        "You are the NeuroForge AI Mentor. Adopt the persona of an 'Encouraging Coach'. Your explanations should be 'detailed' and your tone 'informal and friendly'. When appropriate, offer 'proactive suggestions' for related topics."
        ```
2.  **User-Selectable Profiles:**
    *   In the User Profile settings, users can choose from predefined mentor profiles (e.g., "Quick Helper", "Deep Dive Tutor", "Socratic Guide").
    *   These profiles map to specific system prompt configurations.
    *   Administrators could also define default profiles or create new ones.
3.  **Fine-tuning (Long-term):**
    *   If an open-source model is chosen and sufficient data is collected, fine-tuning can be used to instill desired interaction styles more deeply into the model's behavior. This is more complex but can lead to more natural and consistent stylistic adherence.
4.  **Conditional Logic in AI Mentor Service:**
    *   The service itself can have logic to slightly modify prompts or post-process LLM outputs based on simple rules derived from user settings or context. For example, adding pre-canned encouraging phrases if the user is struggling and has selected a "coach" persona.
5.  **Dynamic Prompt Adjustments:**
    *   The AI Mentor Service can analyze user interaction patterns. If a user consistently asks for shorter answers or uses informal language, the service can subtly adjust the prompt parameters for verbosity or formality over time.

## 4. Integration with Knowledge Graph

The AI Mentor will leverage the Knowledge Graph Service (via its API as defined in `neuroforge_api_design.md`) to ground its responses in factual information and make informed suggestions.

**Key Integration Points:**

*   **Fetching Definitions and Explanations:**
    *   When a user asks about a specific concept or skill (e.g., "What is 'neural network pruning'?"), the AI Mentor can query the Knowledge Graph Service (`GET /concepts/{conceptId}` or `GET /skills/{skillId}`).
    *   The retrieved definition, description, and properties can be used to:
        *   Formulate an accurate answer.
        *   Provide a direct quote or summary from the KG.
        *   Ensure consistency with NeuroForge's curated content.

*   **Understanding Relationships:**
    *   When discussing a topic, the AI Mentor can query the KG for related concepts or skills (`GET /concepts/{conceptId}/prerequisites`, `GET /concepts/{conceptId}/related`).
    *   This helps in:
        *   Explaining how different topics connect.
        *   Identifying foundational knowledge the user might be missing (prerequisites).
        *   Suggesting next logical topics to explore.

*   **Suggesting Relevant Learning Modules or Resources:**
    *   Based on the current conversation context (e.g., a concept the user is struggling with or interested in), the AI Mentor can query the KG for relevant `ContentModules` (`GET /concepts/{conceptId}/modules` or `GET /skills/{skillId}/modules`).
    *   It can then suggest these modules to the user: "I found a video tutorial on 'Neural Network Pruning' that might help. Would you like the link?"
    *   This also applies to suggesting entire `LearningPaths` if the user expresses broader learning goals.

*   **Augmenting Prompts:**
    *   Information retrieved from the KG can be directly inserted into the LLM prompt as context, similar to how memory is used. This helps the LLM generate more accurate and relevant responses.
    *   Example: "User is asking about 'X'. According to our Knowledge Graph, X is defined as '...' and is a prerequisite for 'Y'."

By integrating these components, the AI Mentor can evolve from a generic chatbot into a powerful, personalized, and contextually aware learning companion within the NeuroForge ecosystem.
