# 4. Graph RAG Implementation
# 4.1 What is Graph RAG?

Graph Retrieval Augmented Generation (Graph RAG) combines knowledge graphs with RAG to provide:

Structured Knowledge: Entities and relationships in graph form

Multi-hop Reasoning: Traverse relationships for complex queries

Contextual Understanding: Understand entity relationships

Dynamic Knowledge Updates: Easily update and extend knowledge


```mermaid
graph TB
    A[Query: "Is RSA-2048 still secure?"] --> B[Query Parser]
    B --> C{Semantic Analysis}
    
    C --> D[Extract Keywords & Entities]
    C --> E[Determine Query Intent]
    
    D --> F[Graph Traversal Module]
    E --> F
    
    subgraph "Cryptographic Knowledge Graph"
        G1[Standards Nodes]
        G2[Algorithm Nodes]
        G3[Policy Nodes]
        G4[Compliance Nodes]
        G5[Best Practices Nodes]
        
        G1 -->|NIST SP 800-57| G2
        G2 -->|RSA-2048| G4
        G4 -->|FIPS 140-3| G5
        G2 -->|Security Strength| G3
        G3 -->|PCI DSS| G5
    end
    
    F --> H[Retrieve Relevant Subgraph]
    H --> I[Context Enrichment]
    
    subgraph "Vector Database"
        J1[Embedded Standards Docs]
        J2[Security Whitepapers]
        J3[Compliance Regulations]
        J4[Historical Incident Data]
    end
    
    I --> K[Semantic Search]
    K --> L[Retrieve Top-K Chunks]
    L --> M[Context Assembly]
    
    F --> N[Direct Graph Query Results]
    M --> O[Combine Graph + Vector Results]
    N --> O
    
    O --> P[Generate Comprehensive Answer]
    P --> Q["Answer: RSA-2048 provides 112-bit security,<br/>acceptable until 2030 per NIST guidelines.<br/>Consider RSA-3072 for long-term use."]
    
    Q --> R[Update Query Cache]
    Q --> S[Feedback Loop<br/>for Graph Enhancement]
    
    style G1 fill:#e3f2fd
    style G2 fill:#fce4ec
    style G3 fill:#e8f5e8
    style G4 fill:#fff3e0
    style G5 fill:#f3e5f5
```


# 4.2 Knowledge Graph for Cryptography

```
# knowledge_graph/crypto_knowledge_graph.py
from neo4j import GraphDatabase
from langchain_community.graphs import Neo4jGraph
from typing import List, Dict, Any
import json

class CryptographicKnowledgeGraph:
    """Knowledge graph for cryptographic knowledge"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.graph = Neo4jGraph(url=uri, username=user, password=password)
        self._initialize_schema()
        
    def _initialize_schema(self):
        """Initialize knowledge graph schema"""
        
        # Create constraints and indexes
        self.graph.query("""
        CREATE CONSTRAINT IF NOT EXISTS FOR (a:Algorithm) REQUIRE a.name IS UNIQUE
        """)
        
        self.graph.query("""
        CREATE CONSTRAINT IF NOT EXISTS FOR (s:Standard) REQUIRE s.name IS UNIQUE
        """)
        
        self.graph.query("""
        CREATE CONSTRAINT IF NOT EXISTS FOR (v:Vulnerability) REQUIRE v.cve_id IS UNIQUE
        """)
        
        # Load initial knowledge
        self._load_cryptographic_algorithms()
        self._load_security_standards()
        self._load_cve_database()
    
    def _load_cryptographic_algorithms(self):
        """Load cryptographic algorithms into graph"""
        
        algorithms = [
            {
                "name": "RSA",
                "type": "Asymmetric",
                "key_sizes": [1024, 2048, 3072, 4096],
                "security_level": {"2048": 112, "3072": 128, "4096": 140},
                "standard": "PKCS#1"
            },
            {
                "name": "ECDSA",
                "type": "Asymmetric",
                "curves": ["P-256", "P-384", "P-521"],
                "security_level": {"P-256": 128, "P-384": 192, "P-521": 256},
                "standard": "FIPS 186-4"
            },
            {
                "name": "AES",
                "type": "Symmetric",
                "key_sizes": [128, 192, 256],
                "modes": ["CBC", "GCM", "CTR"],
                "standard": "FIPS 197"
            }
        ]
        
        for algo in algorithms:
            self.graph.query("""
            MERGE (a:Algorithm {name: $name})
            SET a.type = $type,
                a.key_sizes = $key_sizes,
                a.security_level = $security_level,
                a.standard = $standard
            """, algo)
    
    def query_algorithm_recommendation(self, use_case: str, security_level: int):
        """Query graph for algorithm recommendations"""
        
        query = """
        MATCH (a:Algorithm)
        WHERE a.security_level[$security_param] >= $min_security
        OPTIONAL MATCH (a)-[:HAS_VULNERABILITY]->(v:Vulnerability {status: 'ACTIVE'})
        WITH a, COUNT(v) as vulnerability_count
        WHERE vulnerability_count = 0
        RETURN a.name as algorithm,
               a.type as type,
               a.security_level as security_level,
               a.standard as standard
        ORDER BY a.security_level[$security_param] DESC
        """
        
        return self.graph.query(query, {
            "min_security": security_level,
            "security_param": str(security_level)
        })
    
    def find_certificate_dependencies(self, certificate_id: str):
        """Find all dependencies of a certificate"""
        
        query = """
        MATCH (c:Certificate {id: $cert_id})
        OPTIONAL MATCH (c)-[:SIGNED_BY]->(ca:CertificateAuthority)
        OPTIONAL MATCH (c)-[:USES_KEY]->(k:Key)
        OPTIONAL MATCH (c)-[:USED_BY]->(s:Service)
        OPTIONAL MATCH (c)-[:REPLACES]->(old:Certificate)
        RETURN c, ca, k, s, old
        """
        
        return self.graph.query(query, {"cert_id": certificate_id})
```

# 4.3 Graph RAG with Vector Search

```
# rag/graph_rag.py
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PDFLoader
import hashlib

class GraphRAGSystem:
    """Graph-based RAG system for cryptographic knowledge"""
    
    def __init__(self, neo4j_uri: str, neo4j_auth: tuple):
        self.vector_store = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(),
            url=neo4j_uri,
            username=neo4j_auth[0],
            password=neo4j_auth[1],
            index_name="crypto_knowledge",
            node_label="DocumentChunk",
            text_node_properties=["text", "title", "source"],
            embedding_node_property="embedding"
        )
        
        self.knowledge_graph = CryptographicKnowledgeGraph(
            neo4j_uri, neo4j_auth[0], neo4j_auth[1]
        )
    
    def load_cryptographic_documents(self, sources: List[str]):
        """Load cryptographic documents into Graph RAG"""
        
        for source in sources:
            if source.endswith(".pdf"):
                loader = PDFLoader(source)
            else:
                loader = WebBaseLoader(source)
            
            documents = loader.load()
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # Add metadata
            for chunk in chunks:
                chunk.metadata["document_hash"] = hashlib.sha256(
                    chunk.page_content.encode()
                ).hexdigest()
                chunk.metadata["source_type"] = "cryptographic_standard"
            
            # Store in vector database
            self.vector_store.add_documents(chunks)
            
            # Extract entities and relationships for knowledge graph
            self._extract_entities_to_graph(chunks)
    
    def _extract_entities_to_graph(self, chunks):
        """Extract entities and relationships from documents to knowledge graph"""
        
        for chunk in chunks:
            # Extract cryptographic entities using NER
            entities = self._extract_crypto_entities(chunk.page_content)
            
            for entity in entities:
                # Add to knowledge graph
                self.knowledge_graph.add_entity(
                    entity_type=entity["type"],
                    name=entity["name"],
                    properties=entity.get("properties", {}),
                    source_document=chunk.metadata.get("source", "")
                )
    
    def query_with_graph_context(self, question: str, use_graph: bool = True):
        """Query with both vector search and graph traversal"""
        
        # Vector similarity search
        vector_results = self.vector_store.similarity_search(question, k=3)
        
        if use_graph:
            # Extract entities from question for graph traversal
            question_entities = self._extract_crypto_entities(question)
            
            # Query knowledge graph
            graph_results = []
            for entity in question_entities:
                # Find related entities in graph
                related = self.knowledge_graph.find_related_entities(
                    entity["name"], entity["type"], depth=2
                )
                graph_results.extend(related)
            
            # Combine results
            combined_context = self._combine_results(vector_results, graph_results)
        else:
            combined_context = vector_results
        
        # Generate answer with context
        answer = self._generate_answer(question, combined_context)
        
        return {
            "answer": answer,
            "sources": combined_context[:5],  # Top 5 sources
            "graph_entities_used": question_entities if use_graph else []
        }
```

