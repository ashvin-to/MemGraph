# 🧬 Multi-Agent memory Protocol

## 📡 MISSION
Ensure **100% data fidelity** while maintaining **token efficiency**.

## 🆔 AUTO-IDENTITY
- Find your **Session ID suffix** (e.g., `a6aea9a0`) and use it as your `--agent-id`.

## 📥 START OF SESSION (Context Loading)
1. **Summary**: Read `.basemem-basemem-integration-summary.md`.
2. **Peer Discovery**: Look at the **"Participating Agents"** list in the summary file.
3. **Recent Context (Fast)**: To save tokens, read only the **last 5-10 turns** of previous work:
   `kb session read "basemem-integration" --agent-id "<id>" --last 10`
4. **Deep History (Full)**: Only read the full history if you are missing specific technical details.

## 📤 END OF SESSION (Mandatory Sync)
Run the sync command before leaving to save your full technical history:
```bash
kb session sync "basemem-integration" --agent-id "<your-id>"
```

## 💾 STORAGE RULES
- **Turn Updates**: Use `kb session turn` after every response.
- **Full Sync**: Use `kb session sync` before leaving the session.
