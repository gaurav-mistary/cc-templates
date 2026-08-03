# AI-Powered Cascade: Gemini API Integration Guide

This guide details the complete, step-by-step workflow for integrating the **Free Google Gemini API** into your `cc-cli` cascade engine. By the end of this guide, you will know exactly how to intercept a Git merge conflict during `just cc cascade`, send the conflicted file to Gemini 1.5 Flash, and automatically commit the AI-resolved file.

---

## 1. Prerequisites & Getting Your Free API Key

Google offers a generous free tier for Gemini (15 requests per minute, 1 million tokens per minute).

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** in the left sidebar and create a new key.
4. Add this key to your `cc` project's `.env` file:
   ```env
   GEMINI_API_KEY=AIzaSyYourSecretKeyHere...
   ```

---

## 2. Installing the Python SDK

You need the official Google Generative AI SDK. Since you are using `uv`, you can add it to your project:

```bash
uv add google-generativeai python-dotenv
```

---

## 3. The Conceptual Flow

Here is exactly what happens during an AI-powered cascade:

1. **The Merge Fails:** Your script attempts to merge `main` into `traefik`. A Git conflict occurs (e.g., in `docker-compose.yml`).
2. **Git Leaves Markers:** Git stops and injects `<<<<<<< HEAD`, `=======`, and `>>>>>>> upstream` into the file.
3. **The Catch:** Your Python script catches the `GitCommandError`.
4. **Identify Conflicted Files:** You query Git to find which files are conflicted.
5. **The Prompt:** You read the raw conflicted file and send it to Gemini with a strict system prompt instructing it to return *only* the resolved code.
6. **The Resolution:** You take Gemini's response, overwrite `docker-compose.yml`, run `git add .`, run `git commit -m "chore: AI resolved merge conflict"`, and successfully continue the cascade!

---

## 4. The Implementation Details (Code Examples)

### Step A: Setup the AI Client
Create a new file in your engine, e.g., `cc/ai_resolver.py`.

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

def resolve_conflict_with_ai(file_path: str, file_content: str, parent_branch: str, child_branch: str) -> str:
    """Sends the conflicted file to Gemini and returns the resolved content."""
    
    # We use Gemini 1.5 Flash because it is incredibly fast and free.
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "You are an expert DevOps engineer and Git master. Your job is to resolve Git merge conflicts. "
            "You will be given a file containing standard Git conflict markers (<<<<<<<, =======, >>>>>>>). "
            "You must understand the context, intelligently merge both sets of changes, and output the final, clean, working file. "
            "CRITICAL: Return ONLY the raw resolved file content. Do NOT include markdown formatting like ```yaml. "
            "Do NOT include any explanations. If I cannot save your output directly to disk, the pipeline will break."
        )
    )

    prompt = f"""
    The following file ({file_path}) has a merge conflict.
    We are merging the base branch '{parent_branch}' into the hybrid branch '{child_branch}'.
    Please resolve the conflict so both sets of functionality work together.
    
    FILE CONTENT:
    {file_content}
    """

    response = model.generate_content(prompt)
    
    # Strip any potential markdown code blocks the AI might accidentally include
    resolved_text = response.text.strip()
    if resolved_text.startswith("```"):
        # Remove the first line (e.g. ```yaml) and the last line (```)
        resolved_text = "\n".join(resolved_text.split("\n")[1:-1])

    return resolved_text
```

### Step B: Intercepting the Conflict in `cc/cascade.py`

When you run `repo.git.merge()`, you need to wrap it in a `try/except` block to catch the conflict.

```python
from git.exc import GitCommandError
from cc.ai_resolver import resolve_conflict_with_ai

def cascade_merge(repo, parent_branch, child_branch):
    try:
        # Attempt standard git merge
        repo.git.merge(parent_branch)
        logger.success(f"Merged {parent_branch} into {child_branch}")
        
    except GitCommandError as e:
        logger.warning(f"Merge conflict detected between {parent_branch} and {child_branch}!")
        
        # 1. Identify which files are in conflict
        unmerged_blobs = repo.index.unmerged_blobs()
        conflicted_files = list(unmerged_blobs.keys())
        
        for file_path in conflicted_files:
            logger.info(f"Asking Gemini to resolve conflict in: {file_path}")
            
            # 2. Read the conflicted file (which now contains the <<<<<<< markers)
            absolute_path = os.path.join(repo.working_dir, file_path)
            with open(absolute_path, "r") as f:
                conflicted_content = f.read()
                
            # 3. Call the Gemini API
            resolved_content = resolve_conflict_with_ai(
                file_path=file_path, 
                file_content=conflicted_content, 
                parent_branch=parent_branch, 
                child_branch=child_branch
            )
            
            # 4. Write the resolved content back to disk
            with open(absolute_path, "w") as f:
                f.write(resolved_content)
                
            # 5. Tell Git the conflict is resolved for this file
            repo.git.add(absolute_path)
            
        # 6. Complete the merge commit!
        commit_msg = f"chore: AI automatically resolved merge from {parent_branch} into {child_branch}"
        repo.git.commit("-m", commit_msg)
        
        logger.success("AI successfully resolved all conflicts and completed the merge!")
```

---

## 5. Important Considerations for Free Tier

1. **Rate Limits:** The free tier allows **15 requests per minute (RPM)**. If a cascade hits more than 15 files with conflicts at once, the API will throw a `429 Too Many Requests` error. 
   - **Solution:** Import Python's `time` module and add `time.sleep(4)` inside your conflict resolution loop to ensure you never exceed 15 RPM.
2. **Context Window:** Gemini 1.5 Flash supports 1,000,000 tokens (which is roughly 3,000 to 4,000 average sized code files). You will *never* run into size limit issues passing a `docker-compose.yml` or a `cookiecutter.json`.
3. **Data Privacy:** Because you are using the free tier, Google may use your API inputs to train their models. Since these are standard infrastructure templates (Traefik, Let's Encrypt), this is perfectly fine. However, **never hardcode real passwords or API keys** in your templates (which you are already avoiding by using post-gen hooks!).
