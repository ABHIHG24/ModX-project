import psycopg2
from core.config import DATABASE_URL

def get_new_or_updated_documents():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    documents = []

    # Projects
    cur.execute("""
        SELECT p.id, p.title, p.description, p.required_skills, p.tech_stack, u.full_name AS leader_name
        FROM projects p
        JOIN users u ON p.leader_id = u.id
        WHERE p.indexed_at IS NULL OR p.updated_at > p.indexed_at
    """)
    for row in cur.fetchall():
        project_id, title, description, required_skills, tech_stack, leader_name = row
        doc_id = f"project_{project_id}"
        doc_text = f"Project: {title}. Led by: {leader_name}. Description: {description}. Skills: {', '.join(required_skills or [])}. Tech Stack: {tech_stack}."
        metadata = {"doc_type": "project"}
        documents.append((doc_id, doc_text, metadata))

    # Users
    cur.execute("""
        SELECT id, full_name, roles, interest
        FROM users
        WHERE indexed_at IS NULL OR updated_at > indexed_at
    """)
    for row in cur.fetchall():
        user_id, full_name, roles, interest = row
        doc_id = f"user_{user_id}"
        doc_text = f"User: {full_name}. Roles: {', '.join(roles or [])}. Interests: {interest}."
        metadata = {"doc_type": "user"}
        documents.append((doc_id, doc_text, metadata))

    cur.close()
    conn.close()
    return documents

def mark_as_indexed(ids, table):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    query = f"UPDATE {table} SET indexed_at = NOW() WHERE id = ANY(%s)"
    cur.execute(query, (ids,))
    conn.commit()
    cur.close()
    conn.close()