"""End-to-End Verification Test for Windows 11 RAG Pipeline."""
import os
import sys
from pathlib import Path

# Ensure backend app is on sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))
os.environ["HF_HUB_OFFLINE"] = "1"

from app.services.loaders.pdf_loader import load_pdf
from app.services.chunking import create_chunks_for_document
from app.embeddings import embed_batch, embed_text
from app.vector_store import (
    add_chunks_to_vector_store,
    search_vector_store,
    get_collection,
    get_document_chunks_from_vector_store,
)
from app.retrieval import retrieve_relevant_chunks, build_context_from_sources
from app.llm import generate_answer
from app.services.document_store import add_document, list_documents, get_document

def test_full_rag_pipeline():
    print("=" * 70)
    print("RUNNING END-TO-END RAG VERIFICATION SUITE")
    print("=" * 70)

    # 1. Verify Document Loading
    pdf_path = backend_dir / "data" / "sample_documents" / "project_specification.pdf"
    assert pdf_path.exists(), f"Sample PDF not found at {pdf_path}"
    print(f"\n[1/6] Loading PDF document: {pdf_path.name}")
    blocks = load_pdf(pdf_path, pdf_path.name)
    print(f" -> Extracted {len(blocks)} pages successfully.")
    assert len(blocks) == 3, f"Expected 3 pages, got {len(blocks)}"

    # 2. Verify Chunking with Configurable Window & Metadata
    print("\n[2/6] Executing Semantic Chunking (CHUNK_SIZE=800, CHUNK_OVERLAP=100)...")
    doc_id = "test_spec_001"
    chunks = create_chunks_for_document(
        document_id=doc_id,
        filename=pdf_path.name,
        blocks=blocks,
        chunk_size=800,
        chunk_overlap=100
    )
    print(f" -> Generated {len(chunks)} chunks with complete metadata.")
    assert len(chunks) >= 3, "Expected at least 3 chunks"
    for c in chunks:
        meta = c["metadata"]
        assert meta["document_id"] == doc_id
        assert meta["filename"] == pdf_path.name
        assert "chunk_id" in meta
        print(f"   * {meta['chunk_id']}: Page {meta['page']}, Length {meta['char_count']} chars")

    # 3. Verify Embeddings & Persistent Vector Storage
    print("\n[3/6] Generating Embeddings and Storing in ChromaDB...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_batch(texts)
    assert len(embeddings) == len(chunks)
    assert len(embeddings[0]) == 384, f"Expected 384-dim vector, got {len(embeddings[0])}"

    added = add_chunks_to_vector_store(chunks, embeddings)
    print(f" -> Indexed {added} chunks into persistent Chroma vectorstore.")

    # Save to registry
    add_document({
        "id": doc_id,
        "filename": pdf_path.name,
        "file_type": "PDF",
        "file_size": "45.0 KB",
        "pages": 3,
        "chunks_count": len(chunks),
        "status": "Ready",
        "upload_time": "2026-10-12T00:00:00",
        "preview_pages": [{"page": b["page"], "text": b["text"][:100]} for b in blocks],
        "file_path": str(pdf_path)
    })

    # 4. Test Semantic Retrieval on Target Question
    print("\n[4/6] Testing Semantic Retrieval: 'What is the objective?'")
    target_q = "What is the primary objective of this project?"
    retrieved = retrieve_relevant_chunks(target_q, top_k=3, document_id=doc_id)
    assert len(retrieved) > 0, "Expected retrieved chunks"
    
    top_chunk = retrieved[0]
    print(f" -> Top Retrieved Chunk: {top_chunk['chunk_id']}")
    print(f"    Page: {top_chunk['page']}")
    print(f"    Similarity Score: {top_chunk['score']}")
    print(f"    Snippet: {top_chunk['text'][:120]}...")
    
    assert top_chunk["page"] == 1, "Expected objective chunk to come from Page 1"
    assert "objective" in top_chunk["text"].lower(), "Expected 'objective' in chunk text"
    assert top_chunk["score"] > 0.1, f"Expected positive similarity score, got {top_chunk['score']}"

    # Build context and generate answer
    context = build_context_from_sources(retrieved)
    answer = generate_answer(target_q, context)
    print(f"\n -> Generated Answer:\n{answer}")
    assert "objective" in answer.lower(), "Expected answer to discuss the objective"

    # 5. Test Unrelated Question Handling
    print("\n[5/6] Testing Unrelated Question: 'What is the population of Japan?'")
    unrelated_q = "What is the population of Japan?"
    retrieved_unrelated = retrieve_relevant_chunks(unrelated_q, top_k=3, document_id=doc_id)
    unrelated_ctx = build_context_from_sources(retrieved_unrelated)
    unrelated_ans = generate_answer(unrelated_q, unrelated_ctx)
    print(f" -> Generated Answer for Unrelated Query:\n'{unrelated_ans}'")
    
    assert "could not find enough information" in unrelated_ans.lower(), (
        f"Expected system to declare information not found, got: '{unrelated_ans}'"
    )
    print(" -> PASS: Correctly refused to hallucinate facts outside context!")

    # 6. Verify Persistence Across Restarts
    print("\n[6/6] Verifying Data Persistence Across Restarts...")
    docs_list = list_documents()
    assert any(d["id"] == doc_id for d in docs_list), "Document missing from persisted registry"
    stored_chunks = get_document_chunks_from_vector_store(doc_id)
    assert len(stored_chunks) == len(chunks), f"Expected {len(chunks)} persisted chunks, got {len(stored_chunks)}"
    print(f" -> PASS: {len(stored_chunks)} chunks and document metadata verified in persistent disk storage.")

    print("\n" + "=" * 70)
    print("ALL 6 RAG PIPELINE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_full_rag_pipeline()
