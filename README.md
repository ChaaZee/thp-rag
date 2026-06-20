# THP-RAG: Vertical Jumping Knowledge Retrieval System

A Retrieval-Augmented Generation (RAG) system that leverages educational content from The Hunting Project (THP) YouTube channels to answer questions about athletic training, vertical jump improvement, and fitness techniques.

## Overview

This project combines web-scraped YouTube transcripts from 3 THP channels into a semantic search and generation pipeline. Using the Hermes:8b language model with RAG, the system can retrieve relevant training insights and provide contextual answers about improving vertical jump performance.

## What is THP?

The Hunting Project (THP) is an athletic training program focused on helping athletes increase their vertical jump height. The program covers training methodology, nutrition, recovery, biomechanics, and sport-specific techniques.

## Project Architecture

```
YouTube Transcripts (3 THP Channels)
           ↓
    Web Scraping
           ↓
    Text Chunking
           ↓
    Cleaned Dataset (rag_dataset.jsonl)
           ↓
    Vector Embeddings
           ↓
    RAG System (Hermes:8b)
           ↓
    Q&A Responses
```

## Data Pipeline

1. **Web Scraping**: YouTube transcripts collected from 3 THP channels
2. **Chunking**: Transcripts segmented into meaningful context windows
3. **Cleaning**: Low-value content, music tags, and non-athletic content filtered out
4. **Storage**: Clean dataset saved as JSONL format for efficient retrieval

## Tech Stack

- **LLM**: Hermes:8b (Mistral-based model optimized for instruction-following)
- **RAG Framework**: Custom chunking and retrieval pipeline
- **Data Format**: JSONL (JSON Lines)
- **Languages**: Python

## Key Files

- `clean_rag.py` - Data cleaning script that sanitizes raw transcripts
- `rag_dataset.jsonl` - Raw transcript chunks from YouTube
- `cleaned_rag_dataset.jsonl` - Processed dataset ready for RAG

## Dataset Characteristics

- **Total Chunks**: 74,928 (raw) → ~60,977 (cleaned after filtering)
- **Sources**: 3 YouTube channels from The Hunting Project
- **Content**: Athletic training, vertical jump technique, fitness guidance
- **Retention Rate**: 81.4% (sanitization approach preserves more content than filtering)

## Usage

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Place your API keys in .env if using external services
```

### Running the RAG System

```bash
python rag_model.py
```

### Data Cleaning

```bash
python clean_rag.py
```

## Data Cleaning Details

The cleaning process removes:
- Bracketed annotations (`[music]`, `[snorts]`, timestamps)
- Content with no athletic or training value
- Pure banter, greetings, or non-contextual segments
- While **preserving** the underlying educational content

## Project Goals

- Centralize THP training knowledge in a queryable format
- Enable quick retrieval of specific training concepts
- Provide evidence-based answers grounded in actual THP content
- Reduce manual search through hours of video content

## Future Enhancements

- Integration with web UI for easy querying
- Multi-language support
- Fine-tuning Hermes:8b on athletic domain
- Addition of more THP channel sources
- Performance metrics and answer quality evaluation

## Notes

- This is an educational tool designed for personal learning and improvement
- Always consult certified trainers for personalized advice
- The system works best with specific, focused queries about training techniques

---

**Created**: June 2026
**Status**: Active development
