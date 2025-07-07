# 🧠 LangGraph Multi-Agent Runner

This project includes a LangGraph-based multi-agent system for travel planning, with Docker support to run in either:

- `langgraph dev` mode (for use with LangGraph Studio/CLI)
- or standalone `Gradio` UI (custom `graphui.py` interface)

---

## 🚀 Quick Start with Docker Compose

Make sure Docker is installed, then run:

```bash
docker-compose up --build
```


On container trigger langgraph dev ui with command: 

```bash
export env=local
langgraph dev --host 0.0.0.0 --port 3030 
```

On container trigger Gradio UI with command: 

```bash
unset env
python graphui.py
```
