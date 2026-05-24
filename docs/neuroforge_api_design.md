# NeuroForge: Core Services API Design

This document details the API endpoints for core NeuroForge microservices. It follows RESTful principles and uses JSON for request/response payloads. Authentication and authorization are assumed to be handled by an API Gateway and the User Service.

## Table of Contents
1.  [User Service](#1-user-service)
2.  [Knowledge Graph Service](#2-knowledge-graph-service)
3.  [Learning Pathway Service](#3-learning-pathway-service)
4.  [AI Mentor Service](#4-ai-mentor-service)
5.  [Credentialing Service](#5-credentialing-service)
6.  [Cognitive Profiling Service](#6-cognitive-profiling-service)

---

## 1. User Service

Manages user registration, login, and profiles.

### Endpoints

#### 1.1 User Registration
*   **Method:** `POST`
*   **Path:** `/users/register`
*   **Description:** Creates a new user account.
*   **Example Request Body:**
    ```json
    {
      "username": "newlearner",
      "email": "new@example.com",
      "password": "securePassword123",
      "firstName": "New",
      "lastName": "Learner"
    }
    ```
*   **Example Response Body (201 Created):**
    ```json
    {
      "userId": "user_uuid_123",
      "username": "newlearner",
      "email": "new@example.com",
      "firstName": "New",
      "lastName": "Learner",
      "role": "learner",
      "createdAt": "2023-10-27T10:00:00Z"
    }
    ```

#### 1.2 User Login
*   **Method:** `POST`
*   **Path:** `/users/login`
*   **Description:** Authenticates a user and returns a session token (details of token response handled by API Gateway/Auth mechanism, but service confirms credentials).
*   **Example Request Body:**
    ```json
    {
      "email": "learner@example.com",
      "password": "password123"
    }
    ```
*   **Example Response Body (200 OK):**
    ```json
    {
      "userId": "user_uuid_456",
      "message": "Login successful",
      "token": "jwt_token_example" // Or this could be set in an HTTPOnly cookie
    }
    ```

#### 1.3 Get User Profile
*   **Method:** `GET`
*   **Path:** `/users/{userId}`
*   **Description:** Retrieves a specific user's profile information.
*   **Example Response Body (200 OK):**
    ```json
    {
      "userId": "user_uuid_456",
      "username": "currentlearner",
      "email": "current@example.com",
      "firstName": "Current",
      "lastName": "Learner",
      "role": "learner",
      "cognitiveProfile": {
        "learningStyle": "visual",
        "preferredTopics": ["AI", "History"]
      },
      "currentLearningGoals": ["concept_ai_basics", "skill_critical_thinking"],
      "createdAt": "2023-01-15T09:00:00Z",
      "lastLogin": "2023-10-27T12:00:00Z"
    }
    ```

#### 1.4 Update User Profile
*   **Method:** `PUT`
*   **Path:** `/users/{userId}`
*   **Description:** Updates a specific user's profile information.
*   **Example Request Body:**
    ```json
    {
      "firstName": "UpdatedFirstName",
      "lastName": "UpdatedLastName",
      "currentLearningGoals": ["concept_python_advanced", "skill_data_analysis"]
    }
    ```
*   **Example Response Body (200 OK):**
    ```json
    {
      "userId": "user_uuid_456",
      "username": "currentlearner",
      "email": "current@example.com",
      "firstName": "UpdatedFirstName",
      "lastName": "UpdatedLastName",
      "role": "learner",
      "cognitiveProfile": {
        "learningStyle": "visual",
        "preferredTopics": ["AI", "History"]
      },
      "currentLearningGoals": ["concept_python_advanced", "skill_data_analysis"],
      "createdAt": "2023-01-15T09:00:00Z",
      "lastLogin": "2023-10-27T12:00:00Z"
    }
    ```

#### 1.5 Delete User Account
*   **Method:** `DELETE`
*   **Path:** `/users/{userId}`
*   **Description:** Deletes a specific user's account.
*   **Example Response Body (204 No Content):** (Empty body)


---

## 2. Knowledge Graph Service

Provides access to concepts, skills, content modules, and their relationships.

### Endpoints

#### 2.1 Get Concept by ID
*   **Method:** `GET`
*   **Path:** `/concepts/{conceptId}`
*   **Description:** Retrieves a specific concept.
*   **Example Response Body (200 OK):**
    ```json
    {
      "conceptId": "concept_ai_basics",
      "name": "AI Basics",
      "description": "Fundamental concepts of Artificial Intelligence.",
      "difficultyLevel": "Beginner",
      "domain": "Computer Science",
      "subDomain": "Artificial Intelligence",
      "keywords": ["AI", "Machine Learning", "Introduction"]
    }
    ```

#### 2.2 Get Prerequisites for a Concept
*   **Method:** `GET`
*   **Path:** `/concepts/{conceptId}/prerequisites`
*   **Description:** Retrieves all prerequisite concepts for a given concept.
*   **Example Response Body (200 OK):**
    ```json
    [
      {
        "conceptId": "concept_math_logic",
        "name": "Mathematical Logic",
        "description": "..."
      },
      {
        "conceptId": "concept_basic_programming",
        "name": "Basic Programming",
        "description": "..."
      }
    ]
    ```

#### 2.3 Get Related Concepts for a Concept
*   **Method:** `GET`
*   **Path:** `/concepts/{conceptId}/related`
*   **Description:** Retrieves concepts related to the given concept.
*   **Example Response Body (200 OK):** (Similar structure to prerequisites)

#### 2.4 List Concepts
*   **Method:** `GET`
*   **Path:** `/concepts`
*   **Description:** Retrieves a list of concepts, with optional filtering.
*   **Key Query Parameters:** `domain=`, `subDomain=`, `difficultyLevel=`, `keyword=`, `limit=20`, `offset=0`
*   **Example Response Body (200 OK):**
    ```json
    {
      "total": 150,
      "limit": 20,
      "offset": 0,
      "data": [
        {
          "conceptId": "concept_ai_basics",
          "name": "AI Basics",
          "description": "Fundamental concepts of Artificial Intelligence."
        }
        // ... more concepts
      ]
    }
    ```

#### 2.5 Get Skill by ID
*   **Method:** `GET`
*   **Path:** `/skills/{skillId}`
*   **Description:** Retrieves a specific skill.
*   **Example Response Body (200 OK):**
    ```json
    {
      "skillId": "skill_python_programming",
      "name": "Python Programming",
      "description": "Ability to write and debug Python code.",
      "proficiencyLevels": ["Novice", "Competent", "Proficient", "Expert"],
      "domain": "Computer Science",
      "keywords": ["python", "programming", "coding"]
    }
    ```

#### 2.6 List Skills
*   **Method:** `GET`
*   **Path:** `/skills`
*   **Description:** Retrieves a list of skills, with optional filtering.
*   **Key Query Parameters:** `domain=`, `keyword=`, `limit=20`, `offset=0`
*   **Example Response Body (200 OK):** (Similar structure to List Concepts)

#### 2.7 Get Content Module by ID
*   **Method:** `GET`
*   **Path:** `/modules/{moduleId}`
*   **Description:** Retrieves a specific content module.
*   **Example Response Body (200 OK):**
    ```json
    {
      "moduleId": "module_intro_python_video",
      "title": "Introduction to Python - Video",
      "type": "VIDEO",
      "format": "video/mp4",
      "url": "https://content.neuroforge.com/videos/intro_python.mp4",
      "estimatedDurationMinutes": 25,
      "difficultyLevel": "Beginner",
      "description": "A video tutorial covering Python basics.",
      "publishedDate": "2023-02-10T00:00:00Z",
      "conceptsTaught": ["concept_python_syntax", "concept_variables"],
      "skillsDeveloped": ["skill_python_programming_novice"]
    }
    ```

#### 2.8 List Content Modules
*   **Method:** `GET`
*   **Path:** `/modules`
*   **Description:** Retrieves a list of content modules.
*   **Key Query Parameters:** `type=`, `difficultyLevel=`, `conceptId=`, `skillId=`, `limit=20`, `offset=0`
*   **Example Response Body (200 OK):** (Similar structure to List Concepts)

#### 2.9 Get Content Modules for a Concept
*   **Method:** `GET`
*   **Path:** `/concepts/{conceptId}/modules`
*   **Description:** Retrieves all content modules that teach a specific concept.
*   **Example Response Body (200 OK):** (List of ContentModule objects)

#### 2.10 Get Content Modules for a Skill
*   **Method:** `GET`
*   **Path:** `/skills/{skillId}/modules`
*   **Description:** Retrieves all content modules that help develop a specific skill.
*   **Example Response Body (200 OK):** (List of ContentModule objects)

---

## 3. Learning Pathway Service

Manages creation, retrieval, and user progress in learning paths.

### Endpoints

#### 3.1 Create Learning Path
*   **Method:** `POST`
*   **Path:** `/paths`
*   **Description:** Creates a new learning path (typically by educators or AI).
*   **Example Request Body:**
    ```json
    {
      "name": "Foundations of Data Science",
      "description": "A comprehensive path for beginners in Data Science.",
      "targetAudience": "Beginners with some programming knowledge",
      "moduleSequence": [
        {"moduleId": "module_stats_basics", "order": 1, "isOptional": false},
        {"moduleId": "module_python_data", "order": 2, "isOptional": false},
        {"moduleId": "module_ml_intro", "order": 3, "isOptional": true}
      ],
      "conceptsTargeted": ["concept_statistics", "concept_data_analysis"],
      "skillsDeveloped": ["skill_data_analysis_novice", "skill_python_for_ds"]
    }
    ```
*   **Example Response Body (201 Created):**
    ```json
    {
      "pathId": "path_uuid_789",
      "name": "Foundations of Data Science",
      "description": "A comprehensive path for beginners in Data Science.",
      "estimatedTotalDurationMinutes": 720, // Calculated by service
      "moduleSequence": [
        {"moduleId": "module_stats_basics", "order": 1, "isOptional": false, "title": "Statistics Basics"},
        {"moduleId": "module_python_data", "order": 2, "isOptional": false, "title": "Python for Data Handling"},
        {"moduleId": "module_ml_intro", "order": 3, "isOptional": true, "title": "Intro to Machine Learning"}
      ],
      // ... other fields
      "createdBy": "userId_educator_1" // or "AI_MENTOR"
    }
    ```

#### 3.2 Get Learning Path
*   **Method:** `GET`
*   **Path:** `/paths/{pathId}`
*   **Description:** Retrieves a specific learning path.
*   **Example Response Body (200 OK):** (Similar to 3.1 Response)

#### 3.3 Update Learning Path
*   **Method:** `PUT`
*   **Path:** `/paths/{pathId}`
*   **Description:** Updates an existing learning path.
*   **Example Request Body:** (Similar to 3.1 Request)
*   **Example Response Body (200 OK):** (Similar to 3.1 Response)

#### 3.4 Delete Learning Path
*   **Method:** `DELETE`
*   **Path:** `/paths/{pathId}`
*   **Description:** Deletes a learning path.
*   **Example Response Body (204 No Content):** (Empty body)

#### 3.5 List Learning Paths
*   **Method:** `GET`
*   **Path:** `/paths`
*   **Description:** Retrieves a list of available learning paths.
*   **Key Query Parameters:** `keyword=`, `targetAudience=`, `conceptId=`, `skillId=`, `limit=10`, `offset=0`
*   **Example Response Body (200 OK):** (Paginated list of LearningPath summaries)

#### 3.6 Enroll User in Learning Path
*   **Method:** `POST`
*   **Path:** `/users/{userId}/paths/{pathId}/enroll`
*   **Description:** Enrolls a user in a learning path.
*   **Example Request Body:** (Empty or can contain start date preference)
*   **Example Response Body (200 OK):**
    ```json
    {
      "userId": "user_uuid_456",
      "pathId": "path_uuid_789",
      "enrollmentDate": "2023-10-27T14:00:00Z",
      "status": "active",
      "currentModuleId": "module_stats_basics" // First module
    }
    ```

#### 3.7 Get User Enrollment for a Path
*   **Method:** `GET`
*   **Path:** `/users/{userId}/paths/{pathId}/enrollment`
*   **Description:** Retrieves a user's enrollment status and progress for a specific path.
*   **Example Response Body (200 OK):** (Similar to 3.6 Response, with progress details)
    ```json
    {
      "userId": "user_uuid_456",
      "pathId": "path_uuid_789",
      "enrollmentDate": "2023-10-27T14:00:00Z",
      "status": "active",
      "currentModuleId": "module_python_data",
      "completedModules": ["module_stats_basics"],
      "progressPercentage": 33.3
    }
    ```

#### 3.8 Update User Progress in Path
*   **Method:** `PUT`
*   **Path:** `/users/{userId}/paths/{pathId}/progress`
*   **Description:** Updates a user's progress in a learning path (e.g., when a module is completed).
*   **Example Request Body:**
    ```json
    {
      "completedModuleId": "module_python_data",
      "nextModuleId": "module_ml_intro", // Optional, can be determined by service
      "status": "active" // or "completed" if path is finished
    }
    ```
*   **Example Response Body (200 OK):** (Updated enrollment/progress details, similar to 3.7)

#### 3.9 List User's Enrolled Paths
*   **Method:** `GET`
*   **Path:** `/users/{userId}/paths`
*   **Description:** Retrieves all learning paths a user is enrolled in.
*   **Key Query Parameters:** `status=active`, `limit=10`, `offset=0`
*   **Example Response Body (200 OK):** (Paginated list of enrollment objects)

---

## 4. AI Mentor Service

Handles interactions with the AI learning assistant.

### Endpoints

#### 4.1 Submit Query to AI Mentor
*   **Method:** `POST`
*   **Path:** `/mentor/query`
*   **Description:** Sends a user's query to the AI mentor.
*   **Example Request Body:**
    ```json
    {
      "userId": "user_uuid_456",
      "text": "Can you explain the difference between supervised and unsupervised machine learning?",
      "context": { // Optional context, like current module or concept
        "currentModuleId": "module_ml_intro",
        "currentConceptId": "concept_machine_learning_types"
      },
      "conversationId": "conv_uuid_abc" // Optional, for ongoing conversations
    }
    ```
*   **Example Response Body (200 OK):**
    ```json
    {
      "responseId": "resp_uuid_123",
      "conversationId": "conv_uuid_abc", // Maintained or new if not provided
      "userId": "user_uuid_456",
      "responseText": "Supervised learning uses labeled data to train models, where the model learns to map inputs to known outputs. Unsupervised learning, on the other hand, uses unlabeled data, and the model tries to find patterns or structure within the data itself, like clustering similar data points.",
      "suggestedActions": [
        {"type": "VIEW_CONCEPT", "label": "Explore Supervised Learning", "conceptId": "concept_supervised_ml"},
        {"type": "VIEW_MODULE", "label": "Watch Unsupervised Learning Video", "moduleId": "module_unsupervised_video"}
      ],
      "timestamp": "2023-10-27T15:00:00Z"
    }
    ```

#### 4.2 Get Conversation History
*   **Method:** `GET`
*   **Path:** `/mentor/history/{userId}`
*   **Description:** Retrieves the conversation history for a user with the AI mentor.
*   **Key Query Parameters:** `conversationId=`, `limit=20`, `beforeTimestamp=`
*   **Example Response Body (200 OK):**
    ```json
    {
      "userId": "user_uuid_456",
      "conversations": [
        {
          "conversationId": "conv_uuid_abc",
          "lastActivity": "2023-10-27T15:00:00Z",
          "messages": [
            {"sender": "user", "text": "...", "timestamp": "..."},
            {"sender": "ai_mentor", "text": "...", "timestamp": "..."}
          ]
        }
        // ... more conversations
      ]
    }
    ```
*(Internal endpoints for managing user-specific memory/embeddings in the vector DB would likely be part of the service's internal logic triggered by queries or updates, rather than direct public API calls. If specific external triggers are needed, they could be designed, e.g., `POST /mentor/memory/{userId}/update`)*

---

## 5. Credentialing Service

Manages the issuance and verification of learning credentials.

### Endpoints

#### 5.1 Issue Credential
*   **Method:** `POST`
*   **Path:** `/credentials/issue`
*   **Description:** Issues a new credential to a user upon completion of requirements (triggered by Learning Pathway Service or admin).
*   **Example Request Body:**
    ```json
    {
      "userId": "user_uuid_456",
      "name": "Certified Python Programmer - Level 1",
      "description": "Demonstrates foundational knowledge of Python programming.",
      "issuingOrganization": "NeuroForge",
      "pathId": "path_python_foundations", // Optional: path that led to credential
      "skillIds": ["skill_python_programming"], // Optional: skills certified
      "conceptIds": ["concept_python_basics", "concept_data_structures"] // Optional
      // Blockchain details (e.g., address) might be handled internally or passed if pre-generated
    }
    ```
*   **Example Response Body (201 Created):**
    ```json
    {
      "credentialId": "cred_uuid_xyz",
      "userId": "user_uuid_456",
      "name": "Certified Python Programmer - Level 1",
      "description": "Demonstrates foundational knowledge of Python programming.",
      "issuingOrganization": "NeuroForge",
      "issueDate": "2023-10-27T16:00:00Z",
      "credentialUrl": "https://credentials.neuroforge.com/verify/cred_uuid_xyz",
      "imageUrl": "https://credentials.neuroforge.com/images/python_level1.png",
      "blockchainTransactionId": "0xabc123..." // If applicable
    }
    ```

#### 5.2 Get Credential
*   **Method:** `GET`
*   **Path:** `/credentials/{credentialId}`
*   **Description:** Retrieves details of a specific credential.
*   **Example Response Body (200 OK):** (Similar to 5.1 Response)

#### 5.3 Verify Credential
*   **Method:** `GET`
*   **Path:** `/credentials/{credentialId}/verify`
*   **Description:** Verifies the authenticity and status of a credential (can be public).
*   **Example Response Body (200 OK):**
    ```json
    {
      "credentialId": "cred_uuid_xyz",
      "isValid": true,
      "status": "Active", // e.g., Active, Expired, Revoked
      "name": "Certified Python Programmer - Level 1",
      "userId": "user_uuid_456", // Or a hashed/anonymized identifier for public verification
      "userName": "Current Learner", // Optional, with user consent for public display
      "issueDate": "2023-10-27T16:00:00Z",
      "issuingOrganization": "NeuroForge",
      "blockchainVerificationLink": "https://polygonscan.com/tx/0xabc123..." // If applicable
    }
    ```

#### 5.4 List User's Credentials
*   **Method:** `GET`
*   **Path:** `/users/{userId}/credentials`
*   **Description:** Retrieves all credentials earned by a specific user.
*   **Key Query Parameters:** `limit=10`, `offset=0`
*   **Example Response Body (200 OK):** (Paginated list of Credential objects similar to 5.1 response)

---

## 6. Cognitive Profiling Service

Manages user interaction data for behavioral analysis and profile generation.

### Endpoints

#### 6.1 Submit Interaction Event
*   **Method:** `POST`
*   **Path:** `/profiling/interactions`
*   **Description:** Receives interaction data from other services (e.g., UI, Content Service).
*   **Example Request Body:**
    ```json
    {
      "eventId": "event_uuid_interaction_1",
      "userId": "user_uuid_456",
      "targetId": "module_intro_python_video",
      "targetType": "ContentModule",
      "eventType": "VIEW", // e.g., VIEW, COMPLETE, SUBMIT_ANSWER, PAUSE
      "timestamp": "2023-10-27T11:30:00Z",
      "durationSeconds": 300, // For timed interactions
      "details": { // Event-specific data
        "progressPercentage": 25,
        "videoTime": "00:05:00"
      }
    }
    ```
*   **Example Response Body (202 Accepted):**
    ```json
    {
      "message": "Interaction event accepted for processing.",
      "eventId": "event_uuid_interaction_1"
    }
    ```
    *(Processing happens asynchronously)*

#### 6.2 Get User Cognitive Profile Summary
*   **Method:** `GET`
*   **Path:** `/profiling/users/{userId}/summary`
*   **Description:** Retrieves a summary of the user's cognitive profile.
*   **Example Response Body (200 OK):**
    ```json
    {
      "userId": "user_uuid_456",
      "summary": {
        "dominantLearningStyles": ["Visual", "Kinesthetic"],
        "strengths": ["Pattern Recognition", "Problem Solving in Python"],
        "areasForDevelopment": ["Abstract Conceptualization", "Advanced Statistics"],
        "engagementMetrics": {
          "preferredContentTypes": ["VIDEO", "INTERACTIVE_SIMULATION"],
          "averageSessionDurationMinutes": 45
        },
        "lastUpdated": "2023-10-27T18:00:00Z"
      }
    }
    ```

#### 6.3 Get User Behavioral Heatmap
*   **Method:** `GET`
*   **Path:** `/profiling/users/{userId}/heatmap`
*   **Description:** Retrieves specific behavioral heatmap data for a user.
*   **Key Query Parameters:** `topic=`, `timeRange=`, `dataType=` (e.g., `engagement`, `difficulty_struggle`)
*   **Example Response Body (200 OK):**
    ```json
    {
      "userId": "user_uuid_456",
      "heatmapType": "engagement_by_topic",
      "data": [ // Structure depends on the heatmap visualization needs
        {"topicId": "concept_ai_basics", "engagementScore": 0.85},
        {"topicId": "concept_statistics", "engagementScore": 0.60},
        {"topicId": "concept_python_advanced", "engagementScore": 0.92}
      ],
      "generatedAt": "2023-10-27T18:05:00Z"
    }
    ```

---
This initial API design covers the core functionalities. Further iterations would involve refining error handling, adding more specific query parameters, and detailing security schemas (OAuth 2.0, etc.).
