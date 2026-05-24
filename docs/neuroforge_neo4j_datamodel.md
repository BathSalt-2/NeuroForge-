# NeuroForge: Neo4j Knowledge Graph Data Model

This document outlines the data model for NeuroForge's Knowledge Graph, implemented in Neo4j. It defines the node labels, relationship types, and their respective properties, designed to represent the entities and connections within the learning domain.

## 1. Node Labels

Node labels represent the primary entities within the NeuroForge ecosystem.

*   **`User`**
    *   **Description:** Represents an individual interacting with the platform, typically a learner, but could also be an educator or administrator.
    *   **Properties:**
        *   `userId`: STRING (Unique identifier)
        *   `username`: STRING (Public username)
        *   `email`: STRING (Unique email address)
        *   `hashedPassword`: STRING (For authentication)
        *   `firstName`: STRING
        *   `lastName`: STRING
        *   `role`: STRING (e.g., "learner", "educator", "admin")
        *   `cognitiveProfile`: STRING (JSON blob storing behavioral heatmap data, learning style preferences, etc.)
        *   `currentLearningGoals`: LIST<STRING> (List of `conceptId` or `skillId` the user is focused on)
        *   `createdAt`: DATETIME
        *   `lastLogin`: DATETIME

*   **`Concept`**
    *   **Description:** A fundamental piece of knowledge, theory, or topic. Concepts are the building blocks of understanding.
    *   **Properties:**
        *   `conceptId`: STRING (Unique identifier)
        *   `name`: STRING (e.g., "Newton's Laws of Motion", "Object-Oriented Programming")
        *   `description`: STRING (Detailed explanation of the concept)
        *   `difficultyLevel`: STRING (e.g., "Beginner", "Intermediate", "Advanced") or INTEGER (1-5)
        *   `domain`: STRING (e.g., "Physics", "Computer Science")
        *   `subDomain`: STRING (e.g., "Classical Mechanics", "Software Engineering")
        *   `keywords`: LIST<STRING>

*   **`Skill`**
    *   **Description:** A demonstrable ability or competency that a user can acquire and apply. Skills are often built upon understanding one or more concepts.
    *   **Properties:**
        *   `skillId`: STRING (Unique identifier)
        *   `name`: STRING (e.g., "Problem Solving", "Critical Thinking", "Java Programming")
        *   `description`: STRING (Detailed description of the skill)
        *   `proficiencyLevels`: LIST<STRING> (e.g., ["Novice", "Competent", "Proficient", "Expert"])
        *   `domain`: STRING
        *   `keywords`: LIST<STRING>

*   **`ContentModule`**
    *   **Description:** A specific unit of learning material designed to convey information or facilitate learning.
    *   **Properties:**
        *   `moduleId`: STRING (Unique identifier)
        *   `title`: STRING
        *   `type`: STRING (e.g., "VIDEO", "ARTICLE", "QUIZ", "INTERACTIVE_SIMULATION", "PROJECT_ASSIGNMENT")
        *   `format`: STRING (e.g., "video/mp4", "text/markdown", "application/pdf")
        *   `url`: STRING (Link to the content, if external) or internal storage path
        *   `estimatedDurationMinutes`: INTEGER (Estimated time to complete)
        *   `difficultyLevel`: STRING (e.g., "Beginner", "Intermediate", "Advanced") or INTEGER (1-5)
        *   `modalityHints`: LIST<STRING> (e.g., "visual", "auditory", "kinesthetic", "text-based") - to help with personalization
        *   `description`: STRING
        *   `publishedDate`: DATETIME
        *   `author`: STRING (or link to a User node if authored internally)
        *   `version`: STRING

*   **`LearningObjective`**
    *   **Description:** A specific, measurable goal a learner is expected to achieve after engaging with a `ContentModule` or a set of modules.
    *   **Properties:**
        *   `objectiveId`: STRING (Unique identifier)
        *   `description`: STRING (Clear statement of the objective, e.g., "User will be able to define X concept.")
        *   `measurableCriteria`: STRING (How achievement of the objective will be measured)

*   **`Assessment`**
    *   **Description:** A specific task, quiz, test, or project designed to evaluate a user's understanding of concepts or proficiency in skills.
    *   **Properties:**
        *   `assessmentId`: STRING (Unique identifier)
        *   `name`: STRING
        *   `type`: STRING (e.g., "MULTIPLE_CHOICE_QUIZ", "CODING_CHALLENGE", "ESSAY", "PROJECT_SUBMISSION")
        *   `description`: STRING
        *   `passingScoreThreshold`: FLOAT (e.g., 0.75 for 75%)
        *   `maxScore`: FLOAT
        *   `estimatedTimeMinutes`: INTEGER

*   **`Credential`**
    *   **Description:** A digital certificate, badge, or other form of recognition awarded to a user for achieving specific learning outcomes, skills, or completing learning paths.
    *   **Properties:**
        *   `credentialId`: STRING (Unique identifier)
        *   `name`: STRING (e.g., "Certified Python Developer - Level 1")
        *   `description`: STRING
        *   `issuingOrganization`: STRING (NeuroForge, or partnered org)
        *   `issueDate`: DATETIME
        *   `expiryDate`: DATETIME (Optional)
        *   `blockchainTransactionId`: STRING (If applicable, for on-chain credentials)
        *   `credentialUrl`: STRING (Link to view the credential, possibly on a verification platform)
        *   `imageUrl`: STRING (URL for the badge image)

*   **`LearningPath`**
    *   **Description:** A curated or dynamically generated sequence of `ContentModules`, `Concepts`, or `Skills` designed to guide a learner towards a specific goal.
    *   **Properties:**
        *   `pathId`: STRING (Unique identifier)
        *   `name`: STRING (e.g., "Introduction to Data Science Path")
        *   `description`: STRING
        *   `estimatedTotalDurationMinutes`: INTEGER
        *   `targetAudience`: STRING
        *   `isDynamic`: BOOLEAN (True if generated by AI Mentor, False if curated by an educator)
        *   `createdBy`: STRING (`userId` of educator or "AI_MENTOR")

*   **`Resource`**
    *   **Description:** External or supplementary materials that can support learning but are not formal `ContentModules`.
    *   **Properties:**
        *   `resourceId`: STRING (Unique identifier)
        *   `name`: STRING
        *   `type`: STRING (e.g., "RESEARCH_PAPER", "TUTORIAL_WEBSITE", "SOFTWARE_TOOL", "BOOK_REFERENCE")
        *   `url`: STRING
        *   `description`: STRING

*   **`InteractionEvent`**
    *   **Description:** Records significant interactions a user has with content or assessments. Used for cognitive profiling and analytics. This node can grow very large, so consider strategies for aggregation or offloading to analytical databases if performance becomes an issue. Alternatively, some interactions can be properties on relationships (e.g., `COMPLETED_MODULE`).
    *   **Properties:**
        *   `eventId`: STRING (Unique identifier)
        *   `userId`: STRING
        *   `targetId`: STRING (`moduleId`, `assessmentId`, `conceptId`, etc.)
        *   `targetType`: STRING (e.g., "ContentModule", "Assessment")
        *   `eventType`: STRING (e.g., "VIEW", "START", "COMPLETE", "SUBMIT_ANSWER", "PAUSE", "SKIP_CONTENT")
        *   `timestamp`: DATETIME
        *   `durationSeconds`: INTEGER (For timed interactions)
        *   `details`: STRING (JSON blob for event-specific data, e.g., answer given, video progress)

## 2. Relationship Types

Relationship types define how these nodes are connected.

*   **Concept Relationships:**
    *   `(:Concept)-[:PREREQUISITE_OF]->(:Concept)`
        *   **Description:** One concept is a necessary foundation for understanding another. (e.g., "Basic Algebra" -[:PREREQUISITE_OF]-> "Calculus I")
    *   `(:Concept)-[:RELATED_TO]->(:Concept)`
        *   **Description:** Two concepts are thematically or contextually related. (e.g., "Photosynthesis" -[:RELATED_TO]-> "Cellular Respiration")
    *   `(:Concept)-[:PART_OF]->(:Concept)`
        *   **Description:** A concept is a sub-component of a larger conceptual domain. (e.g., "Variable Declaration" -[:PART_OF]-> "Programming Fundamentals")

*   **Skill Relationships:**
    *   `(:Skill)-[:COMPOSED_OF]->(:Skill)`
        *   **Description:** A complex skill is made up of several sub-skills. (e.g., "Scientific Research" -[:COMPOSED_OF]-> "Data Analysis")
    *   `(:Skill)-[:PREREQUISITE_FOR_SKILL]->(:Skill)`
        *   **Description:** One skill should ideally be acquired before another.
    *   `(:Skill)-[:LEADS_TO_DEVELOPMENT_OF]->(:Concept)` (Less common, but a skill might lead to deeper conceptual understanding)

*   **Content & Learning Structure Relationships:**
    *   `(:ContentModule)-[:TEACHES_CONCEPT]->(:Concept)`
        *   **Description:** A content module covers or aims to impart understanding of a specific concept.
    *   `(:ContentModule)-[:DEVELOPS_SKILL]->(:Skill)`
        *   **Description:** A content module is designed to help develop a specific skill.
    *   `(:ContentModule)-[:HAS_OBJECTIVE]->(:LearningObjective)`
        *   **Description:** Connects a module to its stated learning outcomes.
    *   `(:ContentModule)-[:ASSESSES_CONCEPT]->(:Concept)`
        *   **Description:** A module (e.g., a quiz) assesses understanding of a concept.
    *   `(:ContentModule)-[:ASSESSES_SKILL]->(:Skill)`
        *   **Description:** A module (e.g., a project) assesses proficiency in a skill.
    *   `(:LearningObjective)-[:MEASURED_BY_MODULE]->(:ContentModule)` (Inverse of HAS_OBJECTIVE if needed, or through Assessment)
    *   `(:LearningObjective)-[:RELATES_TO_CONCEPT]->(:Concept)`
    *   `(:LearningObjective)-[:RELATES_TO_SKILL]->(:Skill)`

*   **Assessment Relationships:**
    *   `(:Assessment)-[:EVALUATES_CONCEPT]->(:Concept)`
        *   **Description:** An assessment is designed to test knowledge of a concept.
    *   `(:Assessment)-[:EVALUATES_SKILL]->(:Skill)`
        *   **Description:** An assessment is designed to measure proficiency in a skill.
    *   `(:ContentModule)-[:INCLUDES_ASSESSMENT]->(:Assessment)` (If assessment is part of a module)
        *   **Properties:** `order`: INTEGER (If multiple assessments in a module)

*   **User Interaction & Progress Relationships:**
    *   `(:User)-[:HAS_COMPLETED_MODULE]->(:ContentModule)`
        *   **Properties:** `completionDate`: DATETIME, `timeTakenSeconds`: INTEGER, `userRating`: INTEGER (1-5), `notes`: STRING
    *   `(:User)-[:HAS_ACHIEVED_SKILL]->(:Skill)`
        *   **Properties:** `achievementDate`: DATETIME, `proficiencyLevel`: STRING (e.g., "Proficient"), `evidenceUrl`: STRING (Link to project, assessment result)
    *   `(:User)-[:UNDERSTANDS_CONCEPT]->(:Concept)`
        *   **Properties:** `understandingLevel`: STRING (e.g., "Basic", "Deep"), `lastAssessedDate`: DATETIME
    *   `(:User)-[:HAS_EARNED_CREDENTIAL]->(:Credential)`
        *   **Properties:** `issueDate`: DATETIME (Redundant if same as on Credential node, but useful for query)
    *   `(:User)-[:INTERESTED_IN_CONCEPT]->(:Concept)`
        *   **Properties:** `interestLevel`: INTEGER (1-5), `dateAdded`: DATETIME, `source`: STRING (e.g., "user_declared", "ai_suggested")
    *   `(:User)-[:INTERESTED_IN_SKILL]->(:Skill)`
        *   **Properties:** `interestLevel`: INTEGER (1-5), `dateAdded`: DATETIME, `source`: STRING
    *   `(:User)-[:ENROLLED_IN_PATH]->(:LearningPath)`
        *   **Properties:** `enrollmentDate`: DATETIME, `status`: STRING (e.g., "active", "completed", "paused")
    *   `(:User)-[:CURRENTLY_AT_MODULE_IN_PATH]->(:ContentModule)` (Points to current position in a specific LearningPath)
        *   **Properties:** `pathId`: STRING (To specify which path this relation refers to, if user is on multiple paths)
    *   `(:User)-[:ATTEMPTED_ASSESSMENT]->(:Assessment)`
        *   **Properties:** `attemptDate`: DATETIME, `score`: FLOAT, `passed`: BOOLEAN, `answers`: STRING (JSON of answers given)
    *   `(:User)-[:BOOKMARKED_MODULE]->(:ContentModule)`
        *   **Properties:** `dateBookmarked`: DATETIME
    *   `(:User)-[:BOOKMARKED_RESOURCE]->(:Resource)`
        *   **Properties:** `dateBookmarked`: DATETIME
    *   `(:User)-[:FOLLOWS_USER]->(:User)` (For social learning aspects)
    *   `(:User)-[:HAS_RECORDED_EVENT]->(:InteractionEvent)` (Connects user to their raw interaction data)

*   **Learning Path Relationships:**
    *   `(:LearningPath)-[:STARTS_WITH_MODULE]->(:ContentModule)`
    *   `(:LearningPath)-[:CONTAINS_MODULE]->(:ContentModule)`
        *   **Properties:** `sequenceOrder`: INTEGER, `isOptional`: BOOLEAN
    *   `(:ContentModule)-[:NEXT_IN_PATH]->(:ContentModule)` (Used within a specific LearningPath context)
        *   **Properties:** `pathId`: STRING (To specify which path this sequence belongs to)
    *   `(:LearningPath)-[:TARGETS_CONCEPT]->(:Concept)`
        *   **Description:** The learning path aims to teach this concept.
    *   `(:LearningPath)-[:DEVELOPS_SKILL_PATH]->(:Skill)` (Renamed to avoid conflict with ContentModule relationship)
        *   **Description:** The learning path aims to develop this skill.
    *   `(:LearningPath)-[:LEADS_TO_CREDENTIAL]->(:Credential)`

*   **Credentialing Relationships:**
    *   `(:Credential)-[:CERTIFIES_SKILL]->(:Skill)`
        *   **Properties:** `requiredProficiency`: STRING
    *   `(:Credential)-[:CERTIFIES_CONCEPT_MASTERY]->(:Concept)`
    *   `(:Credential)-[:AWARDED_FOR_PATH]->(:LearningPath)`
    *   `(:Credential)-[:AWARDED_FOR_MODULE_COMPLETION]->(:ContentModule)`

*   **Resource & Supplementary Relationships:**
    *   `(:ContentModule)-[:INCLUDES_RESOURCE]->(:Resource)`
    *   `(:Concept)-[:HAS_SUPPLEMENTARY_RESOURCE]->(:Resource)`
    *   `(:Skill)-[:HAS_PRACTICE_RESOURCE]->(:Resource)`

## 3. Properties on Relationships

Many relationship properties are listed above, directly under the relationship they belong to. Key considerations for relationship properties:

*   **Timestamps:** `createdAt`, `startDate`, `endDate`, `completionDate` are common for time-bound interactions.
*   **Contextualizers:** Properties that define the specifics of the connection, e.g., `interestLevel` on `INTERESTED_IN`, `sequenceOrder` on `CONTAINS_MODULE`.
*   **Evidence/Scores:** `score`, `proficiencyLevel`, `evidenceUrl` for achievements and assessments.

## Design Considerations

*   **Granularity vs. Performance:** The `InteractionEvent` node could lead to a very dense graph. For high-frequency events, consider if some data can be stored as properties on user-content relationships or aggregated. Alternatively, use a separate time-series database for fine-grained interaction logs, with the graph storing summaries or significant milestones.
*   **Dynamic vs. Static Data:** User progress and interaction data are highly dynamic. Concepts, skills, and content modules are more static but can evolve.
*   **Query Patterns:** The model is designed to support queries like:
    *   "Recommend next modules for a user based on their current skills and interests."
    *   "Show learning paths that lead to a specific skill or credential."
    *   "Identify concepts a user is struggling with based on assessment attempts."
    *   "Find experts in a particular skill."
    *   "Visualize the prerequisite chain for an advanced concept."
*   **Evolution:** This model provides a solid foundation. As NeuroForge evolves, new node labels, relationships, and properties can be added. For example, `Community` or `ProjectGroup` nodes could be introduced for collaborative features.

This data model aims to create a rich, interconnected representation of the learning landscape within NeuroForge, enabling personalized learning experiences, advanced analytics, and robust knowledge management.
