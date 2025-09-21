import re
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

class QueryType(Enum):
    """Types of queries the system can handle."""
    SIMPLE = "simple"           # Single, direct question
    COMPLEX = "complex"         # Multi-part question requiring decomposition
    COMPARATIVE = "comparative" # Comparing multiple entities/concepts
    ANALYTICAL = "analytical"   # Analysis requiring multiple perspectives
    SUMMARIZATION = "summarization"  # Request for summary of information

@dataclass
class SubQuery:
    """Represents a decomposed sub-query."""
    text: str
    query_type: str
    priority: int  # 1 = highest priority
    context: str = ""
    expected_answer_type: str = "factual"

@dataclass
class ReasoningStep:
    """Represents a step in the reasoning process."""
    step_number: int
    description: str
    sub_queries: List[SubQuery] = None
    results: List[Dict] = None
    synthesis: str = ""

class QueryAnalyzer:
    """Analyzes queries to determine complexity and decomposition strategy."""
    
    def __init__(self):
        # Patterns for different query types
        self.complex_patterns = [
            r'\b(and|also|additionally|furthermore|moreover)\b',
            r'\b(compare|contrast|difference|similarity)\b',
            r'\b(analyze|evaluate|assess|examine)\b',
            r'\b(what are the|list all|enumerate|describe all)\b',
            r'\b(how does|why does|what causes|what leads to)\b',
            r'\b(pros and cons|advantages and disadvantages)\b'
        ]
        
        self.comparative_patterns = [
            r'\b(compare|vs|versus|difference between|similarity between)\b',
            r'\b(better than|worse than|superior to|inferior to)\b'
        ]
        
        self.analytical_patterns = [
            r'\b(analyze|evaluate|assess|examine|investigate)\b',
            r'\b(why|how|what causes|what leads to|what results in)\b'
        ]
    
    def analyze_query(self, query: str) -> QueryType:
        """Analyze query to determine its type."""
        query_lower = query.lower()
        
        # Check for comparative queries
        if any(re.search(pattern, query_lower) for pattern in self.comparative_patterns):
            return QueryType.COMPARATIVE
        
        # Check for analytical queries
        if any(re.search(pattern, query_lower) for pattern in self.analytical_patterns):
            return QueryType.ANALYTICAL
        
        # Check for complex queries
        if any(re.search(pattern, query_lower) for pattern in self.complex_patterns):
            return QueryType.COMPLEX
        
        # Check for summarization requests
        if any(word in query_lower for word in ['summarize', 'summary', 'overview', 'brief']):
            return QueryType.SUMMARIZATION
        
        return QueryType.SIMPLE
    
    def decompose_query(self, query: str, query_type: QueryType) -> List[SubQuery]:
        """Decompose complex queries into sub-queries."""
        if query_type == QueryType.SIMPLE:
            return [SubQuery(text=query, query_type="simple", priority=1)]
        
        elif query_type == QueryType.COMPARATIVE:
            return self._decompose_comparative(query)
        
        elif query_type == QueryType.ANALYTICAL:
            return self._decompose_analytical(query)
        
        elif query_type == QueryType.COMPLEX:
            return self._decompose_complex(query)
        
        elif query_type == QueryType.SUMMARIZATION:
            return self._decompose_summarization(query)
        
        return [SubQuery(text=query, query_type="simple", priority=1)]
    
    def _decompose_comparative(self, query: str) -> List[SubQuery]:
        """Decompose comparative queries."""
        sub_queries = []
        
        # Extract entities being compared
        entities = self._extract_entities(query)
        
        if len(entities) >= 2:
            # Create sub-queries for each entity
            for i, entity in enumerate(entities):
                sub_queries.append(SubQuery(
                    text=f"{entity} technologies and frameworks",
                    query_type="definition",
                    priority=1,
                    context=f"Part of comparison: {query}"
                ))
            
            # Add comparison sub-query
            sub_queries.append(SubQuery(
                text=f"differences between {entities[0]} and {entities[1]}",
                query_type="comparison",
                priority=2,
                context=f"Main comparison query: {query}"
            ))
        else:
            # Fallback for single entity
            topic = self._extract_topic(query)
            sub_queries.append(SubQuery(
                text=f"{topic} technologies",
                query_type="definition",
                priority=1,
                context=f"Analysis of: {query}"
            ))
        
        return sub_queries
    
    def _decompose_analytical(self, query: str) -> List[SubQuery]:
        """Decompose analytical queries."""
        sub_queries = []
        
        # Extract main topic
        topic = self._extract_topic(query)
        
        # Create analytical sub-queries based on topic
        if "projects" in topic.lower() and "skills" in topic.lower():
            sub_queries.extend([
                SubQuery(
                    text="software projects and applications",
                    query_type="projects",
                    priority=1,
                    context=f"Project analysis for: {query}"
                ),
                SubQuery(
                    text="programming languages and technical skills",
                    query_type="skills",
                    priority=2,
                    context=f"Skills analysis for: {query}"
                ),
                SubQuery(
                    text="technologies and frameworks used",
                    query_type="technologies",
                    priority=3,
                    context=f"Technology analysis for: {query}"
                )
            ])
        else:
            # Generic analytical sub-queries
            sub_queries.extend([
                SubQuery(
                    text=f"{topic} overview and details",
                    query_type="definition",
                    priority=1,
                    context=f"Background for: {query}"
                ),
                SubQuery(
                    text=f"{topic} key points and features",
                    query_type="aspects",
                    priority=2,
                    context=f"Key aspects for: {query}"
                )
            ])
        
        return sub_queries
    
    def _decompose_complex(self, query: str) -> List[SubQuery]:
        """Decompose complex multi-part queries."""
        sub_queries = []
        
        # Split by common conjunctions
        parts = re.split(r'\b(and|also|additionally|furthermore|moreover)\b', query, flags=re.IGNORECASE)
        
        for i, part in enumerate(parts):
            part = part.strip()
            if part and len(part) > 10:  # Filter out short fragments
                sub_queries.append(SubQuery(
                    text=part,
                    query_type="sub_query",
                    priority=i+1,
                    context=f"Part {i+1} of: {query}"
                ))
        
        # If no clear splits, create logical sub-queries
        if len(sub_queries) <= 1:
            topic = self._extract_topic(query)
            sub_queries = [
                SubQuery(
                    text=f"What is {topic}?",
                    query_type="definition",
                    priority=1,
                    context=f"Definition for: {query}"
                ),
                SubQuery(
                    text=f"What are the key points about {topic}?",
                    query_type="key_points",
                    priority=2,
                    context=f"Key information for: {query}"
                )
            ]
        
        return sub_queries
    
    def _decompose_summarization(self, query: str) -> List[SubQuery]:
        """Decompose summarization requests."""
        topic = self._extract_topic(query)
        
        if "resume" in topic.lower():
            return [
                SubQuery(
                    text="work experience and internships",
                    query_type="experience",
                    priority=1,
                    context=f"Experience summary for: {query}"
                ),
                SubQuery(
                    text="projects and technical skills",
                    query_type="projects_skills",
                    priority=2,
                    context=f"Projects and skills for: {query}"
                ),
                SubQuery(
                    text="education and certifications",
                    query_type="education",
                    priority=3,
                    context=f"Education summary for: {query}"
                )
            ]
        else:
            return [
                SubQuery(
                    text=f"{topic} key information",
                    query_type="main_points",
                    priority=1,
                    context=f"Key content for summary: {query}"
                ),
                SubQuery(
                    text=f"{topic} important details",
                    query_type="details",
                    priority=2,
                    context=f"Supporting details for summary: {query}"
                )
            ]
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from query for comparison."""
        # Simple entity extraction - can be enhanced with NER
        entities = []
        
        # Look for "A vs B" or "A and B" patterns
        vs_match = re.search(r'(.+?)\s+(?:vs|versus|and)\s+(.+)', query, re.IGNORECASE)
        if vs_match:
            entities = [vs_match.group(1).strip(), vs_match.group(2).strip()]
        
        return entities
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query."""
        # Remove question words and common verbs
        topic = re.sub(r'^(what|how|why|when|where|who|which|tell me about|explain|describe|analyze|evaluate)\s+', '', query, flags=re.IGNORECASE)
        topic = re.sub(r'\?$', '', topic).strip()
        
        # Take first few words as topic
        words = topic.split()
        if len(words) > 5:
            topic = ' '.join(words[:5])
        
        return topic

class ReasoningEngine:
    """Main reasoning engine that orchestrates multi-step query processing."""
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.analyzer = QueryAnalyzer()
        
        # Import simple AI synthesizer (more reliable)
        try:
            from simple_ai_synthesizer import SimpleAISynthesizer
            self.ai_synthesizer = SimpleAISynthesizer()
            print("✅ Simple AI Synthesizer loaded successfully!")
        except Exception as e:
            print(f"⚠️ Simple AI Synthesizer not available: {e}")
            self.ai_synthesizer = None
    
    def process_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Process a query using multi-step reasoning."""
        print(f"🧠 Processing query: '{query}'")
        
        # Step 1: Analyze query
        query_type = self.analyzer.analyze_query(query)
        print(f"📊 Query type: {query_type.value}")
        
        # Step 2: Decompose if complex
        sub_queries = self.analyzer.decompose_query(query, query_type)
        print(f"🔍 Generated {len(sub_queries)} sub-queries")
        
        # Step 3: Execute sub-queries
        reasoning_steps = []
        all_results = []
        
        for i, sub_query in enumerate(sub_queries):
            print(f"  🔸 Executing sub-query {i+1}: {sub_query.text}")
            
            # Search vector database
            results = self.vector_db.search(sub_query.text, top_k=top_k)
            
            # Create reasoning step
            step = ReasoningStep(
                step_number=i+1,
                description=f"Sub-query: {sub_query.text}",
                sub_queries=[sub_query],
                results=results
            )
            reasoning_steps.append(step)
            all_results.extend(results)
        
        # Step 4: Synthesize results
        synthesis = self._synthesize_results(query, query_type, reasoning_steps)
        
        # Step 5: Create final response
        response = {
            "original_query": query,
            "query_type": query_type.value,
            "reasoning_steps": [
                {
                    "step": step.step_number,
                    "description": step.description,
                    "sub_queries": [{"text": sq.text, "type": sq.query_type} for sq in step.sub_queries],
                    "results_count": len(step.results) if step.results else 0
                }
                for step in reasoning_steps
            ],
            "total_results": len(all_results),
            "synthesis": synthesis,
            "raw_results": all_results[:10]  # Limit for response size
        }
        
        return response
    
    def _synthesize_results(self, original_query: str, query_type: QueryType, steps: List[ReasoningStep]) -> str:
        """Synthesize results from multiple reasoning steps."""
        if query_type == QueryType.SIMPLE:
            return self._synthesize_simple(steps)
        elif query_type == QueryType.COMPARATIVE:
            return self._synthesize_comparative(steps)
        elif query_type == QueryType.ANALYTICAL:
            return self._synthesize_analytical(steps)
        elif query_type == QueryType.SUMMARIZATION:
            return self._synthesize_summarization(steps)
        else:
            return self._synthesize_complex(steps)
    
    def _synthesize_simple(self, steps: List[ReasoningStep]) -> str:
        """Synthesize simple query results using AI."""
        if not steps or not steps[0].results:
            return "No relevant information found."
        
        # Use generic AI synthesizer if available
        if self.ai_synthesizer:
            try:
                # Get the original query from the first step
                original_query = steps[0].description.replace("Sub-query: ", "")
                response = self.ai_synthesizer.synthesize_query_response(original_query, steps[0].results)
                if response and "No AI synthesis available" not in response:
                    return response
            except Exception as e:
                print(f"⚠️ AI synthesis failed: {e}")
        
        # Fallback to simple text processing
        best_result = steps[0].results[0]
        text, score, metadata = best_result
        return f"**Answer:**\n\n{text[:300]}{'...' if len(text) > 300 else ''}\n"
    
    def _synthesize_comparative(self, steps: List[ReasoningStep]) -> str:
        """Synthesize comparative query results using AI."""
        if self.ai_synthesizer:
            # Combine all results from all steps
            all_results = []
            for step in steps:
                if step.results:
                    all_results.extend(step.results)
            
            if all_results:
                # Get the original query from the first step
                original_query = steps[0].description.replace("Sub-query: ", "")
                return self.ai_synthesizer.synthesize_comparative_analysis(original_query, all_results)
        
        # Fallback to simple processing
        return "**Comparison Analysis:**\n\nNo AI synthesis available. Please check model installation."
    
    def _synthesize_analytical(self, steps: List[ReasoningStep]) -> str:
        """Synthesize analytical query results using AI."""
        if self.ai_synthesizer:
            # Combine all results from all steps
            all_results = []
            for step in steps:
                if step.results:
                    all_results.extend(step.results)
            
            if all_results:
                # Get the original query from the first step
                original_query = steps[0].description.replace("Sub-query: ", "")
                return self.ai_synthesizer.synthesize_analytical_response(original_query, all_results)
        
        # Fallback to simple processing
        return "**Analytical Analysis:**\n\nNo AI synthesis available. Please check model installation."
    
    def _synthesize_summarization(self, steps: List[ReasoningStep]) -> str:
        """Synthesize summarization results using AI."""
        if self.ai_synthesizer:
            # Combine all results from all steps
            all_results = []
            for step in steps:
                if step.results:
                    all_results.extend(step.results)
            
            if all_results:
                # Get the original query from the first step
                original_query = steps[0].description.replace("Sub-query: ", "")
                return self.ai_synthesizer.synthesize_summary(original_query, all_results)
        
        # Fallback to simple processing
        return "**Summary:**\n\nNo AI synthesis available. Please check model installation."
    
    def _combine_results_text(self, results: List[Tuple[str, float, Dict]]) -> str:
        """Combine text from search results."""
        texts = []
        for text, score, metadata in results:
            if score > 0.3:  # Only include relevant results
                texts.append(text)
        return ' '.join(texts)
    
    def _synthesize_complex(self, steps: List[ReasoningStep]) -> str:
        """Synthesize complex query results."""
        synthesis = "Comprehensive Analysis:\n\n"
        
        for step in steps:
            if step.results:
                synthesis += f"**{step.description}**\n"
                for text, score, metadata in step.results[:2]:
                    synthesis += f"- {text[:150]}{'...' if len(text) > 150 else ''}\n"
                synthesis += "\n"
        
        return synthesis

if __name__ == "__main__":
    # Test the reasoning engine
    from vector_db import VectorDatabase
    
    print("🧪 Testing Reasoning Engine...")
    
    # Load vector database
    vector_db = VectorDatabase()
    if not vector_db.load():
        print("❌ No vector database found. Run vector_db.py first.")
        exit(1)
    
    # Create reasoning engine
    engine = ReasoningEngine(vector_db)
    
    # Test queries
    test_queries = [
        "What is the work experience?",
        "Compare frontend and backend technologies",
        "Analyze the projects and skills",
        "Summarize the resume"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        result = engine.process_query(query)
        print(f"\n📝 Final Answer:")
        print(result["synthesis"])
        print(f"\n🔍 Reasoning Steps: {len(result['reasoning_steps'])}")
        for step in result["reasoning_steps"]:
            print(f"  {step['step']}. {step['description']}")
