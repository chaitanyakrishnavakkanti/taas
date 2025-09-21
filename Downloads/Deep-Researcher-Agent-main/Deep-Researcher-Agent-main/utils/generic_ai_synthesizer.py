import os
from typing import List, Dict, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class GenericAISynthesizer:
    """
    Generic AI-powered synthesis that works with ANY document type.
    No hardcoded information - everything is extracted dynamically by AI models.
    """
    
    def __init__(self, model_name: str = "google/pegasus-xsum"):
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1
        
        print(f"🤖 Loading Enhanced AI Synthesizer: {model_name}")
        print(f"📱 Device: {'CUDA' if self.device == 0 else 'CPU'}")
        
        try:
            # Load enhanced summarization pipeline (Pegasus is much better than BART)
            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                device=self.device,
                max_length=512,
                min_length=50
            )
            
            # Load enhanced question-answering pipeline (RoBERTa is much better than DistilBERT)
            self.qa_pipeline = pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                device=self.device
            )
            
            # Load text generation for complex reasoning
            self.text_generator = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-large",
                device=self.device,
                max_length=200,
                do_sample=True,
                temperature=0.7
            )
            
            print("✅ Enhanced AI models loaded successfully!")
            print("🚀 Using Pegasus (summarization) + RoBERTa (QA) + DialoGPT (reasoning)")
            
        except Exception as e:
            print(f"❌ Error loading enhanced AI models: {e}")
            print("🔄 Falling back to basic models...")
            
            try:
                # Fallback to basic models
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=self.device
                )
                
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model="distilbert-base-cased-distilled-squad",
                    device=self.device
                )
                
                self.text_generator = None
                print("✅ Basic AI models loaded as fallback")
                
            except Exception as e2:
                print(f"❌ Fallback models also failed: {e2}")
                print("🔄 Using simple text processing...")
                self.summarizer = None
                self.qa_pipeline = None
                self.text_generator = None
    
    def synthesize_query_response(self, query: str, results: List[Tuple[str, float, Dict]]) -> str:
        """
        Enhanced AI-powered synthesis for ANY query and ANY document type.
        """
        if not results:
            return "I don't have enough information to answer your question. Please upload some documents first."
        
        # Combine relevant text
        combined_text = self._combine_relevant_text(results, min_score=0.3)
        
        if not combined_text:
            return "I couldn't find relevant information in the uploaded documents to answer your question."
        
        # Use enhanced AI to answer the specific query
        if self.qa_pipeline:
            try:
                # Create a better context for QA
                context = f"Document content: {combined_text[:1000]}"  # Limit context size
                
                # Direct question-answering approach with RoBERTa
                qa_result = self.qa_pipeline(
                    question=query,
                    context=context
                )
                
                if qa_result['score'] > 0.1:  # Lower confidence threshold
                    synthesis = f"**Answer:**\n\n"
                    
                    # Clean up the answer
                    answer = qa_result['answer'].strip()
                    if len(answer) < 10:  # If answer is too short, use summarization instead
                        return self._ai_summarize_for_query(query, combined_text)
                    
                    synthesis += f"{answer}\n\n"
                    
                    # Add relevant context from the documents
                    synthesis += "**Based on the documents:**\n"
                    synthesis += f"{combined_text[:300]}{'...' if len(combined_text) > 300 else ''}\n"
                    
                    return synthesis
                
            except Exception as e:
                print(f"⚠️ QA extraction failed: {e}")
        
        # Fallback to enhanced AI summarization
        return self._ai_summarize_for_query(query, combined_text)
    
    def synthesize_comparative_analysis(self, query: str, results: List[Tuple[str, float, Dict]]) -> str:
        """
        Generic AI-powered comparative analysis for ANY comparison query.
        """
        if not results:
            return "No information found for comparison."
        
        combined_text = self._combine_relevant_text(results, min_score=0.3)
        
        if not combined_text:
            return "No relevant information found for comparison."
        
        # Extract entities being compared from the query
        entities = self._extract_comparison_entities(query)
        
        if self.qa_pipeline and entities:
            try:
                synthesis = f"**Comparison: {query}**\n\n"
                
                # Analyze each entity
                for entity in entities:
                    entity_qa = self.qa_pipeline(
                        question=f"What information is available about {entity}?",
                        context=combined_text
                    )
                    
                    if entity_qa['score'] > 0.3:
                        synthesis += f"**{entity.title()}:**\n"
                        synthesis += f"{entity_qa['answer']}\n\n"
                
                # Overall comparison
                comparison_qa = self.qa_pipeline(
                    question=f"What are the differences and similarities between {', '.join(entities)}?",
                    context=combined_text
                )
                
                if comparison_qa['score'] > 0.3:
                    synthesis += f"**Comparison Analysis:**\n{comparison_qa['answer']}\n"
                
                return synthesis
                
            except Exception as e:
                print(f"⚠️ Comparative analysis failed: {e}")
        
        # Fallback to generic summarization
        return self._ai_summarize_for_query(f"comparative analysis of {query}", combined_text)
    
    def synthesize_analytical_response(self, query: str, results: List[Tuple[str, float, Dict]]) -> str:
        """
        Generic AI-powered analytical response for ANY analytical query.
        """
        if not results:
            return "No information found for analysis."
        
        combined_text = self._combine_relevant_text(results, min_score=0.3)
        
        if not combined_text:
            return "No relevant information found for analysis."
        
        if self.qa_pipeline:
            try:
                synthesis = f"**Analysis: {query}**\n\n"
                
                # Extract key aspects
                aspects_qa = self.qa_pipeline(
                    question=f"What are the key aspects and details related to {query}?",
                    context=combined_text
                )
                
                if aspects_qa['score'] > 0.3:
                    synthesis += f"**Key Aspects:**\n{aspects_qa['answer']}\n\n"
                
                # Extract important details
                details_qa = self.qa_pipeline(
                    question=f"What important details and information are provided about {query}?",
                    context=combined_text
                )
                
                if details_qa['score'] > 0.3:
                    synthesis += f"**Important Details:**\n{details_qa['answer']}\n\n"
                
                # Extract implications or significance
                significance_qa = self.qa_pipeline(
                    question=f"What is the significance or importance of {query}?",
                    context=combined_text
                )
                
                if significance_qa['score'] > 0.3:
                    synthesis += f"**Significance:**\n{significance_qa['answer']}\n"
                
                return synthesis
                
            except Exception as e:
                print(f"⚠️ Analytical analysis failed: {e}")
        
        # Fallback to generic summarization
        return self._ai_summarize_for_query(f"analysis of {query}", combined_text)
    
    def synthesize_summary(self, query: str, results: List[Tuple[str, float, Dict]]) -> str:
        """
        Generic AI-powered summary for ANY document type.
        """
        if not results:
            return "No information found for summarization."
        
        combined_text = self._combine_relevant_text(results, min_score=0.2)
        
        if not combined_text:
            return "No relevant information found for summarization."
        
        # Use AI summarization
        return self._ai_summarize_for_query(f"summary of {query}", combined_text)
    
    def _ai_summarize_for_query(self, query: str, text: str) -> str:
        """Use enhanced AI model (Pegasus) to summarize text for a specific query."""
        if not self.summarizer:
            return self._fallback_summarize(text)
        
        try:
            # Truncate text if too long
            if len(text.split()) > 800:  # Reduced from 1000
                text = ' '.join(text.split()[:800])
            
            # Create a better prompt for summarization
            prompt_text = f"Question: {query}\n\nDocument content: {text}\n\nAnswer:"
            
            # Generate enhanced AI summary using Pegasus
            summary = self.summarizer(
                prompt_text,
                max_length=150,  # Reduced from 200
                min_length=30,   # Reduced from 50
                do_sample=False,
                truncation=True
            )
            
            # Clean up the summary
            summary_text = summary[0]['summary_text'].strip()
            
            # If summary is too short or doesn't make sense, use fallback
            if len(summary_text) < 20 or "rate" in summary_text.lower() or "epoch" in summary_text.lower():
                return self._fallback_summarize(text)
            
            response = f"**Answer:**\n\n{summary_text}\n\n"
            response += "**Source Information:**\n"
            response += f"{text[:200]}{'...' if len(text) > 200 else ''}"
            
            return response
            
        except Exception as e:
            print(f"⚠️ Enhanced AI summarization failed: {e}")
            return self._fallback_summarize(text)
    
    def _fallback_summarize(self, text: str) -> str:
        """Fallback summarization when AI models fail."""
        # Simple extractive summarization
        sentences = text.split('. ')
        if len(sentences) <= 3:
            return f"**Summary:**\n\n{text[:300]}{'...' if len(text) > 300 else ''}"
        
        # Take first few sentences as summary
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences)
        
        return f"**Summary:**\n\n{summary}..."
    
    def _combine_relevant_text(self, results: List[Tuple[str, float, Dict]], min_score: float = 0.3) -> str:
        """Combine relevant text from search results."""
        relevant_texts = []
        
        for text, score, metadata in results:
            if score >= min_score:
                relevant_texts.append(text)
        
        if not relevant_texts:
            return ""
        
        # Combine and deduplicate
        combined = ' '.join(relevant_texts)
        
        # Remove excessive repetition
        words = combined.split()
        seen = set()
        unique_words = []
        
        for word in words:
            if word.lower() not in seen:
                unique_words.append(word)
                seen.add(word.lower())
        
        return ' '.join(unique_words)
    
    def _extract_comparison_entities(self, query: str) -> List[str]:
        """Extract entities being compared from query."""
        import re
        
        # Look for comparison patterns
        patterns = [
            r'compare\s+(.+?)\s+and\s+(.+)',
            r'(.+?)\s+vs\s+(.+)',
            r'(.+?)\s+versus\s+(.+)',
            r'difference\s+between\s+(.+?)\s+and\s+(.+)',
            r'similarity\s+between\s+(.+?)\s+and\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return [match.group(1).strip(), match.group(2).strip()]
        
        # Fallback: extract nouns from query
        words = query.split()
        entities = []
        for word in words:
            if len(word) > 3 and word.isalpha():
                entities.append(word)
                if len(entities) >= 2:
                    break
        
        return entities

if __name__ == "__main__":
    # Test the generic AI synthesizer
    print("🧪 Testing Generic AI Synthesizer...")
    
    # Create test data (simulating any document type)
    test_results = [
        ("The company reported a 15% increase in revenue this quarter. The marketing team implemented new strategies that led to higher customer engagement.", 0.8, {}),
        ("Our research shows that machine learning algorithms can improve efficiency by 30%. The implementation requires Python and TensorFlow.", 0.7, {}),
        ("The project timeline is 6 months with a budget of $50,000. Key deliverables include user interface design and backend development.", 0.6, {})
    ]
    
    # Test generic AI synthesizer
    synthesizer = GenericAISynthesizer()
    
    test_queries = [
        "What is the revenue increase?",
        "Compare machine learning and traditional methods",
        "Analyze the project requirements",
        "Summarize the key information"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        response = synthesizer.synthesize_query_response(query, test_results)
        print(response)
        print("-" * 50)
