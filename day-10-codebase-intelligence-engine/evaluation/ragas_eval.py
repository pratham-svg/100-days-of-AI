import json
import requests
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

API_BASE = "http://localhost:8000/api/v1"


def run_evaluation():
    """
    Runs RAGAS evaluation against the golden dataset.
    Calls the live API for each question to get answers + contexts.
    """
    with open("evaluation/golden_dataset.json") as f:
        golden = json.load(f)
    
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    for item in golden:
        q = item["question"]
        response = requests.post(
            f"{API_BASE}/query",
            json={"question": q, "top_k": 5}
        ).json()
        
        questions.append(q)
        answers.append(response["answer"])
        contexts.append([s["file"] for s in response["sources"]])  # Using file refs as context
        ground_truths.append(item["ground_truth"])
    
    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })
    
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    
    print("\n=== My RAGAS Evaluation Results ===")
    print(result)
    return result


if __name__ == "__main__":
    run_evaluation()
