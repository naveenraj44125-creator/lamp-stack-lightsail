const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { db } = require('../database/init');

const router = express.Router();

// Get all notes
router.get('/', (req, res) => {
  const notes = db.prepare('SELECT * FROM notes ORDER BY updated_at DESC').all();
  res.json(notes);
});

// Get single note
router.get('/:id', (req, res) => {
  const note = db.prepare('SELECT * FROM notes WHERE id = ?').get(req.params.id);
  if (!note) return res.status(404).json({ error: 'Note not found' });
  res.json(note);
});

// Create note
router.post('/', (req, res) => {
  const { title, content } = req.body;
  if (!title) return res.status(400).json({ error: 'Title is required' });
  
  const id = uuidv4();
  const stmt = db.prepare('INSERT INTO notes (id, title, content) VALUES (?, ?, ?)');
  stmt.run(id, title, content || '');
  
  const note = db.prepare('SELECT * FROM notes WHERE id = ?').get(id);
  res.status(201).json(note);
});

// Update note
router.put('/:id', (req, res) => {
  const { title, content } = req.body;
  const stmt = db.prepare('UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
  const result = stmt.run(title, content, req.params.id);
  
  if (result.changes === 0) return res.status(404).json({ error: 'Note not found' });
  
  const note = db.prepare('SELECT * FROM notes WHERE id = ?').get(req.params.id);
  res.json(note);
});

// Delete note
router.delete('/:id', (req, res) => {
  const result = db.prepare('DELETE FROM notes WHERE id = ?').run(req.params.id);
  if (result.changes === 0) return res.status(404).json({ error: 'Note not found' });
  res.json({ message: 'Note deleted' });
});

module.exports = router;
