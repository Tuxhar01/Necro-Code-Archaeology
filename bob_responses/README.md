# Bob 2.0 Response Files

This directory contains prompts for Bob (the AI assistant) and the responses you'll save from the chat.

## Workflow

### For Classification:

1. **Necro generates a prompt file**: `{module_name}_prompt.txt`
2. **You ask Bob** (in this chat) to analyze the module using that prompt
3. **Bob provides analysis** with verdict, confidence, evidence, and reasoning
4. **You save Bob's response** as JSON to: `{module_name}_response.json`

**Expected JSON format:**
```json
{
    "verdict": "Safe to Delete" | "Secretly Load-Bearing" | "Undocumented but Valuable" | "Normal",
    "confidence": "High" | "Medium" | "Low",
    "evidence": [
        "Specific evidence item 1",
        "Specific evidence item 2"
    ],
    "reasoning": "Detailed explanation of the verdict"
}
```

### For Artifact Generation:

1. **Necro generates a prompt file**: `{module_name}_{artifact_type}_prompt.txt`
2. **You ask Bob** to generate the artifact using that prompt
3. **Bob provides the artifact** (patch, documentation, or ADR)
4. **You save Bob's response** as plain text to: `{module_name}_{artifact_type}_response.txt`

## Example

If analyzing `track_user_event`:

1. Necro creates: `track_user_event_prompt.txt`
2. You ask Bob: "Please analyze this module using the prompt in track_user_event_prompt.txt"
3. Bob responds with analysis
4. You save to: `track_user_event_response.json`

## Important

- Bob's responses must be **real analysis** of the actual code in `demo_repo/`
- No templates, no mocks - Bob inspects the real files
- Evidence must include specific line numbers and file references
- This is the actual "Bob 2.0 session" for your hackathon submission