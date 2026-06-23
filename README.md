---
title: ThreadMind AI
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "6.19.0"
python_version: "3.12"
app_file: app.py
pinned: false
---

# ThreadMind AI

A multi-user, multi-conversation AI assistant demonstrating LangChain memory, Supabase chat history, and conversation-level thread isolation.

## Core idea

`conversation_id = LangChain thread_id`

Supabase stores users, conversations, and visible messages. LangChain stores short-term agent memory with `InMemorySaver`.
