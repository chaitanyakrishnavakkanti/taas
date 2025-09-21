# Deep Researcher Agent

🔍 An AI-powered research assistant that can analyze and answer questions about your documents using cutting-edge artificial intelligence.

## ✨ Features

- **🧠 Multi-Step Reasoning**: Breaks down complex questions into manageable parts
- **📚 Local AI Processing**: No external API calls - everything runs on your computer
- **🔍 Intelligent Search**: Semantic search that understands meaning, not just keywords
- **💬 Natural Conversations**: Ask questions in plain English
- **📄 Multiple Document Types**: Supports PDF and TXT files
- **🎯 Real-time Analysis**: Fast, secure, and private document analysis
- **🔧 Web Interface**: Beautiful Streamlit-based user interface
- **📊 Reasoning Transparency**: See how the AI thinks with detailed reasoning steps

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/sathish0416/Deep-Researcher-Agent.git
   cd Deep-Researcher-Agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run_app.py
   ```

5. **Open your browser** and go to `http://localhost:8501`

## 📋 Requirements

- Python 3.8+
- Streamlit
- Transformers
- FAISS
- PyPDF2
- Sentence Transformers
- Torch

## 🎯 Usage

1. **Upload Documents**: Use the sidebar to upload your PDF or TXT files
2. **Process Documents**: Click 'Process Documents' to analyze and index them
3. **Ask Questions**: Type questions about your documents in natural language
4. **Get Answers**: Receive detailed, AI-powered answers with reasoning steps
5. **Explore**: Use the reasoning steps to understand how the AI thinks

## 💡 Example Questions

- "What is this document about?"
- "Summarize the main points"
- "What are the key findings?"
- "Compare the different sections"
- "What are the recommendations?"
- "Explain the methodology used"
- "What are the main conclusions?"

## 🔧 Technical Architecture

### Core Components

- **Vector Database**: FAISS for efficient similarity search and retrieval
- **AI Models**: BART, DistilBERT for summarization and question-answering
- **Embeddings**: Sentence Transformers for semantic understanding
- **Interface**: Streamlit web application with beautiful UI
- **Document Processing**: PyPDF2 for PDF parsing and text extraction

### AI Models Used

- **Embedding Model**: `multi-qa-MPNet-base-dot-v1` for semantic search
- **Summarization**: `facebook/bart-large-cnn` for text summarization
- **Question Answering**: `distilbert-base-cased-distilled-squad` for Q&A
- **Reasoning**: Multi-step query decomposition and synthesis

### File Structure

```
Deep-Researcher-Agent/
├── app.py                 # Main Streamlit application
├── run_app.py            # Application launcher
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── LICENSE              # MIT License
├── utils/               # Core functionality modules
│   ├── vector_db.py     # FAISS vector database
│   ├── reasoning_engine.py  # Multi-step reasoning logic
│   ├── simple_ai_synthesizer.py  # AI response generation
│   ├── ingest.py        # Document processing
│   └── embedder.py      # Embedding generation
├── data/                # Input documents directory
└── embeddings/          # Vector database storage
```

## 🛠️ Development

### Setting up Development Environment

1. Clone the repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `python test_improved_system.py`

### Key Features Implementation

- **Document Ingestion**: Automatic PDF/TXT parsing and chunking
- **Vector Search**: Semantic similarity search using FAISS
- **AI Synthesis**: Dynamic response generation using transformer models
- **Multi-step Reasoning**: Query decomposition and result synthesis
- **Web Interface**: Responsive Streamlit UI with real-time updates

## 📊 Performance

- **Processing Speed**: ~2-5 seconds per document (depending on size)
- **Search Speed**: Sub-second response times for queries
- **Memory Usage**: Efficient chunking and vector storage
- **Scalability**: Handles multiple documents and concurrent queries

## 🔒 Privacy & Security

- **Local Processing**: All AI processing happens on your machine
- **No External APIs**: No data sent to external services
- **Secure Storage**: Vector embeddings stored locally
- **Data Control**: You maintain full control over your documents

## 🐛 Troubleshooting

### Common Issues

1. **"No AI synthesis available"**: Install missing dependencies
   ```bash
   pip install torch transformers
   ```

2. **Memory issues**: Reduce chunk size in settings
3. **Slow processing**: Ensure you have sufficient RAM (8GB+ recommended)

### Debug Mode

Use the "Debug Database" button in the sidebar to inspect:
- Vector database statistics
- Sample content and metadata
- System configuration

## 📈 Future Enhancements

- [ ] Support for more document types (DOCX, HTML, etc.)
- [ ] Advanced query types (comparison, analysis)
- [ ] Export functionality (PDF reports, summaries)
- [ ] Batch processing for large document sets
- [ ] API endpoints for integration
- [ ] Docker containerization
- [ ] Cloud deployment options

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 📞 Support

- **Issues**: Open an issue on GitHub for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check this README and code comments

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the web interface
- [Hugging Face](https://huggingface.co/) for transformer models
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [Sentence Transformers](https://www.sbert.net/) for embeddings

---

**Made with ❤️ for the AI research community**
