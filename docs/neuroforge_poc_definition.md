# NeuroForge: Proof-of-Concept Definition

This document defines a Proof-of-Concept (PoC) for a core feature of the NeuroForge platform, focusing on the interaction between the AI Mentor, Knowledge Graph, and a user interface to provide explanations and content suggestions.

## 1. PoC Title

**NeuroForge AI-Powered Concept Explanation and Content Recommendation PoC**

## 2. Goal of the PoC

The primary goal of this PoC is to validate the basic interaction flow and technical feasibility of integrating a simplified User Interface, the AI Mentor Service (using an external LLM), and the Knowledge Graph Service (with a minimal dataset) to:

1.  Provide users with AI-generated explanations for concepts retrieved from the Knowledge Graph.
2.  Offer relevant content module suggestions based on the discussed concept.
3.  Demonstrate core data retrieval from Neo4j and its use in prompting an LLM.

## 3. Core Components Involved

*   **Simplified User Interface (UI):**
    *   A very basic web page with an input field for questions and an area to display responses.
    *   Alternatively, a command-line interface (CLI) could be used for simplicity.
*   **AI Mentor Service:**
    *   Utilizes a readily available LLM API (e.g., OpenAI GPT-3.5-turbo/GPT-4o, or Google Gemini API).
    *   Contains logic to interact with the Knowledge Graph Service.
    *   Handles prompt engineering to combine KG data with user queries for the LLM.
*   **Knowledge Graph Service:**
    *   A running Neo4j instance.
    *   Manually populated with a small, predefined dataset (a few `Concept` and `ContentModule` nodes and their relationships).
    *   Exposes simplified API endpoints as defined in `neuroforge_api_design.md` (e.g., `GET /concepts/{conceptId}`, `GET /concepts/{conceptId}/modules`).
*   **User Service (Mocked):**
    *   No actual user database or authentication.
    *   A hardcoded `userId` will be used for any interactions requiring user identification.
*   **Content Delivery Service (Mocked):**
    *   No actual content storage or delivery.
    *   Will return placeholder text or a link to a publicly available resource (e.g., a YouTube video) when a content module is "accessed."
*   **Cognitive Profiling Service (Mocked Endpoint):**
    *   A simple mock endpoint (`POST /profiling/interactions`) that acknowledges receipt of interaction data without actual processing or storage of complex profiles.

## 4. User Story/Scenario for the PoC

1.  **User Accesses UI:** User opens the basic web page or CLI for the PoC. A default/mock `userId` is assumed.
2.  **User Asks a Question:** User types into the input field: "What is [Concept X]?"
    *   *[Concept X] is a concept manually populated in the PoC's Knowledge Graph (e.g., "Machine Learning").*
3.  **AI Mentor Service Processes Query:**
    a.  The UI sends the query and mock `userId` to the AI Mentor Service.
    b.  AI Mentor Service makes a call to the (mocked) Cognitive Profiling Service endpoint (`POST /profiling/interactions`) to log the query interaction (e.g., `{"userId": "poc_user_01", "eventType": "ASK_CONCEPT", "details": {"conceptName": "Machine Learning"}}`). The mocked service returns a 202 Accepted.
    c.  AI Mentor Service queries the Knowledge Graph Service: `GET /concepts?name=[Concept X]`. (Assuming the KG service can look up by name for simplicity, or the UI sends a known `conceptId`).
    d.  Knowledge Graph Service returns the details of Concept X (e.g., `conceptId`, `name`, `description`).
    e.  AI Mentor Service constructs a prompt for the LLM, including the description of Concept X from the KG. Example: "Explain the following concept to a beginner: [Concept X Description from KG]."
    f.  AI Mentor Service calls the external LLM API with the prompt.
4.  **AI Mentor Service Returns Explanation:**
    a.  LLM API returns the generated explanation.
    b.  AI Mentor Service sends the explanation back to the UI.
    c.  UI displays the explanation of Concept X.
5.  **AI Mentor Suggests Content:**
    a.  AI Mentor Service, using the `conceptId` of Concept X, queries the Knowledge Graph Service for related content: `GET /concepts/{conceptId}/modules`.
    b.  Knowledge Graph Service returns a list of related `ContentModule` nodes (e.g., one video module related to "Machine Learning").
    c.  AI Mentor Service formats a suggestion: "Would you like to view a video titled '[Module Title]' about [Concept X]?" It includes a button or link.
    d.  AI Mentor Service sends the suggestion to the UI.
    e.  UI displays the suggestion.
6.  **User Accesses Suggested Content:**
    a.  User clicks the link/button for the suggested content module.
    b.  UI sends a request (simulated) to the (mocked) Content Delivery Service, indicating the `moduleId`.
    c.  Mocked Content Delivery Service returns a placeholder (e.g., "Placeholder for video on [Module Title]" or a link to an existing relevant YouTube video).
    d.  UI displays the placeholder content or opens the external link.
    e.  (Optional) UI sends an interaction log to the AI Mentor, which logs it to the mocked Cognitive Profiling Service (`{"userId": "poc_user_01", "eventType": "ACCESS_MODULE", "details": {"moduleId": "module_ml_video_01"}}`).

## 5. Key Functionalities to Implement (Simplified)

*   **Knowledge Graph Population:**
    *   Manually create 2-3 `Concept` nodes in Neo4j (e.g., "Machine Learning," "Neural Networks," "Python Basics").
    *   Manually create 2-3 `ContentModule` nodes (e.g., "Intro to ML Video," "Neural Networks Explained Article").
    *   Manually create `TEACHES_CONCEPT` and `RELATED_TO` (between concepts if desired) or `HAS_OBJECTIVE` (linking module to concept) relationships.
*   **Knowledge Graph Service (Simplified API):**
    *   Implement `GET /concepts/{conceptId}` (or `GET /concepts?name=...`).
    *   Implement `GET /concepts/{conceptId}/modules`.
*   **AI Mentor Service Logic:**
    *   Receive user query.
    *   Call Knowledge Graph Service to fetch concept data.
    *   Construct prompt using KG data and send to an external LLM API.
    *   Receive LLM response.
    *   Call Knowledge Graph Service to fetch related content modules.
    *   Format explanation and suggestion.
    *   (Simplified) Send interaction logs to a mocked Cognitive Profiling Service endpoint.
*   **User Interface (Basic):**
    *   Input field for user queries.
    *   Display area for AI Mentor responses and suggestions.
    *   Clickable links/buttons for content suggestions.
    *   Display area for (mocked) content.
*   **Mocked Services:**
    *   Cognitive Profiling Service: A single endpoint that accepts POST requests and returns a 202 status.
    *   Content Delivery Service: A single endpoint that accepts a module ID and returns a predefined string or link.

## 6. Success Criteria for the PoC

*   User can successfully ask about one of the predefined concepts in the KG via the UI.
*   The UI displays an explanation of the concept, where the explanation is generated by the LLM and demonstrably uses the description text fetched from the KG for that concept.
*   The UI displays a relevant content suggestion (e.g., a link to a module) that is logically connected to the discussed concept within the KG.
*   User can click the content suggestion, and a placeholder for the content is displayed.
*   Logs show successful API calls between:
    *   UI and AI Mentor Service.
    *   AI Mentor Service and Knowledge Graph Service.
    *   AI Mentor Service and external LLM API.
    *   AI Mentor Service and mocked Cognitive Profiling Service.
    *   UI and mocked Content Delivery Service.
*   Basic technical risks and challenges in integrating these core components (LLM, Neo4j, custom service logic) are identified and documented.
*   The PoC can be demonstrated live.

## 7. Scope Limitations (What's NOT in this PoC)

*   **User Authentication & Management:** No actual user login or profiles. A single, hardcoded `userId` will be used.
*   **AI Mentor Memory:** No persistent short-term or long-term memory for the AI Mentor. Each query is treated as independent, though KG context is used.
*   **Complex Cognitive Profiling:** The Cognitive Profiling Service endpoint is a simple mock; no actual data processing, profile generation, or behavioral heatmapping will occur. Only basic interaction logging is simulated.
*   **Blockchain Credentialing:** Completely excluded.
*   **Knowledge Graph Data & Complexity:** Minimal data (e.g., 2-3 concepts, 2-3 modules, basic relationships). No complex graph traversals or reasoning within the KG itself for this PoC.
*   **Advanced UI/UX:** The UI will be extremely basic (e.g., simple HTML page or CLI). No focus on aesthetics or advanced user experience features.
*   **Error Handling & Resilience:** Minimal error handling. Focus is on the "happy path."
*   **Scalability & Performance Testing:** Not in scope.
*   **Content Variety:** Only one or two types of mocked content (e.g., "video placeholder," "article placeholder").
*   **Sophisticated Recommendation Logic:** Content suggestion will be direct (e.g., modules explicitly linked to the concept) rather than complex AI-driven recommendations.
*   **No actual content creation or curation.**
*   **No fine-tuning of LLMs.**

This PoC aims to provide a foundational understanding of the core interaction loop within NeuroForge and de-risk key technical integrations early in the development process.
