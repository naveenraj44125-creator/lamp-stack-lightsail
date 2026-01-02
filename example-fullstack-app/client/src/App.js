import React, { useState, useEffect } from 'react';

const API_URL = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5001/api';

function App() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const res = await fetch(`${API_URL}/notes`);
      const data = await res.json();
      setNotes(data);
    } catch (err) {
      console.error('Error fetching notes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      if (editingId) {
        await fetch(`${API_URL}/notes/${editingId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, content })
        });
      } else {
        await fetch(`${API_URL}/notes`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, content })
        });
      }
      setTitle('');
      setContent('');
      setEditingId(null);
      fetchNotes();
    } catch (err) {
      console.error('Error saving note:', err);
    }
  };

  const handleEdit = (note) => {
    setTitle(note.title);
    setContent(note.content || '');
    setEditingId(note.id);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this note?')) return;
    try {
      await fetch(`${API_URL}/notes/${id}`, { method: 'DELETE' });
      fetchNotes();
    } catch (err) {
      console.error('Error deleting note:', err);
    }
  };

  const styles = {
    container: { maxWidth: '800px', margin: '0 auto', padding: '20px' },
    header: { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', padding: '30px', borderRadius: '12px', marginBottom: '30px', textAlign: 'center' },
    form: { background: '#f8f9fa', padding: '20px', borderRadius: '12px', marginBottom: '30px' },
    input: { width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid #ddd', borderRadius: '8px', fontSize: '16px' },
    textarea: { width: '100%', padding: '12px', marginBottom: '12px', border: '1px solid #ddd', borderRadius: '8px', fontSize: '16px', minHeight: '100px', resize: 'vertical' },
    button: { background: '#667eea', color: 'white', border: 'none', padding: '12px 24px', borderRadius: '8px', cursor: 'pointer', fontSize: '16px' },
    noteCard: { background: 'white', border: '1px solid #e0e0e0', borderRadius: '12px', padding: '20px', marginBottom: '16px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' },
    noteTitle: { fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: '#333' },
    noteContent: { color: '#666', marginBottom: '12px', whiteSpace: 'pre-wrap' },
    noteDate: { fontSize: '12px', color: '#999' },
    actions: { marginTop: '12px' },
    editBtn: { background: '#28a745', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', marginRight: '8px' },
    deleteBtn: { background: '#dc3545', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>📝 Notes App</h1>
        <p>Fullstack React + Node.js Application</p>
      </div>

      <form style={styles.form} onSubmit={handleSubmit}>
        <input style={styles.input} type="text" placeholder="Note title..." value={title} onChange={(e) => setTitle(e.target.value)} required />
        <textarea style={styles.textarea} placeholder="Note content..." value={content} onChange={(e) => setContent(e.target.value)} />
        <button style={styles.button} type="submit">{editingId ? 'Update Note' : 'Add Note'}</button>
        {editingId && <button style={{...styles.button, background: '#6c757d', marginLeft: '8px'}} type="button" onClick={() => { setTitle(''); setContent(''); setEditingId(null); }}>Cancel</button>}
      </form>

      {loading ? (
        <p style={{textAlign: 'center', color: '#666'}}>Loading notes...</p>
      ) : notes.length === 0 ? (
        <p style={{textAlign: 'center', color: '#666'}}>No notes yet. Create your first note!</p>
      ) : (
        notes.map(note => (
          <div key={note.id} style={styles.noteCard}>
            <div style={styles.noteTitle}>{note.title}</div>
            {note.content && <div style={styles.noteContent}>{note.content}</div>}
            <div style={styles.noteDate}>Updated: {new Date(note.updated_at).toLocaleString()}</div>
            <div style={styles.actions}>
              <button style={styles.editBtn} onClick={() => handleEdit(note)}>Edit</button>
              <button style={styles.deleteBtn} onClick={() => handleDelete(note.id)}>Delete</button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default App;
