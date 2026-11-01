"""
Concurrency unit tests for SQLite database under multi-threaded operations.
Verifies WAL (Write-Ahead Logging) mode and busy timeout eliminate write-locking (FAULT-09).
"""
import concurrent.futures
import uuid
from backend.db.session import SessionLocal
from backend.models.database import ConversationModel, MessageModel

def create_and_delete_session(session_id: str):
    db = SessionLocal()
    try:
        # 1. Insert conversation
        conv = ConversationModel(session_id=session_id, language="en", user_profile_snapshot={"test": 1})
        db.add(conv)
        db.commit()

        # 2. Insert messages
        msg1 = MessageModel(conversation_id=session_id, sender="user", message_text="Hello test")
        msg2 = MessageModel(conversation_id=session_id, sender="assistant", message_text="Hi there")
        db.add_all([msg1, msg2])
        db.commit()

        # 3. Read back
        count = db.query(MessageModel).filter(MessageModel.conversation_id == session_id).count()
        assert count == 2

        # 4. Delete
        db.query(MessageModel).filter(MessageModel.conversation_id == session_id).delete(synchronize_session=False)
        db.query(ConversationModel).filter(ConversationModel.session_id == session_id).delete(synchronize_session=False)
        db.commit()
        return True
    finally:
        db.close()

def test_concurrent_sqlite_writes():
    """Executes 20 concurrent sessions reading and writing simultaneously without OperationalError."""
    session_ids = [f"concurrent-test-{uuid.uuid4()}" for _ in range(20)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(create_and_delete_session, session_ids))
    assert all(results)
    assert len(results) == 20

