# Recipe: The Progressive Guide to Approval Testing

**Target Audience:** AI Coding Agents (Claude, Gemini, Copilot) **Goal:** Learn to write tests that scale from simple data verification to complex behavioral narratives. **Tools:** `pytest`, `syrupy`

## The Philosophy: "Additive" Testing

Approval testing is not an "all-or-nothing" approach. You can apply it in layers depending on the complexity of the problem.

1. **Level 1 (Basic):** Snapshotting raw output.

2. **Level 2 (Clean):** Adding "Printers" to remove noise and improve readability.

3. **Level 3 (Narrative):** Adding "Storyboards" to capture sequences and behavior over time.

## Origins & Terminology

**Inspiration:** This approach is heavily inspired by the talk **"Practical Approval Testing"** by Llewellyn Falco and Lada Kesseler. Their concept of using "Printers" and "Storyboards" transforms testing into documentation.

- [Watch the Video: Practical Approval Testing](https://www.youtube.com/watch?v=QEdpE0chA-s "null")

**AKA (Also Known As):** This pattern goes by many names. While the mechanics are similar, the intent differs:

- **Approval Testing:** Focuses on human verification, readability, and "storytelling."

- **Snapshot Testing:** The modern term (popularized by Jest/React). Often implies verifying serialized data structures.

- **Golden Master Testing:** The "old school" term. Usually refers to capturing the output of legacy systems to lock down behavior before refactoring.

- **Characterization Testing:** Testing to document _what the system does now_, regardless of whether it is "correct."

## Setup (The Ingredients)

You need `pytest` for the runner and `syrupy` for the snapshot engine.

**Installation:**

```
pip install pytest syrupy
```

**Configuration (`conftest.py`):** Enable the `AmberSnapshotExtension` to handle multi-line strings beautifully.

```python
import pytest
from syrupy.extensions.amber import AmberSnapshotExtension

@pytest.fixture
def snapshot(snapshot):
    return snapshot.use_extension(AmberSnapshotExtension)
```

## Level 1: Basic Snapshot Testing

**Concept:** Instead of writing `assert x == "expected value"`, you capture the actual return value and save it.

**When to use:**

- Simple functions returning text or clean JSON.

- The output is **deterministic** (no random IDs or timestamps).

- You want to lock down the current behavior quickly (e.g., legacy code).

**Example:**

```python
def test_generate_slug(snapshot):
    # Action
    slug = generate_slug("Hello World! 2024")

    # Verification (Level 1)
    # Just snapshot the raw result.
    assert slug == snapshot
```

- _Result in file:_ `"hello-world-2024"`

## Level 2: The "Printer" Pattern (Reducing Noise)

**Problem with Level 1:** If your object contains a timestamp, a random ID, or memory address, Level 1 breaks every time you run it. Also, huge JSON blobs are hard for humans to read.

**Solution:** Write a **Printer** function that converts the complex object into a clean, readable string, hiding the "noise."

**When to use:**

- The object has dynamic fields (IDs, dates).

- The output is complex (e.g., a massive Order object) and you only care about specific business logic.

- You want non-developers to be able to read the test result.

**Example:**

```python
# The "Printer" Helper
def print_invoice(invoice):
    # We explicitly format meaningful data and IGNORE random IDs/Dates
    return f"""
    Invoice For: {invoice['customer_name']}
    Total:       ${invoice['total']:.2f}
    Items:       {len(invoice['items'])}
    Status:      {invoice['status']}
    """

def test_create_invoice(snapshot):
    invoice = create_invoice(user="Alice", items=["Book", "Pen"])

    # Verification (Level 2)
    # Pass the object through the printer first!
    assert print_invoice(invoice) == snapshot
```

## Level 3: The "Storyboard" Pattern (Testing Narratives)

**Problem with Level 2:** Printers are great for _state_, but bad for _flow_. If a user interacts with a system (like a Chatbot or Game), verifying one single step doesn't tell you if the conversation makes sense.

**Solution:** Record a sequence of interactions into a list (a **Storyboard**) and snapshot the entire history at the end.

**When to use:**

- **Chatbots / AI Agents:** verifying conversation flow.

- **Games:** verifying turns (Player 1 moves, Player 2 moves).

- **Workflows:** Shopping carts, multi-step wizards.

**Example:**

```python
def test_chatbot_conversation(snapshot):
    bot = ChatBot()
    story = []  # The Storyboard

    # Helper to append to the story
    def ask(message):
        story.append(f"USER: {message}")
        response = bot.reply(message)
        story.append(f"BOT : {response}")
        story.append("-" * 20)

    # The Narrative (Level 3)
    ask("Hello, who are you?")
    ask("What is 2 + 2?")
    ask("Goodbye")

    # Verification
    # Join the whole story and snapshot it as one document.
    assert "\n".join(story) == snapshot
```

## Execution & Workflow

**For the Agent (You):** Tests will fail on the first run. You must instruct the user to "Approve" the result.

1. **Run Tests:** `pytest`

    - _Result:_ Fail (Snapshot not found).

2. **Approve (Update) Snapshots:** `pytest --snapshot-update`

    - _Result:_ Syrupy creates `.ambr` files.

3. **Verify:**

    - Ask the user to read the generated file. Does the Story/Printer output look correct? If yes, commit it.

## Summary Cheat Sheet

| **Level** |   **Pattern**    |               **Best For...**               |                      **Code Snippet**                       |
|-------|--------------|-----------------------------------------|---------------------------------------------------------|
|   **1**   | **Raw Snapshot** |   Simple, deterministic strings/JSON.   |                `assert result == snapshot`                |
|   **2**   |   **Printer**    | Complex objects with IDs/Dates (Noise). |          `assert print_obj(result) == snapshot`           |
|   **3**   |  **Storyboard**  |     Sequences, interactions, flows.     | `story.append(step); assert "\n".join(story) == snapshot` |
