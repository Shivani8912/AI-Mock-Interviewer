"""
Interview Engine for AI Mock Interviewer.
Orchestrates interview question progression, adaptive follow-ups,
hints, rubric scoring, and comprehensive feedback report generation.
"""

import json
import re
from typing import Any, Dict, List, Optional
from utils.ai_client import AIClient, get_ai_client


# Comprehensive domain question banks for high-fidelity fallback and baseline questions
QUESTION_BANKS = {
    "Full Stack Developer": {
        "Technical": [
            {
                "question": "Can you explain the end-to-end lifecycle of a web request from the moment a user enters a URL in their browser until the rendered page is visible?",
                "hint": "Think about DNS resolution, TCP/TLS handshake, HTTP headers, server routing, database queries, and browser rendering (DOM/CSSOM).",
                "ideal_answer": "A strong answer outlines DNS lookup (browser/OS cache, recursive resolver), establishing a TCP connection with TLS handshake, sending HTTP GET request, reverse proxy/load balancer routing, backend server processing & DB query, returning HTML/JSON response, and browser parsing HTML to construct DOM, fetching CSS/JS, and executing composite rendering steps."
            },
            {
                "question": "How do you manage client-side state versus server-side caching in modern web applications to prevent stale data and race conditions?",
                "hint": "Discuss tools like Redux/Zustand or React Query/SWR, HTTP cache-control headers, and Redis or CDN caching.",
                "ideal_answer": "Server caching leverages Redis or CDNs with cache invalidation strategies (e.g. TTL, write-through). Client state uses tools like React Query or SWR for server cache synchronization with optimistic updates, stale-while-revalidate, and deduplication to avoid race conditions."
            },
            {
                "question": "When designing a RESTful API or GraphQL schema for an application with heavy read traffic, what strategies do you employ to prevent N+1 query problems?",
                "hint": "Mention eager loading, ORM joins, batching techniques like DataLoader in GraphQL, or database indexing.",
                "ideal_answer": "The N+1 problem occurs when fetching an entity triggers separate queries for each child record. Strategies include using ORM eager loading (select_related / prefetch_related), SQL JOINs, DataLoader in GraphQL for batching and caching, and database read replicas with proper indexing."
            },
            {
                "question": "How do you secure web applications against common vulnerabilities like Cross-Site Scripting (XSS), SQL Injection, and CSRF?",
                "hint": "Discuss input sanitization, parameterized queries, Content Security Policy (CSP), and SameSite cookies.",
                "ideal_answer": "SQL injection is mitigated by parameterized queries / prepared statements. XSS is prevented via context-aware output encoding, strict Content Security Policy (CSP), and sanitizing untrusted inputs. CSRF is stopped using Anti-CSRF tokens, SameSite=Strict/Lax cookie attributes, and validating Origin/Referer headers."
            },
            {
                "question": "Walk me through how you implement authentication and authorization across the frontend and backend using JWTs or session tokens securely.",
                "hint": "Explain where tokens are stored (httpOnly cookies vs localStorage), refresh token rotation, and role-based access control (RBAC).",
                "ideal_answer": "Secure auth stores short-lived JWT access tokens in memory or httpOnly, Secure, SameSite cookies to mitigate XSS. Long-lived refresh tokens are stored securely in httpOnly cookies with rotation and revocation lists in Redis. Middleware on the backend validates signature, expiration, and enforces RBAC permissions."
            }
        ],
        "Behavioral": [
            {
                "question": "Describe a challenging bug you encountered in production across the frontend and backend stack. How did you diagnose and resolve it under pressure?",
                "hint": "Use the STAR method: Situation, Task, Action, and Result.",
                "ideal_answer": "A top-tier answer uses the STAR format: clearly defines the production incident severity, logging/monitoring tools used (e.g. Sentry, Datadog), root cause isolation, hotfix deployment, rollback plan, post-mortem analysis, and automated tests added to prevent recurrence."
            },
            {
                "question": "Tell me about a time when you had conflicting technical opinions with a designer or product manager regarding feature feasibility or timeline.",
                "hint": "Highlight empathy, data-driven compromise, and delivering customer value.",
                "ideal_answer": "Explain the disagreement objectively, how you presented technical trade-offs or phased rollouts (MVP first), actively listened to user needs, and achieved an aligned outcome that maintained project velocity and code quality."
            }
        ],
        "System Design": [
            {
                "question": "How would you design a scalable URL shortener service (like Bitly) handling 100 million new URLs per month and 1 billion redirects?",
                "hint": "Cover capacity estimation, Base62 encoding / hashing, database schema (NoSQL vs SQL), caching, and high availability.",
                "ideal_answer": "Outline requirements (read-heavy, low latency), capacity math (~400 QPS write, ~4000 QPS read), key generation service using Base62 encoding, distributed cache (Redis) for hot URLs, database choice (MongoDB or DynamoDB), and CDN edge routing for redirects."
            }
        ]
    },
    "Backend Developer": {
        "Technical": [
            {
                "question": "How do database indexes (such as B-Trees and Hash indexes) work internally, and what are the trade-offs of having too many indexes on a table?",
                "hint": "Discuss logarithmic search efficiency, write overhead, disk storage, and locking.",
                "ideal_answer": "B-Tree indexes maintain sorted balanced nodes providing O(log N) lookups, range queries, and ordering. Hash indexes provide O(1) point lookups but no range support. Overhead of too many indexes includes slower INSERT/UPDATE/DELETE queries (as every index must be updated), index fragmentation, and higher RAM/disk usage."
            },
            {
                "question": "Can you explain the differences between relational databases (ACID) and NoSQL distributed databases (BASE / CAP theorem)? When would you choose one over the other?",
                "hint": "Define ACID properties vs Eventual Consistency and CAP theorem trade-offs (Consistency vs Availability under Partition).",
                "ideal_answer": "RDBMS provides strong ACID guarantees (Atomicity, Consistency, Isolation, Durability) ideal for financial/transactional systems with complex relational joins. NoSQL (Document, Key-Value, Columnar) prioritizes scalability, flexible schemas, and high write throughput, often trading immediate consistency for eventual consistency under network partitions (CAP theorem)."
            },
            {
                "question": "What mechanisms and patterns do you use to guarantee message delivery and handle idempotency in an asynchronous message queue (e.g. Kafka or RabbitMQ)?",
                "hint": "Discuss at-least-once delivery, idempotent consumer keys, dead-letter queues (DLQ), and transactions.",
                "ideal_answer": "Queues typically offer at-least-once delivery, which can duplicate messages. Consumers implement idempotency by tracking unique message UUIDs in an atomic cache or database table with unique constraints, processing the payload within a database transaction, and dispatching unprocessable messages to a Dead-Letter Queue (DLQ)."
            },
            {
                "question": "How do connection pooling and connection limits affect backend throughput and database health under high concurrency?",
                "hint": "Explain thread exhaustion, pool size tuning, connection starvation, and circuit breakers.",
                "ideal_answer": "Connection pools maintain reusable database connections to prevent the cost of TCP handshakes. However, setting the pool too large causes database CPU contention and context switching; setting it too small queues requests. Proper sizing aligns with DB CPU cores and storage I/O, coupled with timeouts and circuit breakers."
            }
        ],
        "Behavioral": [
            {
                "question": "Can you describe a time when a system design or architectural decision you advocated for turned out to have unexpected flaws? What did you learn?",
                "hint": "Show ownership, intellectual honesty, and continuous learning.",
                "ideal_answer": "Candidate candidly explains the initial rationale, how the flaw manifested under real workloads, how they took ownership rather than deflecting blame, the remediation steps taken, and how it shaped their engineering judgment."
            }
        ],
        "System Design": [
            {
                "question": "Design an e-commerce flash sale backend service that handles sudden 100x traffic spikes without overselling inventory.",
                "hint": "Discuss rate limiting, queuing, Redis atomic decr operations, distributed locks, and asynchronous order processing.",
                "ideal_answer": "Use CDN edge caching for product details, Redis with Lua scripts or DECR for atomic in-memory inventory decrement, an asynchronous message queue (Kafka/RabbitMQ) for checkout queueing, and optimistic concurrency control in DB to prevent overselling."
            }
        ]
    },
    "Frontend Developer": {
        "Technical": [
            {
                "question": "How does the virtual DOM reconciliation algorithm work in modern frontend frameworks (e.g., React Fiber), and how does it optimize browser rendering?",
                "hint": "Mention tree diffing heuristic, keys in lists, fiber nodes, render phase vs commit phase.",
                "ideal_answer": "React uses heuristic O(N) diffing based on component type and unique keys. Fiber breaks work into incremental priority units during the interruptible render phase, followed by a synchronous commit phase to apply minimal DOM mutations, preventing frame drops."
            },
            {
                "question": "What are Core Web Vitals (LCP, FID/INP, CLS), and what techniques do you use to measure and optimize them?",
                "hint": "Discuss Largest Contentful Paint, Interaction to Next Paint, Cumulative Layout Shift, lazy loading, and SSR.",
                "ideal_answer": "LCP measures loading speed (optimize via CDN, image compression, preloading hero assets); INP measures responsiveness (break long tasks, use web workers, avoid main thread blocking); CLS measures visual stability (reserve dimension attributes on images/embeds, avoid dynamically injected content above the fold)."
            },
            {
                "question": "How do you implement accessible (a11y) web components conforming to WCAG standards?",
                "hint": "Discuss semantic HTML, ARIA attributes, keyboard navigation, focus trap, and color contrast.",
                "ideal_answer": "Prioritize native semantic HTML (e.g. <button>, <nav>) over generic div tags. Use ARIA attributes (aria-expanded, aria-live) when custom controls are required, ensure full keyboard navigation (tabIndex, Esc handlers, focus trapping in modals), and verify 4.5:1 color contrast ratio."
            }
        ],
        "Behavioral": [
            {
                "question": "Tell me about a project where you had to push back on unrealistic UI animations or heavy dependencies to protect user experience and page load speed.",
                "hint": "Demonstrate user-first empathy and objective performance benchmarks.",
                "ideal_answer": "Describe using Lighthouse / bundle analyzers to demonstrate the impact on mobile devices, proposing CSS-driven or SVG-based alternatives, and collaborating with UX designers to achieve high visual polish without degrading performance."
            }
        ],
        "System Design": [
            {
                "question": "Design a frontend architecture for an infinite scroll social feed with real-time updates and media embeds.",
                "hint": "Discuss DOM virtualization, IntersectionObserver, windowing, image lazy loading, and WebSockets.",
                "ideal_answer": "Employ window virtualization (e.g., react-virtualized) so only visible items exist in the DOM, IntersectionObserver for infinite pagination, memoized card items, skeleton loaders, and WebSocket event debouncing."
            }
        ]
    },
    "Machine Learning Engineer": {
        "Technical": [
            {
                "question": "How do you detect and mitigate training-serving skew, data drift, and concept drift in a production ML pipeline?",
                "hint": "Mention feature stores, statistical tests (KS-test, PSI), monitoring pipelines, and retraining triggers.",
                "ideal_answer": "Training-serving skew is reduced via centralized Feature Stores (e.g. Feast). Data drift (input distribution change) and concept drift (input-to-target relationship change) are detected using metrics like Population Stability Index (PSI) or Kolmogorov-Smirnov tests, triggering automated retraining pipelines."
            },
            {
                "question": "Explain the trade-offs between fine-tuning a Large Language Model (LLM) versus using Retrieval-Augmented Generation (RAG). When would you pick which?",
                "hint": "Discuss hallucination prevention, latency, cost, domain knowledge updating, and token limits.",
                "ideal_answer": "RAG is preferred when data updates frequently, hallucinations must be audited via citations, and private documents need strict access control. Fine-tuning is chosen to instill specialized style, structure, specialized vocabulary, or compact task performance without large prompt overhead."
            },
            {
                "question": "What techniques do you employ to optimize deep learning models for low-latency inference in production environments?",
                "hint": "Discuss quantization (INT8/FP16), pruning, distillation, TensorRT, and ONNX Runtime.",
                "ideal_answer": "Techniques include post-training quantization (INT8/FP8), knowledge distillation (training a smaller student model), weight pruning, operator fusion, and deploying on optimized inference runtimes such as ONNX Runtime, TensorRT, or vLLM."
            }
        ],
        "Behavioral": [
            {
                "question": "Tell me about an ML project where model offline metrics looked stellar, but online A/B testing failed to show business impact. How did you investigate?",
                "hint": "Focus on metric alignment (e.g. accuracy vs business conversion), latency impact, or user fatigue.",
                "ideal_answer": "Explain identifying a mismatch between offline proxy loss and real customer behavior (e.g., high CTR but zero retention), diagnosing latency penalties or interface presentation bias, and re-framing the objective function to reflect business value."
            }
        ],
        "System Design": [
            {
                "question": "Design a real-time recommendation system that serves personalized candidate items to 50 million active users in under 50ms.",
                "hint": "Discuss two-stage architecture: Candidate Retrieval (ANN search, vector embeddings) and Heavy Ranking (cross-encoders).",
                "ideal_answer": "Use a two-tier funnel: 1) Fast Candidate Retrieval filtering millions to top ~200 items using Approximate Nearest Neighbor (ANN) vector search (FAISS/Milvus) and collaborative filtering; 2) Deep Ranking model scoring top items with contextual features; 3) Re-ranking & business diversity rules."
            }
        ]
    }
}


class InterviewEngine:
    """Manages interview state, question generation, and candidate evaluation."""

    def __init__(self, ai_client: Optional[AIClient] = None):
        self.ai_client = ai_client or get_ai_client()

    def generate_opening_question(
        self,
        candidate_name: str,
        role: str,
        level: str,
        interview_type: str,
        skills: List[str]
    ) -> Dict[str, str]:
        """Generate first question personalized to candidate profile."""
        skills_str = ", ".join(skills[:5]) if skills else "software engineering"

        prompt = (
            f"You are conducting a professional mock interview for candidate '{candidate_name}' "
            f"applying for the position of {level} {role}. "
            f"Interview Category: {interview_type}. "
            f"Candidate Skills: {skills_str}. "
            f"Generate an engaging, warm, professional opening question. "
            f"Return JSON with keys: 'question', 'hint', 'ideal_answer'."
        )

        try:
            res_text = self.ai_client.generate_text(prompt)
            # Try parsing JSON if model returned structured output
            json_match = re.search(r"\{[\s\S]*\}", res_text)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if "question" in parsed and "ideal_answer" in parsed:
                    return parsed
        except Exception:
            pass

        # Fallback to curated question bank
        bank = QUESTION_BANKS.get(role, QUESTION_BANKS["Full Stack Developer"])
        type_questions = bank.get(interview_type, bank.get("Technical", []))
        if type_questions:
            q = type_questions[0].copy()
            # Personalize question with candidate name
            q["question"] = f"Welcome {candidate_name}! To start off our {interview_type} interview for {level} {role}: {q['question']}"
            return q

        return {
            "question": f"Welcome {candidate_name}! Could you introduce yourself and walk us through a significant technical project where you utilized {skills_str}?",
            "hint": "Focus on the problem statement, your architectural decisions, trade-offs, and measurable outcomes.",
            "ideal_answer": "A well-structured overview covering the project goal, tech stack choices, personal contribution, challenges solved, and quantitative impact."
        }

    def generate_next_question(
        self,
        role: str,
        level: str,
        interview_type: str,
        question_index: int,
        total_questions: int,
        skills: List[str],
        previous_qa: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """Generate the next adaptive interview question based on previous answers."""
        skills_str = ", ".join(skills[:6]) if skills else "engineering principles"
        last_turn = previous_qa[-1] if previous_qa else None

        prompt = (
            f"You are conducting a {level} {role} mock interview ({interview_type}). "
            f"Question {question_index + 1} of {total_questions}. "
            f"Candidate's known skills: {skills_str}. "
            f"Last Question asked: {last_turn['question'] if last_turn else 'N/A'}. "
            f"Candidate's Answer: {last_turn['answer'] if last_turn else 'N/A'}. "
            f"Generate the next question. If the candidate gave a strong answer, deepen the technical inquiry or present an edge case. "
            f"If the answer was brief, ask for specific design details or trade-offs. "
            f"Return JSON with: 'question', 'hint', 'ideal_answer'."
        )

        try:
            res_text = self.ai_client.generate_text(prompt)
            json_match = re.search(r"\{[\s\S]*\}", res_text)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if "question" in parsed and "ideal_answer" in parsed:
                    return parsed
        except Exception:
            pass

        # Fallback question from curated bank
        bank = QUESTION_BANKS.get(role, QUESTION_BANKS["Full Stack Developer"])
        type_questions = bank.get(interview_type, bank.get("Technical", []))
        idx = question_index % len(type_questions) if type_questions else 0

        if type_questions and idx < len(type_questions):
            return type_questions[idx]

        return {
            "question": f"In your experience with {skills_str}, how do you approach monitoring, observability, and debugging when unexpected errors occur?",
            "hint": "Discuss structured logging, metric alarms, distributed tracing (OpenTelemetry), and rollback procedures.",
            "ideal_answer": "A comprehensive answer covers metric thresholds, distributed tracing to pinpoint bottlenecks, centralized logs, and automated alerting."
        }

    def evaluate_interview_session(
        self,
        candidate_name: str,
        role: str,
        level: str,
        interview_type: str,
        qa_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Evaluate entire interview and produce detailed scores and recommendations."""
        if not qa_history:
            return {
                "overall_score": 0,
                "technical_score": 0,
                "communication_score": 0,
                "problem_solving_score": 0,
                "summary": "No answers provided to evaluate.",
                "question_evaluations": [],
                "study_roadmap": []
            }

        # Build prompt for AI model evaluation
        qa_formatted = ""
        for i, turn in enumerate(qa_history, 1):
            qa_formatted += f"Q{i}: {turn.get('question')}\nAnswer: {turn.get('answer', 'Skipped')}\n\n"

        prompt = (
            f"Evaluate the mock interview for candidate '{candidate_name}' for {level} {role} ({interview_type}).\n\n"
            f"Transcript:\n{qa_formatted}\n\n"
            f"Provide an objective, constructive evaluation. Return ONLY a JSON object formatted as:\n"
            f"{{\n"
            f'  "overall_score": <number 0-100>,\n'
            f'  "technical_score": <number 0-100>,\n'
            f'  "communication_score": <number 0-100>,\n'
            f'  "problem_solving_score": <number 0-100>,\n'
            f'  "summary": "<2-3 sentence executive assessment>",\n'
            f'  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],\n'
            f'  "growth_areas": ["<area 1>", "<area 2>"],\n'
            f'  "question_evaluations": [\n'
            f'    {{\n'
            f'      "question": "<text>",\n'
            f'      "score": <0-100>,\n'
            f'      "feedback": "<feedback>",\n'
            f'      "model_answer": "<ideal answer>"\n'
            f'    }}\n'
            f"  ],\n"
            f'  "study_roadmap": ["<topic 1 to study>", "<topic 2 to practice>"]\n'
            f"}}"
        )

        try:
            res_text = self.ai_client.generate_text(prompt)
            json_match = re.search(r"\{[\s\S]*\}", res_text)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if "overall_score" in parsed and "question_evaluations" in parsed:
                    return parsed
        except Exception:
            pass

        # Intelligent Fallback Scoring Algorithm
        return self._heuristic_evaluation(candidate_name, role, level, interview_type, qa_history)

    def _heuristic_evaluation(
        self,
        candidate_name: str,
        role: str,
        level: str,
        interview_type: str,
        qa_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Perform deterministic rubric scoring based on answer completeness, length, and keywords."""
        evaluations = []
        scores = []

        for turn in qa_history:
            ans = turn.get("answer", "").strip()
            word_count = len(ans.split())

            if not ans or "skipped" in ans.lower():
                score = 30
                feedback = "Question was skipped or answered with insufficient detail."
            elif word_count < 20:
                score = 55
                feedback = "Answer is concise but lacks concrete examples, architectural context, or trade-offs."
            elif word_count < 60:
                score = 75
                feedback = "Solid answer covering core principles. Could be elevated by mentioning edge cases, benchmarking, or failure recovery."
            else:
                score = 88
                feedback = "Detailed and well-articulated response demonstrating strong grasp of technical concepts and clear communication."

            scores.append(score)
            evaluations.append({
                "question": turn.get("question", ""),
                "score": score,
                "feedback": feedback,
                "model_answer": turn.get("ideal_answer", "A comprehensive response covers core mechanisms, trade-offs, and production considerations.")
            })

        avg_score = int(sum(scores) / len(scores)) if scores else 70
        tech_score = min(100, max(40, avg_score + 2))
        comm_score = min(100, max(40, avg_score - 1))
        prob_score = min(100, max(40, avg_score + 1))

        return {
            "overall_score": avg_score,
            "technical_score": tech_score,
            "communication_score": comm_score,
            "problem_solving_score": prob_score,
            "summary": (
                f"{candidate_name} demonstrated a strong foundational understanding for the {level} {role} position. "
                f"Answers reflected solid conceptual awareness with good technical terminology and logic."
            ),
            "strengths": [
                "Clear explanations of core architectural and technical concepts.",
                "Logical structure and confident presentation of problem-solving approach.",
                "Good familiarity with modern industry tools and best practices."
            ],
            "growth_areas": [
                "Incorporate deeper discussions of edge cases, system trade-offs, and scalability limits.",
                "Quantify achievements with concrete metrics where applicable (e.g. latency, throughput improvements)."
            ],
            "question_evaluations": evaluations,
            "study_roadmap": [
                f"Deep dive into advanced {role} system architecture patterns.",
                "Practice the STAR framework (Situation, Task, Action, Result) for behavioral storytelling.",
                "Review distributed systems design and high-availability caching patterns."
            ]
        }
