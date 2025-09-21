import os
from typing import List, Dict, Tuple
from transformers import pipeline
import torch

class SimpleAISynthesizer:
    """
    Simple, reliable AI synthesizer that focuses on giving good, coherent responses.
    Uses basic models that are more stable and predictable.
    """
    
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        
        print(f"🤖 Loading Simple AI Synthesizer...")
        print(f"📱 Device: {'CUDA' if self.device == 0 else 'CPU'}")
        
        try:
            print("🔄 Loading BART summarization model...")
            # Load basic summarization pipeline (more reliable)
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",  # More reliable than Pegasus
                device=self.device,
                max_length=512,
                min_length=50
            )
            print("✅ BART model loaded!")
            
            print("🔄 Loading DistilBERT QA model...")
            # Load basic question-answering pipeline
            self.qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",  # More reliable
                device=self.device
            )
            print("✅ DistilBERT model loaded!")
            
            print("✅ Simple AI models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading AI models: {e}")
            print("🔄 Using text-based processing...")
            self.summarizer = None
            self.qa_pipeline = None
    
    def synthesize_query_response(self, query: str, results: List[Tuple[str, float, Dict]]) -> str:
        """
        Simple, reliable synthesis for queries.
        """
        if not results:
            return "I don't have enough information to answer your question. Please upload some documents first."
        
        # Get the best results
        best_results = [r for r in results if r[1] > 0.3]  # Only high-confidence results
        
        if not best_results:
            return "I couldn't find relevant information in the uploaded documents to answer your question."
        
        # Combine the best results
        combined_text = self._combine_relevant_text(best_results)
        
        # Try question-answering first
        if self.qa_pipeline:
            try:
                qa_result = self.qa_pipeline(
                    question=query,
                    context=combined_text[:1000]  # Limit context
                )
                
                if qa_result['score'] > 0.1 and len(qa_result['answer']) > 10:
                    answer = qa_result['answer'].strip()
                    
                    # Clean up the answer
                    if self._is_good_answer(answer):
                        response = f"**Answer:**\n\n{answer}\n\n"
                        response += "**Based on the documents:**\n"
                        response += f"{combined_text[:200]}{'...' if len(combined_text) > 200 else ''}"
                        return response
                
            except Exception as e:
                print(f"⚠️ QA failed: {e}")
        
        # Fallback to summarization
        return self._simple_summarize(query, combined_text)
    
    def _simple_summarize(self, query: str, text: str) -> str:
        """Simple, reliable summarization."""
        if not self.summarizer:
            return self._fallback_summarize(text)
        
        try:
            # Limit text length
            if len(text.split()) > 500:
                text = ' '.join(text.split()[:500])
            
            # Generate summary
            summary = self.summarizer(
                text,
                max_length=100,
                min_length=30,
                do_sample=False,
                truncation=True
            )
            
            summary_text = summary[0]['summary_text'].strip()
            
            # Check if summary makes sense
            if self._is_good_answer(summary_text):
                response = f"**Answer:**\n\n{summary_text}\n\n"
                response += "**Source Information:**\n"
                response += f"{text[:200]}{'...' if len(text) > 200 else ''}"
                return response
            else:
                return self._fallback_summarize(text)
                
        except Exception as e:
            print(f"⚠️ Summarization failed: {e}")
            return self._fallback_summarize(text)
    
    def _is_good_answer(self, text: str) -> bool:
        """Check if the answer is good quality."""
        if len(text) < 10:
            return False
        
        # Check for common bad patterns
        bad_patterns = [
            "rate", "epoch", "training", "model", "loss", "accuracy",
            "0.01", "5000", "sigmoid", "neural", "network"
        ]
        
        text_lower = text.lower()
        for pattern in bad_patterns:
            if pattern in text_lower:
                return False
        
        return True
    
    def _fallback_summarize(self, text: str) -> str:
        """Fallback summarization when AI models fail."""
        # Simple extractive summarization
        sentences = text.split('. ')
        if len(sentences) <= 3:
            return f"**Answer:**\n\n{text[:300]}{'...' if len(text) > 300 else ''}"
        
        # Take first few sentences as summary
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences)
        
        return f"**Answer:**\n\n{summary}..."
    
    def _combine_relevant_text(self, results: List[Tuple[str, float, Dict]]) -> str:
        """Combine relevant text from search results."""
        relevant_texts = []
        
        for text, score, metadata in results:
            if score >= 0.3:  # Only high-confidence results
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

if __name__ == "__main__":
    # Test the simple AI synthesizer
    print("🧪 Testing Simple AI Synthesizer...")
    
    # Create test data
    test_results = [
        ("This document discusses artificial intelligence and machine learning applications in healthcare.", 0.9, {}),
        ("AI is being used to improve patient diagnosis and treatment planning in hospitals.", 0.8, {}),
        ("Machine learning algorithms can analyze medical images more accurately than human doctors.", 0.7, {})
    ]
    
    # Test simple AI synthesizer
    synthesizer = SimpleAISynthesizer()
    
    test_query = "What is this document about?"
    response = synthesizer.synthesize_query_response(test_query, test_results)
    print(f"\n🔍 Query: {test_query}")
    print(f"📝 Response: {response}")
